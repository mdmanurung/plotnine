"""
Grid facets with nested (merged) strip labels.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from plotnine.facets.facet_grid import facet_grid
from plotnine.facets.strips import Strips, strip

from ..guides import apply_axis_guides

if TYPE_CHECKING:
    from typing import Optional, Sequence

    from matplotlib.axes import Axes
    from plotnine.iapi import layout_details
    from plotnine.typing import FacetSpaceRatios


class facet_nested(facet_grid):
    """
    Grid facets with nested strips.

    Extends :class:`plotnine.facet_grid` so that hierarchical
    strip labels are merged when adjacent panels share the
    same parent category.

    Parameters
    ----------
    rows : str or list of str, optional
        Variables to facet by in rows.
    cols : str or list of str, optional
        Variables to facet by in columns.
    margins : bool or list of str
        Whether to display marginal facets.
    scales : str
        Whether scales are fixed or free.
    space : str or dict
        Panel spacing mode.
    shrink : bool
        Whether to shrink scales to fit output of statistics.
    labeller : str
        Labelling function for strip text.
    as_table : bool
        If True, facets are laid out like a table.
    drop : bool
        Whether to drop unused factor levels.
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
        nest_line: bool = False,
        solo_line: bool = False,
        resect: float = 0,
        bleed: bool = False,
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
        self.nest_line = nest_line
        self.solo_line = solo_line
        self.resect = resect
        self.bleed = bleed

    def make_strips(self, layout_info: layout_details, ax: Axes) -> Strips:
        """
        Create strips with merged parent labels.

        When adjacent panels share the same value for a parent
        (outer) faceting variable, the duplicate label is blanked
        out so that the parent strip appears to span multiple
        panels.
        """
        lst: list[strip] = []

        if layout_info.is_top and self.cols:
            s = _nested_strip(
                vars=self.cols,
                layout_info=layout_info,
                facet_obj=self,
                ax=ax,
                position="top",
                nest_line=self.nest_line,
                solo_line=self.solo_line,
                resect=self.resect,
                bleed=self.bleed,
            )
            lst.append(s)

        if layout_info.is_right and self.rows:
            s = _nested_strip(
                vars=self.rows,
                layout_info=layout_info,
                facet_obj=self,
                ax=ax,
                position="right",
                nest_line=self.nest_line,
                solo_line=self.solo_line,
                resect=self.resect,
                bleed=self.bleed,
            )
            lst.append(s)

        return Strips(lst)

    def set_limits_breaks_and_labels(self, panel_params, ax):
        super().set_limits_breaks_and_labels(panel_params, ax)
        apply_axis_guides(self, panel_params, ax)


class _nested_strip(strip):
    """
    A strip that blanks out duplicate parent-level labels.

    For hierarchical faceting variables (e.g. ``cols=["outer", "inner"]``),
    when two adjacent panels share the same ``outer`` value the duplicate
    ``outer`` label text is replaced with an empty string.  This gives
    the visual effect of a single merged strip spanning those panels.
    """

    def __init__(
        self,
        vars: Sequence[str],
        layout_info: layout_details,
        facet_obj: facet_nested,
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

        # Initialise the base strip (computes label_info via labeller)
        super().__init__(vars, layout_info, facet_obj, ax, position)  # type: ignore[arg-type]

        # Now blank out parent-level labels that are duplicates of the
        # previous panel along the relevant axis.
        self._blank_duplicate_parents(layout_info, facet_obj, vars, position)

    # ------------------------------------------------------------------
    def _blank_duplicate_parents(
        self,
        layout_info: layout_details,
        facet_obj: facet_nested,
        vars: Sequence[str],
        position: str,
    ) -> None:
        """
        Replace duplicate parent labels with empty strings.

        For ``position="top"`` we look at the panel to the left
        (same row, col-1).  For ``position="right"`` we look at
        the panel above (row-1, same col).
        """
        if len(vars) < 2:
            # Nothing to merge when there is only one variable
            return

        layout_df = facet_obj.layout.layout

        if position == "top":
            prev_col = layout_info.col - 1
            if prev_col < 1:
                return
            prev_mask = (layout_df["ROW"] == layout_info.row) & (
                layout_df["COL"] == prev_col
            )
        else:  # "right"
            prev_row = layout_info.row - 1
            if prev_row < 1:
                return
            prev_mask = (layout_df["ROW"] == prev_row) & (
                layout_df["COL"] == layout_info.col
            )

        if not prev_mask.any():
            return

        prev_row_data = layout_df.loc[prev_mask].iloc[0]

        # The parent variables are all but the last (innermost).
        parent_vars = list(vars[:-1])

        # Check if all parent values match the previous panel
        all_match = all(
            layout_info.variables.get(v) == prev_row_data.get(v)
            for v in parent_vars
        )

        if all_match:
            # Blank out the parent portion of the label text.
            # label_info.text() returns newline-separated labels
            # (one per variable).  We replace the parent lines
            # with empty strings.
            label_text = self.label_info.text()
            lines = label_text.split("\n")
            n_parents = len(parent_vars)
            if len(lines) >= n_parents:
                for i in range(n_parents):
                    lines[i] = ""
                # Update the underlying variables dict so text()
                # returns the blanked version.
                for i, v in enumerate(parent_vars):
                    self.label_info.variables[v] = ""
