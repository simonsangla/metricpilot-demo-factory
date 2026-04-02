"""Schema validator coverage for Phase 3 canonical table checks."""

from __future__ import annotations

import pandas as pd

from metricpilot.contracts import ValidationResult
from metricpilot.fixtures import (
    demo_registry_fixture,
    semantic_mapping_fixture,
    stable_series,
)
from metricpilot.schema_validator import validate_canonical_frames


def test_validate_canonical_frames_accepts_conformant_fixtures() -> None:
    metric_timeseries = stable_series()
    demo_registry = _aligned_demo_registry(metric_timeseries)

    result = validate_canonical_frames(
        metric_timeseries=metric_timeseries,
        demo_registry=demo_registry,
        semantic_mapping=semantic_mapping_fixture(),
    )

    assert isinstance(result, ValidationResult)
    assert result == ValidationResult(ok=True, errors=[])


def test_validate_canonical_frames_rejects_missing_metric_timeseries_column() -> None:
    metric_timeseries = stable_series().drop(columns=["metric_denominator"])

    result = validate_canonical_frames(
        metric_timeseries=metric_timeseries,
        demo_registry=_aligned_demo_registry(stable_series()),
        semantic_mapping=semantic_mapping_fixture(),
    )

    assert result.ok is False
    assert any("metric_timeseries missing required columns" in error for error in result.errors)
    assert any("metric_denominator" in error for error in result.errors)


def test_validate_canonical_frames_rejects_invalid_metric_timeseries_types() -> None:
    metric_timeseries = stable_series().copy()
    metric_timeseries["obs_count"] = metric_timeseries["obs_count"].astype(float)

    result = validate_canonical_frames(
        metric_timeseries=metric_timeseries,
        demo_registry=_aligned_demo_registry(metric_timeseries),
        semantic_mapping=semantic_mapping_fixture(),
    )

    assert result.ok is False
    assert any("metric_timeseries column obs_count must contain integer values" in error for error in result.errors)


def test_validate_canonical_frames_rejects_bad_dimension_name() -> None:
    metric_timeseries = stable_series().copy()
    metric_timeseries.loc[0, "dimension_name"] = "region"

    result = validate_canonical_frames(
        metric_timeseries=metric_timeseries,
        demo_registry=_aligned_demo_registry(metric_timeseries),
        semantic_mapping=semantic_mapping_fixture(),
    )

    assert result.ok is False
    assert any("dimension_name contains values outside the allowlist" in error for error in result.errors)
    assert any("region" in error for error in result.errors)


def test_validate_canonical_frames_rejects_wrong_global_dimension_value() -> None:
    metric_timeseries = stable_series().copy()
    global_row_index = metric_timeseries.index[metric_timeseries["slice_level"] == "global"][0]
    metric_timeseries.loc[global_row_index, "dimension_value"] = "global"

    result = validate_canonical_frames(
        metric_timeseries=metric_timeseries,
        demo_registry=_aligned_demo_registry(metric_timeseries),
        semantic_mapping=semantic_mapping_fixture(),
    )

    assert result.ok is False
    assert any("global rows must use dimension_name='all', dimension_value='all', and slice_level='global'" in error for error in result.errors)


def test_validate_canonical_frames_rejects_mismatched_ratio() -> None:
    metric_timeseries = stable_series().copy()
    metric_timeseries.loc[0, "metric_value"] = metric_timeseries.loc[0, "metric_value"] + 0.02

    result = validate_canonical_frames(
        metric_timeseries=metric_timeseries,
        demo_registry=_aligned_demo_registry(metric_timeseries),
        semantic_mapping=semantic_mapping_fixture(),
    )

    assert result.ok is False
    assert any("metric_value must equal metric_numerator / metric_denominator within tolerance" in error for error in result.errors)


def test_validate_canonical_frames_rejects_demo_id_mismatch() -> None:
    metric_timeseries = stable_series()

    result = validate_canonical_frames(
        metric_timeseries=metric_timeseries,
        demo_registry=demo_registry_fixture(),
        semantic_mapping=semantic_mapping_fixture(),
    )

    assert result.ok is False
    assert any("demo_id values must align between metric_timeseries and demo_registry" in error for error in result.errors)


def _aligned_demo_registry(metric_timeseries: pd.DataFrame) -> pd.DataFrame:
    demo_registry = demo_registry_fixture().copy()
    demo_registry.loc[:, "demo_id"] = metric_timeseries["demo_id"].iloc[0]
    return demo_registry
