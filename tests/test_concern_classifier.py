"""Concern classifier coverage for Phase 3 trend analytics."""

from __future__ import annotations

import pandas as pd

from metricpilot.contracts import ClassificationResult, ConcernLevel
from metricpilot.fixtures import stable_series, structural_decline, temporary_dip
from metricpilot.concern_classifier import classify_decomposition
from metricpilot.trend_decomposer import decompose_timeseries


def test_classify_decomposition_stable_fixture_is_not_concerning() -> None:
    result = _classify_fixture(stable_series())

    assert isinstance(result, ClassificationResult)
    assert result.level is ConcernLevel.NOT_CONCERNING
    assert result.slope > -0.0002
    assert isinstance(result.change_points, list)


def test_classify_decomposition_structural_decline_fixture_is_concerning() -> None:
    result = _classify_fixture(structural_decline())

    assert result.level is ConcernLevel.CONCERNING
    assert result.slope < -0.0005
    assert result.slope_ci[0] <= result.slope <= result.slope_ci[1]


def test_classify_decomposition_temporary_dip_fixture_is_watch_or_not_concerning() -> None:
    result = _classify_fixture(temporary_dip())

    assert result.level in {ConcernLevel.WATCH, ConcernLevel.NOT_CONCERNING}
    assert result.slope_ci[0] <= result.slope <= result.slope_ci[1]
    assert result.evidence_text


def _classify_fixture(frame: pd.DataFrame) -> ClassificationResult:
    series = (
        frame.query("dimension_name == 'all' and dimension_value == 'all'")
        .sort_values("date_day")
        .set_index("date_day")["metric_value"]
    )
    return classify_decomposition(decompose_timeseries(series))
