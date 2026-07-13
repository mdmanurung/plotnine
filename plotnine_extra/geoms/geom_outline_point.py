"""
``geom_outline_point``: points with an outline halo.

Port of ``ggh4x::geom_outline_point``. Implemented by drawing
two stacked point layers: a slightly larger point in the
``outline.colour`` colour, then the regular point on top.
"""

from __future__ import annotations

from plotnine.doctools import document
from plotnine.geoms.geom_point import geom_point


@document
class geom_outline_point(geom_point):
    """
    Draw points with an outline halo.

    {usage}

    Parameters
    ----------
    {common_parameters}
    outline_colour : str, default ``"black"``
        Colour of the halo.
    outline_size : float, default 1.0
        Halo size, added to the regular point size.
    """

    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "outline_colour": "black",
        "outline_size": 1.0,
    }

    def __radd__(self, plot):
        # Build the outline (halo) layer first
        oc = self.params.get("outline_colour", "black")
        os_ = self.params.get("outline_size", 1.0)
        size = self.aes_params.get("size", 3.0)
        try:
            big_size = float(size) + float(os_)
        except (TypeError, ValueError):
            big_size = None
        halo_kwargs = {"color": oc, "fill": oc}
        if big_size is not None:
            halo_kwargs["size"] = big_size
        halo_layer = geom_point(
            mapping=self.mapping,
            data=self.data,
            **halo_kwargs,
        )
        plot = plot + halo_layer
        return super().__radd__(plot)
