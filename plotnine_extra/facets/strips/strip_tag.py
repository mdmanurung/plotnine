"""
Tag-style strip labels rendered as text on panels.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from .strip import Strip

if TYPE_CHECKING:
    from typing import Any, Optional, Sequence


def _default_tags() -> list[str]:
    """Return uppercase A-Z as default panel tags."""
    return [chr(i) for i in range(ord("A"), ord("Z") + 1)]


class strip_tag(Strip):
    """
    Tag-style strip labels.

    Instead of a strip bar above or beside the panel, labels
    are rendered as a small text tag within the panel area
    (e.g. "(a)", "(b)", …).

    Parameters
    ----------
    tag_pool : list of str, optional
        Labels to use. Defaults to uppercase A-Z.
    position : str
        Where within the panel to place the tag. One of
        "topleft", "top", "topright", "left", "right",
        "bottomleft", "bottom", "bottomright".
    prefix : str
        Text prepended to each tag (e.g. "(").
    suffix : str
        Text appended to each tag (e.g. ")").
    """

    def __init__(
        self,
        tag_pool: Optional[Sequence[str]] = None,
        *,
        position: Literal[
            "topleft",
            "top",
            "topright",
            "left",
            "right",
            "bottomleft",
            "bottom",
            "bottomright",
        ] = "topleft",
        prefix: str = "",
        suffix: str = "",
    ):
        self.tag_pool = list(tag_pool) if tag_pool else _default_tags()
        self.position = position
        self.prefix = prefix
        self.suffix = suffix

    def draw(self, label_info: Any) -> Any:
        """Draw tag text within the panel area."""
        raise NotImplementedError(
            "strip_tag requires panel-aware strip drawing hooks that are not "
            "available in plotnine 0.15/0.16"
        )
