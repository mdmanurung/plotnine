"""
ggpubr-style workflow helpers.

These functions provide small compatibility wrappers for common ggpubr
workflows while keeping the implementation on top of plotnine-extra's
existing stats and composition primitives.
"""

from __future__ import annotations

from copy import deepcopy
from itertools import combinations
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from matplotlib.legend import Legend

from plotnine_extra.composition import (
    Compose,
    Wrap,
    plot_annotation,
    plot_layout,
)
from plotnine_extra.geoms import geom_bracket as stat_bracket
from plotnine_extra.stats._common import paired_values_by_wid
from plotnine_extra.stats._p_format import format_p_value, p_to_signif
from plotnine_extra.stats._stat_test import run_stat_test
from plotnine_extra.stats.stat_pwc import _adjust_pvalues

__all__ = (
    "annotate_figure",
    "compare_means",
    "get_breaks",
    "get_legend",
    "ggarrange",
    "stat_bracket",
)

if TYPE_CHECKING:
    from typing import Any, Hashable, Iterable, Literal, Sequence

    from matplotlib.artist import Artist
    from plotnine.ggplot import ggplot


def compare_means(
    formula: str,
    data: pd.DataFrame,
    *,
    method: str = "wilcox.test",
    paired: bool = False,
    comparisons: Sequence[tuple[Hashable, Hashable]] | None = None,
    ref_group: Hashable | None = None,
    p_adjust_method: str = "holm",
    p_digits: int = 3,
    wid: str | None = None,
) -> pd.DataFrame:
    """
    Compute ggpubr-style pairwise mean comparisons.

    Parameters
    ----------
    formula : str
        Simple formula of the form ``"response ~ group"``.
    data : DataFrame
        Source data.
    method : str
        Test method accepted by :func:`run_stat_test`, usually
        ``"wilcox.test"`` or ``"t.test"``.
    paired : bool
        Whether comparisons are paired. Paired tests require ``wid``.
    comparisons : sequence of tuple, optional
        Explicit group pairs. If omitted, all pairwise combinations are used,
        unless ``ref_group`` is supplied.
    ref_group : hashable, optional
        Reference group compared against all other groups.
    p_adjust_method : str
        Adjustment method accepted by ``stat_pwc`` internals.
    p_digits : int
        Digits used for p-value formatting.
    wid : str, optional
        Subject id column for paired tests.
    """
    response, group = _parse_formula(formula)
    missing = [col for col in (response, group) if col not in data.columns]
    if missing:
        msg = f"compare_means missing columns: {missing}"
        raise ValueError(msg)

    test_data = (
        data.loc[:, [c for c in (response, group, wid) if c is not None]]
        .dropna(subset=[response, group])
        .rename(columns={response: ".value.", group: ".group."})
    )
    groups = sorted(test_data[".group."].dropna().unique().tolist())
    if len(groups) < 2:
        raise ValueError("compare_means requires at least two groups")

    pairs = _comparison_pairs(groups, comparisons, ref_group)
    rows: list[dict[str, Any]] = []
    for group1, group2 in pairs:
        if paired:
            g1_values, g2_values = paired_values_by_wid(
                test_data,
                group1,
                group2,
                wid,
                group_col=".group.",
                value_col=".value.",
            )
        else:
            grouped = test_data.groupby(".group.", sort=False)
            g1_values = grouped.get_group(group1)[".value."].to_numpy(
                dtype=float
            )
            g2_values = grouped.get_group(group2)[".value."].to_numpy(
                dtype=float
            )

        result = run_stat_test(
            [g1_values, g2_values],
            method=method,
            paired=paired,
        )
        rows.append(
            {
                ".y.": response,
                "group1": group1,
                "group2": group2,
                "p": float(result.p_value),
                "method": result.method,
            }
        )

    out = pd.DataFrame(rows)
    p_values = out["p"].to_numpy(dtype=float)
    valid = ~np.isnan(p_values)
    adjusted = np.full(len(p_values), np.nan, dtype=float)
    adjusted[valid] = _adjust_pvalues(p_values[valid], p_adjust_method)
    out["p.adj"] = adjusted
    out["p.format"] = [
        format_p_value(p_value, digits=p_digits) for p_value in out["p"]
    ]
    out["p.signif"] = [p_to_signif(p_value) for p_value in out["p"]]
    return out.loc[
        :,
        [
            ".y.",
            "group1",
            "group2",
            "p",
            "p.adj",
            "p.format",
            "p.signif",
            "method",
        ],
    ]


def ggarrange(
    *plots: ggplot | Compose | Iterable[ggplot | Compose],
    nrow: int | None = None,
    ncol: int | None = None,
    widths: Sequence[float] | None = None,
    heights: Sequence[float] | None = None,
    byrow: bool | None = None,
) -> Compose:
    """
    Arrange plots with plotnine-extra's composition API.
    """
    items = _flatten_plots(plots)
    if not items:
        raise ValueError("ggarrange requires at least one plot")
    return Wrap(items) + plot_layout(
        nrow=nrow,
        ncol=ncol,
        widths=widths,
        heights=heights,
        byrow=byrow,
    )


def annotate_figure(
    figure: ggplot | Compose,
    *,
    top: str | None = None,
    bottom: str | None = None,
    left: str | None = None,
    right: str | None = None,
    title: str | None = None,
    subtitle: str | None = None,
    caption: str | None = None,
    footer: str | None = None,
    **kwargs: Any,
) -> Compose:
    """
    Add ggpubr-style figure annotations to a plot or composition.

    ``top`` maps to the composition title, ``bottom`` maps to the caption,
    and ``left``/``right`` are accepted for compatibility but are not exposed
    by the current composition annotation model.
    """
    if left is not None or right is not None:
        msg = (
            "annotate_figure does not support left/right annotations because "
            "plotnine-extra composition annotations expose title, subtitle, "
            "caption, and footer only"
        )
        raise NotImplementedError(msg)

    cmp = figure if isinstance(figure, Compose) else Wrap([figure])
    return cmp + plot_annotation(
        title=title if title is not None else top,
        subtitle=subtitle,
        caption=caption if caption is not None else bottom,
        footer=footer,
        **kwargs,
    )


def get_breaks(
    plot: ggplot,
    axis: Literal["x", "y"] = "x",
    *,
    panel: int = 0,
) -> list[Any]:
    """
    Extract trained axis breaks from a built plot.
    """
    if axis not in {"x", "y"}:
        raise ValueError("axis must be 'x' or 'y'")

    built = deepcopy(plot)
    built._build()
    layout = getattr(built, "layout", None)
    panel_params = getattr(layout, "panel_params", None)
    if panel_params is None:
        msg = "plotnine internals did not expose panel parameters"
        raise RuntimeError(msg)
    try:
        scale_view = getattr(panel_params[panel], axis)
    except (IndexError, AttributeError) as err:
        msg = f"plotnine internals did not expose {axis!r} breaks"
        raise RuntimeError(msg) from err
    breaks = getattr(scale_view, "breaks", None)
    if breaks is None:
        msg = f"plotnine internals did not expose {axis!r} breaks"
        raise RuntimeError(msg)
    return list(breaks)


def get_legend(plot: ggplot) -> Artist:
    """
    Return the legend artist from a drawn plot.

    Plotnine versions differ in how guide boxes are represented. This helper
    returns a normal Matplotlib ``Legend`` or plotnine's anchored guide box
    when either is exposed, otherwise it raises a clear error.
    """
    figure = plot.draw(show=False)
    if figure.legends:
        return figure.legends[0]

    for artist in figure.findobj():
        if isinstance(artist, Legend):
            return artist
        if type(artist).__name__ == "FlexibleAnchoredOffsetbox":
            return artist

    msg = "plotnine internals did not expose a legend artist"
    raise RuntimeError(msg)


def _parse_formula(formula: str) -> tuple[str, str]:
    parts = formula.split("~")
    if len(parts) != 2:
        raise ValueError("formula must be of the form 'response ~ group'")
    response, group = (part.strip() for part in parts)
    if not response or not group:
        raise ValueError("formula must be of the form 'response ~ group'")
    return response, group


def _comparison_pairs(
    groups: Sequence[Hashable],
    comparisons: Sequence[tuple[Hashable, Hashable]] | None,
    ref_group: Hashable | None,
) -> list[tuple[Hashable, Hashable]]:
    if comparisons is not None:
        return [(g1, g2) for g1, g2 in comparisons]
    if ref_group is not None:
        if ref_group not in groups:
            raise ValueError(f"ref_group {ref_group!r} not found")
        return [(ref_group, group) for group in groups if group != ref_group]
    return list(combinations(groups, 2))


def _flatten_plots(
    plots: tuple[ggplot | Compose | Iterable[ggplot | Compose], ...],
) -> list[ggplot | Compose]:
    if len(plots) == 1 and not _is_plot_like(plots[0]):
        return list(plots[0])
    return list(plots)


def _is_plot_like(obj: object) -> bool:
    return isinstance(obj, Compose) or (
        type(obj).__name__ == "ggplot"
        and obj.__class__.__module__.startswith("plotnine")
    )
