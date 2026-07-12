"""
Unit tests for stat internal utility modules.

Tests for _common.py, _label_utils.py, _p_format.py,
and _stat_test.py.
"""

import numpy as np
import pandas as pd
import pytest
from scipy import stats as sp_stats

from plotnine_extra.stats.stat_pwc import _adjust_pvalues
from plotnine_extra.stats._common import (
    preserve_panel_columns,
)
from plotnine_extra.stats._label_utils import (
    compute_label_position,
    format_stat_label,
)
from plotnine_extra.stats._p_format import (
    DEFAULT_CUTPOINTS,
    DEFAULT_SYMBOLS,
    format_p_value,
    p_to_signif,
)
from plotnine_extra.stats._stat_test import (
    StatTestResult,
    run_stat_test,
)


# ---- preserve_panel_columns ----


class TestPreservePanelColumns:
    def test_preserves_panel(self):
        data = pd.DataFrame(
            {"PANEL": [1, 1], "group": [1, 1], "x": [1, 2]}
        )
        result = pd.DataFrame({"x": [1.5]})
        out = preserve_panel_columns(result, data)
        assert "PANEL" in out.columns
        assert out["PANEL"].iloc[0] == 1

    def test_preserves_group(self):
        data = pd.DataFrame(
            {"PANEL": [2, 2], "group": [3, 3], "x": [1, 2]}
        )
        result = pd.DataFrame({"x": [1.5]})
        out = preserve_panel_columns(result, data)
        assert out["group"].iloc[0] == 3

    def test_empty_result_passthrough(self):
        data = pd.DataFrame(
            {"PANEL": [1], "group": [1], "x": [1]}
        )
        result = pd.DataFrame()
        out = preserve_panel_columns(result, data)
        assert out.empty

    def test_no_panel_in_data(self):
        data = pd.DataFrame({"x": [1, 2]})
        result = pd.DataFrame({"x": [1.5]})
        out = preserve_panel_columns(result, data)
        assert "PANEL" not in out.columns

    def test_panel_already_in_result(self):
        data = pd.DataFrame(
            {"PANEL": [1], "group": [1], "x": [1]}
        )
        result = pd.DataFrame(
            {"x": [1.5], "PANEL": [99], "group": [99]}
        )
        out = preserve_panel_columns(result, data)
        # Should not overwrite existing columns
        assert out["PANEL"].iloc[0] == 99
        assert out["group"].iloc[0] == 99


# ---- compute_label_position ----


class TestComputeLabelPosition:
    def test_float_npc(self):
        pos = compute_label_position(0, 100, 0.5)
        assert pos == 50.0

    def test_npc_zero(self):
        pos = compute_label_position(0, 100, 0.0)
        assert pos == 0.0

    def test_npc_one(self):
        pos = compute_label_position(0, 100, 1.0)
        assert pos == 100.0

    def test_string_left(self):
        pos = compute_label_position(0, 100, "left")
        assert pos == 5.0

    def test_string_center(self):
        pos = compute_label_position(0, 100, "center")
        assert pos == 50.0

    def test_string_middle(self):
        pos = compute_label_position(0, 100, "middle")
        assert pos == 50.0

    def test_string_right(self):
        pos = compute_label_position(0, 100, "right")
        assert pos == 95.0

    def test_string_top(self):
        pos = compute_label_position(0, 100, "top")
        assert pos == 95.0

    def test_string_bottom(self):
        pos = compute_label_position(0, 100, "bottom")
        assert pos == 5.0

    def test_unknown_string_defaults_to_center(self):
        pos = compute_label_position(0, 100, "unknown")
        assert pos == 50.0

    def test_negative_range(self):
        pos = compute_label_position(-10, 10, 0.5)
        assert pos == 0.0

    def test_offset_range(self):
        pos = compute_label_position(100, 200, 0.25)
        assert pos == 125.0


# ---- format_stat_label ----


class TestFormatStatLabel:
    def test_basic_template(self):
        result = format_stat_label(
            "R = {r}, p = {p}", r=0.95, p=0.001
        )
        assert result == "R = 0.95, p = 0.001"

    def test_no_placeholders(self):
        result = format_stat_label("no placeholders")
        assert result == "no placeholders"

    def test_missing_key_raises(self):
        with pytest.raises(KeyError):
            format_stat_label("{missing}")


# ---- format_p_value ----


class TestFormatPValue:
    def test_above_threshold(self):
        assert format_p_value(0.05, digits=3) == "p = 0.050"

    def test_below_threshold(self):
        assert format_p_value(0.0001, digits=3) == "p < 0.001"

    def test_exact_threshold(self):
        assert format_p_value(0.001, digits=3) == "p = 0.001"

    def test_nan(self):
        assert format_p_value(np.nan) == "NA"

    def test_very_small(self):
        result = format_p_value(1e-10, digits=3)
        assert result == "p < 0.001"

    def test_digits_2(self):
        result = format_p_value(0.05, digits=2)
        assert result == "p = 0.05"

    def test_no_leading_zero(self):
        result = format_p_value(
            0.05, digits=3, leading_zero=False
        )
        assert result == "p = .050"

    def test_no_leading_zero_below_threshold(self):
        result = format_p_value(
            0.0001, digits=3, leading_zero=False
        )
        assert result == "p < .001"

    def test_one(self):
        result = format_p_value(1.0, digits=3)
        assert result == "p = 1.000"


# ---- p_to_signif ----


class TestPToSignif:
    def test_four_stars(self):
        assert p_to_signif(0.00005) == "****"

    def test_three_stars(self):
        assert p_to_signif(0.0005) == "***"

    def test_two_stars(self):
        assert p_to_signif(0.005) == "**"

    def test_one_star(self):
        assert p_to_signif(0.03) == "*"

    def test_not_significant(self):
        assert p_to_signif(0.1) == "ns"

    def test_nan(self):
        assert p_to_signif(np.nan) == "NA"

    def test_boundary_0001(self):
        assert p_to_signif(0.0001) == "****"

    def test_boundary_001(self):
        assert p_to_signif(0.001) == "***"

    def test_boundary_01(self):
        assert p_to_signif(0.01) == "**"

    def test_boundary_05(self):
        assert p_to_signif(0.05) == "*"

    def test_custom_cutpoints(self):
        result = p_to_signif(
            0.03,
            cutpoints=(0.01, 0.1, 1.0),
            symbols=("**", "*", "ns"),
        )
        assert result == "*"

    def test_defaults_exported(self):
        assert len(DEFAULT_CUTPOINTS) == 5
        assert len(DEFAULT_SYMBOLS) == 5


# ---- StatTestResult ----


class TestStatTestResult:
    def test_creation(self):
        r = StatTestResult(
            statistic=2.5,
            p_value=0.01,
            method="t-test",
        )
        assert r.statistic == 2.5
        assert r.p_value == 0.01
        assert r.method == "t-test"
        assert r.df is None
        assert r.df2 is None
        assert r.estimate is None
        assert r.alternative == "two-sided"
        assert r.extra == {}

    def test_with_all_fields(self):
        r = StatTestResult(
            statistic=5.0,
            p_value=0.001,
            method="ANOVA",
            df=2,
            df2=27,
            estimate=0.5,
            alternative="greater",
            extra={"effect_size": 0.3},
        )
        assert r.df == 2
        assert r.df2 == 27
        assert r.extra["effect_size"] == 0.3


# ---- run_stat_test ----


class TestRunStatTest:
    def test_ttest_independent(self):
        g1 = np.array([1.0, 2, 3, 4, 5])
        g2 = np.array([6.0, 7, 8, 9, 10])
        r = run_stat_test([g1, g2], method="t.test")
        assert r.p_value < 0.05
        assert r.method == "Welch Two Sample t-test"
        assert r.df is not None

    def test_ttest_independent_uses_welch_semantics(self):
        g1 = np.array([1.0, 1.2, 1.4, 1.6])
        g2 = np.array([2.0, 4.0, 8.0, 16.0, 32.0])

        r = run_stat_test([g1, g2], method="t.test")
        expected = sp_stats.ttest_ind(g1, g2, equal_var=False)

        assert r.method == "Welch Two Sample t-test"
        assert r.p_value == pytest.approx(expected.pvalue)
        assert r.p_value != pytest.approx(
            sp_stats.ttest_ind(g1, g2, equal_var=True).pvalue
        )
        assert r.df == pytest.approx(expected.df)

    def test_ttest_paired(self):
        g1 = np.array([1.0, 2, 3, 4, 5])
        g2 = np.array([2.0, 3, 4, 5, 6])
        r = run_stat_test(
            [g1, g2], method="t.test", paired=True
        )
        assert r.method == "Paired t-test"
        assert r.df == 4

    def test_ttest_wrong_groups(self):
        with pytest.raises(ValueError, match="exactly 2"):
            run_stat_test(
                [np.array([1.0]), np.array([2.0]), np.array([3.0])],
                method="t.test",
            )

    def test_wilcox_independent(self):
        g1 = np.array([1.0, 2, 3, 4, 5])
        g2 = np.array([6.0, 7, 8, 9, 10])
        r = run_stat_test([g1, g2], method="wilcox.test")
        assert r.method == "Wilcoxon rank sum test"

    def test_wilcox_paired(self):
        g1 = np.array([1.0, 2, 3, 4, 5])
        g2 = np.array([2.0, 3, 4, 5, 6])
        r = run_stat_test(
            [g1, g2], method="wilcox.test", paired=True
        )
        assert r.method == "Wilcoxon signed-rank test"

    def test_wilcox_wrong_groups(self):
        with pytest.raises(ValueError, match="exactly 2"):
            run_stat_test(
                [np.array([1.0])], method="wilcox.test"
            )

    def test_anova(self):
        g1 = np.array([1.0, 2, 3])
        g2 = np.array([4.0, 5, 6])
        g3 = np.array([7.0, 8, 9])
        r = run_stat_test([g1, g2, g3], method="anova")
        assert r.method == "One-way ANOVA"
        assert r.df == 2
        assert r.df2 == 6

    def test_kruskal(self):
        g1 = np.array([1.0, 2, 3])
        g2 = np.array([4.0, 5, 6])
        g3 = np.array([7.0, 8, 9])
        r = run_stat_test(
            [g1, g2, g3], method="kruskal.test"
        )
        assert r.method == "Kruskal-Wallis"
        assert r.df == 2

    def test_friedman(self):
        g1 = np.array([1.0, 2, 3, 4, 5])
        g2 = np.array([2.0, 3, 4, 5, 6])
        g3 = np.array([3.0, 4, 5, 6, 7])
        r = run_stat_test(
            [g1, g2, g3], method="friedman.test"
        )
        assert r.method == "Friedman test"
        assert r.df == 2

    def test_welch_anova(self):
        g1 = np.array([1.0, 2, 3, 4, 5])
        g2 = np.array([5.0, 6, 7, 8, 9])
        g3 = np.array([3.0, 4, 5, 6, 7])
        r = run_stat_test(
            [g1, g2, g3], method="welch.anova"
        )
        assert r.method == "Welch's ANOVA"
        assert r.df == 2
        assert r.df2 is not None

    def test_unknown_method(self):
        with pytest.raises(ValueError, match="Unknown"):
            run_stat_test(
                [np.array([1.0])], method="nonexistent"
            )

    def test_ttest_alternative(self):
        g1 = np.array([1.0, 2, 3, 4, 5])
        g2 = np.array([6.0, 7, 8, 9, 10])
        r = run_stat_test(
            [g1, g2],
            method="t.test",
            alternative="less",
        )
        assert r.alternative == "less"

    def test_pearson_correlation(self):
        x = np.array([1.0, 2, 3, 4, 5])
        y = np.array([2.0, 4, 6, 8, 10])
        r = run_stat_test(
            [x, y], method="pearson"
        )
        assert r.method == "Pearson correlation"
        assert abs(r.statistic - 1.0) < 1e-6
        assert r.estimate == r.statistic

    def test_spearman_correlation(self):
        x = np.array([1.0, 2, 3, 4, 5])
        y = np.array([2.0, 4, 6, 8, 10])
        r = run_stat_test(
            [x, y], method="spearman"
        )
        assert r.method == "Spearman correlation"
        assert abs(r.statistic - 1.0) < 1e-6

    def test_kendall_correlation(self):
        x = np.array([1.0, 2, 3, 4, 5])
        y = np.array([2.0, 4, 6, 8, 10])
        r = run_stat_test(
            [x, y], method="kendall"
        )
        assert r.method == "Kendall correlation"
        assert abs(r.statistic - 1.0) < 1e-6

    def test_correlation_wrong_groups(self):
        with pytest.raises(
            ValueError, match="exactly 2"
        ):
            run_stat_test(
                [np.array([1.0])], method="pearson"
            )

    def test_correlation_alternative(self):
        x = np.array([1.0, 2, 3, 4, 5])
        y = np.array([2.0, 4, 6, 8, 10])
        r = run_stat_test(
            [x, y],
            method="pearson",
            alternative="greater",
        )
        assert r.alternative == "greater"


class TestAdjustPValues:
    def test_hommel_matches_reference_values(self):
        p_values = np.array([0.001, 0.04, 0.03, 0.2, 0.9])

        adjusted = _adjust_pvalues(p_values, "hommel")

        assert adjusted == pytest.approx(
            np.array([0.005, 0.12, 0.09, 0.4, 0.9])
        )

    def test_unknown_adjustment_method_raises(self):
        with pytest.raises(ValueError, match="Unknown p_adjust_method"):
            _adjust_pvalues(np.array([0.01, 0.02]), "not-a-method")
