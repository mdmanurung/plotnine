"""
``geom_tilemargin``: marginal tiles.

Port of ``ggh4x::geom_tilemargin``. Identical to
:class:`geom_rectmargin` but uses :class:`geom_tile` semantics
(centred ``x`` / ``y`` and ``width`` / ``height``) instead of
explicit corners.
"""

from __future__ import annotations

import numpy as np
from plotnine.doctools import document
from plotnine.geoms.geom_tile import geom_tile


@document
class geom_tilemargin(geom_tile):
    """
    Draw tiles in the panel margin(s).

    {usage}

    Parameters
    ----------
    {common_parameters}
    sides : str, default ``"b"``
        Which margin to draw on. Concatenation of ``"t"``,
        ``"b"``, ``"l"``, ``"r"``.
    """

    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "sides": "b",
    }

    def setup_data(self, data):
        data = super().setup_data(data)
        sides = self.params.get("sides", "b")
        data = data.copy()
        if "b" in sides:
            data["y"] = -np.inf
        if "t" in sides:
            data["y"] = np.inf
        if "l" in sides:
            data["x"] = -np.inf
        if "r" in sides:
            data["x"] = np.inf
        return data
