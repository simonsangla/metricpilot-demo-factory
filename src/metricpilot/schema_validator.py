"""Deterministic validation for canonical MetricPilot tables."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd
from pandas.api.types import is_bool_dtype, is_datetime64_any_dtype, is_integer_dtype, is_numeric_dtype

from metricpilot.contracts import ALLOWED_DIMENSIONS, ValidationResult

_METRIC_TIMESERIES_COLUMNS: tuple[str, ...] = (
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
)

_DEMO_REGISTRY_COLUMNS: tuple[str, ...] = (
    "demo_id",
    "demo_label",
    "target_account",
    "target_vertical",
    "scenario_label",
    "primary_metric",
    "public_data_source",
    "disclaimer_text",
    "default_dimension_name",
)

_SEMANTIC_MAPPING_COLUMNS: tuple[str, ...] = (
    "field_type",
    "raw_key",
    "display_label",
    "business_definition",
    "llm_hint",
    "sort_order",
    "is_active",
)

_RATIO_TOLERANCE = 1e-6


def validate_canonical_frames(
    *,
    metric_timeseries: pd.DataFrame,
    demo_registry: pd.DataFrame,
    semantic_mapping: pd.DataFrame,
) -> ValidationResult:
    """Validate canonical table structure and cross-table consistency."""

    errors: list[str] = []

    errors.extend(_validate_required_columns(metric_timeseries, "metric_timeseries", _METRIC_TIMESERIES_COLUMNS))
    errors.extend(_validate_required_columns(demo_registry, "demo_registry", _DEMO_REGISTRY_COLUMNS))
    errors.extend(_validate_required_columns(semantic_mapping, "semantic_mapping", _SEMANTIC_MAPPING_COLUMNS))

    if errors:
        return ValidationResult(ok=False, errors=errors)

    errors.extend(_validate_metric_timeseries_types(metric_timeseries))
    errors.extend(_validate_demo_registry_types(demo_registry))
    errors.extend(_validate_semantic_mapping_types(semantic_mapping))
    errors.extend(_validate_dimension_allowlist(metric_timeseries, demo_registry))
    errors.extend(_validate_global_row_rules(metric_timeseries))
    errors.extend(_validate_ratio_tolerance(metric_timeseries))
    errors.extend(_validate_demo_id_consistency(metric_timeseries, demo_registry))

    return ValidationResult(ok=not errors, errors=errors)


def _validate_required_columns(
    frame: pd.DataFrame,
    frame_name: str,
    required_columns: tuple[str, ...],
) -> list[str]:
    missing_columns = [column for column in required_columns if column not in frame.columns]
    if not missing_columns:
        return []
    return [
        f"{frame_name} missing required columns: {', '.join(sorted(missing_columns))}"
    ]


def _validate_metric_timeseries_types(metric_timeseries: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    errors.extend(_validate_string_values(metric_timeseries, "metric_timeseries", ("demo_id", "metric_name", "dimension_name", "dimension_value", "slice_level")))
    if not _series_is_date_like(metric_timeseries["date_day"]):
        errors.append("metric_timeseries column date_day must contain date values")
    errors.extend(_validate_numeric_values(metric_timeseries, "metric_timeseries", ("metric_value", "metric_numerator", "metric_denominator")))
    if not is_integer_dtype(metric_timeseries["obs_count"]):
        errors.append("metric_timeseries column obs_count must contain integer values")
    return errors


def _validate_demo_registry_types(demo_registry: pd.DataFrame) -> list[str]:
    return _validate_string_values(
        demo_registry,
        "demo_registry",
        (
            "demo_id",
            "demo_label",
            "target_account",
            "target_vertical",
            "scenario_label",
            "primary_metric",
            "public_data_source",
            "disclaimer_text",
            "default_dimension_name",
        ),
    )


def _validate_semantic_mapping_types(semantic_mapping: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    errors.extend(
        _validate_string_values(
            semantic_mapping,
            "semantic_mapping",
            ("field_type", "raw_key", "display_label", "business_definition", "llm_hint"),
        )
    )
    if not is_integer_dtype(semantic_mapping["sort_order"]):
        errors.append("semantic_mapping column sort_order must contain integer values")
    if not is_bool_dtype(semantic_mapping["is_active"]):
        errors.append("semantic_mapping column is_active must contain boolean values")
    return errors


def _validate_string_values(
    frame: pd.DataFrame,
    frame_name: str,
    columns: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    for column in columns:
        if frame[column].isna().any() or not frame[column].map(lambda value: isinstance(value, str)).all():
            errors.append(f"{frame_name} column {column} must contain string values")
    return errors


def _validate_numeric_values(
    frame: pd.DataFrame,
    frame_name: str,
    columns: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    for column in columns:
        if frame[column].isna().any() or not is_numeric_dtype(frame[column]):
            errors.append(f"{frame_name} column {column} must contain numeric values")
    return errors


def _validate_dimension_allowlist(
    metric_timeseries: pd.DataFrame,
    demo_registry: pd.DataFrame,
) -> list[str]:
    errors: list[str] = []
    invalid_dimensions = sorted(set(metric_timeseries["dimension_name"]) - set(ALLOWED_DIMENSIONS))
    if invalid_dimensions:
        errors.append(
            "dimension_name contains values outside the allowlist: "
            + ", ".join(invalid_dimensions)
        )
    invalid_defaults = sorted(set(demo_registry["default_dimension_name"]) - set(ALLOWED_DIMENSIONS))
    if invalid_defaults:
        errors.append(
            "demo_registry default_dimension_name contains values outside the allowlist: "
            + ", ".join(invalid_defaults)
        )
    return errors


def _validate_global_row_rules(metric_timeseries: pd.DataFrame) -> list[str]:
    global_mask = (
        (metric_timeseries["dimension_name"] == "all")
        | (metric_timeseries["dimension_value"] == "all")
        | (metric_timeseries["slice_level"] == "global")
    )
    if not global_mask.any():
        return ["metric_timeseries must include at least one global row"]

    invalid_global_rows = metric_timeseries.loc[
        global_mask,
        ["dimension_name", "dimension_value", "slice_level"],
    ]
    valid_global_rows = (
        (invalid_global_rows["dimension_name"] == "all")
        & (invalid_global_rows["dimension_value"] == "all")
        & (invalid_global_rows["slice_level"] == "global")
    )
    if valid_global_rows.all():
        return []
    return [
        "global rows must use dimension_name='all', dimension_value='all', and slice_level='global'"
    ]


def _validate_ratio_tolerance(metric_timeseries: pd.DataFrame) -> list[str]:
    invalid_denominator_mask = metric_timeseries["metric_denominator"] <= 0
    if invalid_denominator_mask.any():
        return ["metric_denominator must be greater than zero for every row"]

    recomputed = metric_timeseries["metric_numerator"] / metric_timeseries["metric_denominator"]
    ratio_delta = (recomputed - metric_timeseries["metric_value"]).abs()
    if (ratio_delta > _RATIO_TOLERANCE).any():
        return [
            "metric_value must equal metric_numerator / metric_denominator within tolerance"
        ]
    return []


def _validate_demo_id_consistency(
    metric_timeseries: pd.DataFrame,
    demo_registry: pd.DataFrame,
) -> list[str]:
    metric_demo_ids = sorted(metric_timeseries["demo_id"].unique().tolist())
    registry_demo_ids = sorted(demo_registry["demo_id"].unique().tolist())
    if len(metric_demo_ids) != 1:
        return ["metric_timeseries must contain exactly one demo_id value"]
    if len(registry_demo_ids) != 1:
        return ["demo_registry must contain exactly one demo_id value"]
    if metric_demo_ids[0] != registry_demo_ids[0]:
        return ["demo_id values must align between metric_timeseries and demo_registry"]
    return []


def _series_is_date_like(series: pd.Series) -> bool:
    if series.isna().any():
        return False
    if is_datetime64_any_dtype(series):
        return True
    return series.map(_is_date_like_value).all()


def _is_date_like_value(value: Any) -> bool:
    return isinstance(value, (date, datetime, pd.Timestamp))
