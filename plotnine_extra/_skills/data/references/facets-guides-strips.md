# Facets, Guides, and Strips

Extended facet helpers:

- `facet_grid2`, `facet_wrap2`: plotnine facets with inner-axis controls and
  per-panel scale support.
- `facet_nested`, `facet_nested_wrap`: nested facet variants.
- `facet_manual`: design-matrix layout. Repeated labels span cells; `#` and
  `NA` are empty cells. Validate that the design labels match the facet values.
- `facetted_pos_scales`: low-level per-panel position scale container.
- `scale_x_facet`, `scale_y_facet`: selector-based per-panel scales.

`scale_x_facet` and `scale_y_facet` evaluate selectors against layout rows.
Earlier matching scales have priority over later matching scales. Invalid
selector expressions raise `ValueError`.

## Axis Guides

Use guide helpers through a position scale whenever possible:

```python
from plotnine import scale_x_continuous
from plotnine_extra import guide_axis_manual

scale_x_continuous(
    guide=guide_axis_manual(
        breaks=[0, 5, 10],
        labels=["low", "mid", "high"],
    )
)
```

Supported helpers:

- `guide_axis_manual`: independent breaks and labels, label styling, axis color,
  and truncation.
- `guide_axis_colour` / `guide_axis_color`: per-label color and axis/tick color.
- `guide_axis_minor`: visible minor ticks and optional minor labels.
- `guide_axis_logticks`: log tick marks for requested sides.
- `guide_axis_truncated`: spine bounds from numeric or callable limits.
- `guide_axis_scalebar`: data-coordinate scalebar with an optional label.
- `guide_axis_nested`: delimiter-split multiline labels with nesting lines.
- `guide_dendro`: dendrogram or scipy linkage aligned to tick order.
- `guide_stringlegend`: text-only color/fill legend. Use
  `guides(color=guide_stringlegend(...))` or `guide="stringlegend"`.

Plot-added axis guides default to the x axis unless `position` is left or right.

## Strips

- `strip_nested`: merged adjacent parent labels with nesting-line options.
- `strip_themed`: per-strip text and background theme overrides.
- `strip_split`: routes facet variables to separate strip sides where plotnine
  exposes the needed hooks; unsupported layouts raise a clear error.
- `strip_tag`: panel tags at the requested strip position.
