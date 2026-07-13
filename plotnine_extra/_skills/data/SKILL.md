---
name: plotnine-extra
description: "Use when working with plotnine-extra or `plotnine_extra`: user plots, examples, docs, vignettes, or package code using `geom_pointdensity`, `geom_beeswarm`, `stat_pwc`, `stat_compare_means`, `stat_pvalue_manual`, `facet_manual`, `facet_wrap2`, `scale_x_facet`, `scale_y_facet`, `guide_axis_manual`, `guide_stringlegend`, `strip_nested`, `plot_layout`, or `PlotnineAnimation`. Read this before writing plotnine-extra code, debugging statistical annotations, or porting ggplot2, ggpubr, ggh4x, patchwork, or gganimate-style APIs."
license: MIT
---

# plotnine-extra

`plotnine-extra` extends plotnine with ggplot2-adjacent tools: extra geoms,
stats, facets, guides, strips, composition operators, themes, palettes, and
animation helpers. Prefer the package's public API over reaching into private
modules unless you are fixing the package itself.

Start with `from plotnine_extra import *` when reproducing user examples. For
library code, import the specific object from `plotnine_extra`.

## Workflow

1. Identify the API family in the request, then read the matching reference
   file below before writing code.
2. Check the current source, docstring, or tests for the specific object before
   relying on memory. This package tracks plotnine internals closely.
3. For examples and docs, prefer a minimal plot that can be drawn with
   `plot.draw(show=False)`. Use `MPLCONFIGDIR=/tmp/plotnine-extra-mplconfig`
   when running local smoke checks.
4. For package changes, run focused tests for the touched API plus `ruff check`
   and `ruff format --check` on changed Python files.

## Task to Reference

| If the task is... | Read |
|---|---|
| choosing an extra layer, position, theme, palette, or composition helper | [references/api-map.md](references/api-map.md) |
| statistical annotations, pairwise tests, paired designs, p-value labels, or manual p-values | [references/statistical-annotations.md](references/statistical-annotations.md) |
| extended facets, per-panel scales, axis guides, or strip descriptors | [references/facets-guides-strips.md](references/facets-guides-strips.md) |
| plot composition or animation from multiple plotnine objects | [references/composition-animation.md](references/composition-animation.md) |

## Package Rules

- Requires Python >= 3.10 and plotnine >= 0.15.3,<0.17.
- Axis guide helpers are Matplotlib-backed. Use them through
  `scale_x_continuous(..., guide=...)`, `scale_y_*`, or add a guide object to
  plots that use the extended facets.
- Statistical comparison layers do not support horizontal orientation by
  silently testing encoded discrete y-values. If a user wants horizontal plots,
  orient the data explicitly or expect a clear error.
- For paired tests in `stat_pwc` or `stat_compare_means`, pass `wid=` and keep
  one observation per subject/group pair with complete paired blocks.
- `facet_manual` treats repeated non-empty design labels as spanning panels.
  `#` and `NA` denote empty cells.
- Composition operators mirror patchwork-style syntax: `|`, `/`, `+`, `-`, `&`,
  and `*` have package-specific meanings. Read the composition reference before
  rewriting them.
