"""Club Med proxy adapter coverage for Phase 5 canonical table generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from metricpilot.adapters.clubmed import build_clubmed_proxy_tables
from metricpilot.contracts import ALLOWED_DIMENSIONS, ValidationResult
from metricpilot.schema_validator import validate_canonical_frames


def test_build_clubmed_proxy_tables_outputs_conformant_canonical_tables(tmp_path: Path) -> None:
    csv_path = _write_hotel_bookings_csv(tmp_path)

    metric_timeseries, demo_registry, semantic_mapping = build_clubmed_proxy_tables(csv_path)

    validation = validate_canonical_frames(
        metric_timeseries=metric_timeseries,
        demo_registry=demo_registry,
        semantic_mapping=semantic_mapping,
    )

    assert validation == ValidationResult(ok=True, errors=[])
    assert metric_timeseries["metric_name"].unique().tolist() == ["repeat_guest_rate"]
    assert metric_timeseries["demo_id"].unique().tolist() == ["clubmed_repeat_guest_rate"]
    assert demo_registry.loc[0, "demo_id"] == "clubmed_repeat_guest_rate"
    assert demo_registry.loc[0, "primary_metric"] == "repeat_guest_rate"


def test_build_clubmed_proxy_tables_has_global_and_segment_rows_for_all_allowed_dimensions(
    tmp_path: Path,
) -> None:
    csv_path = _write_hotel_bookings_csv(tmp_path)

    metric_timeseries, _, _ = build_clubmed_proxy_tables(csv_path)

    global_rows = metric_timeseries.query(
        "slice_level == 'global' and dimension_name == 'all' and dimension_value == 'all'"
    )
    segment_rows = metric_timeseries.query("slice_level == 'segment'")

    assert not global_rows.empty
    assert global_rows["date_day"].nunique() == 2
    assert set(segment_rows["dimension_name"].unique()) == set(ALLOWED_DIMENSIONS) - {"all"}


def test_build_clubmed_proxy_tables_keeps_raw_columns_out_of_output_and_creates_other_bucket(
    tmp_path: Path,
) -> None:
    csv_path = _write_hotel_bookings_csv(tmp_path)

    metric_timeseries, _, _ = build_clubmed_proxy_tables(csv_path)

    assert "OTHER" in metric_timeseries.loc[
        metric_timeseries["dimension_name"] == "country_top", "dimension_value"
    ].unique()
    assert list(metric_timeseries.columns) == [
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


def _write_hotel_bookings_csv(tmp_path: Path) -> Path:
    rows: list[dict[str, object]] = []
    top_countries = ["PRT", "FRA", "ESP", "GBR", "DEU", "ITA", "USA", "BRA", "NLD", "BEL"]
    other_country = "CHE"
    month_by_day = {1: "January", 2: "February"}

    for day_of_month in (1, 2):
        for country_index, country in enumerate(top_countries):
            rows.extend(
                _daily_country_rows(
                    day_of_month=day_of_month,
                    month_name=month_by_day[day_of_month],
                    country=country,
                    row_count=40,
                    country_index=country_index,
                )
            )
        rows.extend(
            _daily_country_rows(
                day_of_month=day_of_month,
                month_name=month_by_day[day_of_month],
                country=other_country,
                row_count=30,
                country_index=len(top_countries),
            )
        )

    frame = pd.DataFrame(rows)
    csv_path = tmp_path / "hotel_bookings.csv"
    frame.to_csv(csv_path, index=False)
    return csv_path


def _daily_country_rows(
    *,
    day_of_month: int,
    month_name: str,
    country: str,
    row_count: int,
    country_index: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for booking_index in range(row_count):
        rows.append(
            {
                "arrival_date_year": 2017,
                "arrival_date_month": month_name,
                "arrival_date_day_of_month": day_of_month,
                "hotel": "Resort Hotel" if booking_index % 2 == 0 else "City Hotel",
                "market_segment": "Direct" if booking_index % 3 == 0 else "Corporate",
                "distribution_channel": "Direct" if booking_index % 4 < 2 else "TA/TO",
                "country": country,
                "customer_type": "Transient" if booking_index % 5 < 3 else "Contract",
                "deposit_type": "No Deposit" if booking_index % 2 == 0 else "Refundable",
                "is_repeated_guest": 1 if (booking_index + country_index + day_of_month) % 4 == 0 else 0,
            }
        )
    return rows
