"""
``geom_tufteboxplot``: low-ink boxplots.
"""

from __future__ import annotations

from plotnine.doctools import document
from plotnine.geoms.geom_boxplot import geom_boxplot

from ..stats.stat_fivenumber import stat_fivenumber


@document
class geom_tufteboxplot(geom_boxplot):
    """
    Draw a low-ink boxplot using five-number summaries.

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    DEFAULT_AES = {
        **geom_boxplot.DEFAULT_AES,
        "fill": None,
        "color": "#333333",
    }
    DEFAULT_PARAMS = {
        **geom_boxplot.DEFAULT_PARAMS,
        "stat": stat_fivenumber,
        "outlier_shape": None,
        "fatten": 1,
    }
