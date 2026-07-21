"""
Plot composition, re-exported from plotnine.

plotnine ships plot composition natively (since 0.16.0a1): the composing
operators (``|``, ``/``, ``-``, ``+``) live on ``plotnine.ggplot`` and the
composition objects live in ``plotnine.composition``. plotnine-extra therefore
does **not** vendor its own copy -- doing so caused a namespace collision where
``p1 | p2`` produced plotnine's ``Beside`` while ``plot_layout`` came from
plotnine-extra, and mixing the two crashed.

This module re-exports plotnine's composition API unchanged so that existing
imports such as ``from plotnine_extra import plot_layout`` keep working while
the operators and the objects they build always come from the same source.
"""

from plotnine.composition import (
    Beside,
    Compose,
    Stack,
    Wrap,
    plot_annotation,
    plot_layout,
    plot_spacer,
)

__all__ = (
    "Compose",
    "Stack",
    "Beside",
    "Wrap",
    "plot_annotation",
    "plot_layout",
    "plot_spacer",
)
