"""
Colour palette helpers ported from ggpubr / ggsci.
"""

from ._ggsci import BREWER_PALETTES, GGSCI_PALETTES, all_palette_names
from ._ggthemes import GGTHEMES_PALETTES, ggthemes_palette
from .palettes import (
    change_palette,
    color_palette,
    fill_palette,
    get_palette,
    gradient_color,
    gradient_fill,
    set_palette,
    show_line_types,
    show_point_shapes,
)

__all__ = (
    "BREWER_PALETTES",
    "GGSCI_PALETTES",
    "GGTHEMES_PALETTES",
    "all_palette_names",
    "change_palette",
    "color_palette",
    "fill_palette",
    "get_palette",
    "ggthemes_palette",
    "gradient_color",
    "gradient_fill",
    "set_palette",
    "show_line_types",
    "show_point_shapes",
)
