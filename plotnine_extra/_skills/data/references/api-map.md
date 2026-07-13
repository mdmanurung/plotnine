# API Map

Import from `plotnine_extra` for user examples:

```python
from plotnine import aes, ggplot
from plotnine_extra import geom_pointdensity, theme_pubr
```

## Geoms

- `geom_pointdensity`: scatterplot colored by local point density.
- `geom_beeswarm`, `geom_quasirandom`: categorical point layouts.
- `geom_bracket`, `geom_signif`, `geom_pwc`: significance annotations.
- `geom_richtext`, `geom_textbox`: markdown-like text labels and text boxes.
- `geom_text_repel`, `geom_label_repel`, `geom_text_aimed`: text placement
  helpers.
- `geom_half_violin`, `geom_half_boxplot`, `geom_box`: compact distribution
  layers.
- `geom_pointpath`, `geom_spoke`, `geom_outline_point`, `geom_rectmargin`,
  `geom_tilemargin`, and `annotation_stripes`: specialized plotting layers.

## Positions

- `position_beeswarm`: accepts `method`, `priority`, `side`, and `corral`.
  Invalid option names raise `ValueError`.
- `position_quasirandom`: accepts `method`, `width`, and related categorical
  jitter controls. Invalid option names raise `ValueError`.
- `position_disjoint_ranges`, `position_lineartrans`: range and linear
  transform position helpers.

## Themes, Palettes, and Helpers

- Themes include `theme_pubr`, `theme_pubclean`, `theme_clean`,
  `theme_classic2`, `theme_nature`, `theme_scientific`, `theme_poster`,
  `theme_cleveland`, and `theme_transparent`.
- Styling helpers include `ggpar`, `font`, `bgcolor`, `border`, `grids`,
  `labs_pubr`, `rotate`, `rotate_x_text`, `rotate_y_text`, `rremove`,
  `xscale`, and `yscale`.
- Palette helpers include `set_palette`, `get_palette`, `color_palette`,
  `fill_palette`, `gradient_color`, `gradient_fill`, `change_palette`,
  `show_point_shapes`, and `show_line_types`.
- Summary helpers include `get_summary_stats`, `desc_statby`, `add_summary`,
  `mean_ci`, `mean_sd`, `mean_se_`, `mean_range`, `median_iqr`,
  `median_mad`, `median_range`, `median_q1q3`, and `median_hilow_`.

## Scales and Coordinates

- Multi-aesthetic scales: `scale_color_multi`, `scale_colour_multi`,
  `scale_fill_multi`, and `scale_listed`.
- Manual position scales: `scale_x_manual`, `scale_y_manual`.
- Inside axes: `coord_axes_inside` plus `apply_axes_inside`.
