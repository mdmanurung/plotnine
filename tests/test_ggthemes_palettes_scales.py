"""Tests for ggthemes-compatible palettes and scales."""

import pytest

from plotnine_extra.palettes import GGTHEMES_PALETTES, ggthemes_palette
from plotnine_extra.scales import (
    scale_color_colorblind,
    scale_color_economist,
    scale_color_excel,
    scale_color_few,
    scale_color_fivethirtyeight,
    scale_color_gdocs,
    scale_color_hc,
    scale_color_highcharts,
    scale_color_solarized,
    scale_color_stata,
    scale_color_tableau,
    scale_color_wsj,
    scale_colour_colorblind,
    scale_fill_colorblind,
    scale_fill_economist,
    scale_fill_excel,
    scale_fill_few,
    scale_fill_fivethirtyeight,
    scale_fill_gdocs,
    scale_fill_hc,
    scale_fill_highcharts,
    scale_fill_solarized,
    scale_fill_stata,
    scale_fill_tableau,
    scale_fill_wsj,
)


def test_ggthemes_palette_output_is_deterministic():
    assert ggthemes_palette("colorblind", n=4) == [
        "#000000",
        "#E69F00",
        "#56B4E9",
        "#009E73",
    ]
    assert ggthemes_palette("tableau", n=3) == [
        "#4E79A7",
        "#F28E2B",
        "#E15759",
    ]
    assert ggthemes_palette("tableau", n=2, palette="tableau 20") == [
        "#4E79A7",
        "#A0CBE8",
    ]


def test_ggthemes_palette_names_cover_required_pack():
    required = {
        "colorblind",
        "economist",
        "excel",
        "few",
        "fivethirtyeight",
        "gdocs",
        "hc",
        "highcharts",
        "solarized",
        "stata",
        "tableau",
        "wsj",
    }
    assert required <= set(GGTHEMES_PALETTES)


def test_ggthemes_palette_interpolates_when_more_colors_requested():
    cols = ggthemes_palette("colorblind", n=10)
    assert len(cols) == 10
    assert cols[:3] == ["#000000", "#B37C00", "#96AB81"]
    assert all(c.startswith("#") for c in cols)


def test_ggthemes_palette_rejects_unknown_names():
    with pytest.raises(ValueError, match="Unknown ggthemes palette"):
        ggthemes_palette("not-a-palette")


@pytest.mark.parametrize(
    ("color_scale", "fill_scale"),
    [
        (scale_color_colorblind, scale_fill_colorblind),
        (scale_color_tableau, scale_fill_tableau),
        (scale_color_economist, scale_fill_economist),
        (scale_color_excel, scale_fill_excel),
        (scale_color_few, scale_fill_few),
        (scale_color_fivethirtyeight, scale_fill_fivethirtyeight),
        (scale_color_gdocs, scale_fill_gdocs),
        (scale_color_hc, scale_fill_hc),
        (scale_color_highcharts, scale_fill_highcharts),
        (scale_color_solarized, scale_fill_solarized),
        (scale_color_stata, scale_fill_stata),
        (scale_color_wsj, scale_fill_wsj),
    ],
)
def test_ggthemes_scales_construct(color_scale, fill_scale):
    color = color_scale(k=3)
    fill = fill_scale(k=3)
    assert color is not None
    assert fill is not None
    assert color.aesthetics == ["color"]
    assert fill.aesthetics == ["fill"]


def test_ggthemes_colour_alias_is_color_helper():
    assert scale_colour_colorblind is scale_color_colorblind
