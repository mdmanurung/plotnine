"""
Position adjustment that uses the beeswarm algorithm,
ported from R's ``ggbeeswarm::position_beeswarm``.
"""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

import numpy as np
from plotnine._utils import groupby_apply, resolution
from plotnine.positions.position import position

from ._beeswarm_algorithms import corral_points, offset_beeswarm

_VALID_METHODS = {"swarm", "compactswarm", "center", "centre", "hex", "square"}
_VALID_PRIORITIES = {"ascending", "descending", "density", "random", "none"}
_VALID_SIDES = {-1, 0, 1}
_VALID_CORRALS = {"none", "gutter", "wrap", "random", "omit"}

if TYPE_CHECKING:
    from typing import Optional

    import pandas as pd
    from plotnine.iapi import pos_scales


class position_beeswarm(position):
    """
    Jitter points using the beeswarm algorithm

    Points are arranged so that they do not overlap, producing
    a layout that resembles a beeswarm.  The resulting shape
    gives a good indication of the data distribution while
    showing every individual observation.

    Parameters
    ----------
    method :
        Algorithm for arranging points.

        - ``"swarm"`` (default): place in order, shift sideways
          the minimum amount to avoid overlap.
        - ``"compactswarm"``: greedy strategy for tighter
          packing.
        - ``"center"`` / ``"centre"``: square grid, centred.
        - ``"hex"``: hexagonal grid.
        - ``"square"``: regular square grid.
    cex :
        Scaling factor for point spacing (1-3 recommended).
    side :
        ``0``: both sides (default), ``1``: right/up only,
        ``-1``: left/down only.
    priority :
        Order in which points are placed:
        ``"ascending"`` (default), ``"descending"``,
        ``"density"``, ``"random"``, ``"none"``.
    dodge_width :
        Amount of dodge between aesthetic groups.
    corral :
        How to handle runaway points: ``"none"`` (default),
        ``"gutter"``, ``"wrap"``, ``"random"``, ``"omit"``.
    corral_width :
        Width of the corral region.
    """

    REQUIRED_AES = {"x", "y"}

    def __init__(
        self,
        method: str = "swarm",
        cex: float = 1.0,
        side: int = 0,
        priority: str = "ascending",
        dodge_width: Optional[float] = None,
        corral: str = "none",
        corral_width: float = 0.9,
    ):
        _validate_choice("method", method, _VALID_METHODS)
        _validate_choice("priority", priority, _VALID_PRIORITIES)
        _validate_choice("side", side, _VALID_SIDES)
        _validate_choice("corral", corral, _VALID_CORRALS)
        self.params = {
            "method": method,
            "cex": cex,
            "side": side,
            "priority": priority,
            "dodge_width": dodge_width,
            "corral": corral,
            "corral_width": corral_width,
        }

    def setup_params(self, data: pd.DataFrame) -> dict:
        params = deepcopy(self.params)
        # Estimate point_size from data resolution
        y_res = resolution(data["y"])
        params["point_size"] = y_res / max(len(data) ** 0.25, 2)
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

        def _swarm_group(gdf: pd.DataFrame) -> pd.DataFrame:
            gdf = gdf.copy()
            y = gdf["y"].to_numpy(dtype=np.float64)
            offsets = offset_beeswarm(
                y,
                method=params["method"],
                cex=params["cex"],
                side=params["side"],
                priority=params["priority"],
                point_size=params.get("point_size"),
            )
            offsets = corral_points(
                offsets,
                method=params["corral"],
                width=params["corral_width"],
            )
            gdf["x"] = gdf["x"] + offsets
            return gdf

        return groupby_apply(data, "group", _swarm_group)


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


def _validate_choice(name: str, value, valid: set) -> None:
    if value not in valid:
        msg = f"{name} must be one of {sorted(valid)}, got {value!r}"
        raise ValueError(msg)
