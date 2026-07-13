"""
``geom_polygonraster``: raster cells reparameterised as polygons.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from plotnine.doctools import document
from plotnine.geoms.geom_polygon import geom_polygon


@document
class geom_polygonraster(geom_polygon):
    """
    Draw raster-like cells as individual polygons.

    {usage}

    Parameters
    ----------
    {common_parameters}
    hjust, vjust : float
        Horizontal and vertical justification of each raster cell around
        its ``x`` and ``y`` coordinate.
    """

    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "hjust": 0.5,
        "vjust": 0.5,
    }

    def setup_data(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        hjust = self.params["hjust"]
        vjust = self.params["vjust"]

        x_width = _regular_step_width(data["x"])
        y_width = _regular_step_width(data["y"])

        data["xmin"] = data["x"] - x_width * (1 - hjust)
        data["xmax"] = data["x"] + x_width * hjust
        data["ymin"] = data["y"] - y_width * (1 - vjust)
        data["ymax"] = data["y"] + y_width * vjust
        data["_raster_group"] = np.arange(len(data))

        rows = []
        for raster_id in range(len(data)):
            row = data.iloc[[raster_id]].to_dict("records")[0]
            for x, y in (
                (row["xmin"], row["ymin"]),
                (row["xmax"], row["ymin"]),
                (row["xmax"], row["ymax"]),
                (row["xmin"], row["ymax"]),
            ):
                new_row = dict(row)
                new_row["x"] = x
                new_row["y"] = y
                new_row["_raster_group"] = raster_id
                new_row["group"] = raster_id
                rows.append(new_row)

        if not rows:
            return data.iloc[0:0].copy()
        return pd.DataFrame(rows).reset_index(drop=True)


def _regular_step_width(values: pd.Series) -> float:
    unique = np.sort(pd.Series(values).dropna().unique())
    diffs = np.diff(unique)
    if len(diffs) == 0:
        return 1.0
    return float(diffs.min())
