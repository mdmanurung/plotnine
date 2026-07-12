"""
Individually themed strip labels.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .strip import Strip

if TYPE_CHECKING:
    from typing import Any, Optional, Sequence


class strip_themed(Strip):
    """
    Individually themed strip labels.

    Allows each strip level or individual strips to have
    distinct visual styling (background colour, text style,
    etc.) via per-strip theme elements.

    Parameters
    ----------
    background_x : list of theme elements, optional
        Background themes for horizontal strip levels.
    background_y : list of theme elements, optional
        Background themes for vertical strip levels.
    text_x : list of theme elements, optional
        Text themes for horizontal strip levels.
    text_y : list of theme elements, optional
        Text themes for vertical strip levels.
    """

    def __init__(
        self,
        *,
        background_x: Optional[Sequence[Any]] = None,
        background_y: Optional[Sequence[Any]] = None,
        text_x: Optional[Sequence[Any]] = None,
        text_y: Optional[Sequence[Any]] = None,
    ):
        self.background_x = list(background_x) if background_x else []
        self.background_y = list(background_y) if background_y else []
        self.text_x = list(text_x) if text_x else []
        self.text_y = list(text_y) if text_y else []

    def draw(self, label_info: Any) -> Any:
        """Draw strips with individual theme overrides."""
        raise NotImplementedError(
            "strip_themed requires per-strip theme hooks that are not "
            "available in plotnine 0.15/0.16"
        )
