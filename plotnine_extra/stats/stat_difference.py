"""
``stat_difference``: signed-difference ribbon between two
y-series, ported from ``ggh4x::stat_difference``.

Given an ``x`` aesthetic plus ``ymin`` and ``ymax``, this stat
returns the segments where ``ymax > ymin`` ("positive") and
``ymax < ymin`` ("negative") so that they can be drawn as
two separately filled ribbons.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from plotnine.doctools import document
from plotnine.stats.stat import stat

if TYPE_CHECKING:
    import pandas as pd


@document
class stat_difference(stat):
    """
    Compute the signed-difference ribbon between two y series.

    {usage}

    Parameters
    ----------
    {common_parameters}

    Notes
    -----
    The ``sign`` aesthetic in the output frame can be mapped
    to ``fill`` to colour positive and negative differences
    differently::

        ggplot(d, aes("x", ymin="lo", ymax="hi"))
            + stat_difference(aes(fill="after_stat('sign')"))
    """

    REQUIRED_AES = {"x", "ymin", "ymax"}
    DEFAULT_PARAMS = {
        "geom": "ribbon",
        "position": "identity",
        "na_rm": False,
    }
    CREATES = {"sign"}

    def compute_group(self, data, scales) -> pd.DataFrame:
        d = data.sort_values("x").reset_index(drop=True).copy()
        diff = d["ymax"].to_numpy() - d["ymin"].to_numpy()
        sign = np.where(
            diff > 0, "positive", np.where(diff < 0, "negative", "zero")
        )
        d["sign"] = sign
        return d
