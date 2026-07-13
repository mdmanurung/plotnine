"""
Themes inspired by ggthemes.
"""

from __future__ import annotations

from plotnine import (
    element_blank,
    element_line,
    element_rect,
    element_text,
    theme,
    theme_bw,
    theme_minimal,
)


class theme_economist(theme_bw):
    """Economist-inspired theme."""

    def __init__(self, base_size: float = 11, base_family: str = ""):
        super().__init__(base_size=base_size, base_family=base_family)
        self += theme(
            panel_background=element_rect(fill="#D5E4EB", color=None),
            plot_background=element_rect(fill="#D5E4EB", color=None),
            panel_border=element_blank(),
            panel_grid_major=element_line(color="white", size=0.6),
            panel_grid_minor=element_blank(),
            axis_line=element_blank(),
            axis_ticks=element_blank(),
            plot_title=element_text(weight="bold", size=base_size * 1.25),
            legend_background=element_rect(fill="#D5E4EB", color=None),
            legend_key=element_rect(fill="#D5E4EB", color=None),
        )


class theme_few(theme_bw):
    """Stephen Few-inspired restrained theme."""

    def __init__(self, base_size: float = 11, base_family: str = ""):
        super().__init__(base_size=base_size, base_family=base_family)
        self += theme(
            panel_background=element_rect(fill="white", color=None),
            panel_border=element_blank(),
            panel_grid_major=element_line(color="#DDDDDD", size=0.35),
            panel_grid_minor=element_blank(),
            axis_line=element_line(color="#333333", size=0.35),
            axis_ticks=element_line(color="#333333", size=0.35),
            legend_key=element_rect(fill="white", color=None),
        )


class theme_fivethirtyeight(theme_minimal):
    """FiveThirtyEight-inspired theme."""

    def __init__(self, base_size: float = 12, base_family: str = ""):
        super().__init__(base_size=base_size, base_family=base_family)
        self += theme(
            panel_background=element_rect(fill="#F0F0F0", color=None),
            plot_background=element_rect(fill="#F0F0F0", color=None),
            panel_grid_major=element_line(color="white", size=0.8),
            panel_grid_minor=element_blank(),
            axis_title=element_blank(),
            axis_ticks=element_blank(),
            plot_title=element_text(weight="bold", size=base_size * 1.35),
            legend_background=element_rect(fill="#F0F0F0", color=None),
            legend_key=element_rect(fill="#F0F0F0", color=None),
        )


class theme_tufte(theme_minimal):
    """Tufte-inspired low-ink theme."""

    def __init__(self, base_size: float = 11, base_family: str = ""):
        super().__init__(base_size=base_size, base_family=base_family)
        self += theme(
            panel_grid_major=element_blank(),
            panel_grid_minor=element_blank(),
            axis_line=element_line(color="#222222", size=0.3),
            axis_ticks=element_line(color="#222222", size=0.3),
            legend_key=element_rect(fill="white", color=None),
        )


class theme_wsj(theme_bw):
    """Wall Street Journal-inspired theme."""

    def __init__(self, base_size: float = 11, base_family: str = ""):
        super().__init__(base_size=base_size, base_family=base_family)
        self += theme(
            panel_background=element_rect(fill="#F8F4E8", color=None),
            plot_background=element_rect(fill="#F8F4E8", color=None),
            panel_border=element_blank(),
            panel_grid_major=element_line(color="#D8D0BD", size=0.45),
            panel_grid_minor=element_blank(),
            axis_line=element_line(color="#333333", size=0.35),
            axis_ticks=element_line(color="#333333", size=0.35),
            plot_title=element_text(weight="bold", size=base_size * 1.25),
            legend_background=element_rect(fill="#F8F4E8", color=None),
            legend_key=element_rect(fill="#F8F4E8", color=None),
        )
