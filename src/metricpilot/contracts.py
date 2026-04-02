"""Canonical typed contracts for MetricPilot data tables."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

import pandas as pd

__all__ = [
    "ALLOWED_DIMENSIONS",
    "AnalysisSummary",
    "ClassificationResult",
    "ConcernLevel",
    "DecompositionResult",
    "DemoRegistryRow",
    "MetricTimeseriesRow",
    "NarrativeOutput",
    "SemanticMappingRow",
    "SegmentContribution",
    "ValidationResult",
]


class ConcernLevel(str, Enum):
    NOT_CONCERNING = "not_concerning"
    WATCH = "watch"
    CONCERNING = "concerning"


@dataclass(frozen=True)
class DecompositionResult:
    trend: pd.Series
    seasonal: pd.Series
    residual: pd.Series
    observed: pd.Series


@dataclass(frozen=True)
class ClassificationResult:
    level: ConcernLevel
    slope: float
    slope_ci: tuple[float, float]
    change_points: list[int]
    evidence_text: str


@dataclass(frozen=True)
class SegmentContribution:
    dimension_name: str
    dimension_value: str
    contribution_delta: float
    obs_count: int
    slope: float


@dataclass(frozen=True)
class NarrativeOutput:
    finding: str
    confidence: str
    business_meaning: str
    caveats: list[str]


@dataclass(frozen=True)
class AnalysisSummary:
    classification: ClassificationResult
    segment_contributions: list[SegmentContribution]


ALLOWED_DIMENSIONS: tuple[str, ...] = (
    "all",
    "hotel",
    "market_segment",
    "distribution_channel",
    "customer_type",
    "deposit_type",
    "country_top",
)


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: list[str]


@dataclass(frozen=True)
class MetricTimeseriesRow:
    demo_id: str
    date_day: date
    metric_name: str
    metric_value: float
    dimension_name: str
    dimension_value: str
    slice_level: str
    obs_count: int
    metric_numerator: float
    metric_denominator: float


@dataclass(frozen=True)
class DemoRegistryRow:
    demo_id: str
    demo_label: str
    target_account: str
    target_vertical: str
    scenario_label: str
    primary_metric: str
    public_data_source: str
    disclaimer_text: str
    default_dimension_name: str


@dataclass(frozen=True)
class SemanticMappingRow:
    field_type: str
    raw_key: str
    display_label: str
    business_definition: str
    llm_hint: str
    sort_order: int
    is_active: bool
