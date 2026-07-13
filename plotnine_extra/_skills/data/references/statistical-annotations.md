# Statistical Annotations

Use these helpers when a plot needs test labels or p-value brackets:

- `stat_compare`: generic group comparisons.
- `stat_compare_means`: ggpubr-style comparisons with supported test methods.
- `stat_pwc`: pairwise comparisons, p-value adjustment, brackets, and
  text-only labels with `remove_bracket=True`.
- `stat_pvalue_manual`: place precomputed p-values; use `x_levels=` when string
  group labels need deterministic plot-order mapping.
- `stat_anova_test`, `stat_welch_anova_test`, `stat_kruskal_test`,
  `stat_friedman_test`: omnibus test annotations.
- `create_p_label`, `format_p_value`, `ggadjust_pvalue`,
  `list_p_format_styles`, and `get_p_format_style`: p-value formatting helpers.

## Paired and Repeated Measures

For `stat_pwc(..., paired=True)` and
`stat_compare_means(..., paired=True)`, pass `wid=` with the subject identifier.
The data must contain one observation per subject/group pair and complete paired
blocks. Duplicate subject/group pairs or incomplete observations raise errors.

For `stat_friedman_test`, pass `wid=`. The implementation pivots by subject and
x group, rejects duplicate subject/group pairs, and raises on incomplete blocks.

## Orientation

Horizontal orientation is deliberately strict for comparison stats. Do not run a
test on encoded discrete y-values. If a horizontal-looking plot is needed,
compute the statistics on the original grouping variable or reshape the data so
the tested grouping is still explicit.

## Manual P-Values

When `stat_pvalue_manual` receives string group labels, the default mapping uses
first-seen order. Pass `x_levels=[...]` when the plot has a known order that
should control placement.
