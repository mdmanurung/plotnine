from __future__ import annotations

import numpy as np
import pandas as pd
from plotnine.doctools import document
from plotnine.mapping.evaluation import after_stat
from plotnine.stats.stat import stat

from ._label_utils import compute_label_position


@document
class stat_regline_equation(stat):
    """
    Add regression line equation and R-squared to a plot

    Fits a polynomial regression and formats the equation
    and goodness-of-fit statistics as a text label.

    {usage}

    Parameters
    ----------
    {common_parameters}
    formula : str, default="y ~ x"
        Regression formula. Supported forms:

        - ``"y ~ x"``: simple linear regression
        - ``"y ~ poly(x, n)"``: polynomial of degree n
    label_x_npc : float or str, default="left"
        Normalized x position for the label.
    label_y_npc : float or str, default="top"
        Normalized y position for the label.

    See Also
    --------
    plotnine.geom_text : The default `geom` for this `stat`.
    plotnine.stat_smooth : For the regression line itself.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "label"    # Formatted equation label
    "eq"       # Equation string
    "rr"       # R-squared
    "adj_rr"   # Adjusted R-squared
    "aic"      # Akaike information criterion
    "bic"      # Bayesian information criterion
    ```

    """
    REQUIRED_AES = {"x", "y"}
    DEFAULT_AES = {"label": after_stat("label")}
    DEFAULT_PARAMS = {
        "geom": "text",
        "position": "identity",
        "na_rm": False,
        "formula": "y ~ x",
        "label_x_npc": "left",
        "label_y_npc": "top",
    }
    CREATES = {"label", "eq", "rr", "adj_rr", "aic", "bic"}

    def compute_group(self, data, scales) -> pd.DataFrame:
        x = data["x"].to_numpy(dtype=float)
        y = data["y"].to_numpy(dtype=float)

        if len(x) < 2:
            return pd.DataFrame()

        # Parse formula to get degree
        degree = _parse_formula_degree(self.params["formula"])

        # Fit polynomial
        coeffs = np.polyfit(x, y, degree)
        p = np.poly1d(coeffs)
        y_pred = p(x)

        # Compute statistics
        n = len(x)
        k = degree + 1  # number of parameters including intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)

        rr = 1 - ss_res / ss_tot if ss_tot != 0 else 0
        adj_rr = 1 - (1 - rr) * (n - 1) / (n - k) if n > k else rr

        # AIC and BIC (based on residual sum of squares)
        if n > 0 and ss_res > 0:
            log_likelihood = -n / 2 * (np.log(2 * np.pi * ss_res / n) + 1)
            aic = 2 * k - 2 * log_likelihood
            bic = k * np.log(n) - 2 * log_likelihood
        else:
            aic = np.nan
            bic = np.nan

        # Format equation
        eq = _format_equation(coeffs, degree)
        label = f"{eq}, R² = {rr:.2f}"

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
                "eq": [eq],
                "rr": [rr],
                "adj_rr": [adj_rr],
                "aic": [aic],
                "bic": [bic],
            }
        )


def _parse_formula_degree(formula):
    """Parse a formula string to extract polynomial degree."""
    import re

    formula = formula.strip()
    # Match "y ~ poly(x, n)"
    poly_match = re.match(r"y\s*~\s*poly\s*\(\s*x\s*,\s*(\d+)\s*\)", formula)
    if poly_match:
        return int(poly_match.group(1))

    # Default: "y ~ x" means degree 1
    if re.match(r"y\s*~\s*x", formula):
        return 1

    return 1


def _format_equation(coeffs, degree):
    """Format polynomial coefficients as an equation string."""
    parts = []
    for i, coef in enumerate(coeffs):
        power = degree - i
        coef_str = f"{coef:.2g}"

        if power == 0:
            parts.append(coef_str)
        elif power == 1:
            if coef_str == "1":
                parts.append("x")
            elif coef_str == "-1":
                parts.append("-x")
            else:
                parts.append(f"{coef_str}x")
        else:
            if coef_str == "1":
                parts.append(f"x^{power}")
            elif coef_str == "-1":
                parts.append(f"-x^{power}")
            else:
                parts.append(f"{coef_str}x^{power}")

    eq = "y = "
    for i, part in enumerate(parts):
        if i == 0:
            eq += part
        elif part.startswith("-"):
            eq += f" - {part[1:]}"
        else:
            eq += f" + {part}"
    return eq
