"""
``geom_pwc``: geom counterpart of :class:`stat_pwc`.

In ggpubr, ``geom_pwc`` and ``stat_pwc`` are interchangeable;
both attach pairwise comparison brackets to a plot. The geom
form simply binds the default ``stat`` to ``pwc`` and renders
with the existing bracket machinery.
"""

from __future__ import annotations

from plotnine.doctools import document

from .geom_bracket import geom_bracket


@document
class geom_pwc(geom_bracket):
    """
    Pairwise comparison brackets (geom form of ``stat_pwc``).

    {usage}

    Parameters
    ----------
    {common_parameters}

    Notes
    -----
    All statistical-test parameters live on
    :class:`plotnine_extra.stats.stat_pwc`. This class simply
    sets the default ``stat`` so that calling
    ``geom_pwc(...)`` is equivalent to writing
    ``stat_pwc(geom='bracket', ...)``. Rendering is inherited
    from :class:`geom_bracket`.
    """

    DEFAULT_PARAMS = {
        **geom_bracket.DEFAULT_PARAMS,
        "stat": "pwc",
    }
