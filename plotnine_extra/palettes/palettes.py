"""
Palette helpers ported from ggpubr.

The user-facing entry point is :func:`get_palette`. The
``color_palette`` / ``fill_palette`` and ``gradient_color`` /
``gradient_fill`` helpers return ready-to-add plotnine scales
that draw their colours from the named palettes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ._ggsci import BREWER_PALETTES, GGSCI_PALETTES
from ._ggthemes import GGTHEMES_PALETTES, ggthemes_palette

if TYPE_CHECKING:
    from typing import Sequence

__all__ = (
    "get_palette",
    "color_palette",
    "fill_palette",
    "set_palette",
    "change_palette",
    "gradient_color",
    "gradient_fill",
    "show_point_shapes",
    "show_line_types",
)


_DEFAULT_GREY_GRADIENT = ("#FFFFFF", "#000000")
_DEFAULT_VIRIDIS = (
    "#440154",
    "#482878",
    "#3E4A89",
    "#31688E",
    "#26828E",
    "#1F9E89",
    "#35B779",
    "#6DCD59",
    "#B4DE2C",
    "#FDE725",
)


def _resolve_palette(
    palette: "str | Sequence[str]",
) -> tuple[str, ...]:
    """Return a tuple of hex colours for the given name."""
    if not isinstance(palette, str):
        return tuple(palette)
    name = palette
    if name in GGSCI_PALETTES:
        return GGSCI_PALETTES[name]
    if name in BREWER_PALETTES:
        return BREWER_PALETTES[name]
    if name in GGTHEMES_PALETTES:
        return tuple(ggthemes_palette(name))
    if name.lower() in {"grey", "gray"}:
        return _DEFAULT_GREY_GRADIENT
    if name.lower() == "viridis":
        return _DEFAULT_VIRIDIS
    # Try matplotlib qualitative / sequential cmaps
    try:
        import matplotlib as mpl

        cmap = mpl.colormaps[name]
        n = getattr(cmap, "N", 256)
        return tuple(
            mpl.colors.to_hex(cmap(i / max(1, n - 1)))
            for i in range(min(n, 12))
        )
    except (KeyError, ValueError) as exc:
        raise ValueError(
            f"Unknown palette {palette!r}. Known names: "
            f"ggsci ({sorted(GGSCI_PALETTES)}), "
            f"brewer ({sorted(BREWER_PALETTES)}), "
            f"or any matplotlib colormap."
        ) from exc


def get_palette(
    palette: "str | Sequence[str]" = "default",
    k: int = 8,
) -> list[str]:
    """
    Return ``k`` colours sampled from a named palette.

    Parameters
    ----------
    palette : str or sequence
        Either one of the names in
        :mod:`plotnine_extra.palettes._ggsci`, the strings
        ``"default"`` / ``"grey"`` / ``"viridis"``, a matplotlib
        colormap name, or a custom sequence of colours.
    k : int, default 8
        Number of colours to return. If ``k`` is larger than the
        underlying palette, colours are linearly interpolated.

    Returns
    -------
    list of str
        Hex colour strings of length ``k``.
    """
    if palette == "default":
        cols = GGSCI_PALETTES["npg"]
    else:
        cols = _resolve_palette(palette)
    if len(cols) >= k:
        return list(cols[:k])
    # Interpolate to reach k colours
    return _interpolate_colors(cols, k)


def _interpolate_colors(cols: "Sequence[str]", k: int) -> list[str]:
    import matplotlib as mpl

    rgb = np.array([mpl.colors.to_rgb(c) for c in cols])
    xs_old = np.linspace(0, 1, len(cols))
    xs_new = np.linspace(0, 1, k)
    out = np.column_stack(
        [np.interp(xs_new, xs_old, rgb[:, i]) for i in range(3)]
    )
    return [mpl.colors.to_hex(row) for row in out]


def color_palette(
    palette: "str | Sequence[str]" = "default",
    **kwargs,
):
    """
    Return a discrete plotnine ``scale_color_manual`` using
    the named palette.
    """
    from plotnine import scale_color_manual

    cols = get_palette(palette, k=kwargs.pop("k", 12))
    return scale_color_manual(values=cols, **kwargs)


def fill_palette(
    palette: "str | Sequence[str]" = "default",
    **kwargs,
):
    """
    Return a discrete plotnine ``scale_fill_manual`` using
    the named palette.
    """
    from plotnine import scale_fill_manual

    cols = get_palette(palette, k=kwargs.pop("k", 12))
    return scale_fill_manual(values=cols, **kwargs)


def gradient_color(
    palette: "str | Sequence[str]" = "viridis",
    **kwargs,
):
    """
    Return a continuous plotnine ``scale_color_gradientn`` using
    the named palette.
    """
    from plotnine import scale_color_gradientn

    cols = list(_resolve_palette(palette))
    return scale_color_gradientn(colors=cols, **kwargs)


def gradient_fill(
    palette: "str | Sequence[str]" = "viridis",
    **kwargs,
):
    """
    Return a continuous plotnine ``scale_fill_gradientn`` using
    the named palette.
    """
    from plotnine import scale_fill_gradientn

    cols = list(_resolve_palette(palette))
    return scale_fill_gradientn(colors=cols, **kwargs)


def set_palette(plot, palette: "str | Sequence[str]"):
    """
    Add ``color_palette`` and ``fill_palette`` layers to ``plot``.
    """
    return plot + color_palette(palette) + fill_palette(palette)


def change_palette(plot, palette: "str | Sequence[str]"):
    """Alias of :func:`set_palette`."""
    return set_palette(plot, palette)


def show_point_shapes():
    """
    Return a small ``ggplot`` showing a set of matplotlib
    point shapes (mirrors ``ggpubr::show_point_shapes``).

    Uses matplotlib's string marker codes rather than R's
    integer shape codes. Integer shapes are not valid
    matplotlib markers and would crash the renderer.
    """
    import pandas as pd
    from plotnine import (
        aes,
        element_blank,
        geom_point,
        geom_text,
        ggplot,
        labs,
        scale_shape_identity,
        theme_minimal,
    )

    # Common matplotlib markers with a short descriptive label.
    shapes = [
        ("o", "circle"),
        ("s", "square"),
        ("^", "triangle_up"),
        ("v", "triangle_down"),
        ("D", "diamond"),
        ("P", "plus_filled"),
        ("X", "x_filled"),
        ("*", "star"),
        ("p", "pentagon"),
        ("h", "hexagon"),
        ("<", "triangle_left"),
        (">", "triangle_right"),
    ]
    n = len(shapes)
    rows = 4
    df = pd.DataFrame(
        {
            "shape": [s for s, _ in shapes],
            "x": [i % rows for i in range(n)],
            "y": [-(i // rows) for i in range(n)],
            "label": [f"{s!r}\n{name}" for s, name in shapes],
        }
    )
    return (
        ggplot(df, aes("x", "y"))
        + geom_point(aes(shape="shape"), size=6, fill="#7F7F7F")
        + geom_text(aes(label="label"), nudge_y=-0.4, size=8)
        + scale_shape_identity()
        + labs(title="Point shapes", x=None, y=None)
        + theme_minimal()
        + _no_axes_theme(element_blank)
    )


def show_line_types():
    """
    Return a small ``ggplot`` showing the available matplotlib
    line types (mirrors ``ggpubr::show_line_types``).
    """
    import pandas as pd
    from plotnine import (
        aes,
        element_blank,
        geom_segment,
        geom_text,
        ggplot,
        labs,
        scale_linetype_identity,
        theme_minimal,
    )

    types = ("solid", "dashed", "dotted", "dashdot")
    df = pd.DataFrame(
        {
            "linetype": types,
            "x": [0] * len(types),
            "xend": [1] * len(types),
            "y": list(range(len(types))),
            "yend": list(range(len(types))),
        }
    )
    return (
        ggplot(df)
        + geom_segment(
            aes(
                x="x",
                xend="xend",
                y="y",
                yend="yend",
                linetype="linetype",
            ),
            size=1,
        )
        + geom_text(
            aes(x="xend", y="y", label="linetype"),
            nudge_x=0.05,
            ha="left",
        )
        + scale_linetype_identity()
        + labs(title="Line types", x=None, y=None)
        + theme_minimal()
        + _no_axes_theme(element_blank)
    )


def _no_axes_theme(element_blank):
    from plotnine import theme

    return theme(
        axis_text=element_blank(),
        axis_ticks=element_blank(),
        panel_grid=element_blank(),
    )
