"""
``stat_centroid``: per-group centroid (mean ``x`` and ``y``).

Direct port of ``ggh4x::stat_centroid``. Outputs a single row
per group with the average position. Useful for labelling
clusters.
"""

from __future__ import annotations

import pandas as pd
from plotnine.doctools import document
from plotnine.stats.stat import stat


@document
class stat_centroid(stat):
    """
    Compute the centroid of each group.

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
        return pd.DataFrame(
            {
                "x": [float(data["x"].mean())],
                "y": [float(data["y"].mean())],
            }
        )
