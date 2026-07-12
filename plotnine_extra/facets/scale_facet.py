"""
Per-panel scale adjustment functions.
"""

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from typing import Any

    import pandas as pd


class ScaleFacet:
    """
    Apply a scale modification to specific facet panels.

    Parameters
    ----------
    axis : str
        Which axis this scale targets ("x" or "y").
    expr : str or callable
        Expression or predicate identifying which panels
        to apply the scale to.
    *args : Any
        Positional arguments forwarded to the scale.
    **kwargs : Any
        Keyword arguments forwarded to the scale.
    """

    def __init__(
        self,
        axis: Literal["x", "y"],
        expr: Any,
        *args: Any,
        scale_type: Literal["continuous", "discrete"] = "continuous",
        **kwargs: Any,
    ):
        self.axis = axis
        self.expr = expr
        self.args = args
        self.scale_type = scale_type
        self.kwargs = kwargs

    def __radd__(self, other: Any) -> Any:
        """
        Allow ``ggplot() + scale_x_facet(...)``.

        Stores this object on the plot so that compatible facets
        can consume it when initialising per-panel scales.
        """
        if not hasattr(other, "_scale_facets"):
            other._scale_facets = []
        other._scale_facets.append(self)
        facet = getattr(other, "facet", None)
        if facet is not None:
            if not hasattr(facet, "_scale_facets"):
                facet._scale_facets = []
            facet._scale_facets.append(self)
        return other

    def matches(self, layout_row: Any) -> bool:
        """
        Test whether a layout row matches this scale's selector.

        Parameters
        ----------
        layout_row : dict-like
            A row from the layout DataFrame (or a dict of facet
            variable values for a panel).

        Returns
        -------
        bool
            ``True`` if the panel should use this scale.
        """
        expr = self.expr
        if callable(expr):
            try:
                return bool(expr(layout_row))
            except Exception as exc:
                msg = f"scale_{self.axis}_facet selector failed"
                raise ValueError(msg) from exc
        if isinstance(expr, str):
            # Evaluate the expression string against the
            # layout row values as local variables.
            try:
                return bool(eval(expr, {}, dict(layout_row)))  # noqa: S307
            except Exception as exc:
                msg = f"scale_{self.axis}_facet selector failed"
                raise ValueError(msg) from exc
        return False

    def make_scale(self):
        """Construct the scale object represented by this selector."""
        from plotnine import (
            scale_x_continuous,
            scale_x_discrete,
            scale_y_continuous,
            scale_y_discrete,
        )

        constructors = {
            ("x", "continuous"): scale_x_continuous,
            ("x", "discrete"): scale_x_discrete,
            ("y", "continuous"): scale_y_continuous,
            ("y", "discrete"): scale_y_discrete,
        }
        try:
            constructor = constructors[(self.axis, self.scale_type)]
        except KeyError as exc:
            msg = (
                "scale facet type must be 'continuous' or 'discrete', "
                f"got {self.scale_type!r}"
            )
            raise ValueError(msg) from exc
        return constructor(*self.args, **self.kwargs)


def scale_x_facet(
    expr: Any,
    *args: Any,
    type: Literal["continuous", "discrete"] = "continuous",
    **kwargs: Any,
) -> ScaleFacet:
    """
    Apply x-axis scale to specific facet panels.

    Parameters
    ----------
    expr : str or callable
        Expression identifying which panels to target.
    *args : Any
        Forwarded to the underlying scale constructor.
    **kwargs : Any
        Forwarded to the underlying scale constructor.

    Returns
    -------
    ScaleFacet
        Object that can be added to a ggplot.
    """
    return ScaleFacet("x", expr, *args, scale_type=type, **kwargs)


def scale_y_facet(
    expr: Any,
    *args: Any,
    type: Literal["continuous", "discrete"] = "continuous",
    **kwargs: Any,
) -> ScaleFacet:
    """
    Apply y-axis scale to specific facet panels.

    Parameters
    ----------
    expr : str or callable
        Expression identifying which panels to target.
    *args : Any
        Forwarded to the underlying scale constructor.
    **kwargs : Any
        Forwarded to the underlying scale constructor.

    Returns
    -------
    ScaleFacet
        Object that can be added to a ggplot.
    """
    return ScaleFacet("y", expr, *args, scale_type=type, **kwargs)


def apply_scale_facets(
    scales_ns: object,
    layout: "pd.DataFrame",
    scale_facets: list[ScaleFacet],
) -> None:
    """
    Apply scale facet selectors to initialised panel scales.

    Matching follows ggh4x priority: the first matching selector wins for a
    panel scale index, so later selectors only fill unmatched panels.
    """
    if not scale_facets:
        return

    for axis in ("x", "y"):
        panel_scales = getattr(scales_ns, axis, None)
        if panel_scales is None:
            continue

        scale_col = f"SCALE_{axis.upper()}"
        assigned: set[int] = set()
        selectors = [sf for sf in scale_facets if sf.axis == axis]
        if not selectors:
            continue

        for _, row in layout.iterrows():
            scale_idx = int(row[scale_col]) - 1
            if scale_idx in assigned or scale_idx >= len(panel_scales):
                continue

            for selector in selectors:
                if selector.matches(row):
                    sc = selector.make_scale()
                    panel_scales[scale_idx] = (
                        sc.clone() if hasattr(sc, "clone") else copy(sc)
                    )
                    assigned.add(scale_idx)
                    break
