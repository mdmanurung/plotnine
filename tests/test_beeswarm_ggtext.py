"""
Tests for ggbeeswarm ports (position_beeswarm, position_quasirandom,
geom_beeswarm, geom_quasirandom) and ggtext ports (geom_richtext,
geom_textbox, element_markdown, element_textbox_simple).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# ------------------------------------------------------------------
# Algorithm unit tests
# ------------------------------------------------------------------
from plotnine_extra.geoms.geom_richtext import _parse_markdown
from plotnine_extra.positions import (
    position_beeswarm,
    position_quasirandom,
)
from plotnine_extra.positions._beeswarm_algorithms import (
    corral_points,
    offset_beeswarm,
    offset_quasirandom,
    van_der_corput,
)
from plotnine_extra.themes import (
    element_markdown,
    element_textbox_simple,
)


class TestVanDerCorput:
    """Tests for the van der Corput low-discrepancy sequence."""

    def test_length(self):
        assert len(van_der_corput(0)) == 0
        assert len(van_der_corput(1)) == 1
        assert len(van_der_corput(100)) == 100

    def test_range(self):
        seq = van_der_corput(50)
        assert np.all(seq > 0)
        assert np.all(seq < 1)

    def test_first_values_base2(self):
        seq = van_der_corput(4, base=2)
        np.testing.assert_allclose(seq, [0.5, 0.25, 0.75, 0.125])

    def test_uniqueness(self):
        seq = van_der_corput(100)
        assert len(np.unique(seq)) == 100


class TestOffsetQuasirandom:
    """Tests for quasi-random offset computation."""

    def test_empty(self):
        result = offset_quasirandom(np.array([]))
        assert len(result) == 0

    def test_single_point(self):
        result = offset_quasirandom(np.array([1.0]))
        assert len(result) == 1
        assert result[0] == 0.0

    def test_output_length(self):
        y = np.random.default_rng(42).normal(size=50)
        result = offset_quasirandom(y, width=0.4)
        assert len(result) == len(y)

    def test_centered(self):
        y = np.random.default_rng(42).normal(size=100)
        result = offset_quasirandom(y, width=0.4)
        # Offsets should be roughly centred around 0
        assert abs(result.mean()) < 0.1

    def test_width_scaling(self):
        y = np.random.default_rng(42).normal(size=100)
        narrow = offset_quasirandom(y, width=0.1)
        wide = offset_quasirandom(y, width=1.0)
        assert np.std(narrow) < np.std(wide)

    def test_pseudorandom_method(self):
        y = np.random.default_rng(42).normal(size=50)
        result = offset_quasirandom(y, method="pseudorandom")
        assert len(result) == 50

    def test_varwidth(self):
        y = np.random.default_rng(42).normal(size=50)
        result = offset_quasirandom(
            y,
            width=0.4,
            varwidth=True,
            group_count=10,
            total_count=100,
        )
        assert len(result) == 50


class TestOffsetBeeswarm:
    """Tests for beeswarm offset computation."""

    def test_empty(self):
        result = offset_beeswarm(np.array([]))
        assert len(result) == 0

    def test_single_point(self):
        result = offset_beeswarm(np.array([1.0]))
        assert len(result) == 1
        assert result[0] == 0.0

    def test_output_length(self):
        y = np.sort(np.random.default_rng(42).normal(size=30))
        result = offset_beeswarm(y)
        assert len(result) == len(y)

    def test_no_overlap_swarm(self):
        # Points placed at the same y should be spread out
        y = np.ones(5)
        result = offset_beeswarm(y, method="swarm", cex=1.0)
        assert len(np.unique(np.round(result, 6))) > 1

    def test_methods(self):
        y = np.sort(np.random.default_rng(42).normal(size=20))
        for method in ("swarm", "compactswarm", "center", "hex", "square"):
            result = offset_beeswarm(y, method=method)
            assert len(result) == len(y), f"Failed for {method}"

    def test_side_right(self):
        y = np.sort(np.random.default_rng(42).normal(size=20))
        result = offset_beeswarm(y, side=1)
        assert np.all(result >= -1e-10)

    def test_side_left(self):
        y = np.sort(np.random.default_rng(42).normal(size=20))
        result = offset_beeswarm(y, side=-1)
        assert np.all(result <= 1e-10)

    def test_priorities(self):
        y = np.random.default_rng(42).normal(size=20)
        for p in ("ascending", "descending", "density", "random", "none"):
            result = offset_beeswarm(y, priority=p)
            assert len(result) == len(y), f"Failed for {p}"


class TestCorralPoints:
    """Tests for the corral mechanism."""

    def test_none(self):
        offsets = np.array([-2.0, 0.0, 2.0])
        result = corral_points(offsets, method="none")
        np.testing.assert_array_equal(result, offsets)

    def test_gutter(self):
        offsets = np.array([-2.0, 0.0, 2.0])
        result = corral_points(offsets, method="gutter", width=1.0)
        assert np.all(np.abs(result) <= 0.5 + 1e-10)

    def test_wrap(self):
        offsets = np.array([-2.0, 0.0, 2.0])
        result = corral_points(offsets, method="wrap", width=1.0)
        assert np.all(np.abs(result) <= 0.5 + 1e-10)

    def test_random(self):
        offsets = np.array([-2.0, 0.0, 2.0])
        result = corral_points(offsets, method="random", width=1.0)
        assert np.all(np.abs(result) <= 0.5 + 1e-10)

    def test_omit(self):
        offsets = np.array([-2.0, 0.0, 2.0])
        result = corral_points(offsets, method="omit", width=1.0)
        assert np.isnan(result[0])
        assert result[1] == 0.0
        assert np.isnan(result[2])


# ------------------------------------------------------------------
# Position class tests
# ------------------------------------------------------------------


class TestPositionQuasirandom:
    """Tests for the position_quasirandom class."""

    def test_default_params(self):
        pos = position_quasirandom()
        assert pos.params["method"] == "quasirandom"
        assert pos.params["width"] is None
        assert pos.params["varwidth"] is False

    def test_custom_params(self):
        pos = position_quasirandom(
            method="pseudorandom", width=0.3, bandwidth=1.0
        )
        assert pos.params["method"] == "pseudorandom"
        assert pos.params["width"] == 0.3
        assert pos.params["bandwidth"] == 1.0

    def test_setup_params_auto_width(self):
        pos = position_quasirandom()
        data = pd.DataFrame({"x": [1, 1, 2, 2], "y": [1, 2, 3, 4]})
        params = pos.setup_params(data)
        assert params["width"] is not None
        assert params["width"] > 0

    def test_setup_params_explicit_width(self):
        pos = position_quasirandom(width=0.5)
        data = pd.DataFrame({"x": [1, 1, 2, 2], "y": [1, 2, 3, 4]})
        params = pos.setup_params(data)
        assert params["width"] == 0.5


class TestPositionBeeswarm:
    """Tests for the position_beeswarm class."""

    def test_default_params(self):
        pos = position_beeswarm()
        assert pos.params["method"] == "swarm"
        assert pos.params["cex"] == 1.0
        assert pos.params["side"] == 0
        assert pos.params["priority"] == "ascending"
        assert pos.params["corral"] == "none"

    def test_custom_params(self):
        pos = position_beeswarm(method="hex", cex=2.0, side=1)
        assert pos.params["method"] == "hex"
        assert pos.params["cex"] == 2.0
        assert pos.params["side"] == 1


# ------------------------------------------------------------------
# Geom integration tests (render without error)
# ------------------------------------------------------------------


def _make_categorical_data(seed=42):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "group": np.repeat(["A", "B", "C"], 20),
            "value": np.concatenate(
                [
                    rng.normal(0, 1, 20),
                    rng.normal(1, 1.5, 20),
                    rng.normal(2, 0.5, 20),
                ]
            ),
        }
    )


def _make_label_data():
    return pd.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [1, 2, 3],
            "label": ["Hello", "World", "Test"],
        }
    )


class TestGeomBeeswarm:
    """Integration tests for geom_beeswarm."""

    def test_basic_plot(self):
        from plotnine_extra import aes, geom_beeswarm, ggplot

        df = _make_categorical_data()
        p = ggplot(df, aes("group", "value")) + geom_beeswarm()
        p.draw(show=False)

    def test_methods(self):
        from plotnine_extra import aes, geom_beeswarm, ggplot

        df = _make_categorical_data()
        for method in ("swarm", "center", "hex", "square"):
            p = ggplot(df, aes("group", "value")) + geom_beeswarm(
                method=method
            )
            p.draw(show=False)

    def test_side_parameter(self):
        from plotnine_extra import aes, geom_beeswarm, ggplot

        df = _make_categorical_data()
        p = ggplot(df, aes("group", "value")) + geom_beeswarm(side=1)
        p.draw(show=False)

    def test_corral_parameter(self):
        from plotnine_extra import aes, geom_beeswarm, ggplot

        df = _make_categorical_data()
        p = ggplot(df, aes("group", "value")) + geom_beeswarm(
            corral="gutter", corral_width=0.5
        )
        p.draw(show=False)


class TestGeomQuasirandom:
    """Integration tests for geom_quasirandom."""

    def test_basic_plot(self):
        from plotnine_extra import aes, geom_quasirandom, ggplot

        df = _make_categorical_data()
        p = ggplot(df, aes("group", "value")) + geom_quasirandom()
        p.draw(show=False)

    def test_pseudorandom(self):
        from plotnine_extra import aes, geom_quasirandom, ggplot

        df = _make_categorical_data()
        p = ggplot(df, aes("group", "value")) + geom_quasirandom(
            method="pseudorandom"
        )
        p.draw(show=False)

    def test_width_parameter(self):
        from plotnine_extra import aes, geom_quasirandom, ggplot

        df = _make_categorical_data()
        p = ggplot(df, aes("group", "value")) + geom_quasirandom(width=0.2)
        p.draw(show=False)


class TestGeomRichtext:
    """Integration tests for geom_richtext."""

    def test_basic_labels(self):
        from plotnine_extra import aes, geom_richtext, ggplot

        df = _make_label_data()
        p = ggplot(df, aes("x", "y", label="label")) + geom_richtext()
        p.draw(show=False)

    def test_markdown_bold(self):
        from plotnine_extra import aes, geom_richtext, ggplot

        df = pd.DataFrame(
            {
                "x": [1],
                "y": [1],
                "label": ["**Bold text**"],
            }
        )
        p = ggplot(df, aes("x", "y", label="label")) + geom_richtext()
        p.draw(show=False)

    def test_markdown_italic(self):
        from plotnine_extra import aes, geom_richtext, ggplot

        df = pd.DataFrame(
            {
                "x": [1],
                "y": [1],
                "label": ["*Italic text*"],
            }
        )
        p = ggplot(df, aes("x", "y", label="label")) + geom_richtext()
        p.draw(show=False)

    def test_line_break(self):
        from plotnine_extra import aes, geom_richtext, ggplot

        df = pd.DataFrame(
            {
                "x": [1],
                "y": [1],
                "label": ["Line 1<br>Line 2"],
            }
        )
        p = ggplot(df, aes("x", "y", label="label")) + geom_richtext()
        p.draw(show=False)

    def test_fill_alpha(self):
        from plotnine_extra import aes, geom_richtext, ggplot

        df = _make_label_data()
        p = ggplot(df, aes("x", "y", label="label")) + geom_richtext(
            fill_alpha=0.5
        )
        p.draw(show=False)


class TestGeomTextbox:
    """Integration tests for geom_textbox."""

    def test_basic(self):
        from plotnine_extra import aes, geom_textbox, ggplot

        df = pd.DataFrame(
            {
                "x": [1],
                "y": [1],
                "label": [
                    "This is a long text that should be "
                    "wrapped into multiple lines for display"
                ],
            }
        )
        p = ggplot(df, aes("x", "y", label="label")) + geom_textbox()
        p.draw(show=False)

    def test_custom_width(self):
        from plotnine_extra import aes, geom_textbox, ggplot

        df = pd.DataFrame(
            {
                "x": [1],
                "y": [1],
                "label": ["Short text that wraps at 15 chars"],
            }
        )
        p = ggplot(df, aes("x", "y", label="label")) + geom_textbox(
            text_width=15
        )
        p.draw(show=False)


# ------------------------------------------------------------------
# Theme element tests
# ------------------------------------------------------------------


class TestElementMarkdown:
    """Tests for element_markdown."""

    def test_basic_creation(self):
        em = element_markdown(color="red")
        assert em.properties["color"] == "red"

    def test_face_bold(self):
        em = element_markdown(face="bold")
        assert em.properties["weight"] == "bold"

    def test_face_italic(self):
        em = element_markdown(face="italic")
        assert em.properties["style"] == "italic"

    def test_face_bold_italic(self):
        em = element_markdown(face="bold.italic")
        assert em.properties["weight"] == "bold"
        assert em.properties["style"] == "italic"

    def test_face_plain(self):
        em = element_markdown(face="plain")
        assert em.properties["weight"] == "normal"
        assert em.properties["style"] == "normal"

    def test_colour_alias(self):
        em = element_markdown(colour="blue")
        assert em.properties["color"] == "blue"

    def test_in_theme(self):
        from plotnine_extra import (
            aes,
            geom_point,
            ggplot,
            labs,
            theme,
        )

        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        p = (
            ggplot(df, aes("x", "y"))
            + geom_point()
            + labs(title="Title")
            + theme(
                plot_title=element_markdown(face="bold", color="blue", size=14)
            )
        )
        p.draw(show=False)


class TestElementTextboxSimple:
    """Tests for element_textbox_simple."""

    def test_default_alignment(self):
        et = element_textbox_simple()
        assert et.properties["ha"] == "left"
        assert et.properties["va"] == "top"
        assert et.properties["linespacing"] == 1.2

    def test_custom_params(self):
        et = element_textbox_simple(size=14, color="darkblue", face="bold")
        assert et.properties["size"] == 14
        assert et.properties["color"] == "darkblue"
        assert et.properties["weight"] == "bold"


# ------------------------------------------------------------------
# Markdown parser tests
# ------------------------------------------------------------------


class TestParseMarkdown:
    """Tests for the markdown parser."""

    def test_plain_text(self):
        text, props = _parse_markdown("Hello world")
        assert text == "Hello world"
        assert props == {}

    def test_bold(self):
        text, props = _parse_markdown("**Bold text**")
        assert text == "Bold text"
        assert props["fontweight"] == "bold"

    def test_italic(self):
        text, props = _parse_markdown("*Italic text*")
        assert text == "Italic text"
        assert props["fontstyle"] == "italic"

    def test_line_break(self):
        text, _ = _parse_markdown("Line 1<br>Line 2")
        assert "\n" in text

    def test_br_self_closing(self):
        text, _ = _parse_markdown("Line 1<br/>Line 2")
        assert "\n" in text

    def test_superscript(self):
        text, _ = _parse_markdown("x<sup>2</sup>")
        assert "$^{2}$" in text

    def test_subscript(self):
        text, _ = _parse_markdown("H<sub>2</sub>O")
        assert "$_{2}$" in text
