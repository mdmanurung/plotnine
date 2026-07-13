"""
Discrete colour and fill scales for ggthemes-style palettes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..palettes import ggthemes_palette

if TYPE_CHECKING:
    from collections.abc import Callable


__all__ = (
    "scale_color_colorblind",
    "scale_colour_colorblind",
    "scale_fill_colorblind",
    "scale_color_economist",
    "scale_colour_economist",
    "scale_fill_economist",
    "scale_color_excel",
    "scale_colour_excel",
    "scale_fill_excel",
    "scale_color_few",
    "scale_colour_few",
    "scale_fill_few",
    "scale_color_fivethirtyeight",
    "scale_colour_fivethirtyeight",
    "scale_fill_fivethirtyeight",
    "scale_color_gdocs",
    "scale_colour_gdocs",
    "scale_fill_gdocs",
    "scale_color_hc",
    "scale_colour_hc",
    "scale_fill_hc",
    "scale_color_highcharts",
    "scale_colour_highcharts",
    "scale_fill_highcharts",
    "scale_color_solarized",
    "scale_colour_solarized",
    "scale_fill_solarized",
    "scale_color_stata",
    "scale_colour_stata",
    "scale_fill_stata",
    "scale_color_tableau",
    "scale_colour_tableau",
    "scale_fill_tableau",
    "scale_color_wsj",
    "scale_colour_wsj",
    "scale_fill_wsj",
)


def _manual_scale(
    name: str,
    aesthetic: str,
    *,
    k: int | None = None,
    palette: str | None = None,
    **kwargs,
):
    cols = ggthemes_palette(name, n=k, palette=palette)
    if aesthetic == "fill":
        from plotnine import scale_fill_manual

        return scale_fill_manual(values=cols, **kwargs)

    from plotnine import scale_color_manual

    return scale_color_manual(values=cols, **kwargs)


def _make_scale(name: str, aesthetic: str) -> "Callable":
    def scale(
        *,
        k: int | None = None,
        palette: str | None = None,
        **kwargs,
    ):
        return _manual_scale(
            name,
            aesthetic,
            k=k,
            palette=palette,
            **kwargs,
        )

    scale.__name__ = f"scale_{aesthetic}_{name}"
    scale.__doc__ = (
        f"Return a discrete plotnine {aesthetic} scale using the "
        f"ggthemes {name!r} palette."
    )
    return scale


scale_color_colorblind = _make_scale("colorblind", "color")
scale_colour_colorblind = scale_color_colorblind
scale_fill_colorblind = _make_scale("colorblind", "fill")

scale_color_economist = _make_scale("economist", "color")
scale_colour_economist = scale_color_economist
scale_fill_economist = _make_scale("economist", "fill")

scale_color_excel = _make_scale("excel", "color")
scale_colour_excel = scale_color_excel
scale_fill_excel = _make_scale("excel", "fill")

scale_color_few = _make_scale("few", "color")
scale_colour_few = scale_color_few
scale_fill_few = _make_scale("few", "fill")

scale_color_fivethirtyeight = _make_scale("fivethirtyeight", "color")
scale_colour_fivethirtyeight = scale_color_fivethirtyeight
scale_fill_fivethirtyeight = _make_scale("fivethirtyeight", "fill")

scale_color_gdocs = _make_scale("gdocs", "color")
scale_colour_gdocs = scale_color_gdocs
scale_fill_gdocs = _make_scale("gdocs", "fill")

scale_color_hc = _make_scale("hc", "color")
scale_colour_hc = scale_color_hc
scale_fill_hc = _make_scale("hc", "fill")

scale_color_highcharts = scale_color_hc
scale_colour_highcharts = scale_colour_hc
scale_fill_highcharts = scale_fill_hc

scale_color_solarized = _make_scale("solarized", "color")
scale_colour_solarized = scale_color_solarized
scale_fill_solarized = _make_scale("solarized", "fill")

scale_color_stata = _make_scale("stata", "color")
scale_colour_stata = scale_color_stata
scale_fill_stata = _make_scale("stata", "fill")

scale_color_tableau = _make_scale("tableau", "color")
scale_colour_tableau = scale_color_tableau
scale_fill_tableau = _make_scale("tableau", "fill")

scale_color_wsj = _make_scale("wsj", "color")
scale_colour_wsj = scale_color_wsj
scale_fill_wsj = _make_scale("wsj", "fill")
