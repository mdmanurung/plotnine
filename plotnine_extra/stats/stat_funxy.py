"""
``stat_funxy``: apply arbitrary summary functions to ``x`` and
``y`` separately. Port of ``ggh4x::stat_funxy``.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd
from plotnine.doctools import document
from plotnine.stats.stat import stat


@document
class stat_funxy(stat):
    """
    Reduce each group's x and y to scalar values via callables.

    {usage}

    Parameters
    ----------
    {common_parameters}
    funx : callable, default :func:`numpy.mean`
        Reduction applied to ``x``.
    funy : callable, default :func:`numpy.mean`
        Reduction applied to ``y``.
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "geom": "point",
        "position": "identity",
        "na_rm": False,
        "funx": np.mean,
        "funy": np.mean,
    }

    def compute_group(self, data, scales) -> pd.DataFrame:
        funx: Callable = self.params["funx"]
        funy: Callable = self.params["funy"]
        return pd.DataFrame(
            {
                "x": [float(funx(data["x"].to_numpy(dtype=float)))],
                "y": [float(funy(data["y"].to_numpy(dtype=float)))],
            }
        )
