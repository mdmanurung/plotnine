from __future__ import annotations

from typing import TYPE_CHECKING

from plotnine.doctools import document
from plotnine.mapping.evaluation import after_stat

from ._base_stat_test import _base_stat_test
from ._common import add_wid_mapping, blocked_values_by_wid

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd


@document
class stat_friedman_test(_base_stat_test):
    """
    Add Friedman test p-values to a plot

    Performs the Friedman test, a non-parametric test for
    repeated measures (alternative to repeated-measures
    ANOVA), and displays the result as a text annotation.

    {usage}

    Parameters
    ----------
    {common_parameters}
    wid : str, default=None
        Column name identifying subjects/individuals.
        Required for reshaping the data into the wide
        format needed by the Friedman test.
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
    "label"      # Formatted test result label
    "p"          # P-value
    "p_signif"   # Significance symbol
    "statistic"  # Test statistic (chi-squared)
    "df"         # Degrees of freedom
    "method"     # Name of the test
    ```

    """
    DEFAULT_PARAMS = {
        "geom": "text",
        "position": "identity",
        "na_rm": False,
        "wid": None,
        "label_x_npc": "center",
        "label_y_npc": "top",
        "p_digits": 3,
    }
    DEFAULT_AES = {"label": after_stat("label"), "wid": None}
    CREATES = {
        "label",
        "p",
        "p_signif",
        "statistic",
        "df",
        "method",
    }

    _test_method = "friedman.test"
    _min_groups = 3

    def __init__(self, mapping=None, data=None, **kwargs):
        wid = kwargs.get("wid")
        mapping = add_wid_mapping(mapping, kwargs)
        if wid is not None:
            kwargs = kwargs.copy()
            kwargs.pop("wid", None)
        super().__init__(mapping, data, **kwargs)
        self.params["wid"] = wid

    def _extract_groups(
        self,
        data: pd.DataFrame,
    ) -> list[np.ndarray]:
        """
        Extract groups, using *wid* for subject alignment
        when available.
        """
        return blocked_values_by_wid(data, self.params.get("wid"))
