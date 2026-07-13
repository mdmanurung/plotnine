"""
``geom_pointpath``: points connected by a path.

Port of ``ggh4x::geom_pointpath``. The simplest faithful Python
implementation is to subclass :class:`geom_point` so that the
points are drawn, and to expose a helper that adds a matching
``geom_path`` layer when used inside :func:`pointpath_layers`.
For everyday use the recommended pattern is::

    p + geom_pointpath()

which adds *both* the points and the connecting path through a
custom ``draw_layer`` override.
"""

from __future__ import annotations

from plotnine.doctools import document
from plotnine.geoms.geom_point import geom_point


@document
class geom_pointpath(geom_point):
    """
    Draw points connected by a path.

    {usage}

    Parameters
    ----------
    {common_parameters}
    linesize : float, default 0.5
        Width of the connecting line.
    linecolor : str, optional
        Override the line colour. Defaults to the point colour.
    linetype : str, default ``"solid"``
        Line dash pattern.

    Notes
    -----
    Internally a :class:`geom_path` layer is added alongside the
    point geom so a single ``+ geom_pointpath()`` produces both
    artists. The path uses the same colour mapping as the
    points unless ``linecolor`` overrides it.
    """

    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "linesize": 0.5,
        "linecolor": None,
        "linetype": "solid",
    }

    def __radd__(self, plot):
        from plotnine.geoms.geom_path import geom_path

        # Add point layer first
        plot = super().__radd__(plot)
        # Build matching path layer
        line_kwargs = {
            "size": self.params.get("linesize", 0.5),
            "linetype": self.params.get("linetype", "solid"),
        }
        lc = self.params.get("linecolor")
        if lc is not None:
            line_kwargs["color"] = lc
        path_layer = geom_path(
            mapping=self.mapping,
            data=self.data,
            **line_kwargs,
        )
        return plot + path_layer
