"""
``stat_fivenumber``: five-number summaries for boxplot geoms.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from plotnine.doctools import document
from plotnine.stats.stat import stat


@document
class stat_fivenumber(stat):
    """
    Compute min, hinges, median, and max for each group.

    {usage}

    Parameters
    ----------
    {common_parameters}
    width : float, optional
        Box width passed through to boxplot geoms.
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "geom": "boxplot",
        "position": "dodge",
        "na_rm": False,
        "width": None,
    }

    def compute_group(self, data, scales) -> pd.DataFrame:
        y = data["y"].to_numpy(dtype=float)
        ymin, lower, middle, upper, ymax = np.percentile(
            y,
            [0, 25, 50, 75, 100],
        )
        if isinstance(data["x"].dtype, pd.CategoricalDtype):
            x = data["x"].iloc[0]
        else:
            x = float(np.mean([data["x"].min(), data["x"].max()]))
        return pd.DataFrame(
            {
                "ymin": [float(ymin)],
                "lower": [float(lower)],
                "middle": [float(middle)],
                "upper": [float(upper)],
                "ymax": [float(ymax)],
                "outliers": [[]],
                "notchupper": [float(upper)],
                "notchlower": [float(lower)],
                "x": [x],
                "width": [
                    0.9
                    if self.params.get("width") is None
                    else float(self.params["width"])
                ],
                "relvarwidth": [float(np.sqrt(len(y)))],
                "n": [len(y)],
            }
        )
