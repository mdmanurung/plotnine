"""
Named colour tables inspired by the R ggthemes package.

The tables are intentionally small, dependency-free tuples used by the
ggthemes scale helpers.  Names are normalized by :func:`ggthemes_palette`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Mapping


GGTHEMES_PALETTES: dict[str, tuple[str, ...]] = {
    "colorblind": (
        "#000000",
        "#E69F00",
        "#56B4E9",
        "#009E73",
        "#F0E442",
        "#0072B2",
        "#D55E00",
        "#CC79A7",
    ),
    "economist": (
        "#6794A7",
        "#014D64",
        "#01A2D9",
        "#7AD2F6",
        "#00887D",
        "#76C0C1",
        "#7C260B",
        "#EE8F71",
        "#ADADAD",
    ),
    "excel": (
        "#9999FF",
        "#993366",
        "#FFFFCC",
        "#CCFFFF",
        "#660066",
        "#FF8080",
        "#0066CC",
        "#CCCCFF",
        "#000080",
        "#FF00FF",
    ),
    "few": (
        "#000000",
        "#E69F00",
        "#56B4E9",
        "#009E73",
        "#F0E442",
        "#0072B2",
        "#D55E00",
        "#CC79A7",
    ),
    "fivethirtyeight": (
        "#30A2DA",
        "#FC4F30",
        "#E5AE38",
        "#6D904F",
        "#8B8B8B",
    ),
    "gdocs": (
        "#3366CC",
        "#DC3912",
        "#FF9900",
        "#109618",
        "#990099",
        "#0099C6",
        "#DD4477",
        "#66AA00",
        "#B82E2E",
        "#316395",
    ),
    "hc": (
        "#7CB5EC",
        "#434348",
        "#90ED7D",
        "#F7A35C",
        "#8085E9",
        "#F15C80",
        "#E4D354",
        "#2B908F",
        "#F45B5B",
        "#91E8E1",
    ),
    "highcharts": (
        "#7CB5EC",
        "#434348",
        "#90ED7D",
        "#F7A35C",
        "#8085E9",
        "#F15C80",
        "#E4D354",
        "#2B908F",
        "#F45B5B",
        "#91E8E1",
    ),
    "solarized": (
        "#268BD2",
        "#2AA198",
        "#859900",
        "#B58900",
        "#CB4B16",
        "#DC322F",
        "#D33682",
        "#6C71C4",
    ),
    "stata": (
        "#1A476F",
        "#90353B",
        "#55752F",
        "#E37E00",
        "#6E8E84",
        "#C10534",
        "#938DD2",
        "#CAC27E",
        "#A0522D",
        "#7B92A8",
    ),
    "tableau": (
        "#4E79A7",
        "#F28E2B",
        "#E15759",
        "#76B7B2",
        "#59A14F",
        "#EDC948",
        "#B07AA1",
        "#FF9DA7",
        "#9C755F",
        "#BAB0AC",
    ),
    "wsj": (
        "#0073CF",
        "#FFB100",
        "#D65F00",
        "#850000",
        "#5B6770",
        "#4D772D",
        "#BFA08B",
        "#6B5B95",
    ),
}


_TABLEAU_VARIANTS: dict[str, tuple[str, ...]] = {
    "tableau 10": GGTHEMES_PALETTES["tableau"],
    "tableau 20": (
        "#4E79A7",
        "#A0CBE8",
        "#F28E2B",
        "#FFBE7D",
        "#59A14F",
        "#8CD17D",
        "#B6992D",
        "#F1CE63",
        "#499894",
        "#86BCB6",
        "#E15759",
        "#FF9D9A",
        "#79706E",
        "#BAB0AC",
        "#D37295",
        "#FABFD2",
        "#B07AA1",
        "#D4A6C8",
        "#9D7660",
        "#D7B5A6",
    ),
    "color blind": (
        "#1170AA",
        "#FC7D0B",
        "#A3ACB9",
        "#57606C",
        "#5FA2CE",
        "#C85200",
        "#7B848F",
        "#A3C9E2",
        "#FFBC79",
        "#C8D0D9",
    ),
}


def _normalize_name(name: str) -> str:
    return name.strip().lower().replace("_", " ").replace("-", " ")


def _lookup_variant(
    name: str,
    palette: str | None,
    variants: "Mapping[str, tuple[str, ...]]",
) -> tuple[str, ...]:
    if palette is None:
        return GGTHEMES_PALETTES[name]
    key = _normalize_name(palette)
    try:
        return variants[key]
    except KeyError as exc:
        raise ValueError(
            f"Unknown {name} palette {palette!r}. "
            f"Known variants: {sorted(variants)}."
        ) from exc


def _interpolate_colors(cols: tuple[str, ...], k: int) -> list[str]:
    import matplotlib as mpl

    rgb = np.array([mpl.colors.to_rgb(c) for c in cols])
    xs_old = np.linspace(0, 1, len(cols))
    xs_new = np.linspace(0, 1, k)
    out = np.column_stack(
        [np.interp(xs_new, xs_old, rgb[:, i]) for i in range(3)]
    )
    return [mpl.colors.to_hex(row).upper() for row in out]


def ggthemes_palette(
    name: str,
    n: int | None = None,
    *,
    palette: str | None = None,
) -> list[str]:
    """
    Return colours from a ggthemes-compatible named palette.

    Parameters
    ----------
    name : str
        Palette family name. Supported families include ``colorblind``,
        ``tableau``, ``economist``, ``excel``, ``few``,
        ``fivethirtyeight``, ``gdocs``, ``hc`` / ``highcharts``,
        ``solarized``, ``stata`` and ``wsj``.
    n : int, optional
        Number of colours. If omitted, the full palette is returned. If
        larger than the palette length, colours are interpolated.
    palette : str, optional
        Variant name for families that support variants. Currently used
        by ``tableau``.
    """
    normalized = _normalize_name(name)
    normalized = normalized.replace(" ", "")
    if normalized == "highcharts":
        normalized = "hc"

    if normalized == "tableau":
        cols = _lookup_variant("tableau", palette, _TABLEAU_VARIANTS)
    else:
        try:
            cols = GGTHEMES_PALETTES[normalized]
        except KeyError as exc:
            raise ValueError(
                f"Unknown ggthemes palette {name!r}. "
                f"Known names: {sorted(GGTHEMES_PALETTES)}."
            ) from exc
        if palette is not None:
            raise ValueError(
                f"Palette variants are not supported for {name!r}."
            )

    if n is None:
        return list(cols)
    if n <= len(cols):
        return list(cols[:n])
    return _interpolate_colors(cols, n)
