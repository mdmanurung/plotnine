"""
``geom_rectmargin``: marginal rectangles for one or both axes.

Port of ``ggh4x::geom_rectmargin``. Adds rectangle annotations
hugging the x and/or y axis margins of the panel.
"""

from __future__ import annotations

from plotnine.doctools import document
from plotnine.geoms.geom_rect import geom_rect


@document
class geom_rectmargin(geom_rect):
    """
    Draw rectangles in the panel margin(s).

    {usage}

    Parameters
    ----------
    {common_parameters}
    sides : str, default ``"b"``
        Which margin to draw on. Concatenation of ``"t"``,
        ``"b"``, ``"l"``, ``"r"``.

    Notes
    -----
    Marginal positioning is achieved by mapping ``ymin`` /
    ``ymax`` to ``-Inf`` / ``Inf`` (or ``xmin`` / ``xmax``)
    so the rectangles span the panel edge. ``sides`` controls
    which axis is collapsed.
    """

    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "sides": "b",
    }

    def setup_data(self, data):
        import numpy as np

        data = super().setup_data(data)
        sides = self.params.get("sides", "b")
        data = data.copy()
        if "b" in sides:
            data["ymin"] = -np.inf
            data["ymax"] = data.get("ymax", 0)
        if "t" in sides:
            data["ymin"] = data.get("ymin", 0)
            data["ymax"] = np.inf
        if "l" in sides:
            data["xmin"] = -np.inf
            data["xmax"] = data.get("xmax", 0)
        if "r" in sides:
            data["xmin"] = data.get("xmin", 0)
            data["xmax"] = np.inf
        return data
