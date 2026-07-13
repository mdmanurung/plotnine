"""
``stat_rle``: run-length encoding of a categorical x series.

Port of ``ggh4x::stat_rle``. Each contiguous run of identical
``label`` values becomes a row with ``start``, ``end``,
``run_id``, ``run_length`` and ``runvalue`` columns.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from plotnine.doctools import document
from plotnine.stats.stat import stat

from ._common import preserve_panel_columns


@document
class stat_rle(stat):
    """
    Compute run-length encoded segments of a categorical aes.

    {usage}

    Parameters
    ----------
    {common_parameters}
    align : str, default ``"center"``
        Where to anchor the segment. One of ``"center"``,
        ``"start"`` or ``"end"``.
    """

    REQUIRED_AES = {"x", "label"}
    DEFAULT_PARAMS = {
        "geom": "rect",
        "position": "identity",
        "na_rm": False,
        "align": "center",
    }
    CREATES = {
        "start",
        "end",
        "run_id",
        "run_length",
        "runvalue",
        "xmin",
        "xmax",
    }

    def compute_panel(self, data, scales) -> pd.DataFrame:
        if data.empty:
            return data
        d = data.sort_values("x").reset_index(drop=True)
        labels = d["label"].to_numpy()
        xs = d["x"].to_numpy(dtype=float)
        change = np.concatenate(([True], labels[1:] != labels[:-1]))
        run_id = np.cumsum(change) - 1
        rows = []
        for rid in np.unique(run_id):
            mask = run_id == rid
            seg_x = xs[mask]
            rows.append(
                {
                    "run_id": int(rid),
                    "runvalue": labels[mask][0],
                    "run_length": int(mask.sum()),
                    "start": float(seg_x.min()),
                    "end": float(seg_x.max()),
                    "xmin": float(seg_x.min()),
                    "xmax": float(seg_x.max()),
                    "x": float(seg_x.mean()),
                    "y": 0.0,
                    "ymin": 0.0,
                    "ymax": 1.0,
                }
            )
        result = pd.DataFrame(rows)
        # Carry PANEL / group through so plotnine's position
        # scale training can join against the computed rows.
        return preserve_panel_columns(result, data)
