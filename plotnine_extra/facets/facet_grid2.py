"""
Extended grid facets with independent scales and inner axes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from plotnine.facets.facet_grid import facet_grid

from ..guides import apply_axis_guides
from .scale_facet import apply_scale_facets

if TYPE_CHECKING:
    from typing import Optional, Sequence

    import pandas as pd
    from plotnine.scales.scale import scale
    from plotnine.typing import FacetSpaceRatios


class facet_grid2(facet_grid):
    """
    Extended grid facets with independent scales.

    Extends :class:`plotnine.facet_grid` with support for truly
    independent position scales, configurable inner axes, and
    selective label removal.

    Parameters
    ----------
    rows : str or list of str, optional
        Variables to facet by in rows.
    cols : str or list of str, optional
        Variables to facet by in columns.
    margins : bool or list of str
        Whether to display marginal facets.
    scales : str
        Whether scales are fixed ("fixed"), free ("free",
        "free_x", "free_y").
    space : str or dict
        Panel spacing: "fixed", "free", "free_x", "free_y"
        or a dict of ratios.
    shrink : bool
        Whether to shrink scales to fit output of statistics.
    labeller : str
        Labelling function for strip text.
    as_table : bool
        If True, facets are laid out like a table with the
        highest values at the bottom-right.
    drop : bool
        Whether to drop unused factor levels.
    independent : str
        Which axes have truly independent scales per panel.
        One of "none", "x", "y", or "all".
    axes : str
        Which inner axes to draw. One of "all", "x", "y",
        or "margins".
    remove_labels : str
        Which inner axis labels to remove. One of "none",
        "x", "y", or "all".
    """

    def __init__(
        self,
        rows: Optional[str | Sequence[str]] = None,
        cols: Optional[str | Sequence[str]] = None,
        *,
        margins: bool | Sequence[str] = False,
        scales: Literal["fixed", "free", "free_x", "free_y"] = "fixed",
        space: (
            Literal["fixed", "free", "free_x", "free_y"] | FacetSpaceRatios
        ) = "fixed",
        shrink: bool = True,
        labeller: Literal[
            "label_value", "label_both", "label_context"
        ] = "label_value",
        as_table: bool = True,
        drop: bool = True,
        independent: Literal["none", "x", "y", "all"] = "none",
        axes: Literal["all", "x", "y", "margins"] = "margins",
        remove_labels: Literal["none", "x", "y", "all"] = "none",
    ):
        super().__init__(
            rows=rows,
            cols=cols,
            margins=margins,
            scales=scales,
            space=space,
            shrink=shrink,
            labeller=labeller,
            as_table=as_table,
            drop=drop,
        )
        self.independent = independent
        self.axes = axes
        self.remove_labels = remove_labels

    def compute_layout(
        self,
        data: list[pd.DataFrame],
    ) -> pd.DataFrame:
        layout = super().compute_layout(data)

        # Independent scales: give each panel its own scale index
        # so that plotnine creates separate scale objects per panel.
        if self.independent in ("x", "all"):
            layout["SCALE_X"] = range(1, len(layout) + 1)
        if self.independent in ("y", "all"):
            layout["SCALE_Y"] = range(1, len(layout) + 1)

        # Control which inner axes are drawn
        if self.axes == "all":
            layout["AXIS_X"] = True
            layout["AXIS_Y"] = True
        elif self.axes == "x":
            layout["AXIS_X"] = True
        elif self.axes == "y":
            layout["AXIS_Y"] = True
        # "margins" = keep default from super()

        # Remove labels: hide axes for the specified direction
        if self.remove_labels == "all":
            layout["AXIS_X"] = False
            layout["AXIS_Y"] = False
        elif self.remove_labels == "x":
            layout["AXIS_X"] = False
        elif self.remove_labels == "y":
            layout["AXIS_Y"] = False

        return layout

    def init_scales(
        self,
        layout: pd.DataFrame,
        x_scale: Optional[scale] = None,
        y_scale: Optional[scale] = None,
    ) -> object:
        """
        Initialise scales, applying any ``facetted_pos_scales``.
        """
        import types

        from plotnine.scales.scales import Scales

        scales = types.SimpleNamespace()

        if x_scale is not None:
            n = layout["SCALE_X"].max()
            scales.x = Scales([x_scale.clone() for _i in range(n)])

        if y_scale is not None:
            n = layout["SCALE_Y"].max()
            scales.y = Scales([y_scale.clone() for _i in range(n)])

        # Apply per-panel position scales if attached to the plot
        if hasattr(self, "plot") and hasattr(
            self.plot, "_facetted_pos_scales"
        ):
            self.plot._facetted_pos_scales.apply(scales)
        plot = getattr(self, "plot", None)
        scale_facets = getattr(self, "_scale_facets", None)
        if scale_facets is None:
            scale_facets = getattr(plot, "_scale_facets", [])
        apply_scale_facets(scales, layout, scale_facets)

        return scales

    def set_limits_breaks_and_labels(self, panel_params, ax):
        super().set_limits_breaks_and_labels(panel_params, ax)
        apply_axis_guides(self, panel_params, ax)
