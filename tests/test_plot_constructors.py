import numpy as np
import pandas as pd
from plotnine import ggplot

from plotnine_extra.plots import (
    DimPlot,
    FeatureDimPlot,
    ROCCurve,
    VolcanoPlot,
    ggbarplot,
    ggboxplot,
    ggdensity,
    ggdim,
    ggfeaturedim,
    gghistogram,
    ggline,
    ggpaired,
    ggroc,
    ggscatter,
    ggviolin,
    ggvolcano,
)


def grouped_data():
    return pd.DataFrame(
        {
            "group": ["A", "A", "B", "B", "C", "C"],
            "value": [1.0, 1.5, 2.0, 2.5, 1.2, 1.7],
            "x": [0, 1, 0, 1, 0, 1],
            "y": [1.0, 1.3, 1.6, 1.9, 2.2, 2.5],
            "subject": ["s1", "s2", "s1", "s2", "s1", "s2"],
        }
    )


def embedding_data():
    return pd.DataFrame(
        {
            "UMAP_1": [0.0, 1.0, 0.0, 1.0],
            "UMAP_2": [0.0, 0.0, 1.0, 1.0],
            "cluster": ["a", "a", "b", "b"],
            "gene": [0.1, 0.5, 1.2, 2.4],
        }
    )


def test_ggpubr_style_constructors_return_ggplots():
    data = grouped_data()
    constructors = [
        ggboxplot(data, "group", "value"),
        ggviolin(data, "group", "value", add="boxplot"),
        ggscatter(data, "x", "y", color="group", add="reg.line"),
        gghistogram(data, "value", bins=4),
        ggdensity(data, "value", color="group"),
        ggbarplot(data, "group", "value", stat="summary"),
        ggline(data, "x", "y", color="group"),
        ggpaired(data, "group", "value", id="subject"),
    ]

    assert all(isinstance(plot, ggplot) for plot in constructors)
    for plot in constructors:
        plot.build_test()


def test_ggscatter_accepts_shape_mapping():
    data = grouped_data()

    plot = ggscatter(data, "x", "y", shape="group")

    plot.draw(show=False)


def test_ggpaired_default_color_renders():
    plot = ggpaired(grouped_data(), "group", "value", id="subject")

    plot.draw(show=False)


def test_ggbarplot_summary_deduplicates_aesthetic_groups():
    data = grouped_data()

    for kwargs in (
        {"fill": "group"},
        {"color": "group"},
        {"fill": "group", "color": "group"},
    ):
        plot = ggbarplot(data, "group", "value", stat="summary", **kwargs)
        plot.draw(show=False)


def test_single_cell_plotthis_constructors_return_ggplots():
    data = embedding_data()

    plots = [
        ggdim(data, color="cluster"),
        ggfeaturedim(data, feature="gene"),
        DimPlot(data, color="cluster"),
        FeatureDimPlot(data, feature="gene"),
    ]

    assert all(isinstance(plot, ggplot) for plot in plots)
    for plot in plots:
        plot.build_test()


def test_ggvolcano_labels_selected_points():
    data = pd.DataFrame(
        {
            "log2fc": [-2.0, -0.2, 0.1, 2.1],
            "pvalue": [0.001, 0.8, 0.4, 0.0005],
            "gene": ["left", "flat1", "flat2", "right"],
        }
    )

    plot = ggvolcano(
        data,
        x="log2fc",
        y="pvalue",
        label="gene",
        label_top=2,
    )

    assert isinstance(plot, ggplot)
    built = plot.build_test()
    assert {"left", "right"} == set(built.layers[-1].data["label"])
    assert isinstance(VolcanoPlot(data), ggplot)


def test_ggroc_computes_auc_without_extra_dependencies():
    data = pd.DataFrame(
        {
            "truth": [0, 0, 1, 1],
            "score": [0.1, 0.4, 0.35, 0.8],
        }
    )

    plot = ggroc(data, truth="truth", score="score")

    assert isinstance(plot, ggplot)
    assert np.isclose(plot.data.attrs["auc"], 0.75)
    assert list(plot.data.columns) == ["fpr", "tpr", "threshold"]
    plot.build_test()
    assert isinstance(ROCCurve(data, truth="truth", score="score"), ggplot)
