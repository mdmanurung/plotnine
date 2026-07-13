"""
``geom_text_aimed``: text rotated to follow a direction.

Port of ``ggh4x::geom_text_aimed``. A subclass of
:class:`geom_text` that lets users supply an explicit
``angle`` aesthetic *or* a target ``xend`` / ``yend`` pair from
which the angle is computed automatically.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from plotnine.doctools import document
from plotnine.geoms.geom_text import geom_text

if TYPE_CHECKING:
    import pandas as pd


@document
class geom_text_aimed(geom_text):
    """
    Draw text rotated to align with a target direction.

    {usage}

    Parameters
    ----------
    {common_parameters}

    Notes
    -----
    If the data contains both ``xend`` and ``yend`` columns,
    they are interpreted as the direction the text should
    point. Otherwise the regular ``angle`` aesthetic is used.
    """

    DEFAULT_PARAMS = {
        **geom_text.DEFAULT_PARAMS,
    }

    def setup_data(self, data: "pd.DataFrame") -> "pd.DataFrame":
        data = super().setup_data(data)
        if "xend" in data.columns and "yend" in data.columns:
            dx = data["xend"].to_numpy(dtype=float) - data["x"].to_numpy(
                dtype=float
            )
            dy = data["yend"].to_numpy(dtype=float) - data["y"].to_numpy(
                dtype=float
            )
            data = data.copy()
            data["angle"] = np.degrees(np.arctan2(dy, dx))
        return data
