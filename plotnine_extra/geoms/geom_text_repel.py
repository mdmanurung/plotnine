"""
``geom_text_repel`` / ``geom_label_repel``: text labels with
force-directed repulsion to avoid overlaps, inspired by R's
``ggrepel`` package.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from plotnine.doctools import document
from plotnine.geoms.geom_text import geom_text

if TYPE_CHECKING:
    from typing import Any

    import pandas as pd
    from matplotlib.axes import Axes
    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view


def _repel_labels(
    x: np.ndarray,
    y: np.ndarray,
    labels: np.ndarray,
    ax: Axes,
    *,
    fontsize: float,
    box_padding: float,
    point_padding: float,
    force: float,
    max_iter: int,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    seed: int,
    min_segment_length: float,
    direction: str,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Force-directed label placement algorithm.

    Iteratively pushes overlapping labels apart so they no
    longer occlude each other or the data points they annotate.

    Parameters
    ----------
    x, y
        Original data-point positions.
    labels
        Text strings for each point.
    ax
        Matplotlib *Axes* (unused; reserved for future
        bounding-box queries).
    fontsize
        Average font size, used to estimate text extent.
    box_padding
        Padding around text boxes as a fraction of the
        axis range.
    point_padding
        Padding around data points as a fraction of the
        axis range.
    force
        Repulsion force multiplier.
    max_iter
        Maximum number of iterations.
    xlim, ylim
        Axis limits used to clamp labels inside the plot.
    seed
        Random seed for reproducibility.
    min_segment_length
        Minimum segment length (fraction of x-range) below
        which no connector line is drawn.
    direction
        ``"both"``, ``"x"``, or ``"y"``: restricts which
        axes are affected by repulsion.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Adjusted *(x, y)* label positions.
    """
    n = len(x)
    if n == 0:
        return np.array([]), np.array([])

    rng = np.random.default_rng(seed)

    # Work on float copies
    lx = x.copy().astype(float)
    ly = y.copy().astype(float)

    # Small initial jitter to break exact ties
    lx += rng.uniform(-0.01, 0.01, n)
    ly += rng.uniform(-0.01, 0.01, n)

    x_range = xlim[1] - xlim[0] if xlim[1] > xlim[0] else 1.0
    y_range = ylim[1] - ylim[0] if ylim[1] > ylim[0] else 1.0

    # Approximate text dimensions in data coordinates
    char_w = x_range * 0.015
    text_h = y_range * 0.035

    widths = np.array(
        [len(str(l)) * char_w + 2 * box_padding * x_range for l in labels]
    )
    heights = np.array([text_h + 2 * box_padding * y_range for _ in labels])

    pt_pad_x = point_padding * x_range
    pt_pad_y = point_padding * y_range

    for _iteration in range(max_iter):
        moved = False

        for i in range(n):
            fx, fy = 0.0, 0.0

            # --- repel from other labels ---
            for j in range(n):
                if i == j:
                    continue
                dx = lx[i] - lx[j]
                dy = ly[i] - ly[j]

                ovlp_x = (widths[i] + widths[j]) / 2 - abs(dx)
                ovlp_y = (heights[i] + heights[j]) / 2 - abs(dy)

                if ovlp_x > 0 and ovlp_y > 0:
                    dist = max(np.sqrt(dx**2 + dy**2), 0.001)
                    if direction != "y":
                        fx += force * dx / dist * ovlp_x / x_range
                    if direction != "x":
                        fy += force * dy / dist * ovlp_y / y_range

            # --- repel from data points ---
            for j in range(n):
                if i == j:
                    continue
                dx = lx[i] - x[j]
                dy = ly[i] - y[j]
                dist = max(np.sqrt(dx**2 + dy**2), 0.001)

                close_x = widths[i] / 2 + pt_pad_x - abs(dx)
                close_y = heights[i] / 2 + pt_pad_y - abs(dy)

                if close_x > 0 and close_y > 0:
                    if direction != "y":
                        fx += force * 0.5 * dx / dist
                    if direction != "x":
                        fy += force * 0.5 * dy / dist

            # Apply forces
            if abs(fx) > 1e-6 or abs(fy) > 1e-6:
                lx[i] += fx * x_range * 0.1
                ly[i] += fy * y_range * 0.1
                moved = True

            # Clamp to plot boundaries
            half_w = widths[i] / 2
            half_h = heights[i] / 2
            lx[i] = np.clip(
                lx[i],
                xlim[0] + half_w,
                xlim[1] - half_w,
            )
            ly[i] = np.clip(
                ly[i],
                ylim[0] + half_h,
                ylim[1] - half_h,
            )

        if not moved:
            break

    return lx, ly


# ----- aesthetic / parameter helpers -----

_text_repel_aes = geom_text.DEFAULT_AES.copy()
_text_repel_aes.update(
    {
        "color": "black",
        "alpha": 1,
        "size": 8,
        "angle": 0,
    }
)

_text_repel_params = geom_text.DEFAULT_PARAMS.copy()
_text_repel_params.update(
    {
        "box_padding": 0.01,
        "point_padding": 0.01,
        "force": 1.0,
        "max_iter": 500,
        "seed": 42,
        "min_segment_length": 0.01,
        "segment_color": "grey",
        "segment_alpha": 0.6,
        "segment_size": 0.5,
        "direction": "both",
    }
)


def _draw_repelled_text(
    data: pd.DataFrame,
    panel_params: panel_view,
    coord: coord,
    ax: Axes,
    params: dict[str, Any],
    *,
    use_bbox: bool = False,
) -> None:
    """
    Shared drawing logic for *geom_text_repel* and
    *geom_label_repel*.
    """
    data = coord.transform(data, panel_params)

    if len(data) == 0:
        return

    x = data["x"].to_numpy(dtype=float)
    y = data["y"].to_numpy(dtype=float)
    labels = data["label"].to_numpy()

    mask = np.array([bool(str(l).strip()) for l in labels])
    if not mask.any():
        return

    x = x[mask]
    y = y[mask]
    labels = labels[mask]

    colors = data["color"].to_numpy()[mask]
    alphas = data["alpha"].to_numpy(dtype=float)[mask]
    sizes = data["size"].to_numpy(dtype=float)[mask]

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    fontsize = float(np.mean(sizes))

    new_x, new_y = _repel_labels(
        x,
        y,
        labels,
        ax,
        fontsize=fontsize,
        box_padding=params["box_padding"],
        point_padding=params["point_padding"],
        force=params["force"],
        max_iter=params["max_iter"],
        xlim=xlim,
        ylim=ylim,
        seed=params["seed"],
        min_segment_length=params["min_segment_length"],
        direction=params["direction"],
    )

    seg_color = params["segment_color"]
    seg_alpha = params["segment_alpha"]
    seg_size = params["segment_size"]
    min_seg = params["min_segment_length"]
    zorder = params.get("zorder", 3)
    ha = params.get("ha", "center")
    va = params.get("va", "center")

    x_range = xlim[1] - xlim[0] if xlim[1] > xlim[0] else 1.0

    # Optional label-box settings
    if use_bbox:
        fills = (
            data["fill"].to_numpy()[mask]
            if "fill" in data.columns
            else np.array(["white"] * int(mask.sum()))
        )
        label_pad = params.get("label_padding", 0.25)
        fill_alpha = params.get("fill_alpha", 0.8)

    for i in range(len(labels)):
        # --- connector segment ---
        dist = np.sqrt((new_x[i] - x[i]) ** 2 + (new_y[i] - y[i]) ** 2)
        if dist > min_seg * x_range:
            ax.plot(
                [x[i], new_x[i]],
                [y[i], new_y[i]],
                color=seg_color,
                alpha=seg_alpha,
                linewidth=seg_size,
                zorder=zorder - 0.1,
            )

        # --- text kwargs ---
        kw: dict[str, Any] = {
            "ha": ha,
            "va": va,
            "fontsize": sizes[i],
            "color": colors[i],
            "alpha": alphas[i],
            "zorder": zorder,
            "clip_on": True,
        }

        if use_bbox:
            kw["bbox"] = {
                "boxstyle": f"round,pad={label_pad}",
                "facecolor": fills[i],
                "edgecolor": colors[i],
                "alpha": fill_alpha,
                "linewidth": 0.5,
            }

        ax.text(
            new_x[i],
            new_y[i],
            str(labels[i]),
            **kw,
        )


@document
class geom_text_repel(geom_text):
    """
    Repulsive text labels that avoid overlapping

    Labels are repositioned using a force-directed algorithm
    to avoid overlapping each other and data points.
    Connector segments are drawn from the original data point
    to the repositioned label.

    {usage}

    Parameters
    ----------
    {common_parameters}
    box_padding : float
        Padding around text boxes (fraction of axis range).
    point_padding : float
        Padding around data points (fraction of axis range).
    force : float
        Repulsion force multiplier.
    max_iter : int
        Maximum repulsion iterations.
    seed : int
        Random seed for reproducibility.
    min_segment_length : float
        Minimum segment length (fraction of x-range) below
        which no connector line is drawn.
    segment_color : str
        Colour of connector segments.
    segment_alpha : float
        Alpha of connector segments.
    segment_size : float
        Line width of connector segments.
    direction : str
        ``"both"``, ``"x"``, or ``"y"``: restricts which
        axes are affected by repulsion.

    See Also
    --------
    plotnine.geom_text
    geom_label_repel
    """

    REQUIRED_AES = {"x", "y", "label"}
    DEFAULT_AES = _text_repel_aes
    DEFAULT_PARAMS = _text_repel_params

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
    ):
        _draw_repelled_text(
            data,
            panel_params,
            coord,
            ax,
            self.params,
            use_bbox=False,
        )


# ----- label variant -----

_label_repel_aes = _text_repel_aes.copy()
_label_repel_aes["fill"] = "white"

_label_repel_params = _text_repel_params.copy()
_label_repel_params.update(
    {
        "label_padding": 0.25,
        "fill_alpha": 0.8,
    }
)


@document
class geom_label_repel(geom_text_repel):
    """
    Repulsive text labels with a background box

    Like :class:`geom_text_repel` but draws a filled rectangle
    behind each label for improved readability.

    {usage}

    Parameters
    ----------
    {common_parameters}
    box_padding : float
        Padding around text boxes (fraction of axis range).
    point_padding : float
        Padding around data points (fraction of axis range).
    force : float
        Repulsion force multiplier.
    max_iter : int
        Maximum repulsion iterations.
    seed : int
        Random seed for reproducibility.
    min_segment_length : float
        Minimum connector length (fraction of x-range).
    segment_color : str
        Connector segment colour.
    segment_alpha : float
        Connector segment alpha.
    segment_size : float
        Connector line width.
    direction : str
        ``"both"``, ``"x"``, or ``"y"``.
    label_padding : float
        Padding inside the label box.
    fill_alpha : float
        Alpha for the background fill.

    See Also
    --------
    plotnine.geom_label
    geom_text_repel
    """

    DEFAULT_AES = _label_repel_aes
    DEFAULT_PARAMS = _label_repel_params

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
    ):
        _draw_repelled_text(
            data,
            panel_params,
            coord,
            ax,
            self.params,
            use_bbox=True,
        )
