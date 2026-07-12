# Release Blocker Unblock Plan

## Summary

Implement all remaining release blockers for `plotnine-extra` as a `0.3.1`
release candidate. This plan uses the larger "near ggh4x parity" route: no
exported placeholder/no-op APIs remain, statistical annotations fail loudly
instead of silently producing wrong results, release metadata/workflows validate
the exact artifact, and CI covers the release-critical checks.

Reference behavior should follow the ggh4x docs for `facet_manual`,
`scale_x_facet`/`scale_y_facet`, `guide_axis_manual`, and
`guide_stringlegend`.

## Key Changes

- Commit the existing review fixes first: star-import export restoration,
  Welch/Hommel/stat fixes, import-time performance fix, and
  `plotnine>=0.15.3,<0.17`.
- Bump package version to `0.3.1` in `pyproject.toml`,
  `plotnine_extra.__version__`, README release examples, and tests.
- Implement axis-guide support by adding a shared axis-guide renderer consumed
  by `facet_grid2`, `facet_wrap2`, `facet_nested`, `facet_nested_wrap`, and
  `facet_manual` through `set_limits_breaks_and_labels`.
- Support `scale_x_continuous(..., guide=guide_axis_*())`, `scale_y_*`, and
  `plot + guide_axis_*()` fallback. Fallback attaches to x unless `position` is
  left/right.
- Implement near-parity behavior for:
  - `guide_axis_manual`: independent breaks/labels, label color/size/angle,
    axis color, truncation.
  - `guide_axis_colour`/`guide_axis_color`: per-label color and axis/tick color.
  - `guide_axis_minor`: visible minor ticks and optional minor labels.
  - `guide_axis_logticks`: log-scale tick marks for requested sides.
  - `guide_axis_truncated`: spine bounds from numeric or callable lower/upper
    limits.
  - `guide_axis_scalebar`: data-coordinate scalebar with optional label.
  - `guide_axis_nested`: delimiter-split multiline labels plus nesting line
    support.
  - `guide_dendro`: render scipy linkage or dendrogram dict aligned to tick
    order.
- Implement `guide_stringlegend` as a real plotnine `guide` subclass registered
  as `guide_stringlegend`, usable via `guides(color=guide_stringlegend(...))`
  and scale `guide="stringlegend"`.

## Facets, Strips, And Scale Facets

- Implement `scale_x_facet`/`scale_y_facet` through the existing
  `facetted_pos_scales` mechanism:
  - Add `type="continuous"`/`"discrete"` support.
  - Evaluate selectors against layout rows.
  - Raise `ValueError` on invalid selector expressions.
  - Preserve ggh4x priority: earlier matching scale overrides later matching
    scale.
- Upgrade `facet_manual`:
  - Validate design/facet cardinality instead of silently dropping panels.
  - Treat repeated design labels as spanning panels with row/column span
    metadata.
  - Support `widths`, `heights`, `axes`, `remove_labels`, and `trim_blank`.
  - Keep `#` and `NA` as empty cells.
- Implement exported strip classes:
  - `strip_nested`: merged adjacent parent labels plus `nest_line`,
    `solo_line`, `resect`, `bleed`.
  - `strip_themed`: per-strip text/background theme overrides.
  - `strip_split`: route variables to separate strip sides where plotnine
    permits; otherwise raise a clear unsupported-layout error.
  - `strip_tag`: draw panel tag labels at the requested strip position.
- Update docs so every top-level exported guide/facet/strip API has a real
  example or is clearly marked as partial when plotnine internals prevent exact
  ggh4x parity.

## Statistical And Validation Fixes

- Move horizontal-orientation detection into `plotnine_extra.stats._common` and
  reuse it in `stat_compare`, `stat_pwc`, and `stat_compare_means`. Raise
  `NotImplementedError` instead of silently testing encoded discrete y-values.
- Add `wid` to `stat_pwc` and `stat_compare_means`; when `paired=True`, require
  `wid`, reject duplicate subject/group pairs, and require complete paired
  observations.
- Make `stat_friedman_test(wid=...)` strict: require `wid`, pivot by subject and
  x group, reject duplicates, and raise on incomplete blocks instead of
  sorting/truncating.
- Fix `stat_pvalue_manual` for string group labels by adding `x_levels=None`;
  default maps group labels in first-seen order, while `x_levels` gives
  deterministic plot-order control.
- Wire `stat_pwc(remove_bracket=True)` to use text-only rendering rather than
  silently keeping brackets.
- Replace broad swallowed exceptions in p-value stats with specific empty-data
  handling and clear method/comparison error messages.
- Validate beeswarm/quasirandom options in constructors:
  - `method`, `priority`, `side`, and `corral` must be known values.
  - Typos raise `ValueError` instead of falling back.

## Release Workflow And Tests

- Expand tests before implementation:
  - Numeric regression tests for paired `wid` alignment, incomplete blocks,
    duplicate subject/group pairs, horizontal orientation, string-label
    `stat_pvalue_manual`, `remove_bracket`, and invalid option values.
  - Facet tests for repeated `facet_manual` design labels, too-few design
    labels, `trim_blank`, `axes`/`remove_labels`, and per-panel
    `scale_x_facet`/`scale_y_facet`.
  - Matplotlib object tests for every axis guide proving visible side effects:
    tick labels, tick colors, spine bounds, nesting lines, dendrogram lines,
    scalebar artists.
  - Legend test proving `guide_stringlegend` produces colored text and no key
    glyph boxes.
- Fix test lint by removing unused imports, sorting imports, and replacing
  legacy `np.random.*` calls with `np.random.default_rng`.
- Update CI:
  - Run `ruff check plotnine_extra tests`.
  - Run `ruff format --check plotnine_extra tests`.
  - Add publish build validation: `python -m build`, `twine check dist/*`,
    install built wheel in a clean environment, and smoke-test
    `from plotnine_extra import *`.
  - Add a publish tag guard requiring `refs/tags/v${pyproject.version}` for
    PyPI release jobs.
- Final local verification commands:
  - `MPLCONFIGDIR=/tmp/plotnine-extra-mplconfig python3 -m pytest tests -q`
  - `ruff check plotnine_extra tests`
  - `ruff format --check plotnine_extra tests`
  - `python3 -m compileall -q plotnine_extra`
  - `python3 -m pip check`
  - `python3 -m build`
  - `python3 -m twine check dist/*`
  - Install the wheel into `/tmp/plotnine-extra-install-final` and smoke-test
    import/star-export from `/tmp`.

## Release Provenance

- Commit in small stages: current review fixes, guide implementation,
  facet/strip implementation, stats hardening, workflow/docs/lint, version
  bump.
- Push `main` only after the full local verification suite passes.
- Create annotated tag `v0.3.1` at the exact verified commit.
- Release is blocked until GitHub CI passes on that tag and the publish workflow
  artifact smoke test passes.

## Assumptions

- "Near parity" means visible, tested behavior matching ggh4x semantics where
  plotnine 0.15/0.16 exposes enough hooks; exact layout parity is not required
  when plotnine lacks an equivalent extension point.
- `wid` is the canonical subject-id parameter for paired/repeated-measures APIs.
