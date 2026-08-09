"""
High-level plot constructors.

The functions in this module provide a compact, Pythonic subset of common
ggpubr- and plotthis-style plotting helpers. They return ordinary plotnine
``ggplot`` objects so callers can keep adding layers, scales, facets, and
themes with normal plotnine syntax.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd
from plotnine import (
    aes,
    geom_abline,
    geom_bar,
    geom_boxplot,
    geom_col,
    geom_density,
    geom_histogram,
    geom_hline,
    geom_jitter,
    geom_line,
    geom_path,
    geom_point,
    geom_smooth,
    geom_violin,
    geom_vline,
    ggplot,
    labs,
    scale_color_gradient,
)
from scipy.integrate import trapezoid

from plotnine_extra.geoms import geom_quasirandom, geom_text_repel

AddLayer = Literal["none", "jitter", "boxplot", "mean", "reg.line"]


def _base_mapping(
    x: str | None = None,
    y: str | None = None,
    *,
    color: str | None = None,
    fill: str | None = None,
    group: str | None = None,
    shape: str | None = None,
):
    values = {}
    if x is not None:
        values["x"] = x
    if y is not None:
        values["y"] = y
    if color is not None:
        values["color"] = color
    if fill is not None:
        values["fill"] = fill
    if group is not None:
        values["group"] = group
    if shape is not None:
        values["shape"] = shape
    return aes(**values)


def _as_list(value: str | list[str] | tuple[str, ...] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def _add_point_layer(
    plot: ggplot,
    add: str | None,
    *,
    size: float,
    alpha: float,
) -> ggplot:
    if add is None or add == "none":
        return plot
    if add == "jitter":
        return plot + geom_jitter(width=0.15, size=size, alpha=alpha)
    if add == "quasirandom":
        return plot + geom_quasirandom(size=size, alpha=alpha)
    if add == "boxplot":
        return plot + geom_boxplot(width=0.15, alpha=0.35)
    if add == "reg.line":
        return plot + geom_smooth(method="lm", se=False)
    msg = f"Unsupported add layer: {add!r}"
    raise ValueError(msg)


def ggboxplot(
    data: pd.DataFrame,
    x: str,
    y: str,
    *,
    color: str | None = None,
    fill: str | None = None,
    add: Literal["none", "jitter", "quasirandom"] = "none",
    width: float = 0.75,
    outlier_shape: str | None = None,
    size: float = 1.8,
    alpha: float = 0.8,
) -> ggplot:
    """Create a grouped boxplot.

    Parameters are intentionally small: map ``x`` and ``y``, optionally map
    ``color``/``fill``, and add light point overlays with ``add``.
    """
    plot = ggplot(data, _base_mapping(x, y, color=color, fill=fill))
    plot += geom_boxplot(width=width, outlier_shape=outlier_shape)
    return _add_point_layer(plot, add, size=size, alpha=alpha)


def ggviolin(
    data: pd.DataFrame,
    x: str,
    y: str,
    *,
    color: str | None = None,
    fill: str | None = None,
    add: Literal["none", "boxplot", "jitter", "quasirandom"] = "none",
    trim: bool = True,
    width: float = 0.9,
    size: float = 1.8,
    alpha: float = 0.8,
) -> ggplot:
    """Create a grouped violin plot with optional boxplot or point overlay."""
    plot = ggplot(data, _base_mapping(x, y, color=color, fill=fill))
    plot += geom_violin(trim=trim, width=width, alpha=alpha)
    return _add_point_layer(plot, add, size=size, alpha=alpha)


def ggscatter(
    data: pd.DataFrame,
    x: str,
    y: str,
    *,
    color: str | None = None,
    fill: str | None = None,
    shape: str | None = None,
    add: Literal["none", "reg.line"] = "none",
    size: float = 2.0,
    alpha: float = 0.85,
) -> ggplot:
    """Create a scatter plot, optionally adding a linear trend line."""
    mapping = _base_mapping(x, y, color=color, fill=fill, shape=shape)
    plot = ggplot(data, mapping) + geom_point(size=size, alpha=alpha)
    return _add_point_layer(plot, add, size=size, alpha=alpha)


def gghistogram(
    data: pd.DataFrame,
    x: str,
    *,
    fill: str | None = None,
    color: str | None = None,
    bins: int | None = None,
    binwidth: float | None = None,
    alpha: float = 0.85,
) -> ggplot:
    """Create a histogram for one numeric column."""
    kwargs = {"alpha": alpha}
    if bins is not None:
        kwargs["bins"] = bins
    if binwidth is not None:
        kwargs["binwidth"] = binwidth
    return ggplot(data, _base_mapping(x, color=color, fill=fill)) + (
        geom_histogram(**kwargs)
    )


def ggdensity(
    data: pd.DataFrame,
    x: str,
    *,
    color: str | None = None,
    fill: str | None = None,
    alpha: float = 0.35,
    adjust: float = 1,
) -> ggplot:
    """Create a kernel density plot for one numeric column."""
    return ggplot(data, _base_mapping(x, color=color, fill=fill)) + (
        geom_density(alpha=alpha, adjust=adjust)
    )


def ggbarplot(
    data: pd.DataFrame,
    x: str,
    y: str | None = None,
    *,
    color: str | None = None,
    fill: str | None = None,
    stat: Literal["identity", "summary", "count"] = "identity",
    fun: str = "mean",
    width: float = 0.75,
) -> ggplot:
    """Create a bar plot.

    Use ``stat="identity"`` with a precomputed ``y`` column,
    ``stat="summary"`` to aggregate ``y`` by ``x``, or ``stat="count"`` for
    counts. Summary aggregation currently supports ``mean``, ``median``, and
    ``sum``.
    """
    if stat == "count":
        return ggplot(data, _base_mapping(x, color=color, fill=fill)) + (
            geom_bar(width=width)
        )
    if y is None:
        msg = "y is required unless stat='count'"
        raise ValueError(msg)
    plot_data = data
    y_col = y
    if stat == "summary":
        group_cols = list(
            dict.fromkeys([x, *_as_list(color), *_as_list(fill)])
        )
        if fun not in {"mean", "median", "sum"}:
            msg = "fun must be one of 'mean', 'median', or 'sum'"
            raise ValueError(msg)
        grouped = data.groupby(group_cols, as_index=False, observed=True)[y]
        plot_data = getattr(grouped, fun)()
        y_col = y
    elif stat != "identity":
        msg = "stat must be 'identity', 'summary', or 'count'"
        raise ValueError(msg)
    mapping = _base_mapping(x, y_col, color=color, fill=fill)
    return ggplot(plot_data, mapping) + geom_col(width=width)


def ggline(
    data: pd.DataFrame,
    x: str,
    y: str,
    *,
    color: str | None = None,
    group: str | None = None,
    size: float = 0.8,
    points: bool = True,
) -> ggplot:
    """Create a line plot with optional points."""
    group = group or color
    plot = ggplot(data, _base_mapping(x, y, color=color, group=group))
    plot += geom_line(size=size)
    if points:
        plot += geom_point(size=2)
    return plot


def ggpaired(
    data: pd.DataFrame,
    x: str,
    y: str,
    *,
    id: str,
    color: str | None = None,
    line_color: str = "gray60",
    point_size: float = 2,
) -> ggplot:
    """Create a paired plot with observations connected by ``id``."""
    mapping = _base_mapping(x, y, color=color, group=id)
    plot = ggplot(data, mapping)
    plot += geom_line(color=line_color, alpha=0.7)
    plot += geom_point(size=point_size)
    return plot


def ggvolcano(
    data: pd.DataFrame,
    x: str = "log2fc",
    y: str = "pvalue",
    *,
    label: str | None = None,
    p_cutoff: float = 0.05,
    fc_cutoff: float = 1.0,
    label_top: int = 0,
    size: float = 1.8,
    alpha: float = 0.85,
) -> ggplot:
    """Create a volcano plot from log fold-change and p-value columns."""
    plot_data = data.copy()
    plot_data["_neg_log10_p"] = -np.log10(plot_data[y].clip(lower=1e-300))
    plot_data["_volcano_state"] = "not significant"
    sig = plot_data[y] <= p_cutoff
    plot_data.loc[sig & (plot_data[x] >= fc_cutoff), "_volcano_state"] = "up"
    plot_data.loc[sig & (plot_data[x] <= -fc_cutoff), "_volcano_state"] = (
        "down"
    )

    plot = (
        ggplot(plot_data, aes(x=x, y="_neg_log10_p", color="_volcano_state"))
        + geom_point(size=size, alpha=alpha)
        + geom_vline(xintercept=[-fc_cutoff, fc_cutoff], linetype="dashed")
        + geom_hline(yintercept=-np.log10(p_cutoff), linetype="dashed")
        + labs(y="-log10(pvalue)", color="state")
    )
    if label is not None and label_top > 0:
        label_data = plot_data.nsmallest(label_top, y)
        plot += geom_text_repel(
            aes(label=label),
            data=label_data,
            size=8,
            show_legend=False,
        )
    return plot


def ggdim(
    data: pd.DataFrame,
    x: str = "UMAP_1",
    y: str = "UMAP_2",
    *,
    color: str | None = None,
    size: float = 1.5,
    alpha: float = 0.9,
) -> ggplot:
    """Create an embedding scatter plot, such as UMAP or t-SNE."""
    return ggplot(data, _base_mapping(x, y, color=color)) + geom_point(
        size=size,
        alpha=alpha,
    )


def ggfeaturedim(
    data: pd.DataFrame,
    feature: str,
    x: str = "UMAP_1",
    y: str = "UMAP_2",
    *,
    low: str = "#d9d9d9",
    high: str = "#2166ac",
    size: float = 1.5,
    alpha: float = 0.9,
) -> ggplot:
    """Create an embedding plot colored by one numeric feature."""
    return (
        ggplot(data, aes(x=x, y=y, color=feature))
        + geom_point(size=size, alpha=alpha)
        + scale_color_gradient(low=low, high=high)
    )


def _roc_curve(
    data: pd.DataFrame,
    truth: str,
    score: str,
    *,
    positive: int | str | bool = 1,
) -> pd.DataFrame:
    values = data[[truth, score]].dropna().copy()
    y_true = (values[truth].to_numpy() == positive).astype(int)
    y_score = values[score].to_numpy(dtype=float)
    if y_true.sum() == 0 or y_true.sum() == len(y_true):
        msg = "truth must contain both positive and negative classes"
        raise ValueError(msg)

    order = np.argsort(-y_score, kind="mergesort")
    y_true = y_true[order]
    y_score = y_score[order]
    distinct = np.r_[True, y_score[1:] != y_score[:-1]]
    threshold_idxs = np.flatnonzero(distinct)

    tps = np.cumsum(y_true)[threshold_idxs]
    fps = (1 + threshold_idxs) - tps
    positives = y_true.sum()
    negatives = len(y_true) - positives
    tpr = np.r_[0, tps / positives, 1]
    fpr = np.r_[0, fps / negatives, 1]
    thresholds = np.r_[np.inf, y_score[threshold_idxs], -np.inf]
    roc_data = pd.DataFrame({"fpr": fpr, "tpr": tpr, "threshold": thresholds})
    roc_data.attrs["auc"] = float(trapezoid(roc_data["tpr"], roc_data["fpr"]))
    return roc_data


def ggroc(
    data: pd.DataFrame,
    truth: str,
    score: str,
    *,
    positive: int | str | bool = 1,
    label_auc: bool = True,
) -> ggplot:
    """Create a ROC curve and store the computed AUC in ``plot.data.attrs``."""
    roc_data = _roc_curve(data, truth, score, positive=positive)
    auc = roc_data.attrs["auc"]
    label = f"ROC curve (AUC = {auc:.3f})" if label_auc else "ROC curve"
    return (
        ggplot(roc_data, aes("fpr", "tpr"))
        + geom_path()
        + geom_abline(slope=1, intercept=0, linetype="dashed")
        + labs(x="False positive rate", y="True positive rate", color=label)
    )


VolcanoPlot = ggvolcano
DimPlot = ggdim
FeatureDimPlot = ggfeaturedim
ROCCurve = ggroc

__all__ = (
    "DimPlot",
    "FeatureDimPlot",
    "ROCCurve",
    "VolcanoPlot",
    "ggbarplot",
    "ggboxplot",
    "ggdensity",
    "ggdim",
    "ggfeaturedim",
    "gghistogram",
    "ggline",
    "ggpaired",
    "ggroc",
    "ggscatter",
    "ggviolin",
    "ggvolcano",
)
