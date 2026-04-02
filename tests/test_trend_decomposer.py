"""Trend decomposition coverage for Phase 3 STL analytics."""

from __future__ import annotations

import pandas as pd
import pytest

from metricpilot.contracts import DecompositionResult
from metricpilot.fixtures import stable_series
from metricpilot.trend_decomposer import InsufficientDataError, decompose_timeseries


def test_decompose_timeseries_returns_documented_component_shapes() -> None:
    series = _global_series(stable_series())

    result = decompose_timeseries(series)

    assert isinstance(result, DecompositionResult)
    pd.testing.assert_series_equal(result.observed, series)
    assert len(result.trend) == len(series)
    assert len(result.seasonal) == len(series)
    assert len(result.residual) == len(series)
    assert result.trend.index.equals(series.index)


def test_decompose_timeseries_stable_fixture_has_flat_trend() -> None:
    series = _global_series(stable_series())

    result = decompose_timeseries(series)
    first_window = result.trend.iloc[:30].mean()
    last_window = result.trend.iloc[-30:].mean()

    assert abs(last_window - first_window) < 0.002


def test_decompose_timeseries_rejects_short_series() -> None:
    series = _global_series(stable_series()).iloc[:13]

    with pytest.raises(InsufficientDataError):
        decompose_timeseries(series)


def _global_series(frame: pd.DataFrame) -> pd.Series:
    return (
        frame.query("dimension_name == 'all' and dimension_value == 'all'")
        .sort_values("date_day")
        .set_index("date_day")["metric_value"]
    )
