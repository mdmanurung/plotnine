"""
Pairwise comparisons stat layer.

Performs pairwise statistical tests between groups and
displays the results as bracket annotations with p-values.
This is a Python port of ggpubr's geom_pwc/stat_pwc.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from plotnine.mapping.evaluation import after_stat
from plotnine.stats.stat import stat

from ._common import (
    add_wid_mapping,
    paired_values_by_wid,
    preserve_panel_columns,
    require_vertical_orientation,
)
from ._p_format import format_p_value, p_to_signif
from ._stat_test import run_stat_test


class stat_pwc(stat):
    """
    Add pairwise comparison p-values to a plot

    Performs pairwise statistical tests between groups and
    displays the results as bracket annotations. Supports
    t-test and Wilcoxon (Mann-Whitney U) tests. The default
    geom is ``geom_bracket``.

    {usage}

    Parameters
    ----------
    {common_parameters}
    method : str, default="wilcox.test"
        Statistical test method for pairwise comparisons.
        One of ``"t.test"`` or ``"wilcox.test"``.
    paired : bool, default=False
        Whether to perform a paired test.
    ref_group : str or int, default=None
        Reference group for pairwise comparisons. Each
        group is compared against this reference. If
        ``None``, all pairwise combinations are tested.
    comparisons : list of tuple, default=None
        Explicit list of group pairs to compare, e.g.
        ``[("A", "B"), ("A", "C")]``. Overrides
        ``ref_group`` when specified.
    p_adjust_method : str, default="holm"
        Method for adjusting p-values for multiple
        comparisons. One of ``"bonferroni"``, ``"holm"``,
        ``"hochberg"``, ``"hommel"``, ``"BH"``, ``"BY"``,
        ``"fdr"``, ``"none"``.
    label : str, default="p.format"
        Label format. One of ``"p.format"``,
        ``"p.signif"``, ``"p.adj.format"``,
        ``"p.adj.signif"``, ``"p.format.signif"``,
        ``"p.adj.format.signif"``.
    hide_ns : bool, default=False
        If ``True``, hide non-significant comparisons.
    p_digits : int, default=3
        Number of digits for p-value formatting.
    step_increase : float, default=0.12
        Fraction of y-range to step between comparison
        brackets to minimize overlap.
    bracket_nudge_y : float, default=0.05
        Vertical offset for brackets as a fraction of
        the y-range.
    tip_length : float, default=0.03
        Length of bracket tips as a fraction of y-range,
        passed to ``geom_bracket``.
    bracket_shorten : float, default=0
        Amount to shorten brackets from each end.
    remove_bracket : bool, default=False
        If ``True``, remove brackets and only show labels
        (uses ``geom_text`` instead of ``geom_bracket``).

    See Also
    --------
    plotnine_extra.geom_bracket : The default `geom` for
        this `stat`.
    plotnine_extra.stat_compare_means : Mean comparison
        with support for global tests.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "label"      # Formatted test result label
    "xmin"       # Left x-coordinate of bracket
    "xmax"       # Right x-coordinate of bracket
    "y"          # Y-coordinate of bracket
    "p"          # Raw p-value
    "p_adj"      # Adjusted p-value
    "p_signif"   # Significance symbol (raw p)
    "p_adj_signif" # Significance symbol (adjusted p)
    "method"     # Name of the test
    "group1"     # First group in comparison
    "group2"     # Second group in comparison
    ```

    """
    REQUIRED_AES = {"x", "y"}
    DEFAULT_AES = {"label": after_stat("label"), "wid": None}
    DEFAULT_PARAMS = {
        "geom": "bracket",
        "position": "identity",
        "na_rm": False,
        "method": "wilcox.test",
        "paired": False,
        "ref_group": None,
        "comparisons": None,
        "p_adjust_method": "holm",
        "label": "p.format",
        "hide_ns": False,
        "p_digits": 3,
        "step_increase": 0.12,
        "bracket_nudge_y": 0.05,
        "tip_length": 0.03,
        "bracket_shorten": 0,
        "remove_bracket": False,
        "wid": None,
    }
    CREATES = {
        "label",
        "xmin",
        "xmax",
        "y",
        "p",
        "p_adj",
        "p_signif",
        "p_adj_signif",
        "method",
        "group1",
        "group2",
    }

    def __init__(self, mapping=None, data=None, **kwargs):
        if kwargs.get("remove_bracket") and "geom" not in kwargs:
            kwargs["geom"] = "text"
        wid = kwargs.get("wid")
        mapping = add_wid_mapping(mapping, kwargs)
        if wid is not None:
            kwargs = kwargs.copy()
            kwargs.pop("wid", None)
        super().__init__(mapping, data, **kwargs)
        self.params["wid"] = wid
        # Remove 'label' from _kwargs so it is not forwarded
        # to the geom as a static aesthetic value. The 'label'
        # kwarg is a stat parameter controlling format (e.g.
        # "p.signif"), not a literal label string.
        self._kwargs.pop("label", None)

    def compute_panel(self, data, scales):
        require_vertical_orientation(data, "stat_pwc")
        method = self.params["method"]
        paired = self.params["paired"]
        wid = self.params.get("wid")
        ref_group = self.params["ref_group"]
        comparisons_param = self.params["comparisons"]
        p_adjust_method = self.params["p_adjust_method"]
        label_type = self.params["label"]
        hide_ns = self.params["hide_ns"]
        p_digits = self.params["p_digits"]
        step_increase = self.params["step_increase"]
        bracket_nudge_y = self.params["bracket_nudge_y"]
        bracket_shorten = self.params["bracket_shorten"]

        # Group data by x categories
        grouped = dict(list(data.groupby("x")))
        group_names = sorted(grouped.keys())

        if len(group_names) < 2:
            return pd.DataFrame()

        # Build mapping from original labels to numeric
        # x values if using a discrete scale
        label_to_num = {}
        if hasattr(scales, "x"):
            try:
                # For discrete scales, get the original
                # labels via final_limits or get_labels
                labels = None
                if hasattr(scales.x, "final_limits"):
                    fl = scales.x.final_limits
                    if fl and isinstance(fl[0], str):
                        labels = fl
                if labels is None and hasattr(scales.x, "get_labels"):
                    gl = scales.x.get_labels()
                    if gl and isinstance(gl[0], str):
                        labels = gl
                if labels:
                    for i, lbl in enumerate(labels):
                        num_val = float(i + 1)
                        if num_val in grouped:
                            label_to_num[lbl] = num_val
            except Exception:
                pass

        if not label_to_num:
            for name in group_names:
                label_to_num[name] = name

        # Build reverse mapping for display labels
        num_to_label = {v: k for k, v in label_to_num.items()}

        # Determine what comparisons to make
        if comparisons_param is not None:
            pairs = []
            for g1, g2 in comparisons_param:
                k1 = label_to_num.get(g1, g1)
                k2 = label_to_num.get(g2, g2)
                pairs.append((k1, k2))
        elif ref_group is not None:
            ref_key = label_to_num.get(ref_group, ref_group)
            pairs = [(ref_key, g) for g in group_names if g != ref_key]
        else:
            # All pairwise combinations
            pairs = list(combinations(group_names, 2))

        if not pairs:
            return pd.DataFrame()

        # Run pairwise tests
        y_max = data["y"].max()
        y_range = data["y"].max() - data["y"].min()
        if y_range == 0:
            y_range = abs(y_max) if y_max != 0 else 1.0

        raw_results = []
        for g1, g2 in pairs:
            if g1 not in grouped or g2 not in grouped:
                continue

            if paired:
                group1_vals, group2_vals = paired_values_by_wid(
                    data,
                    g1,
                    g2,
                    wid,
                )
            else:
                group1_vals = grouped[g1]["y"].to_numpy(dtype=float)
                group2_vals = grouped[g2]["y"].to_numpy(dtype=float)

            result = run_stat_test(
                [group1_vals, group2_vals],
                method=method,
                paired=paired,
            )

            raw_results.append(
                {
                    "g1": g1,
                    "g2": g2,
                    "p": result.p_value,
                    "method_name": result.method,
                }
            )

        if not raw_results:
            return pd.DataFrame()

        # Apply p-value adjustment
        raw_p_values = np.array([r["p"] for r in raw_results])
        adjusted_p_values = _adjust_pvalues(raw_p_values, p_adjust_method)

        # Build result rows
        results = []
        for i, raw in enumerate(raw_results):
            g1 = raw["g1"]
            g2 = raw["g2"]
            p_val = raw["p"]
            p_adj = adjusted_p_values[i]
            p_signif = p_to_signif(p_val)
            p_adj_signif = p_to_signif(p_adj)

            # Filter non-significant if requested
            if hide_ns:
                check_signif = (
                    p_adj_signif if "adj" in label_type else p_signif
                )
                if check_signif == "ns":
                    continue

            label = _make_pwc_label(
                label_type,
                p_val,
                p_adj,
                p_signif,
                p_adj_signif,
                p_digits,
            )

            # Position brackets
            x1 = float(g1)
            x2 = float(g2)
            xmin = min(x1, x2) + bracket_shorten
            xmax = max(x1, x2) - bracket_shorten
            y_pos = (
                y_max + y_range * bracket_nudge_y + y_range * step_increase * i
            )

            # Display labels for group1/group2
            g1_label = num_to_label.get(g1, str(g1))
            g2_label = num_to_label.get(g2, str(g2))

            results.append(
                {
                    "xmin": xmin,
                    "xmax": xmax,
                    "x": (xmin + xmax) / 2,
                    "y": y_pos,
                    "label": label,
                    "p": p_val,
                    "p_adj": p_adj,
                    "p_signif": p_signif,
                    "p_adj_signif": p_adj_signif,
                    "method": raw["method_name"],
                    "group1": g1_label,
                    "group2": g2_label,
                }
            )

        if not results:
            return pd.DataFrame()

        return preserve_panel_columns(pd.DataFrame(results), data)


def _make_pwc_label(
    label_type: str,
    p_val: float,
    p_adj: float,
    p_signif: str,
    p_adj_signif: str,
    p_digits: int,
) -> str:
    """Create label based on label type."""
    if label_type == "p.signif":
        return p_signif
    elif label_type == "p.adj.signif":
        return p_adj_signif
    elif label_type == "p.adj.format":
        return format_p_value(p_adj, digits=p_digits)
    elif label_type == "p.format.signif":
        p_str = format_p_value(p_val, digits=p_digits)
        return f"{p_str} ({p_signif})"
    elif label_type == "p.adj.format.signif":
        p_str = format_p_value(p_adj, digits=p_digits)
        return f"{p_str} ({p_adj_signif})"
    else:  # p.format (default)
        return format_p_value(p_val, digits=p_digits)


def _adjust_pvalues(
    p_values: np.ndarray,
    method: str,
) -> np.ndarray:
    """
    Adjust p-values for multiple comparisons.

    Parameters
    ----------
    p_values : array-like
        Raw p-values.
    method : str
        Adjustment method.

    Returns
    -------
    np.ndarray
        Adjusted p-values.
    """
    p = np.asarray(p_values, dtype=float)
    n = len(p)
    method_key = method.lower()
    if n <= 1 or method_key == "none":
        return p.copy()

    if method_key == "bonferroni":
        return np.minimum(p * n, 1.0)

    elif method_key == "holm":
        order = np.argsort(p)
        sorted_p = p[order]
        adjusted = np.empty(n)
        for i in range(n):
            adjusted[i] = sorted_p[i] * (n - i)
        # Enforce monotonicity
        for i in range(1, n):
            adjusted[i] = max(adjusted[i], adjusted[i - 1])
        adjusted = np.minimum(adjusted, 1.0)
        result = np.empty(n)
        result[order] = adjusted
        return result

    elif method_key == "hochberg":
        order = np.argsort(p)[::-1]
        sorted_p = p[order]
        adjusted = np.empty(n)
        for i in range(n):
            adjusted[i] = sorted_p[i] * (i + 1)
        # Enforce monotonicity (decreasing)
        for i in range(1, n):
            adjusted[i] = min(adjusted[i], adjusted[i - 1])
        adjusted = np.minimum(adjusted, 1.0)
        result = np.empty(n)
        result[order] = adjusted
        return result

    elif method_key in ("bh", "fdr"):
        order = np.argsort(p)[::-1]
        sorted_p = p[order]
        adjusted = np.empty(n)
        for i in range(n):
            rank = n - i  # rank from largest to smallest
            adjusted[i] = sorted_p[i] * n / rank
        # Enforce monotonicity (non-increasing after sort)
        for i in range(1, n):
            adjusted[i] = min(adjusted[i], adjusted[i - 1])
        adjusted = np.minimum(adjusted, 1.0)
        result = np.empty(n)
        result[order] = adjusted
        return result

    elif method_key == "by":
        order = np.argsort(p)[::-1]
        sorted_p = p[order]
        q = sum(1.0 / i for i in range(1, n + 1))
        adjusted = np.empty(n)
        for i in range(n):
            rank = n - i
            adjusted[i] = sorted_p[i] * n * q / rank
        for i in range(1, n):
            adjusted[i] = min(adjusted[i], adjusted[i - 1])
        adjusted = np.minimum(adjusted, 1.0)
        result = np.empty(n)
        result[order] = adjusted
        return result

    elif method_key == "hommel":
        order = np.argsort(p)
        sorted_p = p[order]
        adjusted = sorted_p.copy()
        for m in range(n, 1, -1):
            cim = np.min(m * sorted_p[-m:] / np.arange(1, m + 1))
            adjusted[-m:] = np.maximum(adjusted[-m:], cim)
            adjusted[:-m] = np.maximum(
                adjusted[:-m],
                np.minimum(m * sorted_p[:-m], cim),
            )
        adjusted = np.minimum(adjusted, 1.0)
        result = np.empty(n)
        result[order] = adjusted
        return result

    else:
        raise ValueError(f"Unknown p_adjust_method: {method}")
