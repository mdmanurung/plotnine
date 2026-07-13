"""
Convenience utilities ported from ggh4x's ``conveniences.R``.

Provides helpers for distributing theme-element arguments,
weaving categorical factors, and building symmetric limits.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from itertools import product
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from plotnine.themes.elements import element_rect, element_text

if TYPE_CHECKING:
    from typing import Any, Callable


def distribute_args(
    *,
    fun: Callable[..., Any] = element_text,
    cull: bool = True,
    **kwargs: Any,
) -> list[Any]:
    """
    Distribute vectorised keyword arguments across calls.

    Each keyword argument should be a scalar or a sequence.
    The *i*-th element of every kwarg is forwarded to the
    *i*-th invocation of *fun*.  ``None`` values are silently
    dropped before calling *fun*.

    Parameters
    ----------
    fun : callable
        Constructor / factory to call (default `element_text`).
    cull : bool
        If ``True``, only pass keyword arguments whose names
        match a parameter of *fun*.
    **kwargs
        Keyword arguments whose values are scalars or lists.

    Returns
    -------
    list
        One result of *fun* per position.
    """
    if cull:
        sig = inspect.signature(fun)
        valid = set(sig.parameters.keys())
        has_var_kw = any(
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in sig.parameters.values()
        )
        if not has_var_kw:
            kwargs = {k: v for k, v in kwargs.items() if k in valid}

    # Drop keys with empty sequences
    kwargs = {k: v for k, v in kwargs.items() if _has_length(v)}

    if not kwargs:
        return [fun()]

    # Normalise every value to a list
    kwargs = {
        k: v if isinstance(v, (list, tuple)) else [v]
        for k, v in kwargs.items()
    }

    names = list(kwargs.keys())
    values = list(kwargs.values())
    n = max(len(v) for v in values)

    results: list[Any] = []
    for i in range(n):
        call_kwargs: dict[str, Any] = {}
        for name, vals in zip(names, values):
            if i < len(vals):
                val = vals[i]
            else:
                # Recycle: positions beyond the vector length
                # get nothing (mirroring R behaviour).
                continue
            if val is None or _is_na(val):
                continue
            call_kwargs[name] = val
        results.append(fun(**call_kwargs))
    return results


def elem_list_text(**kwargs: Any) -> list[Any]:
    """
    Convenience wrapper: ``distribute_args(fun=element_text)``.

    Parameters
    ----------
    **kwargs
        Forwarded to :func:`distribute_args`.

    Returns
    -------
    list
        A list of :class:`element_text` instances.
    """
    return distribute_args(fun=element_text, **kwargs)


def elem_list_rect(**kwargs: Any) -> list[Any]:
    """
    Convenience wrapper: ``distribute_args(fun=element_rect)``.

    Parameters
    ----------
    **kwargs
        Forwarded to :func:`distribute_args`.

    Returns
    -------
    list
        A list of :class:`element_rect` instances.
    """
    return distribute_args(fun=element_rect, **kwargs)


def weave_factors(
    *args: Any,
    drop: bool = True,
    sep: str = ".",
    replace_na: bool = True,
) -> pd.Categorical:
    """
    Combine categorical / array-like columns into one factor.

    Levels are ordered lexicographically over the input
    factors' levels (Cartesian product, then filtered to
    observed combinations when *drop* is ``True``).

    Parameters
    ----------
    *args : array-like
        Series, arrays, or lists to combine.
    drop : bool
        Drop unobserved level combinations.
    sep : str
        Separator placed between level components.
    replace_na : bool
        If ``True``, replace ``NaN`` / ``None`` with the
        string ``"NA"`` before combining.

    Returns
    -------
    pd.Categorical
        A single categorical with combined levels.
    """
    if not args:
        return pd.Categorical([])

    series_list: list[pd.Categorical] = []
    for a in args:
        s = pd.Series(a)
        if replace_na:
            s = s.fillna("NA")
        cat = pd.Categorical(s)
        series_list.append(cat)

    lengths = [len(c) for c in series_list]
    if len(set(lengths)) != 1:
        msg = f"All arguments must have the same length, got {lengths}"
        raise ValueError(msg)

    n = lengths[0]

    # Build all possible levels (Cartesian product)
    all_levels = [list(c.categories) for c in series_list]
    all_combos = [
        sep.join(str(x) for x in combo) for combo in product(*all_levels)
    ]

    # Build observed values
    codes = [
        sep.join(str(series_list[j][i]) for j in range(len(args)))
        for i in range(n)
    ]

    if drop:
        observed = set(codes)
        categories = [c for c in all_combos if c in observed]
    else:
        categories = all_combos

    return pd.Categorical(codes, categories=categories)


def center_limits(
    around: float = 0,
) -> Callable[[tuple[float, float]], tuple[float, float]]:
    """
    Factory that returns a limits-centering function.

    The returned callable accepts a ``(min, max)`` tuple and
    produces symmetric limits centred on *around*.

    Parameters
    ----------
    around : float
        Centre point for the limits.

    Returns
    -------
    callable
        A function ``(min, max) -> (new_min, new_max)``.

    Examples
    --------
    >>> center_limits(0)((3, 8))
    (-8, 8)
    """

    def _center(
        limits: tuple[float, float],
    ) -> tuple[float, float]:
        max_dev = max(abs(limits[0] - around), abs(limits[1] - around))
        return (around - max_dev, around + max_dev)

    return _center


@dataclass
class SecondaryAxisHelper:
    """
    Projection helper returned by :func:`help_secondary`.
    """

    slope: float
    intercept: float
    name: str | None = None
    method: str = "range"

    def proj(self, values: Any) -> np.ndarray:
        """Project secondary-data values into primary-axis coordinates."""
        return np.asarray(values, dtype=float) * self.slope + self.intercept

    def inverse(self, values: Any) -> np.ndarray:
        """Map projected primary-axis values back to secondary values."""
        return (np.asarray(values, dtype=float) - self.intercept) / self.slope

    def __call__(self, values: Any) -> np.ndarray:
        return self.proj(values)

    def as_plotnine_axis(self) -> None:
        """
        Raise a clear error for unsupported direct secondary-axis use.
        """
        raise NotImplementedError(
            "plotnine does not currently expose ggplot2-style secondary axes; "
            "use help_secondary(...).proj(...) to project secondary data"
        )


def help_secondary(
    data: pd.DataFrame | None = None,
    primary: Any = (0, 1),
    secondary: Any = (0, 1),
    method: str = "range",
    na_rm: bool = True,
    name: str | None = None,
    **kwargs: Any,
) -> SecondaryAxisHelper:
    """
    Build a projection helper for secondary data.

    Parameters
    ----------
    data : pandas.DataFrame, optional
        Data used to resolve string column names.
    primary, secondary : str or array-like
        Primary and secondary values used to estimate the projection.
    method : {"range", "max", "fit", "sortfit", "ccf"}
        Projection method. ``"ccf"`` uses a simple lag search before fitting.
    na_rm : bool
        Drop incomplete observations before fitting.
    name : str, optional
        Label stored on the returned helper.
    **kwargs
        Accepted for API compatibility and stored nowhere.

    Returns
    -------
    SecondaryAxisHelper
        Helper with ``proj`` and ``inverse`` methods.
    """
    del kwargs
    primary_values = _resolve_secondary_values(data, primary)
    secondary_values = _resolve_secondary_values(data, secondary)
    p, s = _align_secondary_values(primary_values, secondary_values, na_rm)

    if method == "range":
        slope, intercept = _range_projection(p, s)
    elif method == "max":
        slope, intercept = _max_projection(p, s)
    elif method == "fit":
        slope, intercept = _fit_projection(p, s)
    elif method == "sortfit":
        slope, intercept = _fit_projection(np.sort(p), np.sort(s))
    elif method == "ccf":
        slope, intercept = _fit_projection(*_ccf_aligned(p, s))
    else:
        msg = (
            "method must be one of 'range', 'max', 'fit', 'sortfit', or 'ccf'"
        )
        raise ValueError(msg)

    return SecondaryAxisHelper(
        slope=float(slope),
        intercept=float(intercept),
        name=name,
        method=method,
    )


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------


def _is_na(x: Any) -> bool:
    """Return ``True`` for NA-like scalars."""
    if x is None:
        return True
    try:
        return bool(np.isnan(x))
    except (TypeError, ValueError):
        return False


def _has_length(v: Any) -> bool:
    """Return ``True`` when *v* is non-empty."""
    if isinstance(v, (list, tuple)):
        return len(v) > 0
    return True


def _resolve_secondary_values(
    data: pd.DataFrame | None,
    values: Any,
) -> np.ndarray:
    if isinstance(values, str):
        if data is None:
            msg = "String primary/secondary values require a data frame"
            raise ValueError(msg)
        return np.asarray(data[values], dtype=float)
    return np.asarray(values, dtype=float)


def _align_secondary_values(
    primary: np.ndarray,
    secondary: np.ndarray,
    na_rm: bool,
) -> tuple[np.ndarray, np.ndarray]:
    if primary.shape[0] != secondary.shape[0]:
        msg = "primary and secondary must have the same length"
        raise ValueError(msg)
    mask = ~(np.isnan(primary) | np.isnan(secondary))
    if not mask.all():
        if not na_rm:
            msg = "primary and secondary contain missing values"
            raise ValueError(msg)
        primary = primary[mask]
        secondary = secondary[mask]
    if len(primary) < 2:
        msg = "help_secondary requires at least two complete observations"
        raise ValueError(msg)
    return primary, secondary


def _range_projection(
    primary: np.ndarray,
    secondary: np.ndarray,
) -> tuple[float, float]:
    pmin, pmax = np.min(primary), np.max(primary)
    smin, smax = np.min(secondary), np.max(secondary)
    if smax == smin:
        msg = "secondary range must be non-zero"
        raise ValueError(msg)
    slope = (pmax - pmin) / (smax - smin)
    return slope, pmin - slope * smin


def _max_projection(
    primary: np.ndarray,
    secondary: np.ndarray,
) -> tuple[float, float]:
    smax = np.max(np.abs(secondary))
    if smax == 0:
        msg = "secondary maximum must be non-zero"
        raise ValueError(msg)
    return np.max(np.abs(primary)) / smax, 0.0


def _fit_projection(
    primary: np.ndarray,
    secondary: np.ndarray,
) -> tuple[float, float]:
    slope, intercept = np.polyfit(secondary, primary, 1)
    return float(slope), float(intercept)


def _ccf_aligned(
    primary: np.ndarray,
    secondary: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    primary_centered = primary - np.mean(primary)
    secondary_centered = secondary - np.mean(secondary)
    corr = np.correlate(primary_centered, secondary_centered, mode="full")
    lag = int(np.argmax(corr) - (len(secondary) - 1))
    if lag > 0:
        return primary[lag:], secondary[:-lag]
    if lag < 0:
        return primary[:lag], secondary[-lag:]
    return primary, secondary
