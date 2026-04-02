"""Streamlit workflow coverage for the Phase 7 compact UI."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from metricpilot.contracts import NarrativeOutput
from metricpilot.streamlit_app import build_diagnostic_view_model


def test_build_diagnostic_view_model_returns_expected_sections(tmp_path: Path) -> None:
    csv_path = _write_hotel_bookings_csv(tmp_path)

    view_model = build_diagnostic_view_model(csv_path)

    assert view_model["demo_registry"]["primary_metric"] == "repeat_guest_rate"
    assert view_model["validation"].ok is True
    assert isinstance(view_model["narrative"], NarrativeOutput)
    assert not view_model["segment_contributions"].empty
    assert list(view_model["global_series"].columns) == ["date_day", "metric_value"]


def test_streamlit_app_runs_local_workflow(tmp_path: Path) -> None:
    csv_path = _write_hotel_bookings_csv(tmp_path)

    app = AppTest.from_file("src/metricpilot/streamlit_app.py")
    app.run()
    app.text_input[0].set_value(str(csv_path))
    app.button[0].click()
    app.run()

    rendered_text = " ".join(node.value for node in app.markdown) + " " + " ".join(node.value for node in app.caption)
    subheaders = [node.value for node in app.subheader]

    assert app.title[0].value == "MetricPilot Demo Factory"
    assert "Club Med Repeat Guest Rate" in subheaders
    assert "Diagnostic summary" in subheaders
    assert "Top segment changes" in subheaders
    assert app.dataframe


def _write_hotel_bookings_csv(tmp_path: Path) -> Path:
    rows: list[dict[str, object]] = []
    top_countries = ["PRT", "FRA", "ESP", "GBR", "DEU", "ITA", "USA", "BRA", "NLD", "BEL"]
    other_country = "CHE"
    day_specs = [
        (2017, "January", day_of_month)
        for day_of_month in range(1, 15)
    ]

    for country_index_offset, (year, month_name, day_of_month) in enumerate(day_specs):
        for country_index, country in enumerate(top_countries):
            rows.extend(
                _daily_country_rows(
                    year=year,
                    day_of_month=day_of_month,
                    month_name=month_name,
                    country=country,
                    row_count=40,
                    country_index=country_index + country_index_offset,
                )
            )
        rows.extend(
            _daily_country_rows(
                year=year,
                day_of_month=day_of_month,
                month_name=month_name,
                country=other_country,
                row_count=30,
                country_index=len(top_countries) + country_index_offset,
            )
        )

    frame = pd.DataFrame(rows)
    csv_path = tmp_path / "hotel_bookings.csv"
    frame.to_csv(csv_path, index=False)
    return csv_path


def _daily_country_rows(
    *,
    year: int,
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
                "arrival_date_year": year,
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
