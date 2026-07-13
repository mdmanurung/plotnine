# Feature Parity Roadmap

Date: 2026-07-13
Project: /exports/para-lipg-hpc/mdmanurung/_hobby/plotnine-extra
Status: planned

## Objective

Use the current `plotnine-extra` API as the baseline for the next feature
roadmap. The target is selective parity with ggpubr, ggh4x, ggthemes, and
plotthis where the result fits a lightweight plotnine extension package.

This roadmap is for post-0.3.1 feature work. It is not a release-blocker list
for the current patch release.

## Parity Snapshot

### ggh4x

Current parity is strongest here. `plotnine-extra` already covers extended
facets, per-panel position scales, axis guide helpers, `guide_stringlegend`,
strip descriptors, multi-scales, selected stats, selected geoms, selected
positions, and axes-inside support.

Remaining high-value gaps:

- `at_panel` and `ggsubset` for targeting layers to selected panels.
- `force_panelsizes` for explicit panel width and height control.
- `strip_vanilla` as the baseline strip descriptor.
- `scale_x_dendrogram` and `scale_y_dendrogram`.
- `center_limits` and `help_secondary`.
- `geom_polygonraster`.
- Smaller theme element and factor helpers such as `element_part_rect`,
  `elem_list_text`, `elem_list_rect`, `weave_factors`, `sep_discrete`, and
  `save_plot`.

### ggpubr

Current parity is useful but incomplete. The package already has statistical
annotation layers, pairwise comparison layers, p-value formatting, summary
helpers, ggpubr-style themes, palette helpers, and styling utilities.

Remaining high-value gaps:

- High-level plot constructors such as `ggboxplot`, `ggviolin`, `ggscatter`,
  `gghistogram`, `ggdensity`, `ggbarplot`, `ggline`, and `ggpaired`.
- `compare_means` as a non-plotting statistical workflow helper.
- Arrangement and figure helpers such as `ggarrange`, `annotate_figure`,
  `get_legend`, and `get_breaks`.
- Compatibility aliases where they improve migration, such as `stat_bracket`.

### ggthemes

Direct parity is low. `plotnine-extra` has publication-oriented themes, but it
does not yet include the recognizable ggthemes palette, scale, theme, and geom
families.

Remaining high-value gaps:

- Palette and scale families for colorblind, Tableau, Economist, Excel, Few,
  FiveThirtyEight, Google Docs, Highcharts, Solarized, Stata, and WSJ.
- Theme families such as `theme_economist`, `theme_few`,
  `theme_fivethirtyeight`, `theme_tufte`, and `theme_wsj`.
- `geom_rangeframe`, `geom_tufteboxplot`, and `stat_fivenumber`.
- Utility helpers such as `bank_slopes`, `extended_range_breaks`, and
  `smart_digits`.

### plotthis

Direct parity is very low, and full parity should not be the default target.
plotthis is a broad high-level plotting package covering common chart wrappers
and domain-specific plots such as volcano plots, dimensional-reduction plots,
ROC curves, heatmaps, networks, enrichment plots, Venn/UpSet diagrams, spatial
plots, Sankey/alluvial plots, and word clouds.

`plotnine-extra` should treat plotthis as selective inspiration. The next
roadmap should adopt lightweight scientific plot builders that can return
ordinary plotnine plots without large required dependencies. Full plotthis
coverage would pull the package toward a separate scientific plotting toolkit,
which is a different dependency and maintenance profile.

Good candidates:

- `ggvolcano`, with a `VolcanoPlot` compatibility alias.
- `ggdim`, with a `DimPlot` compatibility alias.
- `ggfeaturedim`, with a `FeatureDimPlot` compatibility alias.
- `ggroc`, with a `ROCCurve` compatibility alias.

Deferred unless optional dependencies are explicitly accepted:

- Heatmaps and linked heatmaps.
- Network, enrichment, GSEA, and graph layouts.
- Venn, Euler, and UpSet diagrams.
- Spatial plotting.
- Sankey, alluvial, chord, circos, and word cloud plots.

Reference sources:

- ggpubr reference: <https://rpkgs.datanovia.com/ggpubr/reference/index.html>
- ggh4x reference: <https://teunbrand.github.io/ggh4x/reference/index.html>
- ggthemes reference: <https://jrnold.github.io/ggthemes/reference/index.html>
- plotthis reference: <https://pwwang.github.io/plotthis/reference/index.html>
- plotthis repository: <https://github.com/pwwang/plotthis>

## Five Best Next Additions

1. **ggh4x completion pack**

   Add `at_panel`, `ggsubset`, `force_panelsizes`, `strip_vanilla`,
   `center_limits`, `help_secondary`, and `geom_polygonraster`.

   Implementation notes:

   - Keep the public API close to ggh4x names where Python syntax permits.
   - Make layer targeting work with existing facet layout metadata.
   - Prefer plotnine-native scale/theme objects over post-render patches.
   - Document partial behavior when plotnine does not expose a matching hook.

2. **High-level plot constructor pack**

   Add `plotnine_extra.plots` and export ggpubr-style constructors:
   `ggboxplot`, `ggviolin`, `ggscatter`, `gghistogram`, `ggdensity`,
   `ggbarplot`, `ggline`, and `ggpaired`.

   Add selective plotthis-inspired scientific constructors: `ggvolcano`,
   `ggdim`, `ggfeaturedim`, and `ggroc`. Provide `VolcanoPlot`, `DimPlot`,
   `FeatureDimPlot`, and `ROCCurve` as compatibility aliases.

   Implementation notes:

   - Return ordinary plotnine `ggplot` objects unless a split layout requires
     the existing composition system.
   - Use existing `geom_text_repel`, `stat_compare_means`, `stat_pwc`,
     palettes, themes, and composition helpers.
   - Avoid new required dependencies. Implement ROC/AUC calculations with
     numpy/pandas/scipy-level code.
   - Keep argument sets smaller than plotthis where needed; prioritize stable,
     documented behavior over copying every option.

3. **ggpubr workflow utilities**

   Add `compare_means`, `get_legend`, `get_breaks`, `annotate_figure`,
   `ggarrange`, and `stat_bracket`.

   Implementation notes:

   - Reuse the existing statistical test internals so plotted and non-plotted
     results agree.
   - Implement `ggarrange` as a thin compatibility layer over the current
     composition API.
   - Make extraction helpers return deterministic Python objects and raise
     clear errors when plotnine internals do not expose the requested data.

4. **ggthemes palette and scale pack**

   Add named palettes and `scale_color_*` / `scale_colour_*` /
   `scale_fill_*` helpers for colorblind, Tableau, Economist, Excel, Few,
   FiveThirtyEight, Google Docs, Highcharts, Solarized, Stata, and WSJ.

   Implementation notes:

   - Vendor small color tables as data constants.
   - Use the existing palette helper style where possible.
   - Test deterministic color output and plotnine scale construction.

5. **ggthemes theme and geom pack**

   Add `theme_economist`, `theme_few`, `theme_fivethirtyeight`,
   `theme_tufte`, `theme_wsj`, `geom_rangeframe`, `geom_tufteboxplot`,
   `stat_fivenumber`, `bank_slopes`, `extended_range_breaks`, and
   `smart_digits`.

   Implementation notes:

   - Implement themes in the existing `plotnine_extra.themes` style.
   - Keep geoms and stats as normal plotnine subclasses.
   - Treat theme pixel-perfect parity as best effort; test visible structure
     and stable parameters rather than brittle image equality.

## Public API Defaults

- Export stable additions from `plotnine_extra.__init__`.
- Keep required dependencies unchanged: `plotnine` and `scipy`.
- Put high-level constructors in `plotnine_extra/plots/`.
- Use lowercase ggpubr-style names as the primary Python API.
- Use CamelCase aliases only for the selected plotthis compatibility
  constructors.
- Keep domain-heavy plotthis features out of core until optional dependency
  policy is chosen.

## Validation

For each feature pack:

- Add import and star-export tests for every new public symbol.
- Add object-level plot tests that verify returned objects, mappings, layers,
  labels, facets, and scales without fragile image baselines.
- Add numeric tests for `compare_means`, ROC/AUC calculation, volcano
  category assignment, and five-number summaries.
- Add palette and theme tests for deterministic colors and successful drawing.
- Add documentation examples or vignettes for new user-facing APIs.

Final verification commands:

```bash
python3 -m pytest tests -q
ruff check plotnine_extra tests
ruff format --check plotnine_extra tests
python3 -m compileall -q plotnine_extra
```

## Notes

- This roadmap deliberately favors features that fit the current package:
  plotnine extensions, ggpubr-style statistical workflows, ggh4x-style layout
  helpers, and lightweight scientific plot constructors.
- Full plotthis parity should be considered a separate product decision because
  it implies optional dependencies and a broader domain plotting surface.
- Existing `docs/PORTING_PLAN.md` should remain as historical context. This
  file is the current forward-looking roadmap.
