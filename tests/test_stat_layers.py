"""
Unit tests for the new stat layers ported from ggpubr.

These tests verify the compute_group/compute_panel logic
directly using known data, and also test integration with
the ggplot pipeline.
"""

import numpy as np
import pandas as pd
import pytest
from plotnine import aes, geom_point, ggplot

from plotnine_extra import (
    stat_anova_test,
    stat_central_tendency,
    stat_chull,
    stat_compare_means,
    stat_conf_ellipse,
    stat_cor,
    stat_friedman_test,
    stat_kruskal_test,
    stat_mean,
    stat_overlay_normal_density,
    stat_pvalue_manual,
    stat_pwc,
    stat_regline_equation,
    stat_stars,
    stat_welch_anova_test,
)
from plotnine_extra.geoms import geom_bracket
from plotnine_extra.stats._p_format import (
    format_p_value,
    p_to_signif,
)
from plotnine_extra.stats._stat_test import (
    run_stat_test,
)

# ---- Test data ----

rng = np.random.default_rng(42)

# Simple scatter data
scatter_data = pd.DataFrame(
    {
        "x": np.arange(20, dtype=float),
        "y": np.arange(20, dtype=float) * 2 + 1 + rng.normal(0, 1, 20),
    }
)

# Grouped data (3 groups)
grouped_data = pd.DataFrame(
    {
        "x": np.repeat(["A", "B", "C"], 15),
        "y": np.concatenate(
            [
                rng.normal(5, 1, 15),
                rng.normal(7, 1, 15),
                rng.normal(6, 1.5, 15),
            ]
        ),
    }
)


# ---- P-value formatting tests ----


class TestPFormat:
    def test_format_p_value_above_threshold(self):
        result = format_p_value(0.05, digits=3)
        assert result == "p = 0.050"

    def test_format_p_value_below_threshold(self):
        result = format_p_value(0.0001, digits=3)
        assert result == "p < 0.001"

    def test_format_p_value_nan(self):
        result = format_p_value(np.nan)
        assert result == "NA"

    def test_p_to_signif_stars(self):
        assert p_to_signif(0.00001) == "****"
        assert p_to_signif(0.0005) == "***"
        assert p_to_signif(0.005) == "**"
        assert p_to_signif(0.03) == "*"
        assert p_to_signif(0.1) == "ns"

    def test_p_to_signif_nan(self):
        assert p_to_signif(np.nan) == "NA"


# ---- Statistical test wrapper tests ----


class TestStatTest:
    def test_ttest(self):
        g1 = rng.normal(5, 1, 30)
        g2 = rng.normal(7, 1, 30)
        result = run_stat_test([g1, g2], method="t.test")
        assert result.p_value < 0.05
        assert result.method == "Welch Two Sample t-test"

    def test_wilcox(self):
        g1 = rng.normal(5, 1, 30)
        g2 = rng.normal(7, 1, 30)
        result = run_stat_test([g1, g2], method="wilcox.test")
        assert result.p_value < 0.05
        assert result.method == "Wilcoxon rank sum test"

    def test_anova(self):
        g1 = rng.normal(5, 1, 30)
        g2 = rng.normal(7, 1, 30)
        g3 = rng.normal(6, 1, 30)
        result = run_stat_test([g1, g2, g3], method="anova")
        assert result.method == "One-way ANOVA"
        assert result.df == 2

    def test_kruskal(self):
        g1 = rng.normal(5, 1, 30)
        g2 = rng.normal(7, 1, 30)
        g3 = rng.normal(6, 1, 30)
        result = run_stat_test([g1, g2, g3], method="kruskal.test")
        assert result.method == "Kruskal-Wallis"

    def test_welch_anova(self):
        g1 = rng.normal(5, 1, 30)
        g2 = rng.normal(7, 2, 30)
        g3 = rng.normal(6, 0.5, 30)
        result = run_stat_test([g1, g2, g3], method="welch.anova")
        assert result.method == "Welch's ANOVA"

    def test_friedman(self):
        g1 = np.array([1.0, 2, 3, 4, 5])
        g2 = np.array([2.0, 3, 4, 5, 6])
        g3 = np.array([3.0, 4, 5, 6, 7])
        result = run_stat_test([g1, g2, g3], method="friedman.test")
        assert result.method == "Friedman test"


# ---- Tier 1 stat tests ----


class TestStatMean:
    def test_compute(self):
        p = (
            ggplot(scatter_data, aes("x", "y"))
            + geom_point()
            + stat_mean(size=5, color="red")
        )
        p.draw_test()

    def test_mean_values(self):
        data = pd.DataFrame({"x": [1.0, 2, 3], "y": [4.0, 5, 6]})
        s = stat_mean()
        result = s.compute_group(data, None)
        assert result["x"].iloc[0] == 2.0
        assert result["y"].iloc[0] == 5.0


class TestStatChull:
    def test_compute(self):
        p = ggplot(scatter_data, aes("x", "y")) + stat_chull()
        p.draw_test()

    def test_hull_points(self):
        # Square corners should all be hull vertices
        data = pd.DataFrame(
            {
                "x": [0.0, 0, 1, 1, 0.5],
                "y": [0.0, 1, 0, 1, 0.5],
            }
        )
        s = stat_chull()
        result = s.compute_group(data, None)
        # Hull should have 5 points (4 vertices + closing)
        assert len(result) == 5

    def test_too_few_points(self):
        data = pd.DataFrame({"x": [1.0, 2], "y": [3.0, 4]})
        s = stat_chull()
        result = s.compute_group(data, None)
        # With < 3 points, returns original data
        assert len(result) == 2


class TestStatStars:
    def test_compute(self):
        p = ggplot(scatter_data, aes("x", "y")) + stat_stars()
        p.draw_test()

    def test_star_segments(self):
        data = pd.DataFrame(
            {
                "x": [0.0, 2, 4],
                "y": [0.0, 2, 4],
            }
        )
        s = stat_stars()
        result = s.compute_group(data, None)
        assert len(result) == 3
        # All x values should be the mean
        assert all(result["x"] == 2.0)
        assert all(result["y"] == 2.0)
        # xend/yend should be original values
        np.testing.assert_array_equal(result["xend"].values, [0, 2, 4])


# ---- Tier 1 continued ----


class TestStatCentralTendency:
    def test_mean(self):
        data = pd.DataFrame({"x": [1.0, 2, 3, 4, 5]})
        s = stat_central_tendency(type="mean")
        result = s.compute_group(data, None)
        assert result["x"].iloc[0] == 3.0

    def test_median(self):
        data = pd.DataFrame({"x": [1.0, 2, 3, 4, 100]})
        s = stat_central_tendency(type="median")
        result = s.compute_group(data, None)
        assert result["x"].iloc[0] == 3.0

    def test_mode(self):
        data = pd.DataFrame({"x": [1.0, 2, 2, 3, 3, 3]})
        s = stat_central_tendency(type="mode")
        result = s.compute_group(data, None)
        assert result["x"].iloc[0] == 3.0

    def test_invalid_type(self):
        data = pd.DataFrame({"x": [1.0, 2, 3]})
        s = stat_central_tendency(type="invalid")
        with pytest.raises(ValueError):
            s.compute_group(data, None)


class TestStatConfEllipse:
    def test_compute(self):
        p = (
            ggplot(scatter_data, aes("x", "y"))
            + geom_point()
            + stat_conf_ellipse()
        )
        p.draw_test()

    def test_ellipse_points(self):
        data = pd.DataFrame(
            {
                "x": rng.normal(0, 1, 50),
                "y": rng.normal(0, 1, 50),
            }
        )
        s = stat_conf_ellipse(npoint=50)
        result = s.compute_group(data, None)
        assert len(result) == 50

    def test_too_few_points(self):
        data = pd.DataFrame({"x": [1.0, 2], "y": [3.0, 4]})
        s = stat_conf_ellipse()
        result = s.compute_group(data, None)
        assert len(result) == 0


# ---- Tier 2 stat tests ----


class TestStatOverlayNormalDensity:
    def test_compute(self):
        data = pd.DataFrame({"x": rng.normal(0, 1, 100)})
        s = stat_overlay_normal_density(n=50)
        result = s.compute_group(data, None)
        assert len(result) == 50
        assert "density" in result.columns
        # Density should be positive
        assert all(result["density"] > 0)

    def test_zero_std(self):
        data = pd.DataFrame({"x": [5.0, 5.0, 5.0]})
        s = stat_overlay_normal_density()
        result = s.compute_group(data, None)
        assert len(result) == 0


class TestStatCor:
    def test_pearson(self):
        s = stat_cor(method="pearson")
        result = s.compute_group(scatter_data, None)
        assert "label" in result.columns
        assert result["r"].iloc[0] > 0.9
        assert "R =" in result["label"].iloc[0]

    def test_spearman(self):
        s = stat_cor(method="spearman")
        result = s.compute_group(scatter_data, None)
        assert "ρ =" in result["label"].iloc[0]

    def test_kendall(self):
        s = stat_cor(method="kendall")
        result = s.compute_group(scatter_data, None)
        assert "τ =" in result["label"].iloc[0]

    def test_integration(self):
        p = ggplot(scatter_data, aes("x", "y")) + geom_point() + stat_cor()
        p.draw_test()


class TestStatReglineEquation:
    def test_linear(self):
        s = stat_regline_equation(formula="y ~ x")
        result = s.compute_group(scatter_data, None)
        assert "label" in result.columns
        assert "R²" in result["label"].iloc[0]
        assert result["rr"].iloc[0] > 0.8

    def test_polynomial(self):
        s = stat_regline_equation(formula="y ~ poly(x, 2)")
        result = s.compute_group(scatter_data, None)
        assert "label" in result.columns

    def test_integration(self):
        p = (
            ggplot(scatter_data, aes("x", "y"))
            + geom_point()
            + stat_regline_equation()
        )
        p.draw_test()


# ---- Tier 3 stat tests ----


class TestStatKruskalTest:
    def test_compute(self):
        p = (
            ggplot(grouped_data, aes("x", "y"))
            + geom_point()
            + stat_kruskal_test()
        )
        p.draw_test()


class TestStatWelchAnovaTest:
    def test_compute(self):
        p = (
            ggplot(grouped_data, aes("x", "y"))
            + geom_point()
            + stat_welch_anova_test()
        )
        p.draw_test()


class TestStatFriedmanTest:
    def test_compute(self):
        # Friedman test needs repeated measures data
        friedman_data = pd.DataFrame(
            {
                "x": np.repeat(["T1", "T2", "T3"], 10),
                "y": np.concatenate(
                    [
                        rng.normal(5, 1, 10),
                        rng.normal(7, 1, 10),
                        rng.normal(6, 1, 10),
                    ]
                ),
                "subject": np.tile(range(10), 3),
            }
        )
        p = (
            ggplot(friedman_data, aes("x", "y"))
            + geom_point()
            + stat_friedman_test(wid="subject")
        )
        p.draw_test()


class TestStatCompareMeans:
    def test_global(self):
        p = (
            ggplot(grouped_data, aes("x", "y"))
            + geom_point()
            + stat_compare_means()
        )
        p.draw_test()

    def test_pairwise(self):
        p = (
            ggplot(grouped_data, aes("x", "y"))
            + geom_point()
            + stat_compare_means(comparisons=[(1, 2), (2, 3)])
        )
        p.draw_test()


class TestStatAnovaTest:
    def test_compute(self):
        p = (
            ggplot(grouped_data, aes("x", "y"))
            + geom_point()
            + stat_anova_test()
        )
        p.draw_test()


# ---- Tier 4 test ----


class TestStatPvalueManual:
    def test_basic(self):
        pval_data = pd.DataFrame(
            {
                "group1": [1, 1],
                "group2": [2, 3],
                "p": [0.01, 0.5],
                "y_position": [10, 12],
            }
        )
        layers = stat_pvalue_manual(pval_data)
        # Should return layers (segments + text)
        assert len(layers) > 0

    def test_hide_ns(self):
        pval_data = pd.DataFrame(
            {
                "group1": [1, 1],
                "group2": [2, 3],
                "p": [0.01, 0.5],
                "y_position": [10, 12],
            }
        )
        layers = stat_pvalue_manual(pval_data, hide_ns=True)
        # Only significant result should remain
        assert len(layers) > 0

    def test_signif_labels(self):
        pval_data = pd.DataFrame(
            {
                "group1": [1],
                "group2": [2],
                "p": [0.001],
                "y_position": [10],
            }
        )
        layers = stat_pvalue_manual(pval_data, label="p.signif")
        assert len(layers) > 0


# ---- Geom bracket test ----


class TestGeomBracket:
    def test_import(self):
        assert geom_bracket is not None

    def test_basics(self):
        bracket_data = pd.DataFrame(
            {
                "xmin": [1],
                "xmax": [2],
                "y": [10],
                "label": ["***"],
            }
        )
        p = ggplot(bracket_data) + geom_bracket(
            aes(
                xmin="xmin",
                xmax="xmax",
                y="y",
                label="label",
            ),
        )
        # Just check it can be constructed
        assert p is not None


# ---- stat_pwc tests ----


class TestStatPwc:
    def test_all_pairwise(self):
        """Test all pairwise comparisons (default)."""
        p = ggplot(grouped_data, aes("x", "y")) + geom_point() + stat_pwc()
        p.draw_test()

    def test_ref_group(self):
        """Test comparisons against a reference group."""
        p = (
            ggplot(grouped_data, aes("x", "y"))
            + geom_point()
            + stat_pwc(ref_group="A")
        )
        p.draw_test()

    def test_explicit_comparisons(self):
        """Test explicit comparisons list."""
        p = (
            ggplot(grouped_data, aes("x", "y"))
            + geom_point()
            + stat_pwc(comparisons=[("A", "B")])
        )
        p.draw_test()

    def test_t_test_method(self):
        """Test with t-test method."""
        p = (
            ggplot(grouped_data, aes("x", "y"))
            + geom_point()
            + stat_pwc(method="t.test")
        )
        p.draw_test()

    def test_signif_label(self):
        """Test significance symbol labels."""
        p = (
            ggplot(grouped_data, aes("x", "y"))
            + geom_point()
            + stat_pwc(label="p.signif")
        )
        p.draw_test()

    def test_signif_label_not_literal(self):
        """Label should be a significance symbol, not the
        literal string 'p.signif'."""
        s = stat_pwc(label="p.signif")
        data = grouped_data.copy()
        data["x"] = pd.Categorical(data["x"]).codes + 1.0
        result = s.compute_panel(data, None)
        valid_symbols = {"****", "***", "**", "*", "ns"}
        for lbl in result["label"]:
            assert lbl in valid_symbols, (
                f"Expected significance symbol, got '{lbl}'"
            )

    def test_adj_signif_label(self):
        """Test adjusted significance labels."""
        p = (
            ggplot(grouped_data, aes("x", "y"))
            + geom_point()
            + stat_pwc(label="p.adj.signif")
        )
        p.draw_test()

    def test_hide_ns(self):
        """Test hiding non-significant results."""
        p = (
            ggplot(grouped_data, aes("x", "y"))
            + geom_point()
            + stat_pwc(hide_ns=True)
        )
        p.draw_test()

    def test_bonferroni_adjustment(self):
        """Test Bonferroni p-value adjustment."""
        p = (
            ggplot(grouped_data, aes("x", "y"))
            + geom_point()
            + stat_pwc(p_adjust_method="bonferroni")
        )
        p.draw_test()

    def test_p_adjust_methods(self):
        """Test various p-value adjustment methods."""
        for method in ("holm", "BH", "fdr", "none"):
            p = (
                ggplot(grouped_data, aes("x", "y"))
                + geom_point()
                + stat_pwc(p_adjust_method=method)
            )
            p.draw_test()
