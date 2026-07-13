"""Smoke tests for the ggh4x-flavoured stats / geoms / positions / scales."""

import numpy as np
import pandas as pd
import pytest

from plotnine_extra import (
    coord_axes_inside,
    geom_box,
    geom_outline_point,
    geom_pointpath,
    geom_rectmargin,
    geom_text_aimed,
    geom_tilemargin,
    guide_axis_logticks,
    guide_axis_manual,
    guide_axis_minor,
    guide_axis_nested,
    guide_axis_truncated,
    guide_dendro,
    guide_stringlegend,
    position_disjoint_ranges,
    position_lineartrans,
    scale_color_multi,
    scale_colour_multi,
    scale_fill_multi,
    scale_listed,
    scale_x_manual,
    scale_y_manual,
    stat_centroid,
    stat_difference,
    stat_funxy,
    stat_midpoint,
    stat_rle,
    stat_rollingkernel,
    stat_theodensity,
)


@pytest.fixture
def df():
    rng = np.random.default_rng(0)
    return pd.DataFrame(
        {
            "x": np.arange(20, dtype=float),
            "y": rng.normal(size=20),
            "g": ["a"] * 10 + ["b"] * 10,
        }
    )


# ---- ggh4x stats ----------------------------------------------------------


def test_stat_centroid_compute_group(df):
    s = stat_centroid()
    out = s.compute_group(df, scales=None)
    assert out["x"].iloc[0] == pytest.approx(df["x"].mean())
    assert out["y"].iloc[0] == pytest.approx(df["y"].mean())


def test_stat_midpoint_compute_group(df):
    s = stat_midpoint()
    out = s.compute_group(df, scales=None)
    assert out["x"].iloc[0] == pytest.approx(
        (df["x"].min() + df["x"].max()) / 2
    )


def test_stat_funxy_compute_group(df):
    s = stat_funxy(funx=np.median, funy=np.median)
    s.params = {"funx": np.median, "funy": np.median}
    out = s.compute_group(df, scales=None)
    assert out["x"].iloc[0] == pytest.approx(df["x"].median())
    assert out["y"].iloc[0] == pytest.approx(df["y"].median())


def test_stat_difference_creates_sign(df):
    d = pd.DataFrame(
        {
            "x": [0, 1, 2, 3],
            "ymin": [0, 1, 2, 3],
            "ymax": [1, 0, 3, 2],
        }
    )
    s = stat_difference()
    out = s.compute_group(d, scales=None)
    assert "sign" in out.columns
    assert set(out["sign"]) <= {"positive", "negative", "zero"}


def test_stat_rle_groups_runs():
    d = pd.DataFrame(
        {
            "x": list(range(6)),
            "label": ["a", "a", "b", "b", "b", "a"],
            "y": [0] * 6,
        }
    )
    s = stat_rle()
    out = s.compute_panel(d, scales=None)
    assert len(out) == 3
    assert list(out["runvalue"]) == ["a", "b", "a"]


def test_stat_rollingkernel_returns_grid(df):
    s = stat_rollingkernel(bw=2.0, n=15)
    s.params = {
        "bw": 2.0,
        "kernel": "gaussian",
        "n": 15,
    }
    out = s.compute_group(df, scales=None)
    assert len(out) == 15
    assert out["y"].notna().all()


def test_stat_theodensity_norm():
    rng = np.random.default_rng(1)
    d = pd.DataFrame({"x": rng.normal(0, 1, 200)})
    s = stat_theodensity()
    s.params = {"distri": "norm", "n": 64}
    out = s.compute_group(d, scales=None)
    assert len(out) == 64
    assert (out["density"] >= 0).all()


def test_stat_theodensity_unknown():
    s = stat_theodensity()
    s.params = {"distri": "doesnotexist", "n": 32}
    with pytest.raises(ValueError, match="Unknown distri"):
        s.compute_group(pd.DataFrame({"x": [1.0, 2.0, 3.0]}), scales=None)


# ---- ggh4x positions ------------------------------------------------------


def test_position_lineartrans_identity():
    pos = position_lineartrans()
    d = pd.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})
    out = pos.compute_layer(d, {"M": pos.M}, layout=None)
    assert list(out["x"]) == [1.0, 2.0]
    assert list(out["y"]) == [3.0, 4.0]


def test_position_lineartrans_scale():
    pos = position_lineartrans(scale=(2.0, 3.0))
    d = pd.DataFrame({"x": [1.0, 2.0], "y": [1.0, 2.0]})
    out = pos.compute_layer(d, {"M": pos.M}, layout=None)
    assert list(out["x"]) == [2.0, 4.0]
    assert list(out["y"]) == [3.0, 6.0]


def test_position_disjoint_ranges_assigns_rows():
    pos = position_disjoint_ranges()
    d = pd.DataFrame(
        {
            "xmin": [0, 1, 2, 5],
            "xmax": [3, 4, 4, 6],
        }
    )
    out = pos.compute_layer(d, {"extend": 0, "stepsize": 1}, layout=None)
    # Three of the four overlap; the fourth is disjoint
    assert out["y"].nunique() >= 2


# ---- ggh4x geoms (smoke) --------------------------------------------------


def test_geom_box_constructible():
    g = geom_box()
    assert g.DEFAULT_PARAMS["stat"] == "identity"


def test_geom_text_aimed_setup_data():
    g = geom_text_aimed()
    d = pd.DataFrame(
        {
            "x": [0.0, 0.0],
            "y": [0.0, 0.0],
            "xend": [1.0, 1.0],
            "yend": [0.0, 1.0],
            "label": ["east", "northeast"],
        }
    )

    out = g.setup_data(d)

    assert list(out["angle"]) == pytest.approx([0.0, 45.0])


def test_geom_pointpath_constructible():
    g = geom_pointpath()
    assert g is not None


def test_geom_outline_point_constructible():
    g = geom_outline_point()
    assert g is not None


def test_geom_rectmargin_default_sides():
    g = geom_rectmargin()
    assert g.DEFAULT_PARAMS["sides"] == "b"


def test_geom_tilemargin_default_sides():
    g = geom_tilemargin()
    assert g.DEFAULT_PARAMS["sides"] == "b"


# ---- ggh4x scales (smoke) -------------------------------------------------


def test_scale_x_manual_returns_scale():
    s = scale_x_manual(values=["a", "b", "c"])
    assert s is not None


def test_scale_y_manual_returns_scale():
    s = scale_y_manual(values=["x", "y"])
    assert s is not None


def test_scale_colour_multi_returns_list():
    out = scale_colour_multi({"colour": "npg", "colour_alt": "jco"})
    assert isinstance(out, list)
    assert len(out) == 2


def test_scale_color_multi_alias():
    assert scale_color_multi is scale_colour_multi


def test_scale_fill_multi():
    out = scale_fill_multi({"fill": "npg"})
    assert isinstance(out, list)
    assert len(out) == 1


def test_scale_listed_returns_list():
    inner = [scale_x_manual(values=["a", "b"])]
    out = scale_listed(inner)
    assert out == inner


# ---- guides (placeholders) ------------------------------------------------


def test_guide_axis_factories_return_specs():
    for fn in (
        guide_axis_nested,
        guide_axis_manual,
        guide_axis_minor,
        guide_axis_logticks,
        guide_axis_truncated,
        guide_dendro,
        guide_stringlegend,
    ):
        spec = fn()
        assert spec.kind
        assert isinstance(spec.options, dict)


# ---- coord_axes_inside ----------------------------------------------------


def test_coord_axes_inside_attrs():
    c = coord_axes_inside(xintercept=2, yintercept=-1)
    assert c.xintercept == 2
    assert c.yintercept == -1
