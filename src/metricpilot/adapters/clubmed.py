"""Club Med proxy adapter from hotel bookings CSV to canonical tables."""

from __future__ import annotations

from pathlib import Path
import re

import pandas as pd

from metricpilot.contracts import ALLOWED_DIMENSIONS

DEMO_ID = "clubmed_repeat_guest_rate"
METRIC_NAME = "repeat_guest_rate"
PUBLIC_DATA_SOURCE = "Kaggle hotel bookings proxy dataset"
TOP_N_COUNTRIES = 10
MIN_SEGMENT_VOLUME = 30

_RAW_COLUMNS: tuple[str, ...] = (
    "arrival_date_year",
    "arrival_date_month",
    "arrival_date_day_of_month",
    "hotel",
    "market_segment",
    "distribution_channel",
    "country",
    "customer_type",
    "deposit_type",
    "is_repeated_guest",
)

_DIMENSION_COLUMNS: tuple[str, ...] = (
    "hotel",
    "market_segment",
    "distribution_channel",
    "customer_type",
    "deposit_type",
    "country_top",
)

_MONTH_LOOKUP: dict[str, int] = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def build_clubmed_proxy_tables(
    csv_path: str | Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load hotel_bookings.csv and return canonical metric, registry, and mapping tables."""

    raw_frame = pd.read_csv(csv_path)
    _validate_raw_columns(raw_frame)
    prepared = _prepare_raw_frame(raw_frame)

    metric_timeseries = _build_metric_timeseries(prepared)
    demo_registry = _build_demo_registry()
    semantic_mapping = _build_semantic_mapping(metric_timeseries)
    return metric_timeseries, demo_registry, semantic_mapping


def _validate_raw_columns(raw_frame: pd.DataFrame) -> None:
    missing_columns = [column for column in _RAW_COLUMNS if column not in raw_frame.columns]
    if missing_columns:
        raise ValueError(f"hotel_bookings.csv missing required columns: {', '.join(missing_columns)}")


def _prepare_raw_frame(raw_frame: pd.DataFrame) -> pd.DataFrame:
    frame = raw_frame.loc[:, _RAW_COLUMNS].copy()
    frame["date_day"] = _build_date_day(frame)
    frame["repeat_guest_flag"] = frame["is_repeated_guest"].astype(int)
    frame["hotel"] = frame["hotel"].map(_normalize_dimension_value)
    frame["market_segment"] = frame["market_segment"].map(_normalize_dimension_value)
    frame["distribution_channel"] = frame["distribution_channel"].map(_normalize_dimension_value)
    frame["customer_type"] = frame["customer_type"].map(_normalize_dimension_value)
    frame["deposit_type"] = frame["deposit_type"].map(_normalize_dimension_value)
    frame["country_top"] = _build_country_top(frame["country"])
    return frame


def _build_date_day(frame: pd.DataFrame) -> pd.Series:
    month_numbers = frame["arrival_date_month"].map(_month_to_number)
    return pd.to_datetime(
        {
            "year": frame["arrival_date_year"].astype(int),
            "month": month_numbers.astype(int),
            "day": frame["arrival_date_day_of_month"].astype(int),
        }
    ).dt.date


def _month_to_number(month_value: object) -> int:
    month_key = str(month_value).strip().lower()
    if month_key not in _MONTH_LOOKUP:
        raise ValueError(f"unsupported arrival_date_month value: {month_value}")
    return _MONTH_LOOKUP[month_key]


def _build_country_top(country_series: pd.Series) -> pd.Series:
    normalized = country_series.fillna("UNKNOWN").map(lambda value: str(value).strip().upper())
    counts = normalized.value_counts()
    top_countries = counts.sort_values(ascending=False, kind="stable").head(TOP_N_COUNTRIES).index.tolist()
    return normalized.map(lambda country: country if country in top_countries else "OTHER")


def _build_metric_timeseries(prepared: pd.DataFrame) -> pd.DataFrame:
    frames = [_aggregate_global(prepared)]
    for dimension_name in _DIMENSION_COLUMNS:
        frames.append(_aggregate_dimension(prepared, dimension_name))
    return pd.concat(frames, ignore_index=True).sort_values(
        ["date_day", "slice_level", "dimension_name", "dimension_value"],
        kind="stable",
    ).reset_index(drop=True)


def _aggregate_global(prepared: pd.DataFrame) -> pd.DataFrame:
    grouped = prepared.groupby("date_day", sort=True)
    aggregate = grouped.agg(
        obs_count=("repeat_guest_flag", "size"),
        metric_numerator=("repeat_guest_flag", "sum"),
    ).reset_index()
    aggregate["metric_denominator"] = aggregate["obs_count"].astype(float)
    aggregate["metric_value"] = aggregate["metric_numerator"] / aggregate["metric_denominator"]
    aggregate["demo_id"] = DEMO_ID
    aggregate["metric_name"] = METRIC_NAME
    aggregate["dimension_name"] = "all"
    aggregate["dimension_value"] = "all"
    aggregate["slice_level"] = "global"
    return aggregate[
        [
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
    ]


def _aggregate_dimension(prepared: pd.DataFrame, dimension_name: str) -> pd.DataFrame:
    grouped = prepared.groupby(["date_day", dimension_name], sort=True)
    aggregate = grouped.agg(
        obs_count=("repeat_guest_flag", "size"),
        metric_numerator=("repeat_guest_flag", "sum"),
    ).reset_index()
    aggregate["metric_denominator"] = aggregate["obs_count"].astype(float)
    aggregate = aggregate.loc[aggregate["metric_denominator"] >= MIN_SEGMENT_VOLUME].copy()
    aggregate["metric_value"] = aggregate["metric_numerator"] / aggregate["metric_denominator"]
    aggregate["demo_id"] = DEMO_ID
    aggregate["metric_name"] = METRIC_NAME
    aggregate["dimension_name"] = dimension_name
    aggregate["dimension_value"] = aggregate[dimension_name]
    aggregate["slice_level"] = "segment"
    return aggregate[
        [
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
    ]


def _build_demo_registry() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "demo_id": DEMO_ID,
                "demo_label": "Club Med Repeat Guest Rate",
                "target_account": "Club Med",
                "target_vertical": "tourism",
                "scenario_label": "Repeat guest rate diagnostic demo",
                "primary_metric": METRIC_NAME,
                "public_data_source": PUBLIC_DATA_SOURCE,
                "disclaimer_text": "Uses public proxy data for deterministic demo analysis only.",
                "default_dimension_name": "hotel",
            }
        ]
    )


def _build_semantic_mapping(metric_timeseries: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = [
        _mapping_row(
            field_type="metric",
            raw_key=METRIC_NAME,
            display_label="Repeat Guest Rate",
            business_definition="Share of bookings attributed to returning guests.",
            llm_hint="Describe retention movement without causal claims.",
            sort_order=1,
        )
    ]

    for offset, dimension_name in enumerate(ALLOWED_DIMENSIONS, start=10):
        rows.append(
            _mapping_row(
                field_type="dimension",
                raw_key=dimension_name,
                display_label=_display_label(dimension_name),
                business_definition=f"Booking slice by {_display_label(dimension_name).lower()}.",
                llm_hint="Use as a segment axis for comparison.",
                sort_order=offset,
            )
        )

    dimension_values = sorted(metric_timeseries["dimension_value"].unique().tolist(), key=lambda value: (value != "all", value))
    for offset, dimension_value in enumerate(dimension_values, start=100):
        rows.append(
            _mapping_row(
                field_type="dimension_value",
                raw_key=dimension_value,
                display_label=_display_label(dimension_value),
                business_definition=f"Booking slice for {_display_label(dimension_value).lower()}.",
                llm_hint="Use as a deterministic comparison label.",
                sort_order=offset,
            )
        )

    return pd.DataFrame(rows)


def _mapping_row(
    *,
    field_type: str,
    raw_key: str,
    display_label: str,
    business_definition: str,
    llm_hint: str,
    sort_order: int,
) -> dict[str, object]:
    return {
        "field_type": field_type,
        "raw_key": raw_key,
        "display_label": display_label,
        "business_definition": business_definition,
        "llm_hint": llm_hint,
        "sort_order": sort_order,
        "is_active": True,
    }


def _display_label(raw_key: str) -> str:
    if raw_key == "OTHER":
        return "OTHER"
    return raw_key.replace("_", " ").strip().title()


def _normalize_dimension_value(value: object) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")
    if normalized == "resort_hotel":
        return "resort"
    if normalized == "city_hotel":
        return "city"
    return normalized
