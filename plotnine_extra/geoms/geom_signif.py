"""
``geom_signif`` is the ggsignif-style equivalent of
``geom_bracket``. It is implemented as a thin subclass that
keeps the parameter names familiar to ggsignif users and
translates them to the plotnine bracket aesthetics.
"""

from __future__ import annotations

from typing import Any

from .geom_bracket import geom_bracket


class geom_signif(geom_bracket):
    """
    Significance brackets with labels (ggsignif-style alias).

    Matches :class:`geom_bracket` in behaviour but lets
    ggsignif users keep their familiar parameter names:

    * ``y_position`` → bracket ``y`` position (top edge)
    * ``annotations`` → ``label`` aesthetic
    * ``xmin`` / ``xmax`` → passed straight through
    * ``tip_length`` / ``vjust`` → forwarded as-is

    Parameters
    ----------
    Same as :class:`geom_bracket`. ``y_position`` and
    ``annotations`` are accepted as aliases for ``y`` and
    ``label`` to ease migration from ggsignif.
    """

    def __init__(
        self,
        mapping=None,
        data=None,
        *,
        y_position: Any = None,
        annotations: Any = None,
        **kwargs: Any,
    ):
        # Translate ggsignif-style kwargs to plotnine bracket
        # aesthetics. ``y_position`` is the bracket top
        # coordinate; ``annotations`` is the label text.
        if y_position is not None and "y" not in kwargs:
            kwargs["y"] = y_position
        if annotations is not None and "label" not in kwargs:
            kwargs["label"] = annotations
        super().__init__(mapping=mapping, data=data, **kwargs)
