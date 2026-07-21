"""
Manual panel layout using a design string or matrix.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import numpy as np
import pandas as pd
from plotnine._utils import join_keys, match
from plotnine.facets.facet import (
    add_missing_facets,
    combine_vars,
    eval_facet_vars,
    facet,
)
from plotnine.facets.strips import Strips, strip

from ..guides import apply_axis_guides
from .scale_facet import apply_scale_facets

if TYPE_CHECKING:
    from typing import Optional, Sequence, Union

    from matplotlib.axes import Axes
    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine.iapi import layout_details
    from plotnine.scales.scale import scale


def _parse_design(design: str) -> np.ndarray:
    """
    Parse a design string into a 2-D array of panel labels.

    Parameters
    ----------
    design : str
        Multi-line string where each character is a panel
        label. Use ``#`` for empty cells.

    Returns
    -------
    numpy.ndarray
        2-D character array of panel identifiers.

    Examples
    --------
    >>> _parse_design("AB\\nCD")
    array([['A', 'B'],
           ['C', 'D']], dtype='<U1')
    """
    rows = [list(line) for line in design.strip().splitlines()]
    return np.array(rows)


class facet_manual(facet):
    """
    Manually specify panel layout via a design matrix.

    Allows arbitrary placement of facet panels using a text
    design string or a 2-D array. Use ``#`` to denote empty
    cells in the layout.

    Parameters
    ----------
    facets : str or list of str, optional
        Variables to facet by. Each unique combination is
        assigned a panel label from the design.
    design : str or array-like, optional
        Layout specification. A multi-line string like
        ``"AB\\n#C"`` or a 2-D list / numpy array.
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
    respect : bool
        If True, panel sizes respect the aspect ratio.
    """

    def __init__(
        self,
        facets: Optional[str | Sequence[str]] = None,
        *,
        design: Optional[Union[str, list, np.ndarray]] = None,
        scales: Literal["fixed", "free", "free_x", "free_y"] = "fixed",
        shrink: bool = True,
        labeller: Literal[
            "label_value", "label_both", "label_context"
        ] = "label_value",
        as_table: bool = True,
        drop: bool = True,
        respect: bool = False,
        widths: Optional[Sequence[float]] = None,
        heights: Optional[Sequence[float]] = None,
        axes: Literal["all", "x", "y", "margins"] = "margins",
        remove_labels: Literal["none", "x", "y", "all"] = "none",
        trim_blank: bool = False,
    ):
        super().__init__(
            scales=scales,
            shrink=shrink,
            labeller=labeller,
            as_table=as_table,
            drop=drop,
        )
        self.facets = facets
        self.design = design
        self.respect = respect
        self.widths = list(widths) if widths is not None else None
        self.heights = list(heights) if heights is not None else None
        self._panel_widths = self.widths
        self._panel_heights = self.heights
        self.axes = axes
        self.remove_labels = remove_labels
        self.trim_blank = trim_blank
        self._design_matrix: Optional[np.ndarray] = None

        if design is not None:
            if isinstance(design, str):
                self._design_matrix = _parse_design(design)
            else:
                self._design_matrix = np.asarray(design)

        # Normalize facets to a list
        if facets is None:
            self.vars: list[str] = []
        elif isinstance(facets, str):
            self.vars = [facets]
        else:
            self.vars = list(facets)

    def compute_layout(
        self,
        data: list[pd.DataFrame],
    ) -> pd.DataFrame:
        if self._design_matrix is None:
            msg = "facet_manual requires a 'design' argument"
            raise ValueError(msg)

        design = self._design_matrix
        design, kept_rows, kept_cols = self._trim_design(design)
        self._set_panel_sizes(kept_rows, kept_cols)

        # Extract unique panel labels from design, preserving order,
        # excluding '#' / NA (empty cells)
        labels: list[str] = []
        for row in design:
            for cell in row:
                if not _is_empty_design_cell(cell):
                    label = str(cell)
                    if label not in labels:
                        labels.append(label)

        # Get facet variable combinations from data
        if self.vars:
            base = combine_vars(
                data, self.environment, self.vars, drop=self.drop
            )
        else:
            base = pd.DataFrame({"_dummy_": [1]})

        if len(labels) < len(base):
            msg = (
                "facet_manual design does not provide enough panels "
                f"for {len(base)} facet combinations"
            )
            raise ValueError(msg)
        if len(labels) > len(base):
            msg = (
                "facet_manual design provides more panels than facet "
                f"combinations ({len(labels)} labels for {len(base)} panels)"
            )
            raise ValueError(msg)

        n_panels = len(base)

        rows_list = []
        for i in range(n_panels):
            label = labels[i]
            positions = np.argwhere(design.astype(str) == label)
            if positions.size == 0:
                msg = f"facet_manual design label {label!r} not found"
                raise ValueError(msg)
            row_min, col_min = positions.min(axis=0)
            row_max, col_max = positions.max(axis=0)
            _check_rectangular_span(
                label,
                positions,
                int(row_max - row_min + 1),
                int(col_max - col_min + 1),
            )
            r_pos = int(row_min + 1)
            c_pos = int(col_min + 1)

            row_data: dict = {
                "PANEL": i + 1,
                "ROW": r_pos,
                "COL": c_pos,
                "ROWSPAN": int(row_max - row_min + 1),
                "COLSPAN": int(col_max - col_min + 1),
                "SCALE_X": i + 1 if self.free["x"] else 1,
                "SCALE_Y": i + 1 if self.free["y"] else 1,
                "AXIS_X": True,
                "AXIS_Y": True,
            }
            # Add facet variable values
            if self.vars and i < len(base):
                for var in self.vars:
                    row_data[var] = base.iloc[i][var]

            rows_list.append(row_data)

        layout = pd.DataFrame(rows_list)
        layout["PANEL"] = pd.Categorical(
            layout["PANEL"],
            categories=range(1, n_panels + 1),
        )

        # Remove helper column if no facet vars
        if "_dummy_" in layout.columns:
            layout = layout.drop(columns=["_dummy_"])

        self.nrow = int(design.shape[0])
        self.ncol = int(design.shape[1])
        self._apply_axis_flags(layout)
        return layout

    def _trim_design(
        self,
        design: np.ndarray,
    ) -> tuple[np.ndarray, list[int], list[int]]:
        if not self.trim_blank:
            return (
                design,
                list(range(design.shape[0])),
                list(range(design.shape[1])),
            )

        row_mask = [
            any(not _is_empty_design_cell(cell) for cell in design[i, :])
            for i in range(design.shape[0])
        ]
        col_mask = [
            any(not _is_empty_design_cell(cell) for cell in design[:, j])
            for j in range(design.shape[1])
        ]
        kept_rows = [i for i, keep in enumerate(row_mask) if keep]
        kept_cols = [i for i, keep in enumerate(col_mask) if keep]
        if not kept_rows or not kept_cols:
            msg = "facet_manual design contains no panels"
            raise ValueError(msg)
        trimmed = design[np.ix_(kept_rows, kept_cols)]
        return trimmed, kept_rows, kept_cols

    def _set_panel_sizes(self, rows: list[int], cols: list[int]) -> None:
        if self.widths is not None:
            _check_size_length(
                self.widths,
                len(self._design_matrix[0]),
                "widths",
            )
            self._panel_widths = [self.widths[i] for i in cols]
        else:
            self._panel_widths = None
        if self.heights is not None:
            _check_size_length(
                self.heights,
                len(self._design_matrix),
                "heights",
            )
            self._panel_heights = [self.heights[i] for i in rows]
        else:
            self._panel_heights = None

    def _apply_axis_flags(self, layout: pd.DataFrame) -> None:
        if self.axes == "all":
            layout["AXIS_X"] = True
            layout["AXIS_Y"] = True
        elif self.axes == "x":
            layout["AXIS_X"] = True
            layout["AXIS_Y"] = False
        elif self.axes == "y":
            layout["AXIS_X"] = False
            layout["AXIS_Y"] = True

        if self.remove_labels == "all":
            layout["AXIS_X"] = False
            layout["AXIS_Y"] = False
        elif self.remove_labels == "x":
            layout["AXIS_X"] = False
        elif self.remove_labels == "y":
            layout["AXIS_Y"] = False

    def map(self, data: pd.DataFrame, layout: pd.DataFrame) -> pd.DataFrame:
        if not len(data):
            data["PANEL"] = pd.Categorical(
                [],
                categories=layout["PANEL"].cat.categories,
                ordered=True,
            )
            return data

        if not self.vars:
            # No facet variables: all data goes to panel 1
            data["PANEL"] = pd.Categorical(
                [1] * len(data),
                categories=layout["PANEL"].cat.categories,
                ordered=True,
            )
            return data

        facet_vals = eval_facet_vars(data, self.vars, self.environment)
        data, facet_vals = add_missing_facets(
            data, layout, self.vars, facet_vals
        )

        # Assign each data point to a panel
        if len(facet_vals) and len(facet_vals.columns):
            keys = join_keys(facet_vals, layout, self.vars)
            data["PANEL"] = match(keys["x"], keys["y"], start=1)
        else:
            data["PANEL"] = 1

        data["PANEL"] = pd.Categorical(
            data["PANEL"],
            categories=layout["PANEL"].cat.categories,
            ordered=True,
        )
        data.reset_index(drop=True, inplace=True)
        return data

    def make_strips(self, layout_info: layout_details, ax: Axes) -> Strips:
        if not self.vars:
            return Strips([])
        s = strip(self.vars, layout_info, self, ax, "top")
        return Strips([s])

    def _get_panels_gridspec(self) -> "p9GridSpec":
        from plotnine._mpl.gridspec import p9GridSpec

        ratios = {}
        if self._panel_widths is not None:
            ratios["width_ratios"] = self._panel_widths
        if self._panel_heights is not None:
            ratios["height_ratios"] = self._panel_heights

        return p9GridSpec(
            self.nrow,
            self.ncol,
            self.figure,
            nest_into=self.plot._gridspec[0],
            **ratios,
        )

    def _make_axes(self):
        gs = self._get_panels_gridspec()
        self._panels_gridspec = gs
        axs = []
        for _, row in self.layout.layout.sort_values("PANEL").iterrows():
            r0 = int(row["ROW"]) - 1
            c0 = int(row["COL"]) - 1
            r1 = r0 + int(row.get("ROWSPAN", 1))
            c1 = c0 + int(row.get("COLSPAN", 1))
            spec = gs[r0:r1, c0:c1]
            axs.append(self.figure.add_subplot(spec))
        # plotnine >=0.16 setup() unpacks (gridspec, axes) from _make_axes();
        # <0.16 assigns the returned axes list directly.
        if hasattr(self, "_make_gridspec"):
            return gs, axs
        return axs

    def init_scales(
        self,
        layout: pd.DataFrame,
        x_scale: Optional[scale] = None,
        y_scale: Optional[scale] = None,
    ) -> object:
        import types

        from plotnine.scales.scales import Scales

        scales = types.SimpleNamespace()

        if x_scale is not None:
            n = layout["SCALE_X"].max()
            scales.x = Scales([x_scale.clone() for _i in range(n)])

        if y_scale is not None:
            n = layout["SCALE_Y"].max()
            scales.y = Scales([y_scale.clone() for _i in range(n)])

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


def _is_empty_design_cell(cell: object) -> bool:
    if pd.isna(cell):
        return True
    text = str(cell)
    return text == "#" or text.upper() == "NA"


def _check_size_length(
    values: Sequence[float],
    expected: int,
    name: str,
) -> None:
    if len(values) != expected:
        msg = (
            f"facet_manual {name} must have length {expected} to match "
            "the untrimmed design"
        )
        raise ValueError(msg)


def _check_rectangular_span(
    label: str,
    positions: np.ndarray,
    rowspan: int,
    colspan: int,
) -> None:
    if len(positions) != rowspan * colspan:
        msg = (
            "facet_manual repeated design label "
            f"{label!r} must form a rectangle"
        )
        raise ValueError(msg)
