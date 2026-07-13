"""
Common helpers for stat layers.

Provides utilities for preserving panel/group columns
from the input data in compute_panel results.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from typing import Hashable


def preserve_panel_columns(
    result: pd.DataFrame,
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Ensure PANEL and group columns from input data
    are present in the result DataFrame.

    Parameters
    ----------
    result : DataFrame
        The computed result from compute_panel.
    data : DataFrame
        The input data to compute_panel.

    Returns
    -------
    DataFrame
        Result with PANEL and group columns preserved.
    """
    if result.empty:
        return result

    for col in ("PANEL", "group"):
        if col in data.columns and col not in result.columns:
            result[col] = data[col].iloc[0]

    return result


def add_wid_mapping(mapping, kwargs: dict):
    """
    Add ``aes(wid=...)`` when a stat receives a ``wid`` parameter.

    Plotnine drops columns that are neither mapped aesthetics nor needed by the
    layer. Repeated-measures stats accept ``wid`` as a parameter for API
    parity, so we internally map it to preserve the source column.
    """
    wid = kwargs.get("wid")
    if wid is None:
        return mapping

    from plotnine import aes

    if mapping is None:
        return aes(wid=wid)

    mapping = mapping.copy()
    mapping["wid"] = wid
    return mapping


def is_horizontal_orientation(
    data: pd.DataFrame,
    scales: object | None = None,
) -> bool:
    """
    Detect continuous-x/discrete-y horizontal stat orientation.

    Plotnine encodes discrete position scales as integer-valued floats. A
    vertical grouped plot therefore has discrete-looking ``x`` and continuous
    ``y``. The unsupported horizontal form has the reverse.
    """
    if "x" not in data.columns or "y" not in data.columns:
        return False

    if scales is not None:
        x_scale = getattr(scales, "x", None)
        y_scale = getattr(scales, "y", None)
        if x_scale is not None and y_scale is not None:
            return _is_continuous_scale(x_scale) and _is_discrete_scale(
                y_scale
            )

    x_vals = pd.to_numeric(data["x"], errors="coerce").dropna()
    y_vals = pd.to_numeric(data["y"], errors="coerce").dropna()
    if x_vals.empty or y_vals.empty:
        return False

    x_integer = _looks_integer_position(x_vals)
    y_integer = _looks_integer_position(y_vals)
    if not x_integer:
        return y_integer
    if not y_integer:
        return False

    x_unique_ratio = x_vals.nunique() / len(x_vals)
    y_unique_ratio = y_vals.nunique() / len(y_vals)
    return y_unique_ratio < x_unique_ratio


def require_vertical_orientation(
    data: pd.DataFrame,
    stat_name: str,
    scales: object | None = None,
) -> None:
    """Raise for unsupported horizontal orientation."""
    if is_horizontal_orientation(data, scales):
        msg = (
            f"{stat_name} does not yet support horizontal orientation "
            "(continuous x with discrete y). Put the discrete variable on "
            "the x-axis and add coord_flip() for a horizontal display."
        )
        raise NotImplementedError(msg)


def paired_values_by_wid(
    data: pd.DataFrame,
    group1: "Hashable",
    group2: "Hashable",
    wid: str | None,
    *,
    group_col: str = "x",
    value_col: str = "y",
) -> tuple[np.ndarray, np.ndarray]:
    """Return paired value arrays aligned by subject id."""
    if not wid:
        raise ValueError("paired tests require a wid column")
    wid_col = _resolve_wid_column(data, wid)

    subset = data[data[group_col].isin([group1, group2])]
    _validate_no_duplicate_subject_groups(subset, wid_col, group_col)
    wide = subset.pivot_table(
        index=wid_col,
        columns=group_col,
        values=value_col,
        aggfunc="first",
    )
    required = [group1, group2]
    if any(group not in wide.columns for group in required):
        raise ValueError("paired tests require complete paired observations")
    paired = wide.loc[:, required]
    if paired.isna().any().any():
        raise ValueError("paired tests require complete paired observations")
    return (
        paired[group1].to_numpy(dtype=float),
        paired[group2].to_numpy(dtype=float),
    )


def blocked_values_by_wid(
    data: pd.DataFrame,
    wid: str | None,
    *,
    group_col: str = "x",
    value_col: str = "y",
) -> list[np.ndarray]:
    """Return complete repeated-measures blocks for Friedman tests."""
    if not wid:
        raise ValueError("stat_friedman_test requires wid")
    wid_col = _resolve_wid_column(data, wid)
    _validate_no_duplicate_subject_groups(data, wid_col, group_col)

    group_order = sorted(data[group_col].dropna().unique())
    wide = data.pivot_table(
        index=wid_col,
        columns=group_col,
        values=value_col,
        aggfunc="first",
    )
    if any(group not in wide.columns for group in group_order):
        raise ValueError("Friedman test requires complete subject blocks")
    blocked = wide.loc[:, group_order]
    if blocked.isna().any().any():
        raise ValueError("Friedman test requires complete subject blocks")
    return [blocked[group].to_numpy(dtype=float) for group in group_order]


def _looks_integer_position(series: pd.Series) -> bool:
    arr = series.to_numpy(dtype=float)
    return np.allclose(arr, np.round(arr))


def _is_discrete_scale(scale: object) -> bool:
    return "discrete" in type(scale).__name__


def _is_continuous_scale(scale: object) -> bool:
    name = type(scale).__name__
    return "continuous" in name or bool(
        getattr(scale, "domain_is_numerical", False)
    )


def _resolve_wid_column(data: pd.DataFrame, wid: str) -> str:
    if wid in data.columns:
        return wid
    if "wid" in data.columns:
        return "wid"
    raise ValueError(f"wid column {wid!r} not found")


def _validate_no_duplicate_subject_groups(
    data: pd.DataFrame,
    wid: str,
    group_col: str,
) -> None:
    duplicates = data.duplicated([wid, group_col])
    if duplicates.any():
        raise ValueError("duplicate subject/group pairs are not allowed")
