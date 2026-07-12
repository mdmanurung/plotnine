"""
Base class for statistical test stat layers.

Provides a template method for the common pattern shared by
``stat_anova_test``, ``stat_kruskal_test``,
``stat_friedman_test``, and ``stat_welch_anova_test``.

Subclasses override :meth:`_run_test` and :meth:`_build_result`
to customise the test and result columns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from plotnine.mapping.evaluation import after_stat
from plotnine.stats.stat import stat

from ._common import preserve_panel_columns
from ._label_utils import compute_label_position
from ._p_format import format_p_value, p_to_signif
from ._stat_test import StatTestResult, run_stat_test

if TYPE_CHECKING:
    from plotnine.iapi import panel_view


class _base_stat_test(stat):
    """
    Abstract base for omnibus test stat layers.

    Subclasses must set the following class attributes:

    - ``_test_method``: the method name passed to
      :func:`run_stat_test` (e.g. ``"anova"``).
    - ``_min_groups``: minimum number of groups required.

    And may override:

    - :meth:`_extract_groups`: customise how data is split
      into groups (default: group by ``"x"``).
    - :meth:`_build_result`: customise the result DataFrame
      columns returned from ``compute_panel``.
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_AES = {"label": after_stat("label")}

    # Subclasses must override
    _test_method: str = ""
    _min_groups: int = 2

    def _extract_groups(
        self,
        data: pd.DataFrame,
    ) -> list[np.ndarray]:
        """
        Split *data* into groups for testing.

        The default groups by the ``"x"`` column.
        """
        return [grp["y"].to_numpy(dtype=float) for _, grp in data.groupby("x")]

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
        """
        Build the result DataFrame.

        Override in subclasses to add extra columns
        (e.g. effect sizes, extra degrees of freedom).
        """
        label = f"{result.method}, {p_str}"
        return pd.DataFrame(
            {
                "x": [x_pos],
                "y": [y_pos],
                "label": [label],
                "p": [result.p_value],
                "p_signif": [p_signif],
                "statistic": [result.statistic],
                "df": [result.df if result.df is not None else np.nan],
                "method": [result.method],
            }
        )

    def compute_panel(
        self,
        data: pd.DataFrame,
        scales: panel_view,
    ) -> pd.DataFrame:
        """Template method for omnibus test stats."""
        groups = self._extract_groups(data)

        if len(groups) < self._min_groups:
            return pd.DataFrame()

        result = run_stat_test(groups, method=self._test_method)

        p_digits = self.params["p_digits"]
        p_str = format_p_value(result.p_value, digits=p_digits)
        p_signif = p_to_signif(result.p_value)

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

        result_df = self._build_result(
            result,
            p_str,
            p_signif,
            x_pos,
            y_pos,
            data,
            groups,
        )
        return preserve_panel_columns(result_df, data)
