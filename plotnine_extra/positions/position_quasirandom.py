"""
Position adjustment that uses quasi-random jittering,
ported from R's ``ggbeeswarm::position_quasirandom``.
"""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

import numpy as np
from plotnine._utils import groupby_apply, resolution
from plotnine.positions.position import position

from ._beeswarm_algorithms import offset_quasirandom

_VALID_METHODS = {"quasirandom", "pseudorandom"}

if TYPE_CHECKING:
    from typing import Optional

    import pandas as pd
    from plotnine.iapi import pos_scales


class position_quasirandom(position):
    """
    Jitter points using quasi-random noise to reduce overplotting

    Uses density-aware quasi-random jittering (van der Corput
    sequence) so that the point cloud reflects the underlying
    data distribution, similar to a violin plot but with
    individual points.

    Parameters
    ----------
    method :
        ``"quasirandom"`` (default) uses a van der Corput
        sequence; ``"pseudorandom"`` uses uniform random jitter.
    width :
        Maximum jitter width.  If ``None``, ``0.4 * resolution``
        of the data axis is used.
    varwidth :
        If ``True``, scale the width of each group proportionally
        to its size relative to the largest group.
    bandwidth :
        Bandwidth adjustment for the internal kernel density
        estimate.  Values < 1 yield a tighter fit.
    nbins :
        Number of bins for density estimation (passed through but
        currently unused; bandwidth controls smoothing).
    dodge_width :
        Amount by which to dodge groups that share the same
        position.  ``None`` means no dodging.
    """

    REQUIRED_AES = {"x", "y"}

    def __init__(
        self,
        method: str = "quasirandom",
        width: Optional[float] = None,
        varwidth: bool = False,
        bandwidth: float = 0.5,
        nbins: Optional[int] = None,
        dodge_width: Optional[float] = None,
    ):
        if method not in _VALID_METHODS:
            msg = (
                f"method must be one of {sorted(_VALID_METHODS)}, "
                f"got {method!r}"
            )
            raise ValueError(msg)
        self.params = {
            "method": method,
            "width": width,
            "varwidth": varwidth,
            "bandwidth": bandwidth,
            "nbins": nbins,
            "dodge_width": dodge_width,
        }

    def setup_params(self, data: pd.DataFrame) -> dict:
        params = deepcopy(self.params)
        if params["width"] is None:
            params["width"] = resolution(data["x"]) * 0.4
        return params

    @classmethod
    def compute_panel(
        cls,
        data: pd.DataFrame,
        scales: pos_scales,
        params: dict,
    ) -> pd.DataFrame:
        dodge_width = params.get("dodge_width")
        if dodge_width is not None:
            data = _dodge_groups(data, dodge_width)

        total_count = len(data) if params["varwidth"] else None

        def _jitter_group(gdf: pd.DataFrame) -> pd.DataFrame:
            gdf = gdf.copy()
            y = gdf["y"].to_numpy(dtype=np.float64)
            offsets = offset_quasirandom(
                y,
                method=params["method"],
                width=params["width"],
                bandwidth=params["bandwidth"],
                nbins=params["nbins"],
                varwidth=params["varwidth"],
                group_count=len(gdf),
                total_count=total_count,
            )
            gdf["x"] = gdf["x"] + offsets
            return gdf

        return groupby_apply(data, "group", _jitter_group)


def _dodge_groups(data: "pd.DataFrame", dodge_width: float) -> "pd.DataFrame":
    """
    Spread aesthetic groups horizontally so they do not overlap.
    """
    data = data.copy()
    groups = data["group"].unique()
    n_groups = len(groups)
    if n_groups <= 1:
        return data

    offsets = np.linspace(-dodge_width / 2, dodge_width / 2, n_groups)
    group_map = dict(zip(sorted(groups), offsets))
    data["x"] = data["x"] + data["group"].map(group_map)
    return data
