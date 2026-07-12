"""
Mixin for geoms that proxy position parameters.

Provides a shared ``__init__`` that extracts position-
specific keyword arguments from ``**kwargs`` and creates
the appropriate position object automatically.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Optional


class _PositionGeomMixin:
    """
    Mixin that forwards position parameters from geom kwargs.

    Subclasses must define:

    - ``_position_params``: dict of parameter names to
      defaults.
    - ``_position_class``: the position class to instantiate.
    """

    _position_params: dict[str, Any]
    _position_class: type

    def __init__(
        self,
        mapping: Optional[Any] = None,
        data: Optional[Any] = None,
        **kwargs: Any,
    ):
        pos_kwargs = {}
        for key, default in self._position_params.items():
            pos_kwargs[key] = kwargs.pop(key, default)

        kwargs["position"] = self._position_class(**pos_kwargs)
        super().__init__(mapping=mapping, data=data, **kwargs)
