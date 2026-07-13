"""Tests for ggthemes-style themes, geoms, stats, and utilities."""

import numpy as np
import pandas as pd
import pytest
from plotnine import aes, geom_point, ggplot

from plotnine_extra import (
    bank_slopes,
    extended_range_breaks,
    geom_rangeframe,
    geom_tufteboxplot,
    smart_digits,
    stat_fivenumber,
    theme_economist,
    theme_few,
    theme_fivethirtyeight,
    theme_tufte,
    theme_wsj,
)


def test_ggthemes_themes_construct_and_draw():
    data = pd.DataFrame({"x": [1, 2, 3], "y": [2, 3, 5]})
    for theme_fn in (
        theme_economist,
        theme_few,
        theme_fivethirtyeight,
        theme_tufte,
        theme_wsj,
    ):
        plot = ggplot(data, aes("x", "y")) + geom_point() + theme_fn()
        plot.draw(show=False)


def test_stat_fivenumber_computes_boxplot_values():
    data = pd.DataFrame({"x": [1] * 5, "y": [1, 2, 3, 4, 5]})
    stat = stat_fivenumber()
    out = stat.compute_group(data, scales=None)

    assert out.loc[0, "ymin"] == 1
    assert out.loc[0, "lower"] == 2
    assert out.loc[0, "middle"] == 3
    assert out.loc[0, "upper"] == 4
    assert out.loc[0, "ymax"] == 5


def test_geom_rangeframe_setup_data_creates_two_segments():
    data = pd.DataFrame(
        {
            "x": [1, 2, 3],
            "y": [10, 20, 30],
            "PANEL": [1, 1, 1],
            "group": [1, 1, 1],
        }
    )

    out = geom_rangeframe().setup_data(data)

    assert len(out) == 2
    assert set(out["rangeframe_axis"]) == {"x", "y"}
    assert out.loc[out["rangeframe_axis"] == "x", "xend"].iloc[0] == 3
    assert out.loc[out["rangeframe_axis"] == "y", "yend"].iloc[0] == 30


def test_geom_rangeframe_draws():
    data = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})

    plot = ggplot(data, aes("x", "y")) + geom_rangeframe()

    plot.draw(show=False)


def test_geom_tufteboxplot_draws_with_stat_fivenumber():
    data = pd.DataFrame({"x": ["a"] * 5, "y": [1, 2, 3, 4, 5]})

    plot = ggplot(data, aes("x", "y")) + geom_tufteboxplot()

    plot.draw(show=False)


def test_bank_slopes_returns_inverse_median_slope():
    assert bank_slopes([0, 1, 2], [0, 2, 4]) == pytest.approx(0.5)


def test_extended_range_breaks_returns_nice_break_function():
    breaks = extended_range_breaks(n=5)((0.2, 9.7))

    assert len(breaks) <= 6
    assert breaks[0] <= 0.2
    assert breaks[-1] >= 9.7


def test_smart_digits_formats_values_from_resolution():
    labels = smart_digits([0, 0.125, 10])

    assert labels == ["0", "0.125", "10"]
    assert smart_digits(np.array([1.23456]), digits=2) == ["1.23"]
