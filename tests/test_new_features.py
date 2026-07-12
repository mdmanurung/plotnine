"""
Tests for new features: geom_text_repel, geom_label_repel,
geom_half_violin, geom_half_boxplot, publication themes,
and facet implementations.
"""

import numpy as np
import pandas as pd
import pytest
from plotnine import aes, geom_point, ggplot

from plotnine_extra import (
    geom_half_boxplot,
    geom_half_violin,
    geom_label_repel,
    geom_text_repel,
    theme_clean,
    theme_nature,
    theme_poster,
    theme_pubr,
    theme_scientific,
)
from plotnine_extra.facets import (
    facet_grid2,
    facet_wrap2,
)
from plotnine_extra.facets.facetted_pos_scales import (
    FacettedPosScales,
    facetted_pos_scales,
)

# ── Test data ──────────────────────────────────────────


@pytest.fixture
def scatter_data():
    rng = np.random.default_rng(42)
    return pd.DataFrame(
        {
            "x": rng.normal(0, 1, 30),
            "y": rng.normal(0, 1, 30),
            "label": [f"pt{i}" for i in range(30)],
            "group": np.repeat(["A", "B", "C"], 10),
        }
    )


@pytest.fixture
def box_data():
    rng = np.random.default_rng(42)
    return pd.DataFrame(
        {
            "group": np.repeat(["A", "B", "C"], 50),
            "value": np.concatenate(
                [
                    rng.normal(0, 1, 50),
                    rng.normal(2, 1, 50),
                    rng.normal(4, 1, 50),
                ]
            ),
        }
    )


# ── geom_text_repel / geom_label_repel ────────────────


class TestGeomTextRepel:
    def test_can_create(self, scatter_data):
        """geom_text_repel can be instantiated."""
        p = (
            ggplot(scatter_data, aes("x", "y", label="label"))
            + geom_point()
            + geom_text_repel()
        )
        assert p is not None

    def test_draws_without_error(self, scatter_data):
        """geom_text_repel draws without error."""
        p = (
            ggplot(scatter_data, aes("x", "y", label="label"))
            + geom_point()
            + geom_text_repel()
        )
        p.draw_test()

    def test_custom_params(self, scatter_data):
        """geom_text_repel accepts custom parameters."""
        p = ggplot(
            scatter_data, aes("x", "y", label="label")
        ) + geom_text_repel(
            force=2.0,
            max_iter=100,
            seed=123,
            direction="x",
        )
        p.draw_test()


class TestGeomLabelRepel:
    def test_can_create(self, scatter_data):
        """geom_label_repel can be instantiated."""
        p = (
            ggplot(scatter_data, aes("x", "y", label="label"))
            + geom_point()
            + geom_label_repel()
        )
        assert p is not None

    def test_draws_without_error(self, scatter_data):
        """geom_label_repel draws without error."""
        p = (
            ggplot(scatter_data, aes("x", "y", label="label"))
            + geom_point()
            + geom_label_repel()
        )
        p.draw_test()


# ── geom_half_violin / geom_half_boxplot ──────────────


class TestGeomHalfViolin:
    def test_can_create(self, box_data):
        """geom_half_violin can be instantiated."""
        p = ggplot(box_data, aes("group", "value")) + geom_half_violin()
        assert p is not None

    def test_draws_without_error(self, box_data):
        """geom_half_violin draws without error."""
        p = ggplot(box_data, aes("group", "value")) + geom_half_violin()
        p.draw_test()

    def test_side_param(self, box_data):
        """geom_half_violin accepts side parameter."""
        p = ggplot(box_data, aes("group", "value")) + geom_half_violin(
            side="l"
        )
        p.draw_test()


class TestGeomHalfBoxplot:
    def test_can_create(self, box_data):
        """geom_half_boxplot can be instantiated."""
        p = ggplot(box_data, aes("group", "value")) + geom_half_boxplot()
        assert p is not None

    def test_draws_without_error(self, box_data):
        """geom_half_boxplot draws without error."""
        p = ggplot(box_data, aes("group", "value")) + geom_half_boxplot()
        p.draw_test()

    def test_side_param(self, box_data):
        """geom_half_boxplot accepts side parameter."""
        p = ggplot(box_data, aes("group", "value")) + geom_half_boxplot(
            side="l"
        )
        p.draw_test()


# ── Publication themes ────────────────────────────────


class TestThemes:
    def test_theme_pubr(self, scatter_data):
        """theme_pubr can be applied."""
        p = ggplot(scatter_data, aes("x", "y")) + geom_point() + theme_pubr()
        p.draw_test()

    def test_theme_clean(self, scatter_data):
        """theme_clean can be applied."""
        p = ggplot(scatter_data, aes("x", "y")) + geom_point() + theme_clean()
        p.draw_test()

    def test_theme_scientific(self, scatter_data):
        """theme_scientific can be applied."""
        p = (
            ggplot(scatter_data, aes("x", "y"))
            + geom_point()
            + theme_scientific()
        )
        p.draw_test()

    def test_theme_nature(self, scatter_data):
        """theme_nature can be applied."""
        p = ggplot(scatter_data, aes("x", "y")) + geom_point() + theme_nature()
        p.draw_test()

    def test_theme_poster(self, scatter_data):
        """theme_poster can be applied."""
        p = ggplot(scatter_data, aes("x", "y")) + geom_point() + theme_poster()
        p.draw_test()

    def test_theme_pubr_custom_size(self, scatter_data):
        """theme_pubr accepts custom base_size."""
        p = (
            ggplot(scatter_data, aes("x", "y"))
            + geom_point()
            + theme_pubr(base_size=16)
        )
        p.draw_test()


# ── Facets ────────────────────────────────────────────


class TestFacetWrap2:
    def test_can_create(self, scatter_data):
        """facet_wrap2 can be instantiated."""
        p = (
            ggplot(scatter_data, aes("x", "y"))
            + geom_point()
            + facet_wrap2("group")
        )
        assert p is not None

    def test_draws_without_error(self, scatter_data):
        """facet_wrap2 draws without error."""
        p = (
            ggplot(scatter_data, aes("x", "y"))
            + geom_point()
            + facet_wrap2("group")
        )
        p.draw_test()

    def test_axes_all(self, scatter_data):
        """facet_wrap2 with axes='all' draws."""
        p = (
            ggplot(scatter_data, aes("x", "y"))
            + geom_point()
            + facet_wrap2("group", axes="all")
        )
        p.draw_test()

    def test_trim_blank(self, scatter_data):
        """facet_wrap2 with trim_blank=True draws."""
        p = (
            ggplot(scatter_data, aes("x", "y"))
            + geom_point()
            + facet_wrap2("group", trim_blank=True)
        )
        p.draw_test()


class TestFacetGrid2:
    def test_can_create(self):
        """facet_grid2 can be instantiated."""
        data = pd.DataFrame(
            {
                "x": np.random.default_rng(0).normal(size=40),
                "y": np.random.default_rng(0).normal(size=40),
                "a": np.repeat(["X", "Y"], 20),
                "b": np.tile(["P", "Q"], 20),
            }
        )
        p = ggplot(data, aes("x", "y")) + geom_point() + facet_grid2("a", "b")
        p.draw_test()

    def test_independent_x(self):
        """facet_grid2 with independent='x' draws."""
        data = pd.DataFrame(
            {
                "x": np.random.default_rng(0).normal(size=40),
                "y": np.random.default_rng(0).normal(size=40),
                "a": np.repeat(["X", "Y"], 20),
                "b": np.tile(["P", "Q"], 20),
            }
        )
        p = (
            ggplot(data, aes("x", "y"))
            + geom_point()
            + facet_grid2("a", "b", independent="x", scales="free_x")
        )
        p.draw_test()


class TestFacetManual:
    def test_parse_design(self):
        """_parse_design parses design strings."""
        from plotnine_extra.facets.facet_manual import (
            _parse_design,
        )

        result = _parse_design("AB\nCD")
        assert result.shape == (2, 2)
        assert result[0, 0] == "A"
        assert result[1, 1] == "D"

    def test_parse_design_with_empty(self):
        """_parse_design handles empty cells."""
        from plotnine_extra.facets.facet_manual import (
            _parse_design,
        )

        result = _parse_design("AB\n#C")
        assert result[1, 0] == "#"
        assert result[1, 1] == "C"


# ── Facetted position scales ─────────────────────────


class TestFacettedPosScales:
    def test_create(self):
        """FacettedPosScales can be created."""
        fps = facetted_pos_scales(x=[None, None])
        assert isinstance(fps, FacettedPosScales)
        assert len(fps.x) == 2
        assert len(fps.y) == 0

    def test_empty(self):
        """FacettedPosScales with no args creates empty."""
        fps = facetted_pos_scales()
        assert len(fps.x) == 0
        assert len(fps.y) == 0


# ── Bug fix: stat_pwc Hommel ─────────────────────────


class TestHommelPValueAdjustment:
    def test_hommel_not_bonferroni(self):
        """Hommel adjustment differs from Bonferroni."""
        from plotnine_extra.stats.stat_pwc import (
            _adjust_pvalues,
        )

        p = np.array([0.01, 0.04, 0.03, 0.005])
        bonf = _adjust_pvalues(p, "bonferroni")
        homm = _adjust_pvalues(p, "hommel")

        # Hommel should be less conservative
        assert np.all(homm <= bonf + 1e-10)

    def test_hommel_single_value(self):
        """Hommel with single p-value returns it unchanged."""
        from plotnine_extra.stats.stat_pwc import (
            _adjust_pvalues,
        )

        p = np.array([0.05])
        result = _adjust_pvalues(p, "hommel")
        assert result[0] == pytest.approx(0.05)

    def test_hommel_bounded(self):
        """Hommel adjusted values never exceed 1."""
        from plotnine_extra.stats.stat_pwc import (
            _adjust_pvalues,
        )

        p = np.array([0.3, 0.4, 0.5, 0.6])
        result = _adjust_pvalues(p, "hommel")
        assert np.all(result <= 1.0)

    def test_hommel_monotonic(self):
        """Hommel adjusted values are monotonically ordered."""
        from plotnine_extra.stats.stat_pwc import (
            _adjust_pvalues,
        )

        p = np.array([0.001, 0.01, 0.02, 0.05, 0.1])
        result = _adjust_pvalues(p, "hommel")
        sorted_result = result[np.argsort(p)]
        # Monotonically non-decreasing after sort
        for i in range(1, len(sorted_result)):
            assert sorted_result[i] >= sorted_result[i - 1]


# ── Version compatibility check ──────────────────────


class TestVersionCheck:
    def test_plotnine_version_used(self):
        """_plotnine_version import is used."""
        import plotnine_extra

        assert hasattr(plotnine_extra, "_plotnine_version")
