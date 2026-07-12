from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from plotnine.doctools import document

from ._base_stat_test import _base_stat_test

if TYPE_CHECKING:
    from plotnine_extra.stats._stat_test import StatTestResult


@document
class stat_anova_test(_base_stat_test):
    """
    Add ANOVA test p-values to a plot

    Performs one-way ANOVA and displays the result as a
    text annotation including F-statistic, degrees of
    freedom, and p-value.

    {usage}

    Parameters
    ----------
    {common_parameters}
    method : str, default="one_way"
        ANOVA method. Currently supports ``"one_way"``.
    effect_size : str, default="ges"
        Type of effect size. One of ``"ges"``
        (generalized eta-squared) or ``"pes"``
        (partial eta-squared).
    label_x_npc : float or str, default="center"
        Normalized x position for the label.
    label_y_npc : float or str, default="top"
        Normalized y position for the label.
    p_digits : int, default=3
        Number of digits for p-value formatting.

    See Also
    --------
    plotnine.geom_text : The default `geom` for this `stat`.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "label"        # Formatted test result label
    "p"            # P-value
    "p_signif"     # Significance symbol
    "f"            # F-statistic
    "df"           # Numerator degrees of freedom
    "df_residual"  # Denominator degrees of freedom
    "effect_size"  # Effect size (eta-squared)
    "method"       # Name of the test
    ```

    """
    DEFAULT_PARAMS = {
        "geom": "text",
        "position": "identity",
        "na_rm": False,
        "method": "one_way",
        "effect_size": "ges",
        "label_x_npc": "center",
        "label_y_npc": "top",
        "p_digits": 3,
    }
    CREATES = {
        "label",
        "p",
        "p_signif",
        "f",
        "df",
        "df_residual",
        "effect_size",
        "method",
    }

    _test_method = "anova"
    _min_groups = 2

    def _build_result(
        self,
        result: StatTestResult,
        p_str: str,
        p_signif: str,
        x_pos: float,
        y_pos: float,
        data: pd.DataFrame,
        groups: list[np.ndarray],
    ) -> pd.DataFrame:
        # Compute effect size (eta-squared)
        all_data = np.concatenate(groups)
        grand_mean = np.mean(all_data)
        ss_between = sum(
            len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups
        )
        ss_total = np.sum((all_data - grand_mean) ** 2)
        eta_sq = ss_between / ss_total if ss_total > 0 else 0

        df1 = result.df if result.df is not None else np.nan
        df2 = result.df2 if result.df2 is not None else np.nan

        label = (
            f"F({df1:.0f}, {df2:.0f})"
            f" = {result.statistic:.2f}, {p_str},"
            f" η² = {eta_sq:.2f}"
        )

        return pd.DataFrame(
            {
                "x": [x_pos],
                "y": [y_pos],
                "label": [label],
                "p": [result.p_value],
                "p_signif": [p_signif],
                "f": [result.statistic],
                "df": [df1],
                "df_residual": [df2],
                "effect_size": [eta_sq],
                "method": [result.method],
            }
        )
