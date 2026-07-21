import pandas as pd
import pytest
from plotnine import aes, geom_point, ggplot, labs, scale_x_continuous

# ggarrange(layout) and annotate_figure build on plotnine's composition
# layout/annotation API, which is only available in plotnine >=0.16. Skip
# those tests on older plotnine, where the helpers raise a clear upgrade error.
_has_compose_layout = hasattr(
    __import__("plotnine.composition._compose", fromlist=["Compose"]).Compose,
    "layout",
)
requires_compose_layout = pytest.mark.skipif(
    not _has_compose_layout,
    reason="requires plotnine >=0.16 (composition layout/annotation)",
)


def test_ggpubr_workflow_utils_are_public():
    from plotnine_extra.utils import (
        annotate_figure,
        compare_means,
        get_breaks,
        get_legend,
        ggarrange,
        stat_bracket,
    )

    assert compare_means is not None
    assert get_breaks is not None
    assert get_legend is not None
    assert annotate_figure is not None
    assert ggarrange is not None
    assert stat_bracket is not None


def test_compare_means_returns_deterministic_pairwise_table():
    from scipy import stats as sp_stats

    from plotnine_extra.utils import compare_means

    data = pd.DataFrame(
        {
            "dose": ["B", "A", "C", "A", "B", "C"],
            "len": [5.0, 1.0, 8.0, 2.0, 4.0, 9.0],
        }
    )

    result = compare_means("len ~ dose", data, method="t.test")

    assert list(result["group1"]) == ["A", "A", "B"]
    assert list(result["group2"]) == ["B", "C", "C"]
    assert list(result.columns) == [
        ".y.",
        "group1",
        "group2",
        "p",
        "p.adj",
        "p.format",
        "p.signif",
        "method",
    ]
    expected = sp_stats.ttest_ind(
        [1.0, 2.0],
        [4.0, 5.0],
        equal_var=False,
    )
    assert result.loc[0, "p"] == pytest.approx(float(expected.pvalue))


@requires_compose_layout
def test_ggarrange_wraps_plots_with_layout():
    from plotnine_extra.composition import Wrap
    from plotnine_extra.utils import ggarrange

    data = pd.DataFrame({"x": [1, 2], "y": [2, 3]})
    p1 = ggplot(data, aes("x", "y")) + geom_point()
    p2 = ggplot(data, aes("y", "x")) + geom_point()

    arranged = ggarrange(p1, p2, ncol=2)

    assert isinstance(arranged, Wrap)
    assert len(arranged.items) == 2
    assert arranged.layout.ncol == 2


@requires_compose_layout
def test_annotate_figure_adds_composition_annotation():
    from plotnine_extra.utils import annotate_figure, ggarrange

    data = pd.DataFrame({"x": [1, 2], "y": [2, 3]})
    p = ggplot(data, aes("x", "y")) + geom_point()

    annotated = annotate_figure(ggarrange(p, p), top="Title", bottom="Note")

    assert annotated.annotation.title == "Title"
    assert annotated.annotation.caption == "Note"


def test_get_breaks_returns_axis_breaks_from_built_plot():
    from plotnine_extra.utils import get_breaks

    data = pd.DataFrame({"x": [1, 2, 3], "y": [2, 3, 4]})
    p = (
        ggplot(data, aes("x", "y"))
        + geom_point()
        + scale_x_continuous(breaks=[1, 2, 3])
    )

    assert get_breaks(p, "x") == [1, 2, 3]


def test_get_legend_raises_clear_error_when_no_legend_is_drawn():
    from plotnine_extra.utils import get_legend

    data = pd.DataFrame({"x": [1, 2], "y": [2, 3]})
    p = ggplot(data, aes("x", "y")) + geom_point() + labs(color=None)

    with pytest.raises(RuntimeError, match="legend"):
        get_legend(p)
