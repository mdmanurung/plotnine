"""
Manually add p-value annotations with brackets.

Unlike other stat_ layers which are ggproto stat objects,
this is a function that returns a list of plotnine layers
for adding pre-computed p-value annotations to a plot.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from plotnine import aes, geom_segment, geom_text

from ._p_format import format_p_value, p_to_signif


def stat_pvalue_manual(
    data: pd.DataFrame,
    label: str | None = None,
    y_position: str | float | None = None,
    xmin: str | None = "group1",
    xmax: str | None = "group2",
    tip_length: float = 0.02,
    step_increase: float = 0.05,
    step_group_by: str | None = None,
    hide_ns: bool = False,
    remove_bracket: bool = False,
    bracket_nudge_y: float = 0,
    label_size: float = 8,
    vjust: float = -0.5,
    color: str = "black",
    x_levels: list | tuple | None = None,
    **kwargs: Any,
) -> list:
    """
    Add manually specified p-values to a plot with brackets.

    Parameters
    ----------
    data : DataFrame
        Data frame containing at minimum columns for group
        positions and p-values. Expected columns include
        ``group1``, ``group2``, and ``p`` or ``p.adj``.
    label : str, optional
        Column name to use for the label, or ``"p.signif"``
        to auto-convert p-values to significance symbols.
        If ``None``, uses ``"p"`` column formatted.
    y_position : str or float, optional
        Column name for y-coordinates of brackets, or a
        single float value. If ``None``, uses
        ``"y.position"`` or ``"y_position"`` column.
    xmin : str, default="group1"
        Column name for the left x-coordinate of brackets.
    xmax : str, default="group2"
        Column name for the right x-coordinate of brackets.
    tip_length : float, default=0.02
        Length of bracket tips as fraction of y range.
    step_increase : float, default=0.05
        Step increase between brackets as fraction of y
        range.
    step_group_by : str, optional
        Column to group comparisons for stacking.
    hide_ns : bool, default=False
        If ``True``, hide non-significant results.
    remove_bracket : bool, default=False
        If ``True``, show only labels without brackets.
    bracket_nudge_y : float, default=0
        Vertical nudge for brackets.
    label_size : float, default=8
        Font size for labels.
    vjust : float, default=-0.5
        Vertical justification of labels.
    color : str, default="black"
        Color for brackets and labels.
    **kwargs
        Additional aesthetic parameters.

    Returns
    -------
    list
        List of plotnine layers (geom_segment + geom_text)
        that can be added to a ggplot.
    """
    df = data.copy()

    # Resolve label column
    if label == "p.signif":
        p_col = _find_p_column(df)
        df["_label"] = df[p_col].apply(p_to_signif)
    elif label is not None and label in df.columns:
        df["_label"] = df[label].astype(str)
    elif label is not None:
        df["_label"] = label
    else:
        p_col = _find_p_column(df)
        df["_label"] = df[p_col].apply(format_p_value)

    # Resolve y_position
    if isinstance(y_position, (int, float)):
        df["_y_pos"] = float(y_position)
    elif isinstance(y_position, str) and y_position in df.columns:
        df["_y_pos"] = df[y_position].astype(float)
    else:
        # Try common column names
        for col in ("y.position", "y_position"):
            if col in df.columns:
                df["_y_pos"] = df[col].astype(float)
                break
        else:
            raise ValueError(
                "y_position must be specified or data must "
                "contain a 'y.position' or 'y_position' "
                "column"
            )

    # Resolve xmin/xmax
    if xmin and xmin in df.columns:
        xmin_values = df[xmin]
    else:
        raise ValueError(f"Column '{xmin}' not found in data")

    if xmax and xmax in df.columns:
        xmax_values = df[xmax]
    else:
        raise ValueError(f"Column '{xmax}' not found in data")
    df["_xmin"], df["_xmax"] = _map_x_positions(
        xmin_values,
        xmax_values,
        x_levels,
    )

    # Filter non-significant if requested
    if hide_ns:
        p_col = _find_p_column(df)
        df = df[df[p_col] <= 0.05]

    if df.empty:
        return []

    # Apply step increase for stacking
    df = df.reset_index(drop=True)
    y_max = df["_y_pos"].max()
    if step_group_by and step_group_by in df.columns:
        groups = df.groupby(step_group_by)
        for _, group_df in groups:
            for i, idx in enumerate(group_df.index):
                df.loc[idx, "_y_pos"] += step_increase * i * y_max
    else:
        steps = np.arange(len(df)) * step_increase * y_max
        df["_y_pos"] += steps

    df["_y_pos"] += bracket_nudge_y

    layers = []

    if not remove_bracket:
        # Horizontal bars
        bracket_data = pd.DataFrame(
            {
                "x": df["_xmin"],
                "xend": df["_xmax"],
                "y": df["_y_pos"],
                "yend": df["_y_pos"],
            }
        )
        layers.append(
            geom_segment(
                data=bracket_data,
                mapping=aes(x="x", xend="xend", y="y", yend="yend"),
                inherit_aes=False,
                color=color,
                **kwargs,
            )
        )

        # Left tips
        y_range = df["_y_pos"].max() - df["_y_pos"].min()
        if y_range == 0:
            y_range = df["_y_pos"].max()
        tip = tip_length * y_range if y_range > 0 else 0.1

        left_tips = pd.DataFrame(
            {
                "x": df["_xmin"],
                "xend": df["_xmin"],
                "y": df["_y_pos"],
                "yend": df["_y_pos"] - tip,
            }
        )
        layers.append(
            geom_segment(
                data=left_tips,
                mapping=aes(x="x", xend="xend", y="y", yend="yend"),
                inherit_aes=False,
                color=color,
                **kwargs,
            )
        )

        # Right tips
        right_tips = pd.DataFrame(
            {
                "x": df["_xmax"],
                "xend": df["_xmax"],
                "y": df["_y_pos"],
                "yend": df["_y_pos"] - tip,
            }
        )
        layers.append(
            geom_segment(
                data=right_tips,
                mapping=aes(x="x", xend="xend", y="y", yend="yend"),
                inherit_aes=False,
                color=color,
                **kwargs,
            )
        )

    # Labels
    label_data = pd.DataFrame(
        {
            "x": (df["_xmin"] + df["_xmax"]) / 2,
            "y": df["_y_pos"],
            "label": df["_label"],
        }
    )
    layers.append(
        geom_text(
            data=label_data,
            mapping=aes(x="x", y="y", label="label"),
            inherit_aes=False,
            size=label_size,
            va="bottom",
            nudge_y=vjust,
            color=color,
        )
    )

    return layers


def _find_p_column(df: pd.DataFrame) -> str:
    """Find the p-value column in a DataFrame."""
    for col in ("p", "p.adj", "p_adj", "pvalue", "p_value"):
        if col in df.columns:
            return col
    raise ValueError(
        "No p-value column found. Expected one of: "
        "'p', 'p.adj', 'p_adj', 'pvalue', 'p_value'"
    )


def _map_x_positions(
    xmin_values: pd.Series,
    xmax_values: pd.Series,
    x_levels: list | tuple | None,
) -> tuple[pd.Series, pd.Series]:
    """Map string group labels to numeric plot positions."""
    if (
        pd.api.types.is_numeric_dtype(xmin_values)
        and pd.api.types.is_numeric_dtype(xmax_values)
        and x_levels is None
    ):
        return xmin_values.astype(float), xmax_values.astype(float)

    if x_levels is None:
        levels = []
        for value in pd.concat([xmin_values, xmax_values], ignore_index=True):
            if value not in levels:
                levels.append(value)
    else:
        levels = list(x_levels)

    lookup = {value: i + 1.0 for i, value in enumerate(levels)}
    missing = (set(xmin_values) | set(xmax_values)) - set(lookup)
    if missing:
        raise ValueError(f"x_levels missing groups: {sorted(missing)!r}")

    return xmin_values.map(lookup), xmax_values.map(lookup)
