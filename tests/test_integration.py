"""Phase 4 integration coverage for the deterministic analytics chain."""

from __future__ import annotations

import subprocess

import pandas as pd

from metricpilot.concern_classifier import classify_decomposition
from metricpilot.contracts import ClassificationResult, ConcernLevel, SegmentContribution, ValidationResult
from metricpilot.fixtures import (
    demo_registry_fixture,
    segment_shift,
    semantic_mapping_fixture,
    stable_series,
    structural_decline,
    temporary_dip,
)
from metricpilot.schema_validator import validate_canonical_frames
from metricpilot.segment_scanner import scan_segments
from metricpilot.trend_decomposer import decompose_timeseries


def test_stable_series_full_chain_is_not_concerning() -> None:
    validation, classification, segment_results = _run_chain(stable_series())

    assert validation == ValidationResult(ok=True, errors=[])
    assert classification.level is ConcernLevel.NOT_CONCERNING
    assert segment_results
    assert {item.dimension_name for item in segment_results} == {
        "customer_type",
        "hotel",
        "market_segment",
    }


def test_structural_decline_full_chain_is_concerning() -> None:
    validation, classification, segment_results = _run_chain(structural_decline())

    assert validation == ValidationResult(ok=True, errors=[])
    assert classification.level is ConcernLevel.CONCERNING
    assert segment_results


def test_segment_shift_full_chain_is_concerning_and_identifies_top_segment() -> None:
    validation, classification, segment_results = _run_chain(segment_shift())

    assert validation == ValidationResult(ok=True, errors=[])
    assert classification.level is ConcernLevel.CONCERNING
    assert segment_results
    assert (segment_results[0].dimension_name, segment_results[0].dimension_value) == (
        "hotel",
        "resort",
    )


def test_src_metricpilot_has_no_raw_source_column_leaks() -> None:
    raw_source_patterns = [
        r"\barrival_date_year\b",
        r"\barrival_date_month\b",
        r"\barrival_date_day_of_month\b",
        r"\bis_repeated_guest\b",
        r"\bcountry\b",
    ]

    result = subprocess.run(
        [
            "rg",
            "-n",
            "--glob",
            "*.py",
            "--glob",
            "!src/metricpilot/adapters/**",
            "|".join(raw_source_patterns),
            "src/metricpilot",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1, result.stdout


def test_temporary_dip_full_chain_is_watch_or_not_concerning() -> None:
    validation, classification, segment_results = _run_chain(temporary_dip())

    assert validation == ValidationResult(ok=True, errors=[])
    assert classification.level in {ConcernLevel.WATCH, ConcernLevel.NOT_CONCERNING}
    assert segment_results


def _run_chain(
    metric_timeseries: pd.DataFrame,
) -> tuple[ValidationResult, ClassificationResult, list[SegmentContribution]]:
    demo_registry = _aligned_demo_registry(metric_timeseries)
    semantic_mapping = semantic_mapping_fixture()

    validation = validate_canonical_frames(
        metric_timeseries=metric_timeseries,
        demo_registry=demo_registry,
        semantic_mapping=semantic_mapping,
    )
    global_series = (
        metric_timeseries.query("dimension_name == 'all' and dimension_value == 'all'")
        .sort_values("date_day")
        .set_index("date_day")["metric_value"]
    )
    decomposition = decompose_timeseries(global_series)
    classification = classify_decomposition(decomposition)
    segment_results = scan_segments(metric_timeseries, target_metric="repeat_guest_rate")
    return validation, classification, segment_results


def _aligned_demo_registry(metric_timeseries: pd.DataFrame) -> pd.DataFrame:
    """Align metadata to the scenario fixture without changing fixture semantics globally."""

    demo_registry = demo_registry_fixture().copy()
    demo_registry.loc[:, "demo_id"] = metric_timeseries["demo_id"].iloc[0]
    return demo_registry
