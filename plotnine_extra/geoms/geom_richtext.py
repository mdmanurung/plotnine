"""
``geom_richtext``: text labels with rich formatting and box
styling, ported from R's ``ggtext::geom_richtext``.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from plotnine._utils import to_rgba
from plotnine.doctools import document
from plotnine.geoms.geom_text import geom_text

if TYPE_CHECKING:
    from typing import Any

    import pandas as pd
    from matplotlib.axes import Axes
    from matplotlib.offsetbox import DrawingArea
    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.layer import layer


_aes = geom_text.DEFAULT_AES.copy()
_aes.update(
    {
        "fill": "white",
    }
)

_params = geom_text.DEFAULT_PARAMS.copy()
_params.update(
    {
        "boxstyle": "round",
        "boxcolor": None,
        "label_padding": 0.25,
        "label_r": 0.15,
        "label_size": 0.7,
        "tooth_size": None,
        "text_color": None,
        "fill_alpha": None,
    }
)


def _parse_markdown(text: str) -> tuple[str, dict[str, Any]]:
    """
    Parse minimal markdown in *text* and return the cleaned
    string together with any text-property overrides.

    Supported syntax
    ----------------
    - ``**bold**``: fontweight="bold"
    - ``*italic*``: fontstyle="italic"
    - ``<br>`` / ``<br/>``: newline
    - ``<sup>...</sup>``: superscript (via mathtext ``$^{...}$``)
    - ``<sub>...</sub>``: subscript  (via mathtext ``$_{...}$``)

    Returns the cleaned text and a dict of matplotlib text
    property overrides (``fontweight``, ``fontstyle``).
    """
    props: dict[str, Any] = {}

    # <br> / <br/>: newline
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

    # <sup>...</sup>: mathtext superscript
    text = re.sub(
        r"<sup>(.*?)</sup>",
        r"$^{\1}$",
        text,
        flags=re.IGNORECASE,
    )

    # <sub>...</sub>: mathtext subscript
    text = re.sub(
        r"<sub>(.*?)</sub>",
        r"$_{\1}$",
        text,
        flags=re.IGNORECASE,
    )

    # **bold**: set weight and strip markers
    if re.search(r"\*\*(.+?)\*\*", text):
        # If the entire text is bold, set the property
        m = re.fullmatch(r"\*\*(.+)\*\*", text.strip())
        if m:
            text = m.group(1)
            props["fontweight"] = "bold"
        else:
            # Partial bold cannot be drawn inline in plain matplotlib,
            # so just strip the markers
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)

    # *italic*: same approach
    if re.search(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", text):
        m = re.fullmatch(r"\*(.+)\*", text.strip())
        if m:
            text = m.group(1)
            props["fontstyle"] = "italic"
        else:
            text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)

    return text, props


@document
class geom_richtext(geom_text):
    """
    Text labels with a background box and basic rich-text
    formatting

    An enhanced version of :class:`~plotnine.geom_label` that
    supports a subset of markdown and HTML formatting in label
    text:

    * ``**bold**`` → bold text
    * ``*italic*`` → italic text
    * ``<br>`` → line break
    * ``<sup>x</sup>`` → superscript
    * ``<sub>x</sub>`` → subscript

    {usage}

    Parameters
    ----------
    {common_parameters}
    boxstyle : str
        Matplotlib box style (``"round"``, ``"square"``, etc.).
    boxcolor : str | None
        Border colour of the label box.  ``None`` uses the text
        colour.
    label_padding : float
        Padding inside the box.
    label_r : float
        Corner-rounding radius (for round box styles).
    label_size : float
        Border line width of the box.
    text_color : str | None
        Override text colour independently of the box colour.
    fill_alpha : float | None
        Alpha for the fill colour (separate from text alpha).

    See Also
    --------
    plotnine.geom_label
    plotnine.geom_text
    """

    DEFAULT_AES = _aes
    DEFAULT_PARAMS = _params

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        data = coord.transform(data, panel_params)
        zorder = params["zorder"]

        # Text and fill colours
        text_alpha = data["alpha"]
        color = to_rgba(data["color"], text_alpha)

        fill_alpha = params.get("fill_alpha")
        if fill_alpha is not None:
            fill = to_rgba(data["fill"], fill_alpha)
        else:
            fill = to_rgba(data["fill"], text_alpha)

        if isinstance(fill, tuple):
            fill = [list(fill)] * len(data["x"])

        # Build box style string
        tokens = [
            params["boxstyle"],
            f"pad={params['label_padding']}",
        ]
        if params["boxstyle"] in {"round", "round4"}:
            tokens.append(f"rounding_size={params['label_r']}")
        elif params["boxstyle"] in ("roundtooth", "sawtooth"):
            tooth = params.get("tooth_size")
            if tooth is not None:
                tokens.append(f"tooth_size={tooth}")
        boxstyle = ",".join(tokens)
        bbox_base = {
            "linewidth": params["label_size"],
            "boxstyle": boxstyle,
        }

        text_color_override = params.get("text_color")

        for i in range(len(data)):
            row = data.iloc[i]
            label = str(row["label"])

            # Parse simple markdown
            label, md_props = _parse_markdown(label)

            kw: dict[str, Any] = {
                "x": row["x"],
                "y": row["y"],
                "s": label,
                "color": (
                    text_color_override
                    if text_color_override
                    else color
                    if isinstance(color, tuple)
                    else color[i]
                ),
                "size": row["size"],
                "rotation": row["angle"],
                "linespacing": row["lineheight"],
                "ha": row["ha"],
                "va": row["va"],
                "fontweight": md_props.get("fontweight", row["fontweight"]),
                "fontstyle": md_props.get("fontstyle", row["fontstyle"]),
                "zorder": zorder,
                "clip_on": True,
                "rasterized": params.get("raster", False),
            }

            if row.get("family") is not None:
                kw["family"] = row["family"]

            bbox = dict(bbox_base)
            bbox["edgecolor"] = (
                params["boxcolor"]
                if params["boxcolor"] is not None
                else kw["color"]
            )
            bbox["facecolor"] = fill if isinstance(fill, tuple) else fill[i]
            kw["bbox"] = bbox

            txt = ax.text(**kw)
            if params.get("path_effects"):
                txt.set_path_effects(params["path_effects"])

    @staticmethod
    def draw_legend(
        data: pd.Series[Any],
        da: DrawingArea,
        lyr: layer,
    ) -> DrawingArea:
        from matplotlib.patches import Rectangle

        fill = to_rgba(data["fill"], data["alpha"])

        if data["fill"]:
            rect = Rectangle(
                (0, 0),
                width=da.width,
                height=da.height,
                linewidth=0,
                facecolor=fill,
                capstyle="projecting",
            )
            da.add_artist(rect)
        return geom_text.draw_legend(data, da, lyr)
