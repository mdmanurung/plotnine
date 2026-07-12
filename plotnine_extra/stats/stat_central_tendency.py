from __future__ import annotations

import numpy as np
import pandas as pd
from plotnine.doctools import document
from plotnine.stats.stat import stat


@document
class stat_central_tendency(stat):
    """
    Add central tendency measure to a density plot

    Computes the mean, median, or mode of the data and
    returns coordinates for a vertical line at that position.

    {usage}

    Parameters
    ----------
    {common_parameters}
    type : str, default="mean"
        Type of central tendency measure. One of
        ``"mean"``, ``"median"``, or ``"mode"``.

    See Also
    --------
    plotnine.geom_line : The default `geom` for this `stat`.
    """

    _aesthetics_doc = """
    {aesthetics_table}
    """
    REQUIRED_AES = {"x"}
    DEFAULT_PARAMS = {
        "geom": "line",
        "position": "identity",
        "na_rm": False,
        "type": "mean",
    }

    def compute_group(self, data, scales) -> pd.DataFrame:
        ct_type = self.params["type"]
        x = data["x"]

        if ct_type == "mean":
            center = x.mean()
        elif ct_type == "median":
            center = x.median()
        elif ct_type == "mode":
            center = _get_mode(x)
        else:
            raise ValueError(
                f"type must be 'mean', 'median', or 'mode', got '{ct_type}'"
            )

        return pd.DataFrame(
            {
                "x": [center, center],
                "y": [-np.inf, np.inf],
            }
        )


def _get_mode(series):
    """
    Compute the mode of a pandas Series.

    For continuous data, uses the value with the highest
    kernel density estimate approximated by value_counts binning.
    """
    counts = series.value_counts()
    return counts.idxmax()
