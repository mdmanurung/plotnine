"""
``position_disjoint_ranges``: stack overlapping intervals into
disjoint rows. Port of ``ggh4x::position_disjoint_ranges``.

Each layer with ``xmin`` / ``xmax`` aesthetics gets reassigned a
``y`` value so that intervals that overlap on x are placed on
distinct rows.  Useful for gene-track / Gantt-style plots.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from plotnine.positions.position import position

if TYPE_CHECKING:
    import pandas as pd


def _assign_rows(
    starts: np.ndarray, ends: np.ndarray, extend: float = 0.0
) -> np.ndarray:
    """Greedy interval-graph colouring; returns 0-indexed row ids."""
    n = starts.size
    order = np.argsort(starts)
    rows_end: list[float] = []
    out = np.empty(n, dtype=int)
    for idx in order:
        s = starts[idx] - extend
        e = ends[idx] + extend
        placed = False
        for r, current_end in enumerate(rows_end):
            if current_end < s:
                rows_end[r] = e
                out[idx] = r
                placed = True
                break
        if not placed:
            rows_end.append(e)
            out[idx] = len(rows_end) - 1
    return out


class position_disjoint_ranges(position):
    """
    Vertically stack overlapping x intervals into disjoint rows.

    Parameters
    ----------
    extend : float, default 0
        Padding added to each interval before deciding overlap.
        Positive values force more vertical separation.
    stepsize : float, default 1
        Vertical spacing between rows.
    """

    REQUIRED_AES = {"xmin", "xmax"}

    def __init__(self, extend: float = 0.0, stepsize: float = 1.0):
        super().__init__()
        self.extend = extend
        self.stepsize = stepsize

    def setup_params(self, data):
        return {"extend": self.extend, "stepsize": self.stepsize}

    @classmethod
    def compute_layer(
        cls,
        data: pd.DataFrame,
        params,
        layout,
    ) -> pd.DataFrame:
        if "xmin" not in data.columns or "xmax" not in data.columns:
            return data
        data = data.copy()
        starts = data["xmin"].to_numpy(dtype=float)
        ends = data["xmax"].to_numpy(dtype=float)
        rows = _assign_rows(starts, ends, extend=params["extend"])
        ys = (rows + 1) * params["stepsize"]
        data["y"] = ys
        if "ymin" in data.columns:
            data["ymin"] = ys - params["stepsize"] / 2
        if "ymax" in data.columns:
            data["ymax"] = ys + params["stepsize"] / 2
        return data
