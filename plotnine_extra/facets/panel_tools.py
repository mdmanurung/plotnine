"""
Panel-targeting and panel-size helpers.

These helpers cover the parts of ggh4x's panel utilities that can be
implemented through plotnine's public or stable-enough extension points.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MethodType
from typing import TYPE_CHECKING, Any, Callable

import numpy as np

if TYPE_CHECKING:
    from typing import Sequence

    import pandas as pd


PanelSelector = str | Callable[["pd.DataFrame"], Any]


def at_panel(layer: Any, expr: PanelSelector) -> Any:
    """
    Limit a layer to panels selected from the facet layout.

    Parameters
    ----------
    layer : plotnine layer or list of layers
        Layer returned by a plotnine geom/stat constructor.
    expr : str or callable
        Selector evaluated against the facet layout. A string is passed to
        :meth:`pandas.DataFrame.eval`; a callable receives the layout
        dataframe and must return a boolean vector.

    Returns
    -------
    object
        The same layer, modified in place.
    """
    if isinstance(layer, list):
        return [at_panel(item, expr) for item in layer]
    if not hasattr(layer, "compute_aesthetics") and hasattr(layer, "to_layer"):
        layer = layer.to_layer()

    _install_panel_filter(layer, expr)
    return layer


ggsubset = at_panel


@dataclass
class force_panelsizes:  # noqa: N801
    """
    Add relative panel width/height ratios to a facetted plot.

    ``rows`` controls panel heights and ``cols`` controls panel widths. The
    values are repeated or shortened to match the facet's row/column count.
    Absolute ``total_width`` and ``total_height`` units are not supported by
    matplotlib; they are stored for introspection only.
    """

    rows: Sequence[float] | None = None
    cols: Sequence[float] | None = None
    respect: bool | None = None
    total_width: float | None = None
    total_height: float | None = None

    def __radd__(self, plot: Any) -> Any:
        facet = getattr(plot, "facet", None)
        if facet is None:
            msg = "force_panelsizes can only be added to a plot object"
            raise TypeError(msg)

        _apply_panel_size_spec(
            facet,
            rows=self.rows,
            cols=self.cols,
            respect=self.respect,
            total_width=self.total_width,
            total_height=self.total_height,
        )
        return plot


def _install_panel_filter(layer: Any, expr: PanelSelector) -> None:
    original = getattr(layer, "compute_aesthetics", None)
    if original is None:
        msg = "at_panel expects a plotnine layer"
        raise TypeError(msg)

    layer._plotnine_extra_panel_selector = expr
    if hasattr(layer, "_plotnine_extra_original_compute_aesthetics"):
        return

    layer._plotnine_extra_original_compute_aesthetics = original

    def compute_aesthetics(self, plot):
        self.data = _filter_layer_data_by_panel(self.data, plot, expr)
        return self._plotnine_extra_original_compute_aesthetics(plot)

    layer.compute_aesthetics = MethodType(compute_aesthetics, layer)


def _filter_layer_data_by_panel(
    data: pd.DataFrame,
    plot: Any,
    expr: PanelSelector,
) -> pd.DataFrame:
    if data is None or "PANEL" not in data.columns:
        return data

    layout_obj = getattr(getattr(plot, "_build_objs", None), "layout", None)
    layout = getattr(layout_obj, "layout", None)
    if layout is None or not len(layout):
        return data

    selected_panels = _selected_panels(layout, expr)
    panel_values = data["PANEL"].astype(str)
    selected_values = {str(panel) for panel in selected_panels}
    return data[panel_values.isin(selected_values)].copy()


def _selected_panels(layout: pd.DataFrame, expr: PanelSelector) -> list[Any]:
    mask = expr(layout) if callable(expr) else layout.eval(expr)
    mask = np.asarray(mask)
    if mask.dtype != bool or len(mask) != len(layout):
        msg = (
            "at_panel selector must return a boolean vector parallel "
            "to the facet layout"
        )
        raise ValueError(msg)
    return layout.loc[mask, "PANEL"].tolist()


def _apply_panel_size_spec(
    facet: Any,
    *,
    rows: Sequence[float] | None,
    cols: Sequence[float] | None,
    respect: bool | None,
    total_width: float | None,
    total_height: float | None,
) -> None:
    if rows is not None:
        facet._panel_heights = list(rows)
    if cols is not None:
        facet._panel_widths = list(cols)
    facet._force_panel_respect = respect
    facet._force_panel_total_width = total_width
    facet._force_panel_total_height = total_height

    if hasattr(facet, "_plotnine_extra_original_get_panels_gridspec"):
        return
    original = facet._get_panels_gridspec
    facet._plotnine_extra_original_get_panels_gridspec = original

    def _get_panels_gridspec(self):
        from plotnine._mpl.gridspec import p9GridSpec

        width_ratios = _ratios_for(
            getattr(self, "_panel_widths", None),
            getattr(self, "ncol", None),
        )
        height_ratios = _ratios_for(
            getattr(self, "_panel_heights", None),
            getattr(self, "nrow", None),
        )
        if width_ratios is None and height_ratios is None:
            return self._plotnine_extra_original_get_panels_gridspec()

        ratios = {}
        if width_ratios is not None:
            ratios["width_ratios"] = width_ratios
        if height_ratios is not None:
            ratios["height_ratios"] = height_ratios
        return p9GridSpec(
            self.nrow,
            self.ncol,
            self.figure,
            nest_into=self.plot._gridspec[0],
            **ratios,
        )

    facet._get_panels_gridspec = MethodType(_get_panels_gridspec, facet)


def _ratios_for(
    values: Sequence[float] | None,
    n: int | None,
) -> list[float] | None:
    if values is None or n is None:
        return None
    vals = list(values)
    if not vals:
        return None
    return [float(vals[i % len(vals)]) for i in range(n)]
