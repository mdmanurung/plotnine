"""
``geom_box``: rectangular highlight box.

Port of ``ggh4x::geom_box``. A subclass of :class:`geom_rect`
that simply renames the convenience parameters so that
``geom_box(xmin=, xmax=, ymin=, ymax=, ...)`` works as in R.
This geom does not draw the standard ggplot2 box-and-whisker
shape; use :func:`plotnine.geom_boxplot` for that.
"""

from __future__ import annotations

from plotnine.doctools import document
from plotnine.geoms.geom_rect import geom_rect


@document
class geom_box(geom_rect):
    """
    Draw a rectangular highlight box.

    {usage}

    Parameters
    ----------
    {common_parameters}

    Notes
    -----
    This is *not* a box-and-whisker plot. For that, see
    :func:`plotnine.geom_boxplot`. The class is provided to
    match the ggh4x naming.
    """

    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
    }
