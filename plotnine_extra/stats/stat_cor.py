from __future__ import annotations

import numpy as np
import pandas as pd
from plotnine.doctools import document
from plotnine.mapping.evaluation import after_stat
from plotnine.stats.stat import stat

from ._label_utils import compute_label_position
from ._stat_test import run_stat_test

_COEF_NAMES = {
    "pearson": "R",
    "spearman": "ρ",
    "kendall": "τ",
}


@document
class stat_cor(stat):
    """
    Add correlation coefficients with p-values to a scatter plot

    Computes correlation coefficients (Pearson, Spearman, or
    Kendall) and formats them as text labels including p-values.

    {usage}

    Parameters
    ----------
    {common_parameters}
    method : str, default="pearson"
        Correlation method. One of ``"pearson"``,
        ``"spearman"``, or ``"kendall"``.
    alternative : str, default="two-sided"
        Alternative hypothesis. One of ``"two-sided"``,
        ``"greater"``, or ``"less"``.
    label_x_npc : float or str, default="left"
        Normalized x position for the label. Float in
        [0, 1] or one of ``"left"``, ``"center"``,
        ``"right"``.
    label_y_npc : float or str, default="top"
        Normalized y position for the label. Float in
        [0, 1] or one of ``"top"``, ``"center"``,
        ``"bottom"``.
    r_accuracy : float, default=0.01
        Decimal accuracy for the correlation coefficient.
    p_accuracy : float, default=0.001
        Decimal accuracy for the p-value.
    label_sep : str, default=", "
        Separator between the correlation and p-value
        labels.

    See Also
    --------
    plotnine.geom_text : The default `geom` for this `stat`.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "label"    # Formatted correlation label
    "r"        # Correlation coefficient
    "rr"       # R-squared
    "p"        # P-value
    ```

    """
    REQUIRED_AES = {"x", "y"}
    DEFAULT_AES = {"label": after_stat("label")}
    DEFAULT_PARAMS = {
        "geom": "text",
        "position": "identity",
        "na_rm": False,
        "method": "pearson",
        "alternative": "two-sided",
        "label_x_npc": "left",
        "label_y_npc": "top",
        "r_accuracy": 0.01,
        "p_accuracy": 0.001,
        "label_sep": ", ",
    }
    CREATES = {"label", "r", "rr", "p"}

    def compute_group(self, data, scales) -> pd.DataFrame:
        x = data["x"].to_numpy(dtype=float)
        y = data["y"].to_numpy(dtype=float)
        method = self.params["method"]
        alternative = self.params["alternative"]

        if len(x) < 3:
            return pd.DataFrame()

        result = run_stat_test([x, y], method=method, alternative=alternative)

        coef_name = _COEF_NAMES.get(method, "R")
        r = result.statistic
        p = result.p_value
        rr = r**2

        # Format label
        r_accuracy = self.params["r_accuracy"]
        p_accuracy = self.params["p_accuracy"]
        label_sep = self.params["label_sep"]

        r_digits = _accuracy_to_digits(r_accuracy)
        r_str = f"{coef_name} = {r:.{r_digits}f}"
        p_str = _format_p(p, p_accuracy)
        label = f"{r_str}{label_sep}{p_str}"

        # Position the label
        x_pos = compute_label_position(
            x.min(),
            x.max(),
            self.params["label_x_npc"],
        )
        y_pos = compute_label_position(
            y.min(),
            y.max(),
            self.params["label_y_npc"],
        )

        return pd.DataFrame(
            {
                "x": [x_pos],
                "y": [y_pos],
                "label": [label],
                "r": [r],
                "rr": [rr],
                "p": [p],
            }
        )


def _accuracy_to_digits(accuracy: float) -> int:
    """Convert accuracy (e.g. 0.01) to number of digits (e.g. 2)."""
    if accuracy >= 1:
        return 0
    return max(0, int(np.ceil(-np.log10(accuracy))))


def _format_p(p: float, accuracy: float) -> str:
    """Format a p-value with the given accuracy."""
    if p < accuracy:
        digits = _accuracy_to_digits(accuracy)
        return f"p < {accuracy:.{digits}f}"
    digits = _accuracy_to_digits(accuracy)
    return f"p = {p:.{digits}f}"
