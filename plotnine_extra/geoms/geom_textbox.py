"""
``geom_textbox``: text box with word wrapping,
ported from R's ``ggtext::geom_textbox``.
"""

from __future__ import annotations

import textwrap
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

from .geom_richtext import _parse_markdown

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
        "label_padding": 0.4,
        "label_r": 0.15,
        "label_size": 0.5,
        "tooth_size": None,
        "text_width": 30,
        "halign": "left",
        "valign": "top",
    }
)


@document
class geom_textbox(geom_text):
    """
    Text box with word wrapping

    Draws a box of defined size containing text that is
    automatically wrapped at word boundaries.  Supports
    the same basic markdown formatting as
    :class:`~plotnine_extra.geoms.geom_richtext.geom_richtext`.

    {usage}

    Parameters
    ----------
    {common_parameters}
    boxstyle : str
        Matplotlib box style (``"round"``, ``"square"``, etc.).
    boxcolor : str | None
        Border colour of the text box.
    label_padding : float
        Inner padding around the text.
    label_r : float
        Corner-rounding radius.
    label_size : float
        Border line width.
    text_width : int
        Maximum number of characters per line for word wrapping.
    halign : str
        Horizontal text alignment inside the box: ``"left"``
        (default), ``"center"``, or ``"right"``.
    valign : str
        Vertical text alignment inside the box: ``"top"``
        (default), ``"center"``, or ``"bottom"``.

    See Also
    --------
    plotnine_extra.geoms.geom_richtext.geom_richtext
    plotnine.geom_label
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
        text_width = params.get("text_width", 30)

        color = to_rgba(data["color"], data["alpha"])
        fill = to_rgba(data["fill"], data["alpha"])
        if isinstance(fill, tuple):
            fill = [list(fill)] * len(data["x"])

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

        # Map halign/valign to matplotlib ha/va
        halign = params.get("halign", "left")
        valign = params.get("valign", "top")
        va_map = {"top": "top", "center": "center", "bottom": "bottom"}
        va = va_map.get(valign, "top")

        for i in range(len(data)):
            row = data.iloc[i]
            label = str(row["label"])

            # Parse markdown
            label, md_props = _parse_markdown(label)

            # Word-wrap the text
            label = textwrap.fill(label, width=text_width)

            kw: dict[str, Any] = {
                "x": row["x"],
                "y": row["y"],
                "s": label,
                "color": (color if isinstance(color, tuple) else color[i]),
                "size": row["size"],
                "rotation": row["angle"],
                "linespacing": row["lineheight"],
                "ha": halign,
                "va": va,
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
