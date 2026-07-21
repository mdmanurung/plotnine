"""
Plot composition, re-exported from plotnine.

plotnine ships plot composition natively: the composing operators
(``|``, ``/``, ``-``, ``+``) live on ``plotnine.ggplot`` and the composition
objects live in ``plotnine.composition``. plotnine-extra does **not** vendor
its own copy -- doing so caused a namespace collision where ``p1 | p2``
produced plotnine's ``Beside`` while ``plot_layout`` came from plotnine-extra,
and mixing the two crashed.

``Compose``, ``Beside``, ``Stack`` and ``plot_spacer`` exist in every supported
plotnine (>=0.15.3) and are re-exported directly. ``Wrap``, ``plot_layout`` and
``plot_annotation`` were added to plotnine in 0.16; on older plotnine they
resolve to a stub that raises a clear, actionable error, so ``plotnine_extra``
still imports cleanly on stable plotnine and only the extras are gated.
"""

from __future__ import annotations

from plotnine.composition import Beside, Compose, Stack, plot_spacer

_MIN_PLOTNINE = "0.16"


def _requires_plotnine_016(name: str):
    """Build a placeholder for a composition feature added in plotnine 0.16."""

    def _stub(*args, **kwargs):
        import plotnine

        raise RuntimeError(
            f"plotnine_extra.{name} requires plotnine>={_MIN_PLOTNINE}, but "
            f"plotnine {plotnine.__version__} is installed. Upgrade plotnine "
            f"to use composition layouts and annotations, e.g. "
            f"`pip install -U 'plotnine>={_MIN_PLOTNINE}'`."
        )

    _stub.__name__ = name
    _stub.__qualname__ = name
    return _stub


try:
    from plotnine.composition import Wrap, plot_annotation, plot_layout
except ImportError:
    Wrap = _requires_plotnine_016("Wrap")
    plot_annotation = _requires_plotnine_016("plot_annotation")
    plot_layout = _requires_plotnine_016("plot_layout")

__all__ = (
    "Compose",
    "Stack",
    "Beside",
    "Wrap",
    "plot_annotation",
    "plot_layout",
    "plot_spacer",
)
