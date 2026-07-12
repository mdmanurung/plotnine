"""
Split strips placing variables on different sides.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from .strip import Strip

if TYPE_CHECKING:
    from typing import Any, Sequence


class strip_split(Strip):
    """
    Split strip labels across panel sides.

    Places different faceting variable levels on different
    sides of the panel (e.g. one variable on top, another
    on the right).

    Parameters
    ----------
    position : list of str
        Where to place each strip level. Values are
        "top", "bottom", "left", or "right".
    """

    def __init__(
        self,
        position: Sequence[Literal["top", "bottom", "left", "right"]] = (
            "top",
            "right",
        ),
    ):
        self.position = list(position)

    def draw(self, label_info: Any) -> Any:
        """Draw strips on their assigned sides."""
        raise NotImplementedError(
            "strip_split requires plotnine strip-side routing hooks that "
            "are not available in plotnine 0.15/0.16"
        )
