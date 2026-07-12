"""
plotnine_extra: Extension package for plotnine
==============================================

This package extends plotnine with additional geoms, stats,
positions, themes, plot composition, and animation support.

Usage
-----
    from plotnine_extra import *

This imports all of plotnine's public API plus the extra
components provided by this package.

Extra Components
----------------
Geoms:
    - geom_pointdensity: Scatterplot with density estimation
    - geom_spoke: Line segments parameterised by angle/radius
    - geom_bracket: Significance brackets with labels
    - geom_beeswarm: Beeswarm categorical scatter plots
    - geom_quasirandom: Quasi-random categorical scatter plots
    - geom_richtext: Rich text labels with markdown support
    - geom_textbox: Text boxes with word wrapping
    - annotation_stripes: Alternating background stripes

Positions:
    - position_beeswarm: Beeswarm point positioning
    - position_quasirandom: Quasi-random point positioning

Themes:
    - element_markdown: Theme element for markdown-styled text
    - element_textbox_simple: Theme element for boxed text

Stats:
    - stat_pointdensity: Density estimation at each point
    - stat_mean: Group mean points (centroids)
    - stat_chull: Convex hull of point groups
    - stat_stars: Star segments from centroid to data points
    - stat_central_tendency: Mean/median/mode lines
    - stat_conf_ellipse: Confidence ellipses
    - stat_cor: Correlation coefficients with p-values
    - stat_regline_equation: Regression equations with R²
    - stat_overlay_normal_density: Normal density overlays
    - stat_compare_means: Group comparison p-values
    - stat_anova_test: ANOVA test annotations
    - stat_kruskal_test: Kruskal-Wallis test annotations
    - stat_welch_anova_test: Welch ANOVA annotations
    - stat_friedman_test: Friedman test annotations
    - stat_pvalue_manual: Manual p-value placement
    - stat_pwc: Pairwise comparison p-values with brackets

Composition:
    - Compose, Beside, Stack, Wrap: Plot composition operators
    - plot_layout: Customise composition layout
    - plot_annotation: Annotate compositions
    - plot_spacer: Blank space in compositions

Animation:
    - PlotnineAnimation: Create animations from ggplot objects

Datasets (via ``plotnine_extra.data``):
    - ToothGrowth: Tooth growth in guinea pigs (ggpubr example data)
"""

import warnings as _warnings

from plotnine import *  # noqa: F401, F403
from plotnine import __all__ as _plotnine_all
from plotnine import __version__ as _plotnine_version

# Warn if plotnine version is untested
_tested_plotnine = ("0.15", "0.16")
if not any(_plotnine_version.startswith(v) for v in _tested_plotnine):
    _warnings.warn(
        f"plotnine-extra has been tested with plotnine "
        f"0.15.x-0.16.x but you have "
        f"{_plotnine_version}."
        f" Some features may not work correctly.",
        stacklevel=2,
    )

from .animation import PlotnineAnimation  # noqa: E402
from .composition import (
    Beside,
    Compose,
    Stack,
    Wrap,
    plot_annotation,
    plot_layout,
    plot_spacer,
)
from .coords import apply_axes_inside, coord_axes_inside
from .geoms import (
    annotation_stripes,
    geom_beeswarm,
    geom_box,
    geom_bracket,
    geom_half_boxplot,
    geom_half_violin,
    geom_label_repel,
    geom_outline_point,
    geom_pointdensity,
    geom_pointpath,
    geom_pwc,
    geom_quasirandom,
    geom_rectmargin,
    geom_richtext,
    geom_signif,
    geom_spoke,
    geom_text_aimed,
    geom_text_repel,
    geom_textbox,
    geom_tilemargin,
)
from .guides import (
    guide_axis_color,
    guide_axis_colour,
    guide_axis_logticks,
    guide_axis_manual,
    guide_axis_minor,
    guide_axis_nested,
    guide_axis_scalebar,
    guide_axis_truncated,
    guide_dendro,
    guide_stringlegend,
)
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
from .positions import (
    position_beeswarm,
    position_disjoint_ranges,
    position_lineartrans,
    position_quasirandom,
)
from .scales import (
    scale_color_multi,
    scale_colour_multi,
    scale_fill_multi,
    scale_listed,
    scale_x_manual,
    scale_y_manual,
)
from .stats import (
    create_p_label,
    format_p_value,
    get_p_format_style,
    ggadjust_pvalue,
    list_p_format_styles,
    stat_anova_test,
    stat_central_tendency,
    stat_centroid,
    stat_chull,
    stat_compare,
    stat_compare_means,
    stat_conf_ellipse,
    stat_cor,
    stat_difference,
    stat_friedman_test,
    stat_funxy,
    stat_kruskal_test,
    stat_mean,
    stat_midpoint,
    stat_overlay_normal_density,
    stat_pointdensity,
    stat_pvalue_manual,
    stat_pwc,
    stat_regline_equation,
    stat_rle,
    stat_rollingkernel,
    stat_stars,
    stat_theodensity,
    stat_welch_anova_test,
)
from .themes import (
    bgcolor,
    border,
    clean_theme,
    element_markdown,
    element_textbox_simple,
    font,
    ggpar,
    grids,
    labs_pubr,
    rotate,
    rotate_x_text,
    rotate_y_text,
    rremove,
    theme_classic2,
    theme_clean,
    theme_cleveland,
    theme_nature,
    theme_poster,
    theme_pubclean,
    theme_pubr,
    theme_scientific,
    theme_transparent,
    xscale,
    yscale,
)
from .utils import (
    add_summary,
    desc_statby,
    get_summary_stats,
    mean_ci,
    mean_range,
    mean_sd,
    mean_se_,
    median_hilow_,
    median_iqr,
    median_mad,
    median_q1q3,
    median_range,
)

__version__ = "0.3.0"

# Extend plotnine's __all__ with our extras
_extra_all = (
    # Geoms
    "annotation_stripes",
    "geom_beeswarm",
    "geom_box",
    "geom_bracket",
    "geom_half_boxplot",
    "geom_half_violin",
    "geom_label_repel",
    "geom_outline_point",
    "geom_pointdensity",
    "geom_pointpath",
    "geom_pwc",
    "geom_quasirandom",
    "geom_rectmargin",
    "geom_richtext",
    "geom_signif",
    "geom_spoke",
    "geom_text_aimed",
    "geom_text_repel",
    "geom_textbox",
    "geom_tilemargin",
    # Positions
    "position_beeswarm",
    "position_disjoint_ranges",
    "position_lineartrans",
    "position_quasirandom",
    # Theme elements
    "element_markdown",
    "element_textbox_simple",
    # Themes
    "clean_theme",
    "theme_classic2",
    "theme_clean",
    "theme_cleveland",
    "theme_nature",
    "theme_poster",
    "theme_pubclean",
    "theme_pubr",
    "theme_scientific",
    "theme_transparent",
    # Theme styling helpers
    "bgcolor",
    "border",
    "font",
    "ggpar",
    "grids",
    "labs_pubr",
    "rotate",
    "rotate_x_text",
    "rotate_y_text",
    "rremove",
    "xscale",
    "yscale",
    # Palettes
    "change_palette",
    "color_palette",
    "fill_palette",
    "get_palette",
    "gradient_color",
    "gradient_fill",
    "set_palette",
    "show_line_types",
    "show_point_shapes",
    # Scales
    "scale_color_multi",
    "scale_colour_multi",
    "scale_fill_multi",
    "scale_listed",
    "scale_x_manual",
    "scale_y_manual",
    # Guides (placeholders)
    "guide_axis_color",
    "guide_axis_colour",
    "guide_axis_logticks",
    "guide_axis_manual",
    "guide_axis_minor",
    "guide_axis_nested",
    "guide_axis_scalebar",
    "guide_axis_truncated",
    "guide_dendro",
    "guide_stringlegend",
    # Coords
    "coord_axes_inside",
    "apply_axes_inside",
    # Stats
    "stat_anova_test",
    "stat_central_tendency",
    "stat_centroid",
    "stat_chull",
    "stat_compare",
    "stat_compare_means",
    "stat_conf_ellipse",
    "stat_cor",
    "stat_difference",
    "stat_friedman_test",
    "stat_funxy",
    "stat_kruskal_test",
    "stat_mean",
    "stat_midpoint",
    "stat_overlay_normal_density",
    "stat_pointdensity",
    "stat_pvalue_manual",
    "stat_pwc",
    "stat_regline_equation",
    "stat_rle",
    "stat_rollingkernel",
    "stat_stars",
    "stat_theodensity",
    "stat_welch_anova_test",
    # P-value helpers
    "create_p_label",
    "format_p_value",
    "get_p_format_style",
    "ggadjust_pvalue",
    "list_p_format_styles",
    # Summary helpers
    "add_summary",
    "desc_statby",
    "get_summary_stats",
    "mean_ci",
    "mean_range",
    "mean_sd",
    "mean_se_",
    "median_hilow_",
    "median_iqr",
    "median_mad",
    "median_q1q3",
    "median_range",
    # Composition
    "Compose",
    "Beside",
    "Stack",
    "Wrap",
    "plot_annotation",
    "plot_layout",
    "plot_spacer",
    # Animation
    "PlotnineAnimation",
)

__all__ = tuple(dict.fromkeys((*_plotnine_all, *_extra_all)))
