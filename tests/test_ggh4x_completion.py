"""Tests for remaining lightweight ggh4x parity helpers."""

import numpy as np
import pandas as pd
import pytest
from plotnine import aes, geom_point, ggplot

from plotnine_extra import (
    at_panel,
    center_limits,
    facet_wrap2,
    force_panelsizes,
    geom_polygonraster,
    ggsubset,
    help_secondary,
    scale_x_dendrogram,
    scale_y_dendrogram,
    strip_vanilla,
)


def test_strip_vanilla_stores_options():
    strip = strip_vanilla(clip="off", size="variable")

    assert strip.clip == "off"
    assert strip.size == "variable"


def test_strip_vanilla_validates_options():
    with pytest.raises(ValueError, match="clip"):
        strip_vanilla(clip="bad")
    with pytest.raises(ValueError, match="size"):
        strip_vanilla(size="bad")


def test_help_secondary_range_projects_secondary_to_primary_range():
    data = pd.DataFrame({"primary": [0, 10], "secondary": [100, 200]})
    sec = help_secondary(
        data,
        primary="primary",
        secondary="secondary",
        method="range",
        name="secondary",
    )

    assert sec.proj([100, 150, 200]).tolist() == pytest.approx([0, 5, 10])
    assert sec.inverse([0, 5, 10]).tolist() == pytest.approx([100, 150, 200])
    assert sec.name == "secondary"


def test_help_secondary_fit_method():
    data = pd.DataFrame({"primary": [2, 4, 6], "secondary": [1, 2, 3]})
    sec = help_secondary(data, "primary", "secondary", method="fit")

    assert sec.proj([4]).tolist() == pytest.approx([8])


def test_scale_dendrogram_uses_ordered_labels_and_guide():
    scale = scale_x_dendrogram(hclust={"ivl": ["c", "a", "b"]})

    assert list(scale.limits) == ["c", "a", "b"]
    assert scale.guide.kind == "dendro"


def test_scale_y_dendrogram_accepts_explicit_labels():
    linkage = np.array([[0, 1, 0.1, 2], [2, 3, 0.2, 3]], dtype=float)
    scale = scale_y_dendrogram(hclust=linkage, labels=["a", "b", "c"])

    assert sorted(scale.limits) == ["a", "b", "c"]
    assert scale.guide.options["position"] == "left"


def test_geom_polygonraster_expands_pixels_to_polygons():
    geom = geom_polygonraster()
    data = pd.DataFrame(
        {
            "x": [0.0, 1.0],
            "y": [0.0, 0.0],
            "fill": ["red", "blue"],
            "PANEL": [1, 1],
            "group": [1, 2],
        }
    )

    out = geom.setup_data(data)

    assert len(out) == 8
    assert out.groupby("_raster_group").size().tolist() == [4, 4]
    assert {"x", "y", "fill", "group"}.issubset(out.columns)


def test_geom_polygonraster_draws_numeric_only_data():
    data = pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [1.0, 2.0, 3.0]})

    plot = ggplot(data, aes("x", "y")) + geom_polygonraster()

    plot.draw(show=False)


def test_force_panelsizes_attaches_to_facet_and_draws():
    df = pd.DataFrame(
        {
            "x": [1, 2, 3, 4],
            "y": [1, 2, 3, 4],
            "g": ["a", "a", "b", "b"],
        }
    )

    plot = (
        ggplot(df, aes("x", "y"))
        + geom_point()
        + facet_wrap2("g", ncol=2)
        + force_panelsizes(cols=[2, 1])
    )

    assert plot.facet._panel_widths == [2, 1]
    plot.draw(show=False)


def test_at_panel_filters_layer_to_matching_layout_rows():
    df = pd.DataFrame(
        {
            "x": [1, 2, 3, 4],
            "y": [1, 2, 3, 4],
            "g": ["a", "a", "b", "b"],
        }
    )
    layer = at_panel(geom_point(color="red"), "g == 'b'")
    plot = ggplot(df, aes("x", "y")) + layer + facet_wrap2("g")

    plot._build()
    out = plot._build_objs.layers[0].data

    assert out["PANEL"].astype(int).unique().tolist() == [2]


def test_ggsubset_aliases_at_panel():
    layer = ggsubset(geom_point(), "PANEL == 1")

    assert getattr(layer, "_plotnine_extra_panel_selector") == "PANEL == 1"


def test_help_secondary_explicit_plotnine_axis_error():
    sec = help_secondary(primary=[0, 1], secondary=[0, 10])

    with pytest.raises(NotImplementedError, match="secondary axes"):
        sec.as_plotnine_axis()


def test_center_limits_existing_helper_remains_exported():
    assert center_limits(1)((-1, 2)) == (-1, 3)
