"""
Extended wrapped facets with inner axes and trimming.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import numpy as np
from plotnine.facets.facet_wrap import facet_wrap

from ..guides import apply_axis_guides
from .scale_facet import apply_scale_facets

if TYPE_CHECKING:
    from typing import Optional, Sequence

    import pandas as pd


class facet_wrap2(facet_wrap):
    """
    Extended wrapped facets.

    Extends :class:`plotnine.facet_wrap` with configurable inner
    axes, selective label removal, and blank-panel trimming.

    Parameters
    ----------
    facets : str or list of str, optional
        Variables to facet by.
    nrow : int, optional
        Number of rows.
    ncol : int, optional
        Number of columns.
    scales : str
        Whether scales are fixed ("fixed"), free ("free",
        "free_x", "free_y").
    shrink : bool
        Whether to shrink scales to fit output of statistics.
    labeller : str
        Labelling function for strip text.
    as_table : bool
        If True, facets are laid out like a table.
    drop : bool
        Whether to drop unused factor levels.
    dir : str
        Direction: "h" for horizontal, "v" for vertical.
    axes : str
        Which inner axes to draw. One of "all", "x", "y",
        or "margins".
    remove_labels : str
        Which inner axis labels to remove. One of "none",
        "x", "y", or "all".
    trim_blank : bool
        If True, trim blank panels from the layout.
    """

    def __init__(
        self,
        facets: Optional[str | Sequence[str]] = None,
        *,
        nrow: Optional[int] = None,
        ncol: Optional[int] = None,
        scales: Literal["fixed", "free", "free_x", "free_y"] = "fixed",
        shrink: bool = True,
        labeller: Literal[
            "label_value", "label_both", "label_context"
        ] = "label_value",
        as_table: bool = True,
        drop: bool = True,
        dir: Literal["h", "v"] = "h",
        axes: Literal["all", "x", "y", "margins"] = "margins",
        remove_labels: Literal["none", "x", "y", "all"] = "none",
        trim_blank: bool = True,
    ):
        super().__init__(
            facets=facets,
            nrow=nrow,
            ncol=ncol,
            scales=scales,
            shrink=shrink,
            labeller=labeller,
            as_table=as_table,
            drop=drop,
            dir=dir,
        )
        self.axes = axes
        self.remove_labels = remove_labels
        self.trim_blank = trim_blank

    def compute_layout(
        self,
        data: list[pd.DataFrame],
    ) -> pd.DataFrame:
        layout = super().compute_layout(data)

        # Trim blank panels: remove panels that have no data
        if self.trim_blank:
            used_panels: set[int] = set()
            for d in data:
                if d is not None and "PANEL" in d.columns:
                    used_panels.update(d["PANEL"].unique())
            if used_panels:
                layout = layout[layout["PANEL"].isin(used_panels)].copy()
                # Reassign ROW/COL positions compactly
                panels = layout.sort_values("PANEL")
                n = len(panels)
                ncol = self._ncol or int(np.ceil(np.sqrt(n)))
                nrow = int(np.ceil(n / ncol))
                for idx, (i, _) in enumerate(panels.iterrows()):
                    layout.loc[i, "ROW"] = idx // ncol + 1
                    layout.loc[i, "COL"] = idx % ncol + 1
                self.nrow = nrow
                self.ncol = ncol

        # Control which inner axes are drawn
        if self.axes == "all":
            layout["AXIS_X"] = True
            layout["AXIS_Y"] = True
        elif self.axes == "x":
            layout["AXIS_X"] = True
            # keep AXIS_Y as default (outer only)
        elif self.axes == "y":
            layout["AXIS_Y"] = True
            # keep AXIS_X as default (outer only)
        # "margins" = keep default from super()

        # Remove labels: hide axes entirely for the specified direction.
        # plotnine ties tick marks and labels together via AXIS_X/AXIS_Y,
        # so removing labels also removes ticks.
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
        x_scale: Optional[object] = None,
        y_scale: Optional[object] = None,
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

        # Apply per-panel position scales
        plot = getattr(self, "plot", None)
        fps = getattr(plot, "_facetted_pos_scales", None)
        if fps is not None:
            fps.apply(scales)
        scale_facets = getattr(self, "_scale_facets", None)
        if scale_facets is None:
            scale_facets = getattr(plot, "_scale_facets", [])
        apply_scale_facets(scales, layout, scale_facets)

        return scales

    def set_limits_breaks_and_labels(self, panel_params, ax):
        super().set_limits_breaks_and_labels(panel_params, ax)
        apply_axis_guides(self, panel_params, ax)
