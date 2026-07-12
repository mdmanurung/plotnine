from __future__ import annotations

import numpy as np
import pandas as pd
from plotnine.stats.stat import stat
from scipy.spatial import ConvexHull


class stat_chull(stat):
    """
    Compute the convex hull of a set of points

    Calculates the convex hull for each group and returns
    the subset of points that form the hull boundary.

    {usage}

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.geom_path : The default `geom` for this `stat`.
    plotnine.geom_polygon : Alternative `geom` for filled hulls.
    """

    _aesthetics_doc = """
    {aesthetics_table}
    """
    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "geom": "path",
        "position": "identity",
        "na_rm": False,
    }

    def compute_group(self, data, scales) -> pd.DataFrame:
        x = data["x"].to_numpy()
        y = data["y"].to_numpy()

        if len(x) < 3:
            return data

        points = np.column_stack([x, y])

        try:
            hull = ConvexHull(points)
        except Exception:
            return data

        # Get hull vertices in order and close the polygon
        vertices = hull.vertices
        vertices = np.append(vertices, vertices[0])

        return pd.DataFrame(
            {
                "x": x[vertices],
                "y": y[vertices],
            }
        )
