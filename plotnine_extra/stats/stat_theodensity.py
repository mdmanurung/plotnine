"""
``stat_theodensity``: theoretical density curve.

Port of ``ggh4x::stat_theodensity``. Fits a parametric
distribution to the data via maximum likelihood and returns the
density evaluated on a grid spanning the observed range.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from plotnine.doctools import document
from plotnine.stats.stat import stat
from scipy import stats as _sps

_DIST_MAP = {
    "norm": _sps.norm,
    "normal": _sps.norm,
    "lnorm": _sps.lognorm,
    "lognormal": _sps.lognorm,
    "gamma": _sps.gamma,
    "beta": _sps.beta,
    "exp": _sps.expon,
    "exponential": _sps.expon,
    "weibull": _sps.weibull_min,
    "cauchy": _sps.cauchy,
    "logistic": _sps.logistic,
    "t": _sps.t,
}


@document
class stat_theodensity(stat):
    """
    Fit a parametric distribution and return its density curve.

    {usage}

    Parameters
    ----------
    {common_parameters}
    distri : str, default ``"norm"``
        Name of the distribution to fit. Anything in
        :data:`_DIST_MAP`.
    n : int, default 256
        Number of grid points along the x range.
    """

    REQUIRED_AES = {"x"}
    DEFAULT_PARAMS = {
        "geom": "line",
        "position": "identity",
        "na_rm": False,
        "distri": "norm",
        "n": 256,
    }

    def compute_group(self, data, scales) -> pd.DataFrame:
        distri = self.params["distri"]
        if distri not in _DIST_MAP:
            raise ValueError(
                f"Unknown distri {distri!r}; expected one of "
                f"{sorted(_DIST_MAP)}"
            )
        dist = _DIST_MAP[distri]
        x = data["x"].to_numpy(dtype=float)
        x = x[~np.isnan(x)]
        if x.size < 2:
            return pd.DataFrame({"x": [], "y": [], "density": []})
        params = dist.fit(x)
        grid = np.linspace(x.min(), x.max(), int(self.params["n"]))
        density = dist.pdf(grid, *params)
        return pd.DataFrame(
            {
                "x": grid,
                "y": density,
                "density": density,
            }
        )
