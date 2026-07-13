"""
``stat_rollingkernel``: rolling kernel smoother.

Port of ``ggh4x::stat_rollingkernel``. Computes a kernel-weighted
moving average of ``y`` along ``x``. Output columns are
``x`` (the evaluation grid) and ``y`` (the smoothed value).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from plotnine.doctools import document
from plotnine.stats.stat import stat

_KERNELS = {
    "gaussian": lambda u: np.exp(-0.5 * u * u),
    "triangular": lambda u: np.maximum(0, 1 - np.abs(u)),
    "epanechnikov": lambda u: np.maximum(0, 0.75 * (1 - u * u)),
    "uniform": lambda u: (np.abs(u) <= 1).astype(float),
}


@document
class stat_rollingkernel(stat):
    """
    Smooth a series with a rolling kernel.

    {usage}

    Parameters
    ----------
    {common_parameters}
    bw : float, default 1.0
        Kernel bandwidth (in x units).
    kernel : str, default ``"gaussian"``
        One of ``"gaussian"``, ``"triangular"``,
        ``"epanechnikov"`` or ``"uniform"``.
    n : int, default 100
        Number of evaluation points along the x range.
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "geom": "line",
        "position": "identity",
        "na_rm": False,
        "bw": 1.0,
        "kernel": "gaussian",
        "n": 100,
    }

    def compute_group(self, data, scales) -> pd.DataFrame:
        kernel = _KERNELS.get(self.params["kernel"])
        if kernel is None:
            raise ValueError(
                f"Unknown kernel {self.params['kernel']!r}; "
                f"expected one of {sorted(_KERNELS)}"
            )
        bw = float(self.params["bw"])
        n = int(self.params["n"])
        xs = data["x"].to_numpy(dtype=float)
        ys = data["y"].to_numpy(dtype=float)
        if xs.size == 0:
            return pd.DataFrame({"x": [], "y": []})
        grid = np.linspace(xs.min(), xs.max(), n)
        out = np.empty(n, dtype=float)
        for i, g in enumerate(grid):
            w = kernel((xs - g) / bw)
            total = w.sum()
            out[i] = (w * ys).sum() / total if total > 0 else np.nan
        return pd.DataFrame({"x": grid, "y": out})
