"""
Small utility helpers inspired by ggthemes.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np
from matplotlib.ticker import MaxNLocator

if TYPE_CHECKING:
    from typing import Any, Callable, Sequence


def bank_slopes(x: "Sequence[float]", y: "Sequence[float]") -> float:
    """
    Return an aspect ratio that banks median line slopes to 45 degrees.
    """
    x_values = np.asarray(x, dtype=float)
    y_values = np.asarray(y, dtype=float)
    if len(x_values) != len(y_values):
        msg = "x and y must have the same length"
        raise ValueError(msg)
    if len(x_values) < 2:
        msg = "bank_slopes requires at least two points"
        raise ValueError(msg)
    order = np.argsort(x_values, kind="mergesort")
    dx = np.diff(x_values[order])
    dy = np.diff(y_values[order])
    valid = dx != 0
    if not valid.any():
        msg = "x must contain at least two distinct values"
        raise ValueError(msg)
    slopes = np.abs(dy[valid] / dx[valid])
    slope = float(np.median(slopes[slopes > 0]))
    if not math.isfinite(slope) or slope == 0:
        return 1.0
    return 1.0 / slope


def extended_range_breaks(n: int = 5, **kwargs: "Any") -> "Callable":
    """
    Return a break function using Matplotlib's extended locator.
    """

    def breaks(limits: tuple[float, float]) -> list[float]:
        locator = MaxNLocator(nbins=n, **kwargs)
        values = locator.tick_values(float(limits[0]), float(limits[1]))
        return [float(value) for value in values]

    return breaks


def smart_digits(
    values: "Sequence[float]",
    *,
    digits: int | None = None,
    min_digits: int = 0,
    max_digits: int = 6,
) -> list[str]:
    """
    Format numeric labels with enough digits for the data resolution.
    """
    arr = np.asarray(values, dtype=float)
    if digits is not None:
        return [f"{value:.{digits}f}".rstrip("0").rstrip(".") for value in arr]

    labels = [
        np.format_float_positional(
            value,
            precision=max_digits,
            fractional=True,
            trim="-",
        )
        for value in arr
    ]
    if min_digits:
        labels = [_pad_decimal(label, min_digits) for label in labels]
    return labels


def _digits_from_resolution(
    values: np.ndarray,
    min_digits: int,
    max_digits: int,
) -> int:
    finite = np.sort(np.unique(values[np.isfinite(values)]))
    if len(finite) < 2:
        return min_digits
    diffs = np.diff(finite)
    resolution = float(np.min(diffs[diffs > 0]))
    if resolution >= 1:
        return min_digits
    digits = int(math.ceil(-math.log10(resolution))) + 1
    return min(max(digits, min_digits), max_digits)


def _pad_decimal(label: str, digits: int) -> str:
    if "." not in label:
        return label + "." + ("0" * digits)
    after = len(label.split(".", maxsplit=1)[1])
    if after >= digits:
        return label
    return label + ("0" * (digits - after))
