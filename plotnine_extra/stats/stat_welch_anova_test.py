from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from plotnine.doctools import document

from ._base_stat_test import _base_stat_test

if TYPE_CHECKING:
    from plotnine_extra.stats._stat_test import StatTestResult


@document
class stat_welch_anova_test(_base_stat_test):
    """
    Add Welch's ANOVA test p-values to a plot

    Performs Welch's one-way ANOVA, which does not assume
    equal variances across groups, and displays the result
    as a text annotation.

    {usage}

    Parameters
    ----------
    {common_parameters}
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
    "label"    # Formatted test result label
    "p"        # P-value
    "p_signif" # Significance symbol
    "f"        # F-statistic
    "df1"      # Numerator degrees of freedom
    "df2"      # Denominator degrees of freedom
    "method"   # Name of the test
    ```

    """
    DEFAULT_PARAMS = {
        "geom": "text",
        "position": "identity",
        "na_rm": False,
        "label_x_npc": "center",
        "label_y_npc": "top",
        "p_digits": 3,
    }
    CREATES = {
        "label",
        "p",
        "p_signif",
        "f",
        "df1",
        "df2",
        "method",
    }

    _test_method = "welch.anova"
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
        df1 = result.df if result.df is not None else np.nan
        df2 = result.df2 if result.df2 is not None else np.nan
        label = (
            f"Welch's ANOVA, F({df1:.0f}, {df2:.1f})"
            f" = {result.statistic:.2f}, {p_str}"
        )
        return pd.DataFrame(
            {
                "x": [x_pos],
                "y": [y_pos],
                "label": [label],
                "p": [result.p_value],
                "p_signif": [p_signif],
                "f": [result.statistic],
                "df1": [df1],
                "df2": [df2],
                "method": [result.method],
            }
        )
