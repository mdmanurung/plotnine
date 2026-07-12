"""
Wrapped facets with nested (merged) strip labels.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from plotnine.facets.facet_wrap import facet_wrap
from plotnine.facets.strips import Strips, strip

from ..guides import apply_axis_guides

if TYPE_CHECKING:
    from typing import Optional, Sequence

    from matplotlib.axes import Axes
    from plotnine.iapi import layout_details


class facet_nested_wrap(facet_wrap):
    """
    Wrapped facets with nested strips.

    Extends :class:`plotnine.facet_wrap` so that hierarchical
    strip labels are merged when adjacent panels share the
    same parent category.

    Parameters
    ----------
    facets : str or list of str, optional
        Variables to facet by.
    nrow : int, optional
        Number of rows.
    ncol : int, optional
        Number of columns.
    scales : str
        Whether scales are fixed or free.
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
    nest_line : bool
        If True, draw a nesting indicator line between
        parent and child strip levels.
    solo_line : bool
        If True, draw a line even when a parent category
        has only one child.
    resect : float
        Amount (in [0, 1]) to shorten the nesting line
        at each end.
    bleed : bool
        If True, allow nesting indicators to extend into
        neighbouring strips.
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
        nest_line: bool = False,
        solo_line: bool = False,
        resect: float = 0,
        bleed: bool = False,
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
        self.nest_line = nest_line
        self.solo_line = solo_line
        self.resect = resect
        self.bleed = bleed

    def make_strips(self, layout_info: layout_details, ax: Axes) -> Strips:
        """
        Create strips with merged parent labels.

        When adjacent panels (in the same row) share the same
        value for a parent faceting variable, the duplicate label
        is blanked out so the parent strip visually spans those
        panels.
        """
        if not self.vars:
            return Strips([])

        s = _nested_wrap_strip(
            vars=self.vars,
            layout_info=layout_info,
            facet_obj=self,
            ax=ax,
            position="top",
            nest_line=self.nest_line,
            solo_line=self.solo_line,
            resect=self.resect,
            bleed=self.bleed,
        )
        return Strips([s])

    def set_limits_breaks_and_labels(self, panel_params, ax):
        super().set_limits_breaks_and_labels(panel_params, ax)
        apply_axis_guides(self, panel_params, ax)


class _nested_wrap_strip(strip):
    """
    A strip for wrapped facets that blanks duplicate parent labels.

    For hierarchical faceting variables, when the panel to the left
    (same row) shares the same parent-level values, the parent
    portion of the label is replaced with an empty string.
    """

    def __init__(
        self,
        vars: Sequence[str],
        layout_info: layout_details,
        facet_obj: facet_nested_wrap,
        ax: Axes,
        position: str,
        *,
        nest_line: bool = False,
        solo_line: bool = False,
        resect: float = 0,
        bleed: bool = False,
    ):
        self.nest_line = nest_line
        self.solo_line = solo_line
        self.resect = resect
        self.bleed = bleed

        super().__init__(vars, layout_info, facet_obj, ax, position)  # type: ignore[arg-type]
        self._blank_duplicate_parents(layout_info, facet_obj, vars)

    def _blank_duplicate_parents(
        self,
        layout_info: layout_details,
        facet_obj: facet_nested_wrap,
        vars: Sequence[str],
    ) -> None:
        """
        Replace duplicate parent labels with empty strings.

        Looks at the panel to the left (same row, col - 1).
        """
        if len(vars) < 2:
            return

        layout_df = facet_obj.layout.layout

        prev_col = layout_info.col - 1
        if prev_col < 1:
            return

        prev_mask = (layout_df["ROW"] == layout_info.row) & (
            layout_df["COL"] == prev_col
        )

        if not prev_mask.any():
            return

        prev_row_data = layout_df.loc[prev_mask].iloc[0]

        # Parent variables are all but the last (innermost)
        parent_vars = list(vars[:-1])

        all_match = all(
            layout_info.variables.get(v) == prev_row_data.get(v)
            for v in parent_vars
        )

        if all_match:
            for v in parent_vars:
                self.label_info.variables[v] = ""
