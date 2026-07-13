"""
Vanilla strip descriptor.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from .strip import Strip

if TYPE_CHECKING:
    from typing import Any


class strip_vanilla(Strip):  # noqa: N801
    """
    Default strip descriptor compatible with ggh4x naming.

    Plotnine owns the actual strip drawing. This descriptor records the
    requested vanilla-strip options so extended facets can accept the same
    public API as other strip descriptors.
    """

    def __init__(
        self,
        *,
        clip: Literal["inherit", "on", "off"] = "inherit",
        size: Literal["constant", "variable"] = "constant",
    ):
        if clip not in {"inherit", "on", "off"}:
            msg = "strip_vanilla clip must be 'inherit', 'on', or 'off'"
            raise ValueError(msg)
        if size not in {"constant", "variable"}:
            msg = "strip_vanilla size must be 'constant' or 'variable'"
            raise ValueError(msg)
        self.clip = clip
        self.size = size

    def setup(self, layout: Any) -> None:
        self.layout = layout

    def draw(self, label_info: Any) -> Any:
        raise NotImplementedError(
            "strip_vanilla direct drawing is handled by plotnine facets"
        )
