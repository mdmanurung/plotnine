"""
``coord_axes_inside``: draw the axes inside the panel.

Port of ``ggh4x::coord_axes_inside``. The R version repositions
the axis lines to a chosen origin inside the panel area; the
Python implementation here is a thin subclass of
:class:`coord_cartesian` that records the origin and a small
post-build hook for tweaking the matplotlib axes once the figure
has been drawn.

.. note::

    Because plotnine's tick / spine drawing is done directly
    inside ``facet.set_breaks_and_labels``, this class only
    captures the desired origin. Users should call
    :func:`apply_axes_inside` on the rendered ``ggplot.figure``
    *after* calling ``ggplot.draw()`` to actually move the
    spines. A future plotnine release that exposes a draw hook
    will let us automate this step.
"""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from plotnine.coords.coord_cartesian import coord_cartesian

if TYPE_CHECKING:
    from matplotlib.figure import Figure

__all__ = ("coord_axes_inside", "apply_axes_inside")


class coord_axes_inside(coord_cartesian):
    """
    Cartesian coordinates with axes drawn inside the panel.

    Parameters
    ----------
    xlim, ylim, expand
        Same as :class:`coord_cartesian`.
    xintercept : float, default 0
        x-position at which the y axis spine should sit.
    yintercept : float, default 0
        y-position at which the x axis spine should sit.
    labels_inside : bool, default False
        If ``True``, tick labels are drawn alongside the
        relocated spine; otherwise the standard outer labels
        are kept.

    Notes
    -----
    Plotnine 0.15/0.16 does not expose a post-draw hook on the
    coord class. This implementation therefore wraps
    :meth:`ggplot.draw` via ``__radd__`` so that
    :func:`apply_axes_inside` is invoked on the resulting
    matplotlib :class:`~matplotlib.figure.Figure` after
    plotnine finishes rendering. The standard axis spines are
    otherwise left alone by ``coord_cartesian``.
    """

    is_linear = True

    def __init__(
        self,
        xlim=None,
        ylim=None,
        expand: bool = True,
        xintercept: float = 0.0,
        yintercept: float = 0.0,
        labels_inside: bool = False,
    ):
        super().__init__(xlim=xlim, ylim=ylim, expand=expand)
        self.xintercept = xintercept
        self.yintercept = yintercept
        self.labels_inside = labels_inside

    def __radd__(self, other):
        # Attach the coord the normal plotnine way, then wrap
        # the ggplot's ``draw`` method so the spines get moved
        # once matplotlib finishes rendering.
        plot = super().__radd__(other)

        # Avoid wrapping the same ggplot twice (e.g. when the
        # user chains two coord_axes_inside calls).
        if getattr(plot.draw, "_axes_inside_wrapped", False):
            return plot

        orig_draw = plot.draw
        xintercept = self.xintercept
        yintercept = self.yintercept
        labels_inside = self.labels_inside

        @functools.wraps(orig_draw)
        def _wrapped_draw(*args, **kwargs):
            fig = orig_draw(*args, **kwargs)
            if fig is not None:
                apply_axes_inside(
                    fig,
                    xintercept=xintercept,
                    yintercept=yintercept,
                    labels_inside=labels_inside,
                )
            return fig

        _wrapped_draw._axes_inside_wrapped = True  # type: ignore[attr-defined]
        plot.draw = _wrapped_draw  # type: ignore[method-assign]
        return plot


def apply_axes_inside(
    figure: "Figure",
    xintercept: float = 0.0,
    yintercept: float = 0.0,
    labels_inside: bool = False,
) -> "Figure":
    """
    Reposition the axis spines of every ``Axes`` in ``figure``
    so that they cross at ``(xintercept, yintercept)``.

    This is the manual half of :class:`coord_axes_inside`.
    Call it after ``ggplot.draw()``::

        fig = (p + coord_axes_inside(xintercept=5)).draw(show=False)
        apply_axes_inside(fig, xintercept=5)
    """
    for ax in figure.axes:
        ax.spines["left"].set_position(("data", xintercept))
        ax.spines["bottom"].set_position(("data", yintercept))
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        if labels_inside:
            ax.xaxis.set_ticks_position("bottom")
            ax.yaxis.set_ticks_position("left")
    return figure
