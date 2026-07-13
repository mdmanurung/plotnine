"""
Beeswarm offset algorithms.

Pure-Python implementations of the beeswarm and quasirandom
jittering algorithms, ported from the R packages ``beeswarm``
and ``vipor``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray


# -------------------------------------------------------------------
# Van der Corput sequence (used by quasirandom)
# -------------------------------------------------------------------


def van_der_corput(n: int, base: int = 2) -> NDArray[np.float64]:
    """
    Generate the first *n* elements of the van der Corput
    low-discrepancy sequence in the given *base*.

    Values lie in (0, 1) and are well-distributed.
    """
    seq = np.zeros(n, dtype=np.float64)
    for i in range(n):
        q = 0.0
        denom = 1.0
        m = i + 1
        while m > 0:
            denom *= base
            q += (m % base) / denom
            m //= base
        seq[i] = q
    return seq


# -------------------------------------------------------------------
# Quasirandom offset (density-aware jitter)
# -------------------------------------------------------------------


def _kde_density(
    values: NDArray[np.float64],
    bandwidth: float = 0.5,
    nbins: int | None = None,
) -> NDArray[np.float64]:
    """
    Estimate density at each data point using a Gaussian KDE.

    Returns an array of density values the same length as *values*.
    """
    from scipy.stats import gaussian_kde

    if len(values) < 2:
        return np.ones_like(values)

    try:
        kde = gaussian_kde(values, bw_method=bandwidth)
        density = kde(values)
    except np.linalg.LinAlgError:
        density = np.ones_like(values)

    # Normalize so max == 1
    dmax = density.max()
    if dmax > 0:
        density /= dmax
    return density


def offset_quasirandom(
    values: NDArray[np.float64],
    *,
    method: str = "quasirandom",
    width: float = 0.4,
    bandwidth: float = 0.5,
    nbins: int | None = None,
    varwidth: bool = False,
    group_count: int | None = None,
    total_count: int | None = None,
) -> NDArray[np.float64]:
    """
    Compute quasi-random x-offsets for a single group.

    Parameters
    ----------
    values
        The data-axis values (e.g. y in a vertical plot).
    method
        ``"quasirandom"`` (van der Corput) or ``"pseudorandom"``.
    width
        Maximum spread of the jitter.
    bandwidth
        Bandwidth adjustment for KDE.
    nbins
        Number of bins for density estimation (unused, kept for
        API compatibility).
    varwidth
        If *True*, scale width by relative group size.
    group_count
        Size of this group (for *varwidth*).
    total_count
        Total number of observations (for *varwidth*).

    Returns
    -------
    offsets
        Array of horizontal offsets, centred around 0.
    """
    n = len(values)
    if n == 0:
        return np.array([], dtype=np.float64)
    if n == 1:
        return np.zeros(1, dtype=np.float64)

    # Density at each point
    density = _kde_density(values, bandwidth=bandwidth, nbins=nbins)

    # Base jitter values in (-0.5, 0.5)
    if method == "pseudorandom":
        rng = np.random.default_rng()
        jitter = rng.uniform(-0.5, 0.5, size=n)
    else:
        # quasirandom (default): van der Corput sequence
        vdc = van_der_corput(n)
        jitter = vdc - 0.5  # centre around 0

    # Scale by density so dense regions are wider
    offsets = jitter * density

    # Scale to desired width
    if varwidth and group_count and total_count and total_count > 0:
        scale = group_count / total_count
    else:
        scale = 1.0

    offsets *= width * scale
    return offsets


# -------------------------------------------------------------------
# Beeswarm offset (avoid-overlap placement)
# -------------------------------------------------------------------


def offset_beeswarm(
    values: NDArray[np.float64],
    *,
    method: str = "swarm",
    cex: float = 1.0,
    side: int = 0,
    priority: str = "ascending",
    point_size: float | None = None,
) -> NDArray[np.float64]:
    """
    Compute beeswarm x-offsets for a single group.

    Parameters
    ----------
    values
        Data-axis values (e.g. y-coordinates for a vertical plot).
    method
        ``"swarm"`` (default), ``"compactswarm"``, ``"center"``,
        ``"square"``, or ``"hex"``.
    cex
        Scaling factor for point spacing (higher = more spread).
    side
        ``0``: both sides, ``1``: right/up only,
        ``-1``: left/down only.
    priority
        Order in which points are placed: ``"ascending"`` (default),
        ``"descending"``, ``"density"``, ``"random"``, ``"none"``.
    point_size
        Physical size of a point in data units.  If *None* an
        estimate is derived from the data range.

    Returns
    -------
    offsets
        Horizontal offsets centred around 0.
    """
    n = len(values)
    if n == 0:
        return np.array([], dtype=np.float64)
    if n == 1:
        return np.zeros(1, dtype=np.float64)

    # Estimate point size in data-axis units
    if point_size is None:
        val_range = values.max() - values.min()
        point_size = 1.0 if val_range == 0 else val_range / max(n, 10)
    point_size *= cex

    if method in ("swarm", "compactswarm"):
        return _swarm(values, point_size, method, priority, side)
    if method in ("center", "centre"):
        return _grid(values, point_size, side, mode="center")
    if method == "hex":
        return _grid(values, point_size, side, mode="hex")
    # default: "square"
    return _grid(values, point_size, side, mode="square")


def _order_indices(
    values: NDArray[np.float64], priority: str
) -> NDArray[np.intp]:
    """Return indices in the desired placement order."""
    if priority == "descending":
        return np.argsort(-values)
    if priority == "random":
        idx = np.arange(len(values))
        np.random.default_rng().shuffle(idx)
        return idx
    if priority == "density":
        from scipy.stats import gaussian_kde

        try:
            kde = gaussian_kde(values)
            density = kde(values)
        except np.linalg.LinAlgError:
            density = np.ones_like(values)
        return np.argsort(-density)
    if priority == "none":
        return np.arange(len(values))
    # ascending (default)
    return np.argsort(values)


def _swarm(
    values: NDArray[np.float64],
    point_size: float,
    method: str,
    priority: str,
    side: int,
) -> NDArray[np.float64]:
    """
    Core swarm algorithm: place points one at a time, shifting
    sideways by the minimum amount needed to avoid overlap.
    """
    n = len(values)
    offsets = np.zeros(n, dtype=np.float64)
    order = _order_indices(values, priority)

    placed_y = np.empty(0, dtype=np.float64)
    placed_x = np.empty(0, dtype=np.float64)

    for idx in order:
        y_i = values[idx]

        if len(placed_y) == 0:
            offsets[idx] = 0.0
            placed_y = np.append(placed_y, y_i)
            placed_x = np.append(placed_x, 0.0)
            continue

        # Find all previously placed points within point_size
        # distance on the data axis
        dy = np.abs(placed_y - y_i)
        neighbours = dy < point_size

        if not neighbours.any():
            offsets[idx] = 0.0
        else:
            # For each overlapping neighbour, compute the
            # minimum horizontal distance needed
            neighbour_x = placed_x[neighbours]
            neighbour_dy = dy[neighbours]

            # From the overlap circle: dx² + dy² >= d²
            # => dx >= sqrt(d² - dy²)
            min_dx = np.sqrt(np.maximum(point_size**2 - neighbour_dy**2, 0))

            if method == "compactswarm":
                x_i = _compact_place(neighbour_x, min_dx, side)
            else:
                x_i = _swarm_place(neighbour_x, min_dx, side)
            offsets[idx] = x_i

        placed_y = np.append(placed_y, y_i)
        placed_x = np.append(placed_x, offsets[idx])

    return offsets


def _swarm_place(
    neighbour_x: NDArray[np.float64],
    min_dx: NDArray[np.float64],
    side: int,
) -> float:
    """
    Find the closest valid x-position to 0 that does not overlap
    with any neighbour.
    """
    # Candidate positions: for each neighbour, try placing on
    # both sides
    candidates = []
    for nx, mdx in zip(neighbour_x, min_dx):
        candidates.append(nx + mdx)
        candidates.append(nx - mdx)
    candidates.append(0.0)

    # Filter by side constraint
    if side == 1:
        candidates = [c for c in candidates if c >= -1e-10]
    elif side == -1:
        candidates = [c for c in candidates if c <= 1e-10]

    if not candidates:
        candidates = [0.0]

    # Check each candidate for validity (no overlap)
    valid = []
    for c in candidates:
        dists = np.abs(neighbour_x - c)
        if np.all(dists >= min_dx - 1e-10):
            valid.append(c)

    if valid:
        # Return the candidate closest to 0
        valid_arr = np.array(valid)
        return float(valid_arr[np.argmin(np.abs(valid_arr))])

    # Fallback: place at outer edge
    if side >= 0:
        return float(np.max(neighbour_x + min_dx))
    return float(np.min(neighbour_x - min_dx))


def _compact_place(
    neighbour_x: NDArray[np.float64],
    min_dx: NDArray[np.float64],
    side: int,
) -> float:
    """
    Compact placement: find the position closest to 0 that
    does not overlap, searching outward from centre.
    """
    # Generate candidate positions more densely
    candidates = [0.0]
    for nx, mdx in zip(neighbour_x, min_dx):
        candidates.append(nx + mdx)
        candidates.append(nx - mdx)

    if side == 1:
        candidates = [c for c in candidates if c >= -1e-10]
    elif side == -1:
        candidates = [c for c in candidates if c <= 1e-10]

    if not candidates:
        candidates = [0.0]

    # Sort by distance from 0 (compact placement)
    candidates.sort(key=abs)

    for c in candidates:
        dists = np.abs(neighbour_x - c)
        if np.all(dists >= min_dx - 1e-10):
            return float(c)

    # Fallback
    if side >= 0:
        return float(np.max(neighbour_x + min_dx))
    return float(np.min(neighbour_x - min_dx))


def _grid(
    values: NDArray[np.float64],
    point_size: float,
    side: int,
    mode: str = "square",
) -> NDArray[np.float64]:
    """
    Place points on a regular grid (square, hex, or centred).
    """
    n = len(values)
    if n == 0:
        return np.array([], dtype=np.float64)

    # Bin the values
    val_min, val_max = values.min(), values.max()
    val_range = val_max - val_min

    if val_range == 0:
        # All same value: arrange in a line
        offsets = np.arange(n, dtype=np.float64) - (n - 1) / 2.0
        offsets *= point_size
        return _apply_side(offsets, side)

    n_bins = max(1, int(np.ceil(val_range / point_size)))
    bin_edges = np.linspace(val_min, val_max + 1e-10, n_bins + 1)
    bin_idx = np.digitize(values, bin_edges) - 1
    bin_idx = np.clip(bin_idx, 0, n_bins - 1)

    offsets = np.zeros(n, dtype=np.float64)

    for b in range(n_bins):
        mask = bin_idx == b
        count = mask.sum()
        if count == 0:
            continue

        positions = np.arange(count, dtype=np.float64)
        positions -= (count - 1) / 2.0  # centre around 0
        positions *= point_size

        if mode == "hex" and b % 2 == 1:
            positions += point_size * 0.5

        if mode == "center":
            # Re-centre so the swarm is symmetric
            positions -= positions.mean()

        offsets[mask] = positions

    return _apply_side(offsets, side)


def _apply_side(
    offsets: NDArray[np.float64], side: int
) -> NDArray[np.float64]:
    """Shift offsets to one side if requested."""
    if side == 1:
        offsets = np.abs(offsets)
    elif side == -1:
        offsets = -np.abs(offsets)
    return offsets


# -------------------------------------------------------------------
# Corral helpers
# -------------------------------------------------------------------


def corral_points(
    offsets: NDArray[np.float64],
    method: str = "none",
    width: float = 0.9,
) -> NDArray[np.float64]:
    """
    Handle runaway points that extend beyond the corral boundary.

    Parameters
    ----------
    offsets
        Horizontal offsets.
    method
        ``"none"``: no correction,
        ``"gutter"``: clamp to boundary,
        ``"wrap"``: periodic wrap,
        ``"random"``: random within boundary,
        ``"omit"``: set to NaN.
    width
        Half-width of the corral region.
    """
    if method == "none":
        return offsets

    half = width / 2.0
    out_of_bounds = np.abs(offsets) > half

    if not out_of_bounds.any():
        return offsets

    offsets = offsets.copy()

    if method == "gutter":
        offsets = np.clip(offsets, -half, half)
    elif method == "wrap":
        offsets[out_of_bounds] = (
            (offsets[out_of_bounds] + half) % width
        ) - half
    elif method == "random":
        rng = np.random.default_rng()
        n_out = out_of_bounds.sum()
        offsets[out_of_bounds] = rng.uniform(-half, half, size=n_out)
    elif method == "omit":
        offsets[out_of_bounds] = np.nan

    return offsets
