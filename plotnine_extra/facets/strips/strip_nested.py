"""
Nested strips that merge adjacent labels sharing a parent.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .strip import Strip

if TYPE_CHECKING:
    from typing import Any


class strip_nested(Strip):
    """
    Nested strip labels.

    Merges adjacent strip labels that share the same parent
    value, producing a hierarchical strip display.

    Parameters
    ----------
    nest_line : bool
        If True, draw a line between parent and child
        strip levels.
    solo_line : bool
        If True, draw a line even when there is only one
        child category.
    resect : float
        Amount (in [0, 1]) to shorten the nesting line
        at each end.
    bleed : bool
        If True, nesting indicators may extend into
        neighbouring strips.
    """

    def __init__(
        self,
        *,
        nest_line: bool = False,
        solo_line: bool = False,
        resect: float = 0,
        bleed: bool = False,
    ):
        self.nest_line = nest_line
        self.solo_line = solo_line
        self.resect = resect
        self.bleed = bleed

    def setup(self, layout: Any) -> None:
        """Prepare nested strip data from the layout."""
        self.layout = layout

    def draw(self, label_info: Any) -> Any:
        """Draw merged strip labels with optional nest lines."""
        raise NotImplementedError(
            "strip_nested direct drawing is not available through "
            "plotnine's public strip API; use facet_nested instead"
        )
