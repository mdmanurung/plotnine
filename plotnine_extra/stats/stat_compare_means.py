from __future__ import annotations

import pandas as pd
from plotnine.mapping.evaluation import after_stat
from plotnine.stats.stat import stat

from ._common import (
    add_wid_mapping,
    drop_forwarded_kwarg,
    paired_values_by_wid,
    preserve_panel_columns,
    require_vertical_orientation,
)
from ._label_utils import compute_label_position
from ._p_format import format_p_value, p_to_signif
from ._stat_test import run_stat_test


class stat_compare_means(stat):
    """
    Add mean comparison p-values to a plot

    Performs statistical tests comparing groups and displays
    the results as text annotations. Supports t-test,
    Wilcoxon, ANOVA, and Kruskal-Wallis tests.

    {usage}

    Parameters
    ----------
    {common_parameters}
    method : str, default="wilcox.test"
        Statistical test method. One of ``"t.test"``,
        ``"wilcox.test"``, ``"anova"``, ``"kruskal.test"``.
    paired : bool, default=False
        Whether to perform a paired test.
    comparisons : list of tuple, default=None
        List of group pairs to compare, e.g.
        ``[("A", "B"), ("A", "C")]``. If ``None``, performs
        a global test across all groups.
    ref_group : str, default=None
        Reference group for pairwise comparisons. Each
        group is compared against this reference.
    hide_ns : bool, default=False
        If ``True``, hide non-significant results.
    label : str, default="p.format"
        Label format. One of ``"p.format"``,
        ``"p.signif"``, ``"p.format.signif"``.
    label_x_npc : float or str, default="center"
        Normalized x position for global test label.
    label_y_npc : float or str, default="top"
        Normalized y position for global test label.
    p_digits : int, default=3
        Number of digits for p-value formatting.
    step_increase : float, default=0.1
        Fraction of y-range to step between comparison
        brackets.

    See Also
    --------
    plotnine.geom_text : The default `geom` for this `stat`.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "label"    # Formatted test result label
    "p"        # P-value
    "p_signif" # Significance symbol
    "method"   # Name of the test
    ```

    """
    REQUIRED_AES = {"x", "y"}
    DEFAULT_AES = {"label": after_stat("label"), "wid": None}
    DEFAULT_PARAMS = {
        "geom": "text",
        "position": "identity",
        "na_rm": False,
        "method": "wilcox.test",
        "paired": False,
        "comparisons": None,
        "ref_group": None,
        "hide_ns": False,
        "label": "p.format",
        "label_x_npc": "center",
        "label_y_npc": "top",
        "p_digits": 3,
        "step_increase": 0.1,
        "wid": None,
    }
    CREATES = {"label", "p", "p_signif", "method"}

    def __init__(self, mapping=None, data=None, **kwargs):
        wid = kwargs.get("wid")
        mapping = add_wid_mapping(mapping, kwargs)
        if wid is not None:
            kwargs = kwargs.copy()
            kwargs.pop("wid", None)
        super().__init__(mapping, data, **kwargs)
        self.params["wid"] = wid
        # 'label' is a stat parameter controlling format (e.g.
        # "p.signif"), not a literal label string, so it must not
        # be forwarded to the geom as a static aesthetic value.
        drop_forwarded_kwarg(self, "label")

    def compute_panel(self, data, scales) -> pd.DataFrame:
        require_vertical_orientation(data, "stat_compare_means", scales)
        method = self.params["method"]
        paired = self.params["paired"]
        wid = self.params.get("wid")
        comparisons = self.params["comparisons"]
        ref_group = self.params["ref_group"]
        hide_ns = self.params["hide_ns"]
        label_type = self.params["label"]
        p_digits = self.params["p_digits"]
        step_increase = self.params["step_increase"]

        # Group data by x categories
        grouped = dict(list(data.groupby("x")))
        group_names = sorted(grouped.keys())

        if len(group_names) < 2:
            return pd.DataFrame()

        # Build mapping from original labels to numeric
        # x values if using a discrete scale
        label_to_num = {}
        if hasattr(scales, "x") and hasattr(scales.x, "range"):
            try:
                limits = scales.x.limits
                if limits and isinstance(limits[0], str):
                    for lbl in limits:
                        mapped = scales.x.map([lbl])
                        if len(mapped) > 0:
                            label_to_num[lbl] = mapped[0]
            except Exception:
                pass

        # If label_to_num is still empty, build it from
        # group_names directly (already numeric)
        if not label_to_num:
            for name in group_names:
                label_to_num[name] = name

        # Determine what comparisons to make
        if comparisons is not None:
            # Map string labels to numeric keys
            mapped_pairs = []
            for g1, g2 in comparisons:
                k1 = label_to_num.get(g1, g1)
                k2 = label_to_num.get(g2, g2)
                mapped_pairs.append((k1, k2))
            pairs = mapped_pairs
        elif ref_group is not None:
            ref_key = label_to_num.get(ref_group, ref_group)
            pairs = [(ref_key, g) for g in group_names if g != ref_key]
        else:
            # Global test
            return self._global_test(
                data,
                grouped,
                group_names,
                method,
                paired,
                wid,
            )

        # Pairwise comparisons
        return self._pairwise_test(
            data,
            grouped,
            pairs,
            method,
            paired,
            hide_ns,
            label_type,
            p_digits,
            step_increase,
            wid,
        )

    def _global_test(self, data, grouped, group_names, method, paired, wid):
        """Run a global test across all groups."""
        if paired:
            if len(group_names) != 2:
                msg = (
                    "paired global stat_compare_means tests are only "
                    "supported for exactly two groups; provide explicit "
                    "comparisons for pairwise paired tests"
                )
                raise NotImplementedError(msg)
            if method not in ("t.test", "wilcox.test"):
                msg = (
                    "paired global stat_compare_means only supports "
                    "'t.test' and 'wilcox.test'"
                )
                raise NotImplementedError(msg)
            groups = list(
                paired_values_by_wid(
                    data,
                    group_names[0],
                    group_names[1],
                    wid,
                )
            )
        else:
            groups = [
                grouped[g]["y"].to_numpy(dtype=float) for g in group_names
            ]

        # For 2 groups, use pairwise test method
        # For >2 groups, use ANOVA or Kruskal-Wallis
        if len(groups) > 2:
            if method in ("t.test", "wilcox.test"):
                global_method = (
                    "kruskal.test" if method == "wilcox.test" else "anova"
                )
            else:
                global_method = method
        else:
            global_method = method

        result = run_stat_test(groups, method=global_method, paired=paired)
        p_digits = self.params["p_digits"]
        p_signif = p_to_signif(result.p_value)

        label = self._make_label(result.p_value, p_signif, p_digits)

        x_pos = compute_label_position(
            data["x"].min(),
            data["x"].max(),
            self.params["label_x_npc"],
        )
        y_pos = compute_label_position(
            data["y"].min(),
            data["y"].max(),
            self.params["label_y_npc"],
        )

        return preserve_panel_columns(
            pd.DataFrame(
                {
                    "x": [x_pos],
                    "y": [y_pos],
                    "label": [label],
                    "p": [result.p_value],
                    "p_signif": [p_signif],
                    "method": [result.method],
                }
            ),
            data,
        )

    def _pairwise_test(
        self,
        data,
        grouped,
        pairs,
        method,
        paired,
        hide_ns,
        label_type,
        p_digits,
        step_increase,
        wid,
    ):
        """Run pairwise tests between specified pairs."""
        results = []
        y_max = data["y"].max()
        y_range = data["y"].max() - data["y"].min()

        for i, (g1, g2) in enumerate(pairs):
            if g1 not in grouped or g2 not in grouped:
                continue

            if paired:
                group1, group2 = paired_values_by_wid(data, g1, g2, wid)
            else:
                group1 = grouped[g1]["y"].to_numpy(dtype=float)
                group2 = grouped[g2]["y"].to_numpy(dtype=float)

            result = run_stat_test(
                [group1, group2],
                method=method,
                paired=paired,
            )

            p_signif = p_to_signif(result.p_value)

            if hide_ns and p_signif == "ns":
                continue

            label = self._make_label(result.p_value, p_signif, p_digits)

            # Position: midpoint between groups
            # Get x positions of groups
            x1 = grouped[g1]["x"].iloc[0]
            x2 = grouped[g2]["x"].iloc[0]
            x_mid = (x1 + x2) / 2
            y_pos = y_max + y_range * 0.05 + y_range * step_increase * i

            results.append(
                {
                    "x": x_mid,
                    "y": y_pos,
                    "label": label,
                    "p": result.p_value,
                    "p_signif": p_signif,
                    "method": result.method,
                }
            )

        if not results:
            return pd.DataFrame()

        return preserve_panel_columns(pd.DataFrame(results), data)

    def _make_label(self, p_value, p_signif, p_digits):
        """Create label based on label type."""
        label_type = self.params["label"]
        if label_type == "p.signif":
            return p_signif
        elif label_type == "p.format.signif":
            p_str = format_p_value(p_value, digits=p_digits)
            return f"{p_str} ({p_signif})"
        else:  # p.format
            return format_p_value(p_value, digits=p_digits)
