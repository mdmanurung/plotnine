"""
``geom_quasirandom``: categorical scatter with quasi-random jitter,
ported from R's ``ggbeeswarm::geom_quasirandom``.
"""

from __future__ import annotations

from plotnine.doctools import document
from plotnine.geoms.geom_point import geom_point

from ..positions.position_quasirandom import position_quasirandom
from ._position_geom_mixin import _PositionGeomMixin


@document
class geom_quasirandom(_PositionGeomMixin, geom_point):
    """
    Points jittered to reduce overplotting using quasi-random noise

    The jitter is density-aware so the point cloud reflects the
    underlying data distribution, similar to a violin plot with
    individual points.

    {usage}

    Parameters
    ----------
    {common_parameters}
    method : str
        ``"quasirandom"`` (default) for a van der Corput
        low-discrepancy sequence, or ``"pseudorandom"`` for
        uniform random jitter.
    width : float | None
        Maximum jitter width.  ``None`` auto-calculates from
        the data resolution.
    varwidth : bool
        Scale width proportionally to group size.
    bandwidth : float
        Bandwidth adjustment for the density estimate.
    nbins : int | None
        Number of bins for density estimation.
    dodge_width : float | None
        Amount by which to dodge overlapping groups.

    See Also
    --------
    plotnine_extra.positions.position_quasirandom
    plotnine_extra.geoms.geom_beeswarm.geom_beeswarm
    """

    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
    }

    _position_class = position_quasirandom
    _position_params = {
        "method": "quasirandom",
        "width": None,
        "varwidth": False,
        "bandwidth": 0.5,
        "nbins": None,
        "dodge_width": None,
    }
