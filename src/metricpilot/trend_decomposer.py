"""STL-based trend decomposition helpers for canonical KPI series."""

from __future__ import annotations

import pandas as pd
from statsmodels.tsa.seasonal import STL

from metricpilot.contracts import DecompositionResult

MIN_SERIES_LENGTH = 14
DEFAULT_PERIOD = 7


class InsufficientDataError(ValueError):
    """Raised when a series is too short for deterministic STL decomposition."""


def decompose_timeseries(
    series: pd.Series,
    *,
    period: int = DEFAULT_PERIOD,
) -> DecompositionResult:
    """Run STL decomposition on a single KPI series."""

    observed = _normalize_series(series)
    if len(observed) < MIN_SERIES_LENGTH:
        raise InsufficientDataError(
            f"series length must be at least {MIN_SERIES_LENGTH}, got {len(observed)}"
        )

    stl_result = STL(observed, period=period, robust=True).fit()
    return DecompositionResult(
        trend=stl_result.trend.rename(observed.name),
        seasonal=stl_result.seasonal.rename(observed.name),
        residual=stl_result.resid.rename(observed.name),
        observed=observed,
    )


def _normalize_series(series: pd.Series) -> pd.Series:
    observed = pd.Series(series, copy=True)
    if observed.isna().any():
        raise ValueError("series must not contain null values")
    return observed.astype(float)
