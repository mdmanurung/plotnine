"""
Animation, re-exported from plotnine.

plotnine ships ``PlotnineAnimation`` natively (in every supported version),
and it tracks plotnine's own draw internals -- which change between releases
(e.g. the ``ggplot._sub_gridspec`` draw wiring in 0.16). plotnine-extra used
to vendor a copy of it, which broke on those internal changes. We now
re-export plotnine's implementation so it stays correct across plotnine
versions with no maintenance.
"""

from __future__ import annotations

from plotnine.animation import PlotnineAnimation

__all__ = ("PlotnineAnimation",)
