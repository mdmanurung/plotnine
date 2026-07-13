"""
``geom_rangeframe``: draw compact range-frame axis segments.
"""

from __future__ import annotations

import pandas as pd
from plotnine.doctools import document
from plotnine.geoms.geom_segment import geom_segment


@document
class geom_rangeframe(geom_segment):
    """
    Draw x- and y-range line segments for each panel.

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_AES = geom_segment.DEFAULT_AES.copy()
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "lineend": "butt",
        "arrow": None,
    }

    def setup_data(self, data: pd.DataFrame) -> pd.DataFrame:
        group_cols = ["PANEL"] if "PANEL" in data.columns else [None]
        rows = []
        iterator = (
            data.groupby("PANEL", sort=False, observed=True)
            if group_cols == ["PANEL"]
            else [(None, data)]
        )
        for panel_id, (panel, frame) in enumerate(iterator):
            xmin = frame["x"].min()
            xmax = frame["x"].max()
            ymin = frame["y"].min()
            ymax = frame["y"].max()
            base = {}
            if panel is not None:
                base["PANEL"] = panel
            rows.extend(
                [
                    {
                        **base,
                        "x": xmin,
                        "xend": xmax,
                        "y": ymin,
                        "yend": ymin,
                        "group": panel_id * 2,
                        "rangeframe_axis": "x",
                    },
                    {
                        **base,
                        "x": xmin,
                        "xend": xmin,
                        "y": ymin,
                        "yend": ymax,
                        "group": panel_id * 2 + 1,
                        "rangeframe_axis": "y",
                    },
                ]
            )
        return pd.DataFrame(rows)
