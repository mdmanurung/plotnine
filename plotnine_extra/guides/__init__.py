"""
Guide helpers ported from ggh4x.

The axis guide helpers are lightweight plotnine guide objects. Plotnine's
legend system accepts them on position scales, while the actual rendering is
handled by the extended facet classes in :mod:`plotnine_extra.facets`.
"""

from __future__ import annotations

import hashlib
from copy import copy
from itertools import islice
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.offsetbox import HPacker, TextArea, VPacker
from plotnine.guides.guide import guide
from plotnine.guides.guide_legend import GuideElementsLegend, guide_legend

if TYPE_CHECKING:
    from typing import Any, Callable, Sequence

    from matplotlib.axes import Axes
    from matplotlib.text import Text
    from plotnine.iapi import panel_view, scale_view


__all__ = (
    "GuideAxisSpec",
    "apply_axis_guides",
    "guide_axis_nested",
    "guide_axis_manual",
    "guide_axis_minor",
    "guide_axis_logticks",
    "guide_axis_truncated",
    "guide_axis_scalebar",
    "guide_axis_colour",
    "guide_axis_color",
    "guide_dendro",
    "guide_stringlegend",
)


class GuideAxisSpec(guide):
    """
    Descriptor and inert plotnine guide for axis-guide rendering.

    Plotnine validates ``scale_x_*(guide=...)`` values through its guide
    registry. Subclassing :class:`plotnine.guides.guide.guide` lets position
    scale guide specs pass that validation. Training returns ``None`` so these
    objects never create legend boxes; extended facets consume the stored
    ``kind`` and ``options`` when setting axis limits, breaks, and labels.
    """

    def __init__(self, kind: str, options: dict[str, Any] | None = None):
        super().__init__()
        self.kind = kind
        self.options = dict(options or {})
        self.available_aes = {"x", "y"}
        self.hash = hashlib.sha256(
            f"{kind}:{sorted(self.options)}".encode()
        ).hexdigest()

    def __radd__(self, other):
        axis = _axis_from_position(self.options.get("position"), "x")
        guides = getattr(other, "_plotnine_extra_axis_guides", {}).copy()
        guides[axis] = self
        other._plotnine_extra_axis_guides = guides
        return other

    def __add__(self, other):
        return self.__radd__(other)

    def train(self, scale, aesthetic=None):  # noqa: D102
        return None

    def create_geoms(self):  # noqa: D102
        return None

    def draw(self):  # noqa: D102
        raise NotImplementedError("GuideAxisSpec is rendered by facets")


def guide_axis_nested(
    delim: str = "_",
    extend: float = 0.1,
    inv: bool = False,
    nest_line: bool = True,
    **kwargs,
) -> GuideAxisSpec:
    """Multi-level axis labels split by *delim*."""
    return GuideAxisSpec(
        "nested",
        {
            "delim": delim,
            "extend": extend,
            "inv": inv,
            "nest_line": nest_line,
            **kwargs,
        },
    )


def guide_axis_manual(
    breaks: "Sequence | None" = None,
    labels: "Sequence | None" = None,
    label_colour: "str | Sequence[str] | None" = None,
    label_size: "float | Sequence[float] | None" = None,
    title: str | None = None,
    **kwargs,
) -> GuideAxisSpec:
    """User-supplied axis breaks and labels."""
    return GuideAxisSpec(
        "manual",
        {
            "breaks": breaks,
            "labels": labels,
            "label_colour": label_colour,
            "label_size": label_size,
            "title": title,
            **kwargs,
        },
    )


def guide_axis_minor(**kwargs) -> GuideAxisSpec:
    """Render visible minor ticks and optional minor labels."""
    return GuideAxisSpec("minor", kwargs)


def guide_axis_logticks(
    sides: str = "bl",
    short: float = 0.5,
    mid: float = 1.0,
    long: float = 1.5,
    **kwargs,
) -> GuideAxisSpec:
    """Render log-style tick marks on the requested sides."""
    return GuideAxisSpec(
        "logticks",
        {
            "sides": sides,
            "short": short,
            "mid": mid,
            "long": long,
            **kwargs,
        },
    )


def guide_axis_truncated(
    trunc_lower: "Any | Callable | None" = None,
    trunc_upper: "Any | Callable | None" = None,
    **kwargs,
) -> GuideAxisSpec:
    """Truncate the axis spine to numeric or callable bounds."""
    return GuideAxisSpec(
        "truncated",
        {
            "trunc_lower": trunc_lower,
            "trunc_upper": trunc_upper,
            **kwargs,
        },
    )


def guide_axis_scalebar(
    size: float = 1.0,
    label: str | None = None,
    **kwargs,
) -> GuideAxisSpec:
    """Draw a data-coordinate scalebar with an optional label."""
    return GuideAxisSpec(
        "scalebar",
        {"size": size, "label": label, **kwargs},
    )


def guide_axis_colour(
    colours: "Sequence[str] | None" = None,
    **kwargs,
) -> GuideAxisSpec:
    """Colour axis tick labels individually."""
    return GuideAxisSpec("colour", {"colours": colours, **kwargs})


guide_axis_color = guide_axis_colour


def guide_dendro(
    dendro: "Any | None" = None,
    position: str = "top",
    **kwargs,
) -> GuideAxisSpec:
    """Draw a compact dendrogram aligned to tick order."""
    return GuideAxisSpec(
        "dendro",
        {"dendro": dendro, "position": position, **kwargs},
    )


class guide_stringlegend(guide_legend):  # noqa: N801
    """
    Text-only legend guide.

    The guide uses the mapped aesthetic value as the label colour and does not
    allocate or draw key glyph boxes.
    """

    def __post_init__(self):
        super().__post_init__()
        self._elements_cls = GuideElementsStringLegend
        self.kind = "stringlegend"
        self.options = {"ncol": self.ncol, "nrow": self.nrow}

    def setup(self, guides):  # noqa: D102
        # plotnine < 0.16 binds guides to the plot through setup().
        super().setup(guides)
        self._plot = guides.plot

    def _bind_source(self, plot):
        # plotnine >= 0.16 renamed the per-guide binding hook to
        # _bind_source(plot); capture the plot reference here too.
        super()._bind_source(plot)
        self._plot = plot

    def __radd__(self, other):
        other.guides.color = self
        other.guides.colour = copy(self)
        other.guides.fill = copy(self)
        return other

    def __add__(self, other):
        return self.__radd__(other)

    def draw(self):
        elements = self.elements
        targets = self.theme.targets

        title = "" if self.title is None else str(self.title)
        title_box = TextArea(title)
        targets.legend_title = title_box._text  # type: ignore[attr-defined]

        colour_values = _legend_layer_text_colours(self)
        text = elements.text
        if hasattr(text, "has"):
            # plotnine >= 0.16: per-label horizontal/vertical alignments
            alignments = list(zip(text.has, text.vas))
        else:
            # plotnine < 0.16: a single alignment shared by all labels
            alignments = [(text.ha, text.va)] * len(colour_values)
        labels = [
            TextArea(
                str(label),
                textprops={"ha": ha, "va": va, "color": colour},
            )
            for label, colour, (ha, va) in zip(
                self.key["label"], colour_values, alignments
            )
        ]
        targets.legend_text_legend = [
            label._text
            for label in labels  # type: ignore[attr-defined]
        ]
        _register_stringlegend_theme_callback(
            self._plot,
            list(zip(targets.legend_text_legend, colour_values)),
        )
        targets.legend_key = []

        keys_order = slice(None, None, -1) if self.reverse else slice(0, None)
        key_boxes = labels[keys_order]

        nrow, ncol = self._calculate_rows_and_cols(elements)
        if self.byrow:
            chunk_size = ncol
            packer_dim1, packer_dim2 = HPacker, VPacker
            sep1 = elements.key_spacing_x
            sep2 = elements.key_spacing_y
        else:
            chunk_size = nrow
            packer_dim1, packer_dim2 = VPacker, HPacker
            sep1 = elements.key_spacing_y
            sep2 = elements.key_spacing_x

        chunks = []
        for i in range(len(key_boxes)):
            start = i * chunk_size
            stop = start + chunk_size
            chunks.append(list(islice(key_boxes, start, stop)))
            if stop >= len(key_boxes):
                break

        chunk_boxes = [
            packer_dim1(children=chunk, align="left", sep=sep1, pad=0)
            for chunk in chunks
        ]
        entries_box = packer_dim2(
            children=chunk_boxes,
            align="baseline",
            sep=sep2,
            pad=0,
        )

        lookup = {
            "right": (HPacker, slice(None, None, -1)),
            "left": (HPacker, slice(0, None)),
            "bottom": (VPacker, slice(None, None, -1)),
            "top": (VPacker, slice(0, None)),
        }
        packer, slc = lookup[elements.title_position]
        children = (
            [entries_box]
            if elements.title.is_blank
            else [
                title_box,
                entries_box,
            ][slc]
        )

        return packer(
            children=children,
            sep=elements.title.margin,
            align=elements.title.align,
            pad=elements.margin,
        )


def apply_axis_guides(
    facet_obj: object,
    panel_params: "panel_view",
    ax: "Axes",
) -> None:
    """Apply plotnine-extra axis guide specs to a matplotlib axis."""
    callbacks = []
    for axis in ("x", "y"):
        spec = _resolve_axis_spec(facet_obj, panel_params, axis)
        if spec is not None:
            _apply_axis_spec(ax, panel_params, axis, spec)
            callbacks.append(
                (
                    ax,
                    panel_params,
                    axis,
                    spec,
                )
            )
    if callbacks:
        _register_axis_theme_callbacks(facet_obj, callbacks)


class GuideElementsStringLegend(GuideElementsLegend):
    """Use standard legend themeables for stringlegend text margins."""

    def __post_init__(self):
        super().__post_init__()
        self.guide_kind = "legend"


def _register_axis_theme_callbacks(
    facet_obj: object,
    callbacks: list[tuple["Axes", "panel_view", str, GuideAxisSpec]],
) -> None:
    plot = getattr(facet_obj, "plot", None)
    if plot is None:
        return

    existing = getattr(plot, "_plotnine_extra_axis_callbacks", [])
    existing.extend(callbacks)
    plot._plotnine_extra_axis_callbacks = existing

    theme = getattr(plot, "theme", None)
    if theme is None or getattr(theme, "_plotnine_extra_axis_hooked", False):
        return

    original_apply = theme.apply

    def apply_with_axis_guides():
        original_apply()
        pending = getattr(plot, "_plotnine_extra_axis_callbacks", [])
        plot._plotnine_extra_axis_callbacks = []
        for cb_ax, cb_params, cb_axis, cb_spec in pending:
            _apply_axis_spec(cb_ax, cb_params, cb_axis, cb_spec)

    theme.apply = apply_with_axis_guides
    theme._plotnine_extra_axis_hooked = True


def _register_stringlegend_theme_callback(
    plot: object,
    callbacks: list[tuple[Text, str]],
) -> None:
    existing = getattr(plot, "_plotnine_extra_stringlegend_callbacks", [])
    existing.extend(callbacks)
    plot._plotnine_extra_stringlegend_callbacks = existing

    theme = getattr(plot, "theme", None)
    if theme is None or getattr(
        theme,
        "_plotnine_extra_stringlegend_hooked",
        False,
    ):
        return

    original_apply = theme.apply

    def apply_with_stringlegend():
        original_apply()
        pending = getattr(plot, "_plotnine_extra_stringlegend_callbacks", [])
        plot._plotnine_extra_stringlegend_callbacks = []
        for text, colour in pending:
            text.set_color(colour)

    theme.apply = apply_with_stringlegend
    theme._plotnine_extra_stringlegend_hooked = True


def _resolve_axis_spec(
    facet_obj: object,
    panel_params: "panel_view",
    axis: str,
) -> GuideAxisSpec | None:
    view = getattr(panel_params, axis)
    spec = getattr(getattr(view, "scale", None), "guide", None)
    if isinstance(spec, GuideAxisSpec):
        return spec

    plot = getattr(facet_obj, "plot", None)
    fallback = getattr(plot, "_plotnine_extra_axis_guides", {})
    spec = fallback.get(axis)
    return spec if isinstance(spec, GuideAxisSpec) else None


def _apply_axis_spec(
    ax: "Axes",
    panel_params: "panel_view",
    axis: str,
    spec: GuideAxisSpec,
) -> None:
    view = getattr(panel_params, axis)
    if spec.kind == "manual":
        _apply_manual(ax, view, axis, spec.options)
    elif spec.kind == "colour":
        _apply_colour(ax, axis, spec.options)
    elif spec.kind == "minor":
        _apply_minor(ax, view, axis, spec.options)
    elif spec.kind == "logticks":
        _apply_logticks(ax, view, axis, spec.options)
    elif spec.kind == "truncated":
        _apply_truncated(ax, view, axis, spec.options)
    elif spec.kind == "scalebar":
        _apply_scalebar(ax, axis, spec.options)
    elif spec.kind == "nested":
        _apply_nested(ax, view, axis, spec.options)
    elif spec.kind == "dendro":
        _apply_dendro(ax, view, axis, spec.options)


def _apply_manual(
    ax: "Axes",
    view: "scale_view",
    axis: str,
    options: dict[str, Any],
) -> None:
    breaks = _option_or_view(options, "breaks", view.breaks)
    labels = _option_or_view(options, "labels", view.labels)
    _set_major_ticks(ax, axis, breaks, labels)
    _style_major_labels(
        ax,
        axis,
        colours=_first_non_none(
            options.get("label_colour"),
            options.get("label_color"),
        ),
        sizes=options.get("label_size"),
        angle=options.get("angle"),
    )
    _apply_axis_colour(ax, axis, options)
    if "trunc_lower" in options or "trunc_upper" in options:
        _apply_truncated(ax, view, axis, options)


def _apply_colour(ax: "Axes", axis: str, options: dict[str, Any]) -> None:
    colours = _first_non_none(options.get("colours"), options.get("colors"))
    _style_major_labels(ax, axis, colours=colours)
    _apply_axis_colour(ax, axis, options)


def _apply_minor(
    ax: "Axes",
    view: "scale_view",
    axis: str,
    options: dict[str, Any],
) -> None:
    breaks = options.get("minor_breaks", options.get("breaks"))
    if breaks is None:
        breaks = view.minor_breaks
    labels = options.get("labels")
    _set_minor_ticks(ax, axis, breaks, labels)


def _apply_logticks(
    ax: "Axes",
    view: "scale_view",
    axis: str,
    options: dict[str, Any],
) -> None:
    _remove_artists_with_gid(ax, "plotnine_extra_axis_logtick")
    sides = str(options.get("sides", "bl"))
    positions = _numeric_positions(view.minor_breaks)
    if not positions:
        positions = _numeric_positions(view.breaks)
    if not positions:
        lo, hi = _axis_limits(ax, axis)
        positions = np.linspace(lo, hi, 8).tolist()

    for pos in positions:
        for side in sides:
            if axis == "x" and side in {"b", "t"}:
                y0, y1 = (0, -0.035) if side == "b" else (1, 1.035)
                line = Line2D(
                    [pos, pos],
                    [y0, y1],
                    color="black",
                    linewidth=0.8,
                    transform=ax.get_xaxis_transform(),
                    clip_on=False,
                )
            elif axis == "y" and side in {"l", "r"}:
                x0, x1 = (-0.035, 0) if side == "l" else (1, 1.035)
                line = Line2D(
                    [x0, x1],
                    [pos, pos],
                    color="black",
                    linewidth=0.8,
                    transform=ax.get_yaxis_transform(),
                    clip_on=False,
                )
            else:
                continue
            line.set_gid("plotnine_extra_axis_logtick")
            ax.add_line(line)


def _apply_truncated(
    ax: "Axes",
    view: "scale_view",
    axis: str,
    options: dict[str, Any],
) -> None:
    lo, hi = _axis_limits(ax, axis)
    limits = (lo, hi)
    lower = _resolve_bound(options.get("trunc_lower"), limits, lo)
    upper = _resolve_bound(options.get("trunc_upper"), limits, hi)
    _spine(ax, axis, options).set_bounds(lower, upper)


def _apply_scalebar(
    ax: "Axes",
    axis: str,
    options: dict[str, Any],
) -> None:
    _remove_artists_with_gid(ax, "plotnine_extra_axis_scalebar")
    size = float(options.get("size", 1.0))
    label = options.get("label")
    if axis == "x":
        lo, hi = ax.get_xlim()
        ylo, yhi = ax.get_ylim()
        start = lo + 0.05 * (hi - lo)
        y = ylo + 0.08 * (yhi - ylo)
        line = Line2D([start, start + size], [y, y], color="black")
        text_x, text_y = start + size / 2, y
        text_kwargs = {"ha": "center", "va": "bottom"}
    else:
        xlo, xhi = ax.get_xlim()
        lo, hi = ax.get_ylim()
        x = xlo + 0.08 * (xhi - xlo)
        start = lo + 0.05 * (hi - lo)
        line = Line2D([x, x], [start, start + size], color="black")
        text_x, text_y = x, start + size / 2
        text_kwargs = {"ha": "left", "va": "center", "rotation": 90}
    line.set_gid("plotnine_extra_axis_scalebar")
    ax.add_line(line)
    if label:
        text = ax.text(text_x, text_y, str(label), **text_kwargs)
        text.set_gid("plotnine_extra_axis_scalebar")


def _apply_nested(
    ax: "Axes",
    view: "scale_view",
    axis: str,
    options: dict[str, Any],
) -> None:
    _remove_artists_with_gid(ax, "plotnine_extra_axis_nested_line")
    delim = str(options.get("delim", "_"))
    labels = ["\n".join(str(label).split(delim)) for label in view.labels]
    _set_major_ticks(ax, axis, view.breaks, labels)
    if options.get("nest_line", True) and len(view.breaks) >= 2:
        if axis == "x":
            line = Line2D(
                [0.05, 0.95],
                [-0.16, -0.16],
                color="black",
                linewidth=0.8,
                transform=ax.transAxes,
                clip_on=False,
            )
        else:
            line = Line2D(
                [-0.16, -0.16],
                [0.05, 0.95],
                color="black",
                linewidth=0.8,
                transform=ax.transAxes,
                clip_on=False,
            )
        line.set_gid("plotnine_extra_axis_nested_line")
        ax.add_line(line)


def _apply_dendro(
    ax: "Axes",
    view: "scale_view",
    axis: str,
    options: dict[str, Any],
) -> None:
    _remove_artists_with_gid(ax, "plotnine_extra_axis_dendro")
    positions = _numeric_positions(view.breaks)
    if len(positions) < 2:
        return
    pos_min, pos_max = min(positions), max(positions)
    mid = (pos_min + pos_max) / 2
    if axis == "x":
        coords = [
            ([pos_min, pos_min, mid], [1.02, 1.08, 1.08]),
            ([mid, pos_max, pos_max], [1.08, 1.08, 1.02]),
        ]
        transform = ax.get_xaxis_transform()
    else:
        coords = [
            ([1.02, 1.08, 1.08], [pos_min, pos_min, mid]),
            ([1.08, 1.08, 1.02], [mid, pos_max, pos_max]),
        ]
        transform = ax.get_yaxis_transform()
    for xs, ys in coords:
        line = Line2D(
            xs,
            ys,
            color="black",
            linewidth=0.8,
            transform=transform,
            clip_on=False,
        )
        line.set_gid("plotnine_extra_axis_dendro")
        ax.add_line(line)


def _legend_layer_text_colours(guide_obj: guide_stringlegend) -> list[str]:
    for col in ("color", "colour", "fill"):
        if col in guide_obj.key.columns:
            values = _valid_colour_values(guide_obj.key[col])
            if values is not None:
                return values
    for params in guide_obj._layer_parameters:
        for col in ("color", "colour", "fill"):
            if col in params.data.columns:
                values = _valid_colour_values(params.data[col])
                if values is not None:
                    return values
    return ["black"] * len(guide_obj.key)


def _valid_colour_values(values: Any) -> list[str] | None:
    colours = [str(value) for value in values]
    invalid = {"none", "nan", "nat", ""}
    if colours and not all(value.lower() in invalid for value in colours):
        return colours
    return None


def _axis_from_position(position: Any, default: str) -> str:
    if position in {"left", "right"}:
        return "y"
    if position in {"top", "bottom"}:
        return "x"
    return default


def _option_or_view(
    options: dict[str, Any],
    key: str,
    default: Any,
) -> Any:
    value = options.get(key)
    return default if value is None else value


def _first_non_none(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def _remove_artists_with_gid(ax: "Axes", gid: str) -> None:
    for artist in list(ax.findobj(lambda artist: artist.get_gid() == gid)):
        artist.remove()


def _set_major_ticks(
    ax: "Axes",
    axis: str,
    breaks: Any,
    labels: Any,
) -> None:
    if axis == "x":
        ax.set_xticks(breaks, labels)
    else:
        ax.set_yticks(breaks, labels)


def _set_minor_ticks(
    ax: "Axes",
    axis: str,
    breaks: Any,
    labels: Any | None,
) -> None:
    break_values = [float(value) for value in breaks]
    _remove_minor_positions_from_major_ticks(ax, axis, break_values)
    if axis == "x":
        ax.set_xticks(break_values, minor=True)
        if labels is not None:
            ax.set_xticklabels(labels, minor=True)
        ax.tick_params(axis="x", which="minor", bottom=True)
    else:
        ax.set_yticks(break_values, minor=True)
        if labels is not None:
            ax.set_yticklabels(labels, minor=True)
        ax.tick_params(axis="y", which="minor", left=True)


def _remove_minor_positions_from_major_ticks(
    ax: "Axes",
    axis: str,
    minor_positions: list[float],
) -> None:
    if not minor_positions:
        return
    if axis == "x":
        locs = list(ax.get_xticks())
        labels = [text.get_text() for text in ax.get_xticklabels()]
        setter = ax.set_xticks
    else:
        locs = list(ax.get_yticks())
        labels = [text.get_text() for text in ax.get_yticklabels()]
        setter = ax.set_yticks

    keep_locs = []
    keep_labels = []
    for loc, label in zip(locs, labels):
        if not any(np.isclose(loc, minor) for minor in minor_positions):
            keep_locs.append(loc)
            keep_labels.append(label)
    setter(keep_locs, keep_labels)


def _style_major_labels(
    ax: "Axes",
    axis: str,
    *,
    colours: Any | None = None,
    sizes: Any | None = None,
    angle: Any | None = None,
) -> None:
    labels = ax.get_xticklabels() if axis == "x" else ax.get_yticklabels()
    for i, text in enumerate(labels):
        if colours is not None:
            text.set_color(_indexed(colours, i))
        if sizes is not None:
            text.set_fontsize(_indexed(sizes, i))
        if angle is not None:
            text.set_rotation(angle)


def _apply_axis_colour(
    ax: "Axes",
    axis: str,
    options: dict[str, Any],
) -> None:
    colour = options.get("axis_colour", options.get("axis_color"))
    if colour is None:
        return
    _spine(ax, axis, options).set_color(colour)
    ax.tick_params(axis=axis, color=colour)


def _spine(
    ax: "Axes",
    axis: str,
    options: dict[str, Any],
):
    position = options.get("position")
    if axis == "x":
        return ax.spines["top" if position == "top" else "bottom"]
    return ax.spines["right" if position == "right" else "left"]


def _axis_limits(ax: "Axes", axis: str) -> tuple[float, float]:
    return ax.get_xlim() if axis == "x" else ax.get_ylim()


def _resolve_bound(value: Any, limits: tuple[float, float], default: float):
    if value is None:
        return default
    if callable(value):
        return value(limits)
    return value


def _indexed(value: Any, i: int) -> Any:
    if isinstance(value, str) or not hasattr(value, "__iter__"):
        return value
    seq = list(value)
    if not seq:
        return value
    return seq[min(i, len(seq) - 1)]


def _numeric_positions(values: Any) -> list[float]:
    try:
        return [float(v) for v in values if pd.notna(v)]
    except (TypeError, ValueError):
        return []
