"""Contract structure tests for the canonical schema layer."""

from dataclasses import fields, is_dataclass
from datetime import date
from enum import Enum
from typing import get_type_hints

import pandas as pd

from metricpilot.contracts import (
    ALLOWED_DIMENSIONS,
    AnalysisSummary,
    ClassificationResult,
    ConcernLevel,
    DecompositionResult,
    DemoRegistryRow,
    MetricTimeseriesRow,
    NarrativeOutput,
    SemanticMappingRow,
    SegmentContribution,
    ValidationResult,
)


def test_concern_level_matches_documented_members_and_values() -> None:
    assert issubclass(ConcernLevel, Enum)
    assert [member.name for member in ConcernLevel] == [
        "NOT_CONCERNING",
        "WATCH",
        "CONCERNING",
    ]
    assert [member.value for member in ConcernLevel] == [
        "not_concerning",
        "watch",
        "concerning",
    ]


def test_decomposition_result_matches_documented_fields() -> None:
    assert is_dataclass(DecompositionResult)
    assert [field.name for field in fields(DecompositionResult)] == [
        "trend",
        "seasonal",
        "residual",
        "observed",
    ]
    assert get_type_hints(DecompositionResult) == {
        "trend": pd.Series,
        "seasonal": pd.Series,
        "residual": pd.Series,
        "observed": pd.Series,
    }


def test_classification_result_matches_documented_fields() -> None:
    assert is_dataclass(ClassificationResult)
    assert [field.name for field in fields(ClassificationResult)] == [
        "level",
        "slope",
        "slope_ci",
        "change_points",
        "evidence_text",
    ]
    assert get_type_hints(ClassificationResult) == {
        "level": ConcernLevel,
        "slope": float,
        "slope_ci": tuple[float, float],
        "change_points": list[int],
        "evidence_text": str,
    }


def test_segment_contribution_matches_documented_fields() -> None:
    assert is_dataclass(SegmentContribution)
    assert [field.name for field in fields(SegmentContribution)] == [
        "dimension_name",
        "dimension_value",
        "contribution_delta",
        "obs_count",
        "slope",
    ]
    assert get_type_hints(SegmentContribution) == {
        "dimension_name": str,
        "dimension_value": str,
        "contribution_delta": float,
        "obs_count": int,
        "slope": float,
    }


def test_narrative_output_matches_documented_fields() -> None:
    assert is_dataclass(NarrativeOutput)
    assert [field.name for field in fields(NarrativeOutput)] == [
        "finding",
        "confidence",
        "business_meaning",
        "caveats",
    ]
    assert get_type_hints(NarrativeOutput) == {
        "finding": str,
        "confidence": str,
        "business_meaning": str,
        "caveats": list[str],
    }


def test_analysis_summary_matches_documented_fields() -> None:
    assert is_dataclass(AnalysisSummary)
    assert [field.name for field in fields(AnalysisSummary)] == [
        "classification",
        "segment_contributions",
    ]
    assert get_type_hints(AnalysisSummary) == {
        "classification": ClassificationResult,
        "segment_contributions": list[SegmentContribution],
    }


def test_allowed_dimensions_match_canonical_schema() -> None:
    assert isinstance(ALLOWED_DIMENSIONS, tuple)
    assert ALLOWED_DIMENSIONS == (
        "all",
        "hotel",
        "market_segment",
        "distribution_channel",
        "customer_type",
        "deposit_type",
        "country_top",
    )


def test_validation_result_matches_documented_fields() -> None:
    assert is_dataclass(ValidationResult)
    assert [field.name for field in fields(ValidationResult)] == ["ok", "errors"]
    assert get_type_hints(ValidationResult) == {
        "ok": bool,
        "errors": list[str],
    }


def test_metric_timeseries_row_matches_canonical_schema() -> None:
    assert is_dataclass(MetricTimeseriesRow)
    assert [field.name for field in fields(MetricTimeseriesRow)] == [
        "demo_id",
        "date_day",
        "metric_name",
        "metric_value",
        "dimension_name",
        "dimension_value",
        "slice_level",
        "obs_count",
        "metric_numerator",
        "metric_denominator",
    ]
    assert get_type_hints(MetricTimeseriesRow) == {
        "demo_id": str,
        "date_day": date,
        "metric_name": str,
        "metric_value": float,
        "dimension_name": str,
        "dimension_value": str,
        "slice_level": str,
        "obs_count": int,
        "metric_numerator": float,
        "metric_denominator": float,
    }


def test_demo_registry_row_matches_canonical_schema() -> None:
    assert is_dataclass(DemoRegistryRow)
    assert [field.name for field in fields(DemoRegistryRow)] == [
        "demo_id",
        "demo_label",
        "target_account",
        "target_vertical",
        "scenario_label",
        "primary_metric",
        "public_data_source",
        "disclaimer_text",
        "default_dimension_name",
    ]
    assert get_type_hints(DemoRegistryRow) == {
        "demo_id": str,
        "demo_label": str,
        "target_account": str,
        "target_vertical": str,
        "scenario_label": str,
        "primary_metric": str,
        "public_data_source": str,
        "disclaimer_text": str,
        "default_dimension_name": str,
    }


def test_semantic_mapping_row_matches_canonical_schema() -> None:
    assert is_dataclass(SemanticMappingRow)
    assert [field.name for field in fields(SemanticMappingRow)] == [
        "field_type",
        "raw_key",
        "display_label",
        "business_definition",
        "llm_hint",
        "sort_order",
        "is_active",
    ]
    assert get_type_hints(SemanticMappingRow) == {
        "field_type": str,
        "raw_key": str,
        "display_label": str,
        "business_definition": str,
        "llm_hint": str,
        "sort_order": int,
        "is_active": bool,
    }


def test_contracts_are_import_safe() -> None:
    component = pd.Series([1.0, 2.0, 3.0], name="repeat_guest_rate")
    decomposition = DecompositionResult(
        trend=component,
        seasonal=component,
        residual=component,
        observed=component,
    )
    classification = ClassificationResult(
        level=ConcernLevel.WATCH,
        slope=-0.01,
        slope_ci=(-0.02, 0.0),
        change_points=[30, 90],
        evidence_text="Trend and change-point evidence recorded.",
    )
    contribution = SegmentContribution(
        dimension_name="hotel",
        dimension_value="resort",
        contribution_delta=-0.03,
        obs_count=120,
        slope=-0.01,
    )
    narrative = NarrativeOutput(
        finding="Repeat guest rate is under observation.",
        confidence="moderate",
        business_meaning="Retention patterns changed within the analysis window.",
        caveats=["Proxy-data interpretation only."],
    )
    summary = AnalysisSummary(
        classification=classification,
        segment_contributions=[contribution],
    )
    validation = ValidationResult(ok=True, errors=[])
    row = MetricTimeseriesRow(
        demo_id="clubmed-repeat-guest-rate",
        date_day=date(2026, 1, 1),
        metric_name="repeat_guest_rate",
        metric_value=0.42,
        dimension_name="all",
        dimension_value="all",
        slice_level="global",
        obs_count=100,
        metric_numerator=42.0,
        metric_denominator=100.0,
    )
    assert classification.level is ConcernLevel.WATCH
    assert summary.segment_contributions[0].dimension_name == "hotel"
    assert narrative.caveats == ["Proxy-data interpretation only."]
    assert validation.ok is True
    assert len(decomposition.trend) == 3
    assert row.metric_name == "repeat_guest_rate"
