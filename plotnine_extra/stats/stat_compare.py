"""
``stat_compare``: group-mean comparison stat ported from
`HMU-WH/ggcompare <https://github.com/HMU-WH/ggcompare>`_.

Improves on ``ggsignif::geom_signif`` and
``ggpubr::stat_compare_means`` by:

1. Stable adaptation to faceting (per-panel detection of which
   x-positions actually contain data).
2. Layer-level p-value adjustment across panels (vs ggpubr's
   panel-only adjustment), toggled by ``panel_indep``.
3. Smoothly handling missing groupings inside individual
   panels.
4. Auto-selecting the test method: t-test / Wilcoxon for two
   groups, ANOVA / Kruskal-Wallis for more than two, switched
   by the ``parametric`` flag.

The default ``geom`` is :class:`geom_bracket`, so ``stat_compare``
can be added to any plot in one line::

    ggplot(mpg, aes("class", "displ"))
        + geom_boxplot()
        + stat_compare()
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from plotnine.doctools import document
from plotnine.mapping.evaluation import after_stat
from plotnine.stats.stat import stat
from scipy import stats as _sps

from ._common import (
    is_horizontal_orientation,
    preserve_panel_columns,
    require_vertical_orientation,
)
from .stat_pwc import _adjust_pvalues

if TYPE_CHECKING:
    from typing import Any, Callable


__all__ = ("stat_compare",)


# Methods accepted by the ``correction`` parameter, mirroring
# R's ``p.adjust.methods``. ``"none"`` and ``"BH"`` (= ``"fdr"``)
# are aliases for the same thing.
_VALID_CORRECTIONS = {
    "none",
    "bonferroni",
    "holm",
    "hochberg",
    "hommel",
    "BH",
    "fdr",
    "BY",
}


@document
class stat_compare(stat):
    """
    Add group-mean comparison brackets to a plot.

    {usage}

    Parameters
    ----------
    {common_parameters}
    nudge : float, default 0
        Vertical nudge of the bracket start position, as a
        fraction of the panel y-range.
    start : float, optional
        Bracket start (top) position. Defaults to the maximum
        of the panel y-range.
    breaks : sequence of float, optional
        Cutpoints for converting p-values to significance
        labels (e.g. ``[0, 0.001, 0.01, 0.05, 1]``).
    labels : sequence of str, optional
        Labels matching ``breaks``. Defaults to the
        ``"***"``/``"**"``/``"*"``/``"ns"`` family.
    cutoff : float, optional
        Hide labels with adjusted p-values above this value.
    method : callable, optional
        Custom test function. Must accept two 1-D arrays
        (``x``, ``y``) and return an object with a ``.pvalue``
        attribute (e.g. a scipy ``HypothesisResult``). When
        omitted, the test is selected automatically based on
        ``parametric`` and the number of groups.
    overall : bool, default False
        If True, compare each group on the axis against the
        combined remaining groups (each x against "the rest").
        Ignored when ``ref_group`` or ``comparisons`` is set.
    ref_group : str or int, optional
        Reference x-axis group; every other group is compared
        against this one.
    tip_length : float, default 0.02
        Bracket tip length as a fraction of the panel y-range.
    parametric : bool, default False
        If True, use parametric tests (t-test for 2 groups,
        one-way ANOVA for more). Otherwise use the
        non-parametric counterparts (Wilcoxon, Kruskal-Wallis).
    correction : str, default ``"none"``
        Multiple-testing correction method, one of
        ``"none"``, ``"bonferroni"``, ``"holm"``, ``"hochberg"``,
        ``"hommel"``, ``"BH"``/``"fdr"``, ``"BY"``.
    panel_indep : bool, default False
        If True, p-value correction is applied within each
        panel (matching ggpubr); otherwise it is applied at
        the layer level (across all panels).
    method_args : dict, optional
        Additional keyword arguments forwarded to the test
        function.
    comparisons : list of tuple, optional
        Explicit pairs of x-axis groups to compare, e.g.
        ``[("compact", "midsize"), ("pickup", "suv")]``.
    step_increase : float, default 0.1
        Vertical spacing between consecutive brackets, as a
        fraction of the panel y-range.

    See Also
    --------
    plotnine_extra.geoms.geom_bracket : default ``geom``.
    plotnine_extra.stats.stat_pwc : pairwise comparisons with
        manual configuration.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Computed variables**

    ```python
    "p"      # raw p-value
    "q"      # adjusted p-value
    "label"  # display label (depends on breaks/labels/cutoff)
    "method" # test method name
    "xmin"   # bracket left edge
    "xmax"   # bracket right edge
    "y"      # bracket top
    ```
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_AES = {"label": after_stat("label")}
    DEFAULT_PARAMS = {
        "geom": "bracket",
        "position": "identity",
        "na_rm": False,
        "nudge": 0,
        "start": None,
        "breaks": None,
        "labels": None,
        "cutoff": None,
        "method": None,
        "overall": False,
        "ref_group": None,
        "tip_length": 0.02,
        "parametric": False,
        "correction": "none",
        "panel_indep": False,
        "method_args": None,
        "comparisons": None,
        "step_increase": 0.1,
    }
    CREATES = {"p", "q", "label", "method", "xmin", "xmax", "y"}

    def __init__(self, mapping=None, data=None, **kwargs):
        super().__init__(mapping, data, **kwargs)
        # ``label`` here is the *aesthetic* mapping; we should
        # not forward it to the geom as a literal value.
        self._kwargs.pop("label", None)

    # ------------------------------------------------------
    # compute_panel: detect mode + run tests
    # ------------------------------------------------------
    def compute_panel(self, data, scales) -> pd.DataFrame:
        params = self.params
        correction = params["correction"]
        if correction not in _VALID_CORRECTIONS:
            raise ValueError(
                f"correction must be one of "
                f"{sorted(_VALID_CORRECTIONS)}, got "
                f"{correction!r}"
            )

        if data.empty:
            return pd.DataFrame()

        # Horizontal-orientation guard. ggcompare's R version
        # swaps x/y via ``flip_data`` when the discrete axis is
        # on the y. plotnine 0.15/0.16 does not expose a clean
        # equivalent, so we detect the mismatch (continuous x +
        # discrete-looking y) and refuse rather than silently
        # producing wrong brackets.
        require_vertical_orientation(data, "stat_compare", scales)

        # Add a synthetic group column if missing
        if "group" not in data.columns:
            data = data.copy()
            data["group"] = data["x"]

        nudge = float(params["nudge"])
        start = params["start"]
        method = params["method"]
        overall = bool(params["overall"])
        ref_group = params["ref_group"]
        tip_length = float(params["tip_length"])
        parametric = bool(params["parametric"])
        method_args = params["method_args"] or {}
        comparisons = params["comparisons"]
        step_increase = float(params["step_increase"])

        # Determine y-scale range
        y_range = self._panel_y_range(data, scales)
        scale_range = float(y_range[1] - y_range[0])
        bracket_spacing = (
            0.0 if step_increase == 0 else scale_range * step_increase
        )
        if start is None:
            start = float(y_range[1] + nudge * scale_range)
        else:
            start = float(start)

        if ref_group is None and comparisons is None:
            result = self._compute_auto(
                data,
                scale_range=scale_range,
                start=start,
                tip_length=tip_length,
                bracket_spacing=bracket_spacing,
                overall=overall,
                method=method,
                method_args=method_args,
                parametric=parametric,
            )
        else:
            result = self._compute_explicit(
                data,
                scales=scales,
                scale_range=scale_range,
                start=start,
                tip_length=tip_length,
                bracket_spacing=bracket_spacing,
                ref_group=ref_group,
                comparisons=comparisons,
                method=method,
                method_args=method_args,
                parametric=parametric,
            )

        # Apply correction at the panel level. compute_layer will
        # re-adjust at the layer level when ``panel_indep`` is
        # False, mirroring ggcompare's two-stage logic so that
        # ``panel_indep=True`` actually returns corrected
        # p-values per panel.
        if not result.empty and "p" in result.columns:
            p_arr = result["p"].to_numpy(dtype=float)
            valid = ~np.isnan(p_arr)
            if valid.any():
                adj = _adjust_pvalues(p_arr[valid], correction)
                q = p_arr.copy()
                q[valid] = adj
                result = result.copy()
                result["q"] = q

        return preserve_panel_columns(result, data)

    # ------------------------------------------------------
    # compute_layer: layer-level p-adjust + label formatting
    # ------------------------------------------------------
    def compute_layer(self, data, layout) -> pd.DataFrame:
        out = super().compute_layer(data, layout)
        if out is None or len(out) == 0:
            return out

        params = self.params
        correction = params.get("correction", "none")
        panel_indep = bool(params.get("panel_indep", False))

        # Layer-level adjustment across panels
        if not panel_indep:
            p_arr = out["p"].to_numpy(dtype=float)
            valid = ~np.isnan(p_arr)
            if valid.any():
                adj = _adjust_pvalues(p_arr[valid], correction)
                q = p_arr.copy()
                q[valid] = adj
                out = out.copy()
                out["q"] = q

        # Label formatting
        breaks = params.get("breaks")
        user_labels = params.get("labels")
        out = out.copy()
        out["label"] = _format_labels(
            out["q"].to_numpy(dtype=float),
            breaks=breaks,
            labels=user_labels,
        )

        # Hide labels above the cutoff and shift the remaining
        # brackets down by their ``space`` so the layout stays
        # tight (matches R ggcompare's compute_layer).
        cutoff = params.get("cutoff")
        if cutoff is not None:
            q_arr = out["q"].to_numpy(dtype=float)
            mask = q_arr > cutoff
            out.loc[mask, "label"] = ""
            if "PANEL" in out.columns and "space" in out.columns:
                out = _shift_hidden_brackets(out)

        # Drop rows where every test stat is NA
        keep = ~(out["p"].isna() & out["q"].isna() & out["method"].isna())
        out = out.loc[keep].reset_index(drop=True)

        # ``geom_bracket`` consumes y, not ymin/ymax. Set y to
        # the bracket top (the R version uses ymax).
        if "ymax" in out.columns:
            out["y"] = out["ymax"]
        return out

    # ------------------------------------------------------
    # Helpers
    # ------------------------------------------------------
    @staticmethod
    def _panel_y_range(data, scales) -> tuple[float, float]:
        if scales is not None:
            sy = getattr(scales, "y", None)
            if sy is not None:
                rng = getattr(sy, "range", None)
                rng_obj = getattr(rng, "range", None)
                if rng_obj is not None and len(rng_obj) == 2:
                    return float(rng_obj[0]), float(rng_obj[1])
                if rng is not None and hasattr(rng, "__len__"):
                    return float(rng[0]), float(rng[1])
        ys = data["y"].dropna().to_numpy(dtype=float)
        if ys.size == 0:
            return (0.0, 1.0)
        return (float(ys.min()), float(ys.max()))

    def _compute_auto(
        self,
        data: pd.DataFrame,
        *,
        scale_range: float,
        start: float,
        tip_length: float,
        bracket_spacing: float,
        overall: bool,
        method: "Callable | None",
        method_args: dict,
        parametric: bool,
    ) -> pd.DataFrame:
        """Auto-detect global / per-x / overall mode."""
        # Per-x group counts
        per_x_groups = data.groupby("x")["group"].nunique().reset_index()
        any_subgroups = (per_x_groups["group"] > 1).any()

        if overall:
            global_mode = False
            multiple = False
        elif any_subgroups:
            global_mode = False
            multiple = int(per_x_groups["group"].max()) > 2
        else:
            global_mode = True
            multiple = data["group"].nunique() > 2

        rows: list[dict[str, Any]] = []
        if global_mode:
            res = _run_test(
                data,
                multiple=multiple,
                parametric=parametric,
                method=method,
                method_args=method_args,
            )
            xmin = float(data["x"].min()) - 0.45
            xmax = float(data["x"].max()) + 0.45
            rows.append(
                {
                    **res,
                    "x": (xmin + xmax) / 2,
                    "xmin": xmin,
                    "xmax": xmax,
                    "ymin": start,
                    "ymax": start + tip_length * scale_range,
                    "space": 0.0,
                    "group": 0,
                }
            )
        elif overall:
            for xv in sorted(data["x"].unique()):
                subset = data.copy()
                subset["group"] = (subset["x"] == xv).astype(int)
                res = _run_test(
                    subset,
                    multiple=False,
                    parametric=parametric,
                    method=method,
                    method_args=method_args,
                )
                rows.append(
                    {
                        **res,
                        "x": float(xv),
                        "xmin": float(xv) - 0.45,
                        "xmax": float(xv) + 0.45,
                        "ymin": start,
                        "ymax": start,
                        "space": 0.0,
                        "group": float(xv),
                    }
                )
        else:
            for xv, sub in data.groupby("x"):
                res = _run_test(
                    sub,
                    multiple=multiple,
                    parametric=parametric,
                    method=method,
                    method_args=method_args,
                )
                rows.append(
                    {
                        **res,
                        "x": float(xv),
                        "xmin": float(xv) - 0.45,
                        "xmax": float(xv) + 0.45,
                        "ymin": start,
                        "ymax": start + tip_length * scale_range,
                        "space": 0.0,
                        "group": float(xv),
                    }
                )

        df = pd.DataFrame(rows)
        # ``q`` is set later by ``compute_panel`` after the
        # panel-level correction step.
        df["q"] = np.nan
        return df

    def _compute_explicit(
        self,
        data: pd.DataFrame,
        *,
        scales,
        scale_range: float,
        start: float,
        tip_length: float,
        bracket_spacing: float,
        ref_group,
        comparisons,
        method: "Callable | None",
        method_args: dict,
        parametric: bool,
    ) -> pd.DataFrame:
        """Build comparisons from ref_group / comparisons."""
        groups = sorted(data["x"].unique())
        if len(groups) <= 1:
            return pd.DataFrame()

        # Resolve string ref_group / comparisons via the x scale
        if comparisons is None:
            rg = _resolve_scale(scales, ref_group)
            if rg in groups:
                comparisons = [(g, rg) for g in groups if g != rg]
            else:
                return pd.DataFrame()
        else:
            comparisons = [
                tuple(_resolve_scale(scales, v) for v in pair)
                for pair in comparisons
            ]

        rows: list[dict[str, Any]] = []
        i = 0
        for comp in comparisons:
            a, b = comp
            x_a = data["y"][data["x"] == a].to_numpy(dtype=float)
            x_b = data["y"][data["x"] == b].to_numpy(dtype=float)
            res = _pair_test(
                x_a,
                x_b,
                parametric=parametric,
                method=method,
                method_args=method_args,
            )
            bracket_start = start + i * bracket_spacing
            annotation_start = bracket_start + tip_length * scale_range
            if not np.isnan(res["p"]):
                i += 1
            rows.append(
                {
                    **res,
                    "x": float(a),
                    "xmin": float(min(comp)),
                    "xmax": float(max(comp)),
                    "ymin": bracket_start,
                    "ymax": annotation_start,
                    "space": bracket_spacing,
                    "group": "-".join(str(v) for v in sorted(comp)),
                }
            )
        df = pd.DataFrame(rows)
        df["q"] = np.nan
        return df


# ------------------------------------------------------------
# Bracket layout helpers
# ------------------------------------------------------------


def _shift_hidden_brackets(data: pd.DataFrame) -> pd.DataFrame:
    """
    Shift visible brackets down to fill gaps left by hidden
    labels, mirroring ggcompare's compute_layer behaviour.

    For each panel, sort by ``ymin`` descending, walk the rows
    and for every row whose ``label`` is empty but whose ``p``
    is not NaN, subtract ``space`` from the ``ymin`` / ``ymax``
    of all rows up to and including that index. The original
    row order is restored before returning.
    """
    if "PANEL" not in data.columns:
        return data

    pieces: list[pd.DataFrame] = []
    for _, panel in data.groupby("PANEL"):
        panel = panel.copy()
        panel["_orig_idx"] = np.arange(len(panel))
        panel = panel.sort_values("ymin", ascending=False).reset_index(
            drop=True
        )
        labels = panel["label"].to_numpy()
        p_vals = panel["p"].to_numpy(dtype=float).copy()
        ymin = panel["ymin"].to_numpy(dtype=float).copy()
        ymax = panel["ymax"].to_numpy(dtype=float).copy()
        space = panel["space"].to_numpy(dtype=float).copy()
        for i in range(len(panel)):
            if labels[i] == "" and not np.isnan(p_vals[i]):
                # Shift this row and every row above it
                ymin[: i + 1] -= space[: i + 1]
                ymax[: i + 1] -= space[: i + 1]
        panel["ymin"] = ymin
        panel["ymax"] = ymax
        panel = panel.sort_values("_orig_idx").drop(columns="_orig_idx")
        pieces.append(panel)
    return pd.concat(pieces, ignore_index=True)


# ------------------------------------------------------------
# Orientation detection
# ------------------------------------------------------------


def _is_horizontal(data: pd.DataFrame) -> bool:
    """
    Heuristic detection of horizontal orientation.

    plotnine maps a discrete scale to integer codes ``1..N``
    (as floats) so a *vertical* boxplot has discrete-coded
    ``x`` (few unique integer-valued floats) and a continuous
    ``y``. A *horizontal* plot (``aes("displ", "class")``) has
    continuous ``x`` and discrete-coded ``y``.

    We flag the horizontal case when ``y`` looks discrete
    (few unique values, all integers) but ``x`` does not.
    """
    return is_horizontal_orientation(data)


# ------------------------------------------------------------
# Test runners
# ------------------------------------------------------------


def _run_test(
    data: pd.DataFrame,
    *,
    multiple: bool,
    parametric: bool,
    method,
    method_args: dict,
) -> dict:
    """Run the appropriate test on a dataframe with x, y, group."""
    try:
        if multiple:
            samples = [
                d["y"].dropna().to_numpy(dtype=float)
                for _, d in data.groupby("group")
                if d["y"].dropna().size > 0
            ]
            if len(samples) < 2:
                return {"p": np.nan, "method": None}
            if method is not None:
                res = method(*samples, **method_args)
                return {
                    "p": float(getattr(res, "pvalue", np.nan)),
                    "method": getattr(method, "__name__", "user method"),
                }
            if parametric:
                res = _sps.f_oneway(*samples)
                return {
                    "p": float(res.pvalue),
                    "method": "One-way ANOVA",
                }
            res = _sps.kruskal(*samples)
            return {
                "p": float(res.pvalue),
                "method": "Kruskal-Wallis rank sum test",
            }

        groups_sorted = sorted(data["group"].dropna().unique())
        if len(groups_sorted) < 2:
            return {"p": np.nan, "method": None}
        x = (
            data["y"][data["group"] == groups_sorted[0]]
            .dropna()
            .to_numpy(dtype=float)
        )
        y = (
            data["y"][data["group"] == groups_sorted[1]]
            .dropna()
            .to_numpy(dtype=float)
        )
        return _pair_test(
            x,
            y,
            parametric=parametric,
            method=method,
            method_args=method_args,
        )
    except Exception:  # noqa: BLE001
        return {"p": np.nan, "method": None}


def _pair_test(
    x: np.ndarray,
    y: np.ndarray,
    *,
    parametric: bool,
    method,
    method_args: dict,
) -> dict:
    """Run a two-sample test on x and y."""
    if x.size == 0 or y.size == 0:
        return {"p": np.nan, "method": None}
    try:
        if method is not None:
            res = method(x, y, **method_args)
            return {
                "p": float(getattr(res, "pvalue", np.nan)),
                "method": getattr(method, "__name__", "user method"),
            }
        if parametric:
            res = _sps.ttest_ind(x, y, equal_var=False)
            return {
                "p": float(res.pvalue),
                "method": "Welch Two Sample t-test",
            }
        res = _sps.mannwhitneyu(x, y, alternative="two-sided")
        return {
            "p": float(res.pvalue),
            "method": "Wilcoxon rank sum test",
        }
    except Exception:  # noqa: BLE001
        return {"p": np.nan, "method": None}


# ------------------------------------------------------------
# Label formatting
# ------------------------------------------------------------


def _format_labels(
    q_values: np.ndarray,
    *,
    breaks,
    labels,
) -> list[str]:
    eps = float(np.finfo(float).eps)
    if breaks is None:
        out = []
        for q in q_values:
            if np.isnan(q):
                out.append("")
            elif q < eps:
                out.append(f"p < {eps:.2e}")
            else:
                out.append(_format_g(q))
        return out

    breaks = list(breaks)
    if labels is None:
        n = len(breaks) - 1
        labels = ["*" * (n - 1 - i) for i in range(n - 1)] + ["ns"]
    if len(labels) != len(breaks) - 1:
        raise ValueError("labels must have one entry less than breaks")

    out = []
    for q in q_values:
        if np.isnan(q):
            out.append("")
            continue
        placed = False
        for i in range(len(breaks) - 1):
            lower = breaks[i]
            upper = breaks[i + 1]
            in_range = (
                (q > lower and q <= upper)
                if i > 0
                else (q >= lower and q <= upper)
            )
            if in_range:
                out.append(labels[i])
                placed = True
                break
        if not placed:
            out.append("")
    return out


def _format_g(value: float) -> str:
    """Mimic R's ``sprintf("%.2g", x)``."""
    if value == 0:
        return "0"
    return f"{value:.2g}"


# ------------------------------------------------------------
# Scale resolution
# ------------------------------------------------------------


def _resolve_scale(scales, value):
    """
    Map a discrete-scale value (e.g. ``"minivan"``) to its
    integer position. Numeric values are returned unchanged.
    """
    if value is None or isinstance(value, (int, float, np.integer)):
        try:
            return float(value)
        except (TypeError, ValueError):
            return value
    if scales is None:
        return value
    sx = getattr(scales, "x", None)
    if sx is None:
        return value
    # plotnine discrete scales expose ``map`` for label -> code
    try:
        mapped = sx.map(pd.Series([value]))
        if hasattr(mapped, "iloc"):
            return float(mapped.iloc[0])
        return float(mapped[0])
    except Exception:  # noqa: BLE001
        # Try the limits / breaks pathway
        try:
            limits = list(getattr(sx, "limits", []) or [])
            if value in limits:
                return float(limits.index(value) + 1)
        except Exception:  # noqa: BLE001
            pass
        return value
