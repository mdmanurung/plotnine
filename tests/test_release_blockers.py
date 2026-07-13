"""Release-blocker regressions for the 0.3.1 candidate."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.text import Text
from plotnine import (
    aes,
    geom_point,
    ggplot,
    guides,
    scale_color_discrete,
    scale_x_continuous,
    scale_x_log10,
)
from scipy import stats as sp_stats
from scipy.cluster.hierarchy import linkage

import plotnine_extra as pe
from plotnine_extra import (
    guide_axis_colour,
    guide_axis_logticks,
    guide_axis_manual,
    guide_axis_minor,
    guide_axis_nested,
    guide_axis_scalebar,
    guide_axis_truncated,
    guide_dendro,
    guide_stringlegend,
    position_beeswarm,
    position_quasirandom,
    stat_compare_means,
    stat_friedman_test,
    stat_pvalue_manual,
    stat_pwc,
)
from plotnine_extra.facets import (
    facet_manual,
    facet_wrap2,
    scale_x_facet,
    scale_y_facet,
)
from plotnine_extra.stats import _common


@pytest.fixture(autouse=True)
def close_figures():
    plt.close("all")
    yield
    plt.close("all")


def _simple_axis_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "x": [0.0, 5.0, 10.0],
            "y": [1.0, 2.0, 3.0],
            "g": ["panel"] * 3,
        }
    )


def _draw_axis_plot(scale):
    p = (
        ggplot(_simple_axis_data(), aes("x", "y"))
        + geom_point()
        + facet_wrap2("g")
        + scale
    )
    fig = p.draw(show=False)
    return fig, fig.axes[0]


def _artists_with_gid(fig, gid: str):
    return [artist for artist in fig.findobj() if artist.get_gid() == gid]


def test_scale_level_guide_axis_manual_styles_ticks_and_spine():
    fig, ax = _draw_axis_plot(
        scale_x_continuous(
            guide=guide_axis_manual(
                breaks=[0, 5],
                labels=["zero", "five"],
                label_colour=["red", "blue"],
                label_size=[9, 10],
                angle=45,
                axis_colour="green",
                trunc_lower=0,
                trunc_upper=5,
            )
        )
    )

    labels = [text for text in ax.get_xticklabels() if text.get_text()]
    assert [text.get_text() for text in labels] == ["zero", "five"]
    assert [text.get_color() for text in labels] == ["red", "blue"]
    assert [text.get_fontsize() for text in labels] == [9, 10]
    assert [text.get_rotation() for text in labels] == [45, 45]
    assert ax.spines["bottom"].get_edgecolor() == matplotlib.colors.to_rgba(
        "green"
    )
    assert ax.spines["bottom"].get_bounds() == (0, 5)
    assert fig is not None


def test_plot_added_axis_guide_falls_back_to_x_axis():
    p = (
        ggplot(_simple_axis_data(), aes("x", "y"))
        + geom_point()
        + facet_wrap2("g")
        + guide_axis_manual(breaks=[0, 10], labels=["low", "high"])
    )

    fig = p.draw(show=False)
    ax = fig.axes[0]

    assert [
        text.get_text() for text in ax.get_xticklabels() if text.get_text()
    ] == ["low", "high"]


def test_plot_added_axis_guide_position_left_targets_y_axis():
    p = (
        ggplot(_simple_axis_data(), aes("x", "y"))
        + geom_point()
        + facet_wrap2("g")
        + guide_axis_manual(
            breaks=[1, 3], labels=["bottom", "top"], position="left"
        )
    )

    fig = p.draw(show=False)
    ax = fig.axes[0]

    assert [
        text.get_text() for text in ax.get_yticklabels() if text.get_text()
    ] == ["bottom", "top"]


def test_guide_axis_colour_sets_label_tick_and_spine_colours():
    _, ax = _draw_axis_plot(
        scale_x_continuous(
            breaks=[0, 5],
            labels=["a", "b"],
            guide=guide_axis_colour(
                colours=["#ff0000", "#0000ff"], axis_colour="#008000"
            ),
        )
    )

    labels = [text for text in ax.get_xticklabels() if text.get_text()]
    assert [text.get_color() for text in labels] == ["#ff0000", "#0000ff"]
    assert ax.spines["bottom"].get_edgecolor() == matplotlib.colors.to_rgba(
        "#008000"
    )


def test_axis_guides_accept_numpy_colour_vectors():
    _, ax = _draw_axis_plot(
        scale_x_continuous(
            breaks=[0, 5],
            labels=["a", "b"],
            guide=guide_axis_manual(
                label_colour=np.array(["#ff0000", "#0000ff"])
            ),
        )
    )

    labels = [text for text in ax.get_xticklabels() if text.get_text()]
    assert [text.get_color() for text in labels] == ["#ff0000", "#0000ff"]


def test_guide_axis_minor_draws_minor_ticks_and_labels():
    _, ax = _draw_axis_plot(
        scale_x_continuous(
            minor_breaks=[2.5, 7.5],
            guide=guide_axis_minor(labels=["mid-a", "mid-b"]),
        )
    )

    assert list(ax.xaxis.get_minorticklocs()) == [2.5, 7.5]
    assert [
        text.get_text()
        for text in ax.xaxis.get_minorticklabels()
        if text.get_text()
    ] == ["mid-a", "mid-b"]


def test_guide_axis_logticks_draws_requested_log_tick_artists():
    df = pd.DataFrame(
        {
            "x": [1.0, 10.0, 100.0],
            "y": [1.0, 2.0, 3.0],
            "g": ["panel"] * 3,
        }
    )
    p = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + facet_wrap2("g")
        + scale_x_log10(guide=guide_axis_logticks(sides="b"))
    )
    fig = p.draw(show=False)

    assert _artists_with_gid(fig, "plotnine_extra_axis_logtick")


def test_guide_axis_truncated_sets_spine_bounds_from_callables():
    _, ax = _draw_axis_plot(
        scale_x_continuous(
            limits=(0, 10),
            expand=(0, 0),
            guide=guide_axis_truncated(
                trunc_lower=lambda limits: limits[0] + 1,
                trunc_upper=lambda limits: limits[1] - 1,
            ),
        )
    )

    assert ax.spines["bottom"].get_bounds() == pytest.approx((1, 9))


def test_guide_axis_scalebar_draws_line_and_label():
    fig, _ = _draw_axis_plot(
        scale_x_continuous(guide=guide_axis_scalebar(size=2, label="2 units"))
    )

    assert len(_artists_with_gid(fig, "plotnine_extra_axis_scalebar")) == 2
    assert any(
        isinstance(text, Text) and text.get_text() == "2 units"
        for text in fig.findobj(Text)
    )


def test_guide_axis_nested_splits_labels_and_draws_nesting_line():
    df = pd.DataFrame(
        {
            "x": ["A_one", "A_two"],
            "y": [1.0, 2.0],
            "g": ["panel", "panel"],
        }
    )
    p = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + facet_wrap2("g")
        + guide_axis_nested(delim="_", nest_line=True)
    )
    fig = p.draw(show=False)
    ax = fig.axes[0]

    assert [
        text.get_text() for text in ax.get_xticklabels() if text.get_text()
    ] == ["A\none", "A\ntwo"]
    assert len(_artists_with_gid(fig, "plotnine_extra_axis_nested_line")) == 1


def test_guide_dendro_draws_dendrogram_lines():
    z = linkage(np.array([[0.0], [1.0], [2.0]]), method="single")
    fig, _ = _draw_axis_plot(
        scale_x_continuous(
            breaks=[0, 5, 10],
            labels=["a", "b", "c"],
            guide=guide_dendro(z, position="bottom"),
        )
    )

    assert len(_artists_with_gid(fig, "plotnine_extra_axis_dendro")) == 2


def test_guide_stringlegend_draws_coloured_text_without_key_boxes():
    df = pd.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [1, 2, 3],
            "grp": ["a", "b", "c"],
        }
    )
    p = (
        ggplot(df, aes("x", "y", color="grp"))
        + geom_point()
        + scale_color_discrete(guide="stringlegend")
        + guides(color=guide_stringlegend(title="group"))
    )

    fig = p.draw(show=False)
    legend_text = [
        text
        for text in fig.findobj(Text)
        if text.get_text() in {"a", "b", "c"}
    ]
    legend_keys = _artists_with_gid(fig, "plotnine_extra_stringlegend_key")

    assert {text.get_text() for text in legend_text} == {"a", "b", "c"}
    assert len({text.get_color() for text in legend_text}) == 3
    assert {text.get_color() for text in legend_text} != {"black"}
    assert legend_keys == []


def test_guide_stringlegend_added_to_fill_aesthetic_draws_coloured_text():
    df = pd.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [1, 2, 3],
            "grp": ["a", "b", "c"],
        }
    )
    p = (
        ggplot(df, aes("x", "y", fill="grp"))
        + geom_point(size=4)
        + guide_stringlegend(title="group")
    )

    fig = p.draw(show=False)
    legend_text = [
        text
        for text in fig.findobj(Text)
        if text.get_text() in {"a", "b", "c"}
    ]

    assert {text.get_text() for text in legend_text} == {"a", "b", "c"}
    assert {text.get_color() for text in legend_text} != {"black"}


def test_guide_stringlegend_added_to_color_and_fill_keeps_both_guides():
    df = pd.DataFrame(
        {
            "x": ["a", "b", "c"],
            "y": [1, 2, 3],
            "outline": ["one", "two", "three"],
            "inside": ["alpha", "beta", "gamma"],
        }
    )
    p = (
        ggplot(df, aes("x", "y", color="outline", fill="inside"))
        + pe.geom_col()
        + guide_stringlegend(title="group")
    )

    fig = p.draw(show=False)
    labels = {
        text.get_text(): text.get_color()
        for text in fig.findobj(Text)
        if text.get_text() in {"one", "two", "three", "alpha", "beta", "gamma"}
    }

    assert set(labels) == {"one", "two", "three", "alpha", "beta", "gamma"}
    assert {labels[name] for name in {"one", "two", "three"}} != {"black"}
    assert {labels[name] for name in {"alpha", "beta", "gamma"}} != {"black"}


def test_scale_facet_selectors_override_panel_scales_by_priority():
    df = pd.DataFrame(
        {
            "x": [0.0, 1.0, 10.0, 11.0],
            "y": [0.0, 1.0, 0.0, 1.0],
            "g": ["A", "A", "B", "B"],
        }
    )
    p = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + facet_wrap2("g", scales="free_x")
        + scale_x_facet("g == 'B'", limits=(9, 12), type="continuous")
        + scale_x_facet("True", limits=(-1, 2), type="continuous")
    )

    p.draw(show=False)
    layout = p._build_objs.layout
    built = layout.layout
    panel_a = built.loc[built["g"] == "A", "SCALE_X"].iloc[0] - 1
    panel_b = built.loc[built["g"] == "B", "SCALE_X"].iloc[0] - 1

    assert layout.panel_scales_x[panel_a].limits == (-1, 2)
    assert layout.panel_scales_x[panel_b].limits == (9, 12)


def test_scale_facet_invalid_selector_raises_value_error():
    df = pd.DataFrame({"x": [1.0], "y": [1.0], "g": ["A"]})
    p = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + facet_wrap2("g", scales="free_x")
        + scale_x_facet("missing_column == 'A'", limits=(0, 1))
    )

    with pytest.raises(ValueError, match="scale_x_facet selector failed"):
        p.draw(show=False)


def test_scale_y_facet_supports_discrete_scales():
    df = pd.DataFrame(
        {
            "x": [1.0, 2.0],
            "y": ["low", "high"],
            "g": ["A", "B"],
        }
    )
    p = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + facet_wrap2("g", scales="free_y")
        + scale_y_facet("g == 'B'", type="discrete", limits=["high"])
    )

    p.draw(show=False)
    layout = p._build_objs.layout
    built = layout.layout
    panel_b = built.loc[built["g"] == "B", "SCALE_Y"].iloc[0] - 1

    assert layout.panel_scales_y[panel_b].limits == ["high"]


def test_facet_manual_repeated_design_labels_create_span_metadata():
    df = pd.DataFrame({"x": [1, 2], "y": [1, 2], "g": ["A", "B"]})
    p = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + facet_manual("g", design="AA\nBB", axes="all")
    )

    p.draw(show=False)
    layout = p._build_objs.layout.layout

    assert layout.loc[layout["g"] == "A", "COL"].iloc[0] == 1
    assert layout.loc[layout["g"] == "A", "COLSPAN"].iloc[0] == 2
    assert layout.loc[layout["g"] == "B", "ROWSPAN"].iloc[0] == 1
    assert layout["AXIS_X"].all()
    assert layout["AXIS_Y"].all()


def test_facet_manual_repeated_design_labels_render_spanning_axes():
    df = pd.DataFrame({"x": [1, 2], "y": [1, 2], "g": ["A", "B"]})
    p = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + facet_manual("g", design="AA\nBB")
    )

    p.draw(show=False)
    top = p.axs[0].get_position()
    bottom = p.axs[1].get_position()

    assert top.x0 == pytest.approx(bottom.x0)
    assert top.width == pytest.approx(bottom.width)
    assert top.y0 > bottom.y0


def test_facet_manual_repeated_labels_must_form_rectangle():
    df = pd.DataFrame({"x": [1, 2], "y": [1, 2], "g": ["A", "B"]})
    p = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + facet_manual("g", design="AA\nAB")
    )

    with pytest.raises(ValueError, match="must form a rectangle"):
        p.draw(show=False)


def test_facet_manual_too_few_design_labels_raise():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3], "g": ["A", "B", "C"]})
    p = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + facet_manual("g", design="AB")
    )

    with pytest.raises(ValueError, match="does not provide enough panels"):
        p.draw(show=False)


def test_facet_manual_empty_cells_trim_blank_and_remove_labels():
    df = pd.DataFrame({"x": [1], "y": [1], "g": ["A"]})
    p = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + facet_manual(
            "g",
            design=[["#", "#"], ["NA", "A"]],
            trim_blank=True,
            axes="all",
            remove_labels="x",
            widths=[1, 3],
            heights=[2, 1],
        )
    )

    p.draw(show=False)
    layout = p._build_objs.layout.layout

    assert p.facet.nrow == 1
    assert p.facet.ncol == 1
    assert p.facet.widths == [1, 3]
    assert p.facet.heights == [2, 1]
    assert p.facet._panel_widths == [3]
    assert p.facet._panel_heights == [1]
    assert layout["AXIS_X"].eq(False).all()
    assert layout["AXIS_Y"].eq(True).all()


def test_facet_manual_trim_blank_can_draw_repeatedly():
    df = pd.DataFrame({"x": [1], "y": [1], "g": ["A"]})
    p = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + facet_manual(
            "g",
            design=[["#", "#"], ["NA", "A"]],
            trim_blank=True,
            widths=[1, 3],
            heights=[2, 1],
        )
    )

    p.draw(show=False)
    p.draw(show=False)

    assert p.facet.widths == [1, 3]
    assert p.facet.heights == [2, 1]


def test_horizontal_orientation_helper_and_stats_raise():
    df = pd.DataFrame(
        {
            "x": [1.0, 2.0, 1.5, 2.5],
            "y": [1.0, 1.0, 2.0, 2.0],
            "group": [1, 1, 2, 2],
        }
    )

    assert _common.is_horizontal_orientation(df)
    with pytest.raises(NotImplementedError, match="horizontal orientation"):
        stat_pwc().compute_panel(df, None)
    with pytest.raises(NotImplementedError, match="horizontal orientation"):
        stat_compare_means().compute_panel(df, None)


def test_horizontal_orientation_helper_handles_many_discrete_levels():
    df = pd.DataFrame(
        {
            "x": np.linspace(0.1, 10.1, 51),
            "y": np.arange(1, 52, dtype=float),
        }
    )

    assert _common.is_horizontal_orientation(df)
    with pytest.raises(NotImplementedError, match="horizontal orientation"):
        stat_pwc().compute_panel(df, None)


def test_plot_level_horizontal_orientation_rejects_integer_continuous_x():
    df = pd.DataFrame(
        {
            "value": [1, 2, 3, 4],
            "group": ["A", "A", "B", "B"],
        }
    )
    p = ggplot(df, aes("value", "group")) + stat_compare_means()

    with pytest.raises(NotImplementedError, match="horizontal orientation"):
        p.draw(show=False)


def test_stat_pwc_paired_requires_complete_wid_alignment():
    df = pd.DataFrame(
        {
            "x": [1.0, 1.0, 2.0, 2.0],
            "y": [1.0, 2.0, 2.0, 4.0],
            "wid": ["s1", "s2", "s1", "s2"],
        }
    )

    with pytest.raises(ValueError, match="wid"):
        stat_pwc(method="t.test", paired=True).compute_panel(df, None)

    duplicate = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        stat_pwc(method="t.test", paired=True, wid="wid").compute_panel(
            duplicate, None
        )

    incomplete = df.iloc[:-1].copy()
    with pytest.raises(ValueError, match="complete paired"):
        stat_pwc(method="t.test", paired=True, wid="wid").compute_panel(
            incomplete, None
        )

    result = stat_pwc(
        method="t.test",
        paired=True,
        wid="wid",
        comparisons=[(1, 2)],
        p_adjust_method="none",
    ).compute_panel(df, None)
    expected = sp_stats.ttest_rel([1.0, 2.0], [2.0, 4.0])

    assert result["p"].iloc[0] == pytest.approx(expected.pvalue)


def test_plot_level_stat_pwc_preserves_wid_for_paired_tests():
    df = pd.DataFrame(
        {
            "x": [1.0, 1.0, 2.0, 2.0],
            "y": [1.0, 2.0, 2.0, 4.0],
            "wid": ["s1", "s2", "s1", "s2"],
        }
    )
    p = ggplot(df, aes("x", "y")) + stat_pwc(
        method="t.test",
        paired=True,
        wid="wid",
        comparisons=[(1, 2)],
        p_adjust_method="none",
    )

    p.draw(show=False)
    layer_data = p._build_objs.layers[0].data
    expected = sp_stats.ttest_rel([1.0, 2.0], [2.0, 4.0])

    assert layer_data["p"].iloc[0] == pytest.approx(expected.pvalue)


def test_stat_compare_means_uses_wid_for_paired_pairwise_tests():
    df = pd.DataFrame(
        {
            "x": [1.0, 1.0, 2.0, 2.0],
            "y": [1.0, 2.0, 2.0, 4.0],
            "wid": ["s1", "s2", "s1", "s2"],
        }
    )
    result = stat_compare_means(
        method="t.test",
        paired=True,
        wid="wid",
        comparisons=[(1, 2)],
    ).compute_panel(df, None)
    expected = sp_stats.ttest_rel([1.0, 2.0], [2.0, 4.0])

    assert result["p"].iloc[0] == pytest.approx(expected.pvalue)


def test_stat_compare_means_uses_wid_for_global_paired_tests():
    df = pd.DataFrame(
        {
            "x": [1.0, 1.0, 2.0, 2.0],
            "y": [1.0, 2.0, 2.0, 4.0],
            "wid": ["s1", "s2", "s1", "s2"],
        }
    )
    result = stat_compare_means(
        method="t.test",
        paired=True,
        wid="wid",
    ).compute_panel(df, None)
    expected = sp_stats.ttest_rel([1.0, 2.0], [2.0, 4.0])

    assert result["p"].iloc[0] == pytest.approx(expected.pvalue)
    assert result["method"].iloc[0] == "Paired t-test"


def test_stat_friedman_test_requires_complete_subject_blocks():
    df = pd.DataFrame(
        {
            "x": [1.0, 1.0, 2.0, 2.0, 3.0, 3.0],
            "y": [1.0, 2.0, 2.0, 4.0, 3.0, 5.0],
            "wid": ["s1", "s2", "s1", "s2", "s1", "s2"],
        }
    )

    with pytest.raises(ValueError, match="wid"):
        stat_friedman_test().compute_panel(df, None)

    duplicate = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        stat_friedman_test(wid="wid").compute_panel(duplicate, None)

    incomplete = df.iloc[:-1].copy()
    with pytest.raises(ValueError, match="complete"):
        stat_friedman_test(wid="wid").compute_panel(incomplete, None)

    result = stat_friedman_test(wid="wid").compute_panel(df, None)
    expected = sp_stats.friedmanchisquare([1.0, 2.0], [2.0, 4.0], [3.0, 5.0])

    assert result["p"].iloc[0] == pytest.approx(expected.pvalue)


def test_stat_friedman_test_rejects_horizontal_orientation():
    df = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 1.5, 2.5, 3.5],
            "y": [1.0, 2.0, 3.0, 1.0, 2.0, 3.0],
            "wid": ["s1", "s1", "s1", "s2", "s2", "s2"],
        }
    )

    assert _common.is_horizontal_orientation(df)
    with pytest.raises(NotImplementedError, match="horizontal orientation"):
        stat_friedman_test(wid="wid").compute_panel(df, None)


def test_stat_pvalue_manual_maps_string_groups_with_x_levels():
    pval_data = pd.DataFrame(
        {
            "group1": ["A"],
            "group2": ["B"],
            "p": [0.01],
            "y_position": [10],
        }
    )

    layers = stat_pvalue_manual(pval_data, x_levels=["B", "A"])
    text_layer = layers[-1]

    assert text_layer.data["x"].iloc[0] == 1.5
    assert text_layer.data["label"].iloc[0] == "p = 0.010"


def test_stat_pwc_remove_bracket_uses_text_geom():
    layer = stat_pwc(remove_bracket=True)

    assert layer.params["geom"] == "text"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"method": "swram"},
        {"priority": "densitty"},
        {"side": 2},
        {"corral": "guttre"},
    ],
)
def test_position_beeswarm_invalid_options_raise(kwargs):
    with pytest.raises(ValueError):
        position_beeswarm(**kwargs)


def test_position_quasirandom_invalid_method_raises():
    with pytest.raises(ValueError):
        position_quasirandom(method="quasi")


def test_strip_classes_are_exported_and_fail_clearly_for_unsupported_draw():
    assert pe.strip_nested(nest_line=True).nest_line is True
    assert pe.strip_themed(text_x=["theme"]).text_x == ["theme"]
    assert pe.strip_tag(prefix="(", suffix=")").prefix == "("

    with pytest.raises(NotImplementedError, match="strip_split"):
        pe.strip_split().draw({})
