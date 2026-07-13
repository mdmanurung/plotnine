"""
``stat_midpoint``: per-group midpoint of x / y ranges.

Port of ``ggh4x::stat_midpoint``. Returns a single row per
group with x at ``(min + max) / 2`` for each axis.
"""

from __future__ import annotations

import pandas as pd
from plotnine.doctools import document
from plotnine.stats.stat import stat


@document
class stat_midpoint(stat):
    """
    Compute the midpoint of each group's x / y range.

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "geom": "point",
        "position": "identity",
        "na_rm": False,
    }

    def compute_group(self, data, scales) -> pd.DataFrame:
        x = data["x"].to_numpy(dtype=float)
        y = data["y"].to_numpy(dtype=float)
        return pd.DataFrame(
            {
                "x": [(x.min() + x.max()) / 2],
                "y": [(y.min() + y.max()) / 2],
            }
        )
