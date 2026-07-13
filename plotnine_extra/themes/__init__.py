"""
Theme elements and publication-ready themes.

``element_markdown`` and ``element_textbox_simple`` are ported
from R's ``ggtext``.

``element_markdown`` and ``element_textbox_simple`` extend
plotnine's ``element_text`` with convenience defaults and
markdown-aware parameter translation.

.. note::

   Full HTML/CSS rendering as in R's ggtext is not available
   because matplotlib does not support inline rich text.
   These elements provide the subset that *can* be expressed
   through matplotlib's text properties: bold, italic,
   background colour, and padding.
"""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Any, Literal, Sequence

from plotnine.themes.elements.element_text import element_text

from .styling import (  # noqa: E402
    bgcolor as bgcolor,
)
from .styling import (
    border as border,
)
from .styling import (
    font as font,
)
from .styling import (
    ggpar as ggpar,
)
from .styling import (
    grids as grids,
)
from .styling import (
    labs_pubr as labs_pubr,
)
from .styling import (
    rotate as rotate,
)
from .styling import (
    rotate_x_text as rotate_x_text,
)
from .styling import (
    rotate_y_text as rotate_y_text,
)
from .styling import (
    rremove as rremove,
)
from .styling import (
    xscale as xscale,
)
from .styling import (
    yscale as yscale,
)
from .theme_ggthemes import (
    theme_economist as theme_economist,
)
from .theme_ggthemes import (
    theme_few as theme_few,
)
from .theme_ggthemes import (
    theme_fivethirtyeight as theme_fivethirtyeight,
)
from .theme_ggthemes import (
    theme_tufte as theme_tufte,
)
from .theme_ggthemes import (
    theme_wsj as theme_wsj,
)
from .theme_pub import (  # noqa: E402
    clean_theme as clean_theme,
)
from .theme_pub import (
    theme_classic2 as theme_classic2,
)
from .theme_pub import (
    theme_clean as theme_clean,
)
from .theme_pub import (
    theme_cleveland as theme_cleveland,
)
from .theme_pub import (
    theme_nature as theme_nature,
)
from .theme_pub import (
    theme_poster as theme_poster,
)
from .theme_pub import (
    theme_pubclean as theme_pubclean,
)
from .theme_pub import (
    theme_pubr as theme_pubr,
)
from .theme_pub import (
    theme_scientific as theme_scientific,
)
from .theme_pub import (
    theme_transparent as theme_transparent,
)

if TYPE_CHECKING:
    from plotnine.themes.elements.margin import margin as Margin


class element_markdown(element_text):
    """
    Theme element for rendering text with markdown-style
    parameters

    A convenience wrapper around :class:`~plotnine.element_text`
    that accepts extra styling shortcuts inspired by R's
    ``ggtext::element_markdown``.

    Parameters
    ----------
    family : str
        Font family.
    style : str
        Font style (``"normal"``, ``"italic"``).
    weight : str | int
        Font weight (``"normal"``, ``"bold"``, etc.).
    color : str | tuple
        Text colour.
    size : float
        Font size.
    ha : str
        Horizontal alignment.
    va : str
        Vertical alignment.
    rotation : float
        Rotation angle in degrees.
    linespacing : float
        Line spacing multiplier.
    backgroundcolor : str | tuple
        Background colour behind the text.
    margin : dict | Margin
        Margin around the text.
    face : str
        Convenience shortcut: ``"bold"``, ``"italic"``,
        ``"bold.italic"``, or ``"plain"``.
    **kwargs :
        Extra matplotlib text properties.

    Notes
    -----
    R's ``element_markdown`` can render arbitrary inline
    HTML/CSS inside plot titles and labels.  matplotlib does
    not support this; only whole-element properties (colour,
    weight, style, background) are available.
    """

    def __init__(
        self,
        family: str | list[str] | None = None,
        style: str | Sequence[str] | None = None,
        weight: int | str | Sequence[int | str] | None = None,
        color: str | tuple | Sequence[str | tuple] | None = None,
        size: float | Sequence[float] | None = None,
        ha: (Literal["center", "left", "right"] | float | None) = None,
        va: (
            Literal[
                "center",
                "top",
                "bottom",
                "baseline",
                "center_baseline",
            ]
            | float
            | None
        ) = None,
        rotation: (
            Literal["vertical", "horizontal"] | float | Sequence[float] | None
        ) = None,
        linespacing: float | None = None,
        backgroundcolor: (str | tuple | Sequence[str | tuple] | None) = None,
        margin: "Margin | dict[str, Any] | None" = None,
        face: str | None = None,
        **kwargs: Any,
    ):
        # Translate 'face' shortcut
        if face is not None:
            if face == "bold":
                weight = weight or "bold"
            elif face == "italic":
                style = style or "italic"
            elif face == "bold.italic":
                weight = weight or "bold"
                style = style or "italic"
            elif face == "plain":
                weight = weight or "normal"
                style = style or "normal"

        # Accept ggplot2-style 'colour'
        with suppress(KeyError):
            color = color or kwargs.pop("colour")

        super().__init__(
            family=family,
            style=style,
            weight=weight,
            color=color,
            size=size,
            ha=ha,
            va=va,
            rotation=rotation,
            linespacing=linespacing,
            backgroundcolor=backgroundcolor,
            margin=margin,
            **kwargs,
        )


class element_textbox_simple(element_text):
    """
    Theme element for text rendered inside a box

    A convenience wrapper that sets sensible defaults for
    boxed text (transparent fill, no border, full width).
    Inspired by R's ``ggtext::element_textbox_simple``.

    Parameters
    ----------
    family : str
        Font family.
    style : str
        Font style.
    weight : str | int
        Font weight.
    color : str | tuple
        Text colour.
    size : float
        Font size.
    ha : str
        Horizontal alignment.
    va : str
        Vertical alignment.
    linespacing : float
        Line spacing (default ``1.2``).
    backgroundcolor : str | tuple
        Background colour.
    margin : dict | Margin
        Margin around the text.
    face : str
        Convenience shortcut: ``"bold"``, ``"italic"``,
        ``"bold.italic"``, or ``"plain"``.
    **kwargs :
        Extra matplotlib text properties.

    Notes
    -----
    In R, ``element_textbox_simple`` renders a word-wrapped
    text box.  In plotnine, word wrapping must be done at the
    data level (e.g. with ``textwrap.fill``).  This element
    applies the visual styling.
    """

    def __init__(
        self,
        family: str | list[str] | None = None,
        style: str | Sequence[str] | None = None,
        weight: int | str | Sequence[int | str] | None = None,
        color: str | tuple | Sequence[str | tuple] | None = None,
        size: float | Sequence[float] | None = None,
        ha: (Literal["center", "left", "right"] | float | None) = "left",
        va: (
            Literal[
                "center",
                "top",
                "bottom",
                "baseline",
                "center_baseline",
            ]
            | float
            | None
        ) = "top",
        linespacing: float | None = 1.2,
        backgroundcolor: (str | tuple | Sequence[str | tuple] | None) = None,
        margin: "Margin | dict[str, Any] | None" = None,
        face: str | None = None,
        **kwargs: Any,
    ):
        # Translate 'face' shortcut
        if face is not None:
            if face == "bold":
                weight = weight or "bold"
            elif face == "italic":
                style = style or "italic"
            elif face == "bold.italic":
                weight = weight or "bold"
                style = style or "italic"
            elif face == "plain":
                weight = weight or "normal"
                style = style or "normal"

        with suppress(KeyError):
            color = color or kwargs.pop("colour")

        super().__init__(
            family=family,
            style=style,
            weight=weight,
            color=color,
            size=size,
            ha=ha,
            va=va,
            linespacing=linespacing,
            backgroundcolor=backgroundcolor,
            margin=margin,
            **kwargs,
        )
