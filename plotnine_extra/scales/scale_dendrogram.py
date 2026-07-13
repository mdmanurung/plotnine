"""
Dendrogram position scales.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import numpy as np
from plotnine import scale_x_discrete, scale_y_discrete
from scipy.cluster.hierarchy import leaves_list

from ..guides import guide_dendro

if TYPE_CHECKING:
    from typing import Any, Sequence


def scale_x_dendrogram(
    *,
    hclust: "Any | None" = None,
    labels: "Sequence[str] | None" = None,
    guide: "Any | None" = None,
    position: Literal["bottom", "top"] = "bottom",
    **kwargs: "Any",
):
    """
    Discrete x scale ordered by a dendrogram.

    The visual dendrogram is delegated to :func:`guide_dendro`, which is
    rendered by plotnine-extra's extended facets.
    """
    limits = _dendrogram_order(hclust, labels)
    dendro_guide = guide
    if dendro_guide is None:
        dendro_guide = guide_dendro(hclust, position=position)
    scale = scale_x_discrete(limits=limits, guide=dendro_guide, **kwargs)
    scale.guide = dendro_guide
    return scale


def scale_y_dendrogram(
    *,
    hclust: "Any | None" = None,
    labels: "Sequence[str] | None" = None,
    guide: "Any | None" = None,
    position: Literal["left", "right"] = "left",
    **kwargs: "Any",
):
    """
    Discrete y scale ordered by a dendrogram.
    """
    limits = _dendrogram_order(hclust, labels)
    dendro_guide = guide
    if dendro_guide is None:
        dendro_guide = guide_dendro(hclust, position=position)
    scale = scale_y_discrete(limits=limits, guide=dendro_guide, **kwargs)
    scale.guide = dendro_guide
    return scale


def _dendrogram_order(
    hclust: "Any | None",
    labels: "Sequence[str] | None",
) -> list[str] | None:
    if hclust is None:
        return list(labels) if labels is not None else None

    if isinstance(hclust, dict):
        if "ivl" in hclust:
            return [str(item) for item in hclust["ivl"]]
        if "leaves" in hclust:
            return _labels_from_indices(hclust["leaves"], labels)

    arr = np.asarray(hclust)
    if arr.ndim == 2 and arr.shape[1] >= 4:
        leaves = leaves_list(arr)
        return _labels_from_indices(leaves, labels)

    msg = (
        "hclust must be None, a scipy linkage matrix, or a dendrogram "
        "dict with 'ivl' or 'leaves'"
    )
    raise ValueError(msg)


def _labels_from_indices(
    leaves: "Sequence[int]",
    labels: "Sequence[str] | None",
) -> list[str]:
    if labels is None:
        return [str(int(i)) for i in leaves]
    labels_list = list(labels)
    return [str(labels_list[int(i)]) for i in leaves]
