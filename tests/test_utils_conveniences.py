"""
Unit tests for plotnine_extra.utils.conveniences.

Tests for distribute_args, elem_list_text, elem_list_rect,
weave_factors, center_limits, and internal helpers.
"""

import numpy as np
import pandas as pd
import pytest
from plotnine.themes.elements import element_rect, element_text

from plotnine_extra.utils.conveniences import (
    _has_length,
    _is_na,
    center_limits,
    distribute_args,
    elem_list_rect,
    elem_list_text,
    weave_factors,
)

# ---- _is_na helper ----


class TestIsNa:
    def test_none_is_na(self):
        assert _is_na(None) is True

    def test_nan_is_na(self):
        assert _is_na(float("nan")) is True

    def test_np_nan_is_na(self):
        assert _is_na(np.nan) is True

    def test_number_is_not_na(self):
        assert _is_na(0) is False
        assert _is_na(42) is False
        assert _is_na(3.14) is False

    def test_string_is_not_na(self):
        assert _is_na("hello") is False

    def test_empty_string_is_not_na(self):
        assert _is_na("") is False


# ---- _has_length helper ----


class TestHasLength:
    def test_non_empty_list(self):
        assert _has_length([1, 2]) is True

    def test_empty_list(self):
        assert _has_length([]) is False

    def test_non_empty_tuple(self):
        assert _has_length((1,)) is True

    def test_empty_tuple(self):
        assert _has_length(()) is False

    def test_scalar(self):
        assert _has_length(42) is True
        assert _has_length("hello") is True
        assert _has_length(None) is True


# ---- distribute_args ----


class TestDistributeArgs:
    def test_no_kwargs_returns_single(self):
        result = distribute_args()
        assert len(result) == 1
        assert isinstance(result[0], element_text)

    def test_scalar_kwargs(self):
        result = distribute_args(color="red")
        assert len(result) == 1

    def test_vector_kwargs(self):
        result = distribute_args(color=["red", "blue"])
        assert len(result) == 2

    def test_mixed_lengths_recycles(self):
        result = distribute_args(
            color=["red", "blue", "green"],
            size=[10],
        )
        # Longer vector determines length
        assert len(result) == 3

    def test_none_values_dropped(self):
        result = distribute_args(color=[None, "blue"])
        assert len(result) == 2

    def test_nan_values_dropped(self):
        result = distribute_args(
            color=["red", np.nan],
        )
        assert len(result) == 2

    def test_custom_fun(self):
        def custom(x=0, y=0):
            return (x, y)

        result = distribute_args(fun=custom, x=[1, 2], y=[3, 4])
        assert result == [(1, 3), (2, 4)]

    def test_cull_filters_invalid_params(self):
        def simple(a=0):
            return a

        result = distribute_args(
            fun=simple,
            cull=True,
            a=[1, 2],
            b=[3, 4],  # b is not a valid param
        )
        assert result == [1, 2]

    def test_cull_false_passes_all(self):
        def with_kwargs(**kw):
            return kw

        result = distribute_args(
            fun=with_kwargs,
            cull=False,
            a=[1],
            b=[2],
        )
        assert result == [{"a": 1, "b": 2}]

    def test_empty_list_kwargs_dropped(self):
        result = distribute_args(color=[], size=[10])
        assert len(result) == 1


# ---- elem_list_text ----


class TestElemListText:
    def test_basic(self):
        result = elem_list_text(color=["red", "blue"])
        assert len(result) == 2
        assert all(isinstance(r, element_text) for r in result)

    def test_empty(self):
        result = elem_list_text()
        assert len(result) == 1


# ---- elem_list_rect ----


class TestElemListRect:
    def test_basic(self):
        result = elem_list_rect(fill=["red", "blue"])
        assert len(result) == 2
        assert all(isinstance(r, element_rect) for r in result)


# ---- weave_factors ----


class TestWeaveFactors:
    def test_single_factor(self):
        result = weave_factors(["A", "B", "A"])
        assert isinstance(result, pd.Categorical)
        assert len(result) == 3

    def test_two_factors(self):
        result = weave_factors(["A", "A", "B"], ["X", "Y", "X"])
        assert len(result) == 3
        expected = ["A.X", "A.Y", "B.X"]
        assert list(result) == expected

    def test_custom_separator(self):
        result = weave_factors(["A", "B"], ["X", "Y"], sep="-")
        assert list(result) == ["A-X", "B-Y"]

    def test_drop_true(self):
        result = weave_factors(["A", "A"], ["X", "X"], drop=True)
        # Only observed combo should be in categories
        assert list(result.categories) == ["A.X"]

    def test_drop_false(self):
        result = weave_factors(["A", "A"], ["X", "X"], drop=False)
        # All combos should be in categories
        assert "A.X" in result.categories

    def test_unequal_lengths_raises(self):
        with pytest.raises(ValueError, match="same length"):
            weave_factors([1, 2, 3], [4, 5])

    def test_empty_input(self):
        result = weave_factors()
        assert len(result) == 0

    def test_replace_na_true(self):
        result = weave_factors(["A", None, "B"], replace_na=True)
        assert "NA" in list(result)

    def test_three_factors(self):
        result = weave_factors(["A", "B"], ["X", "Y"], ["1", "2"])
        assert list(result) == ["A.X.1", "B.Y.2"]


# ---- center_limits ----


class TestCenterLimits:
    def test_center_around_zero(self):
        fn = center_limits(0)
        result = fn((3, 8))
        assert result == (-8, 8)

    def test_center_around_zero_negative(self):
        fn = center_limits(0)
        result = fn((-10, 3))
        assert result == (-10, 10)

    def test_center_around_value(self):
        fn = center_limits(5)
        result = fn((3, 8))
        assert result == (2, 8)

    def test_symmetric_input(self):
        fn = center_limits(0)
        result = fn((-5, 5))
        assert result == (-5, 5)

    def test_returns_callable(self):
        fn = center_limits(0)
        assert callable(fn)
