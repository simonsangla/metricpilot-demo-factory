"""Deterministic canonical fixtures for Phase 2 time-series tests."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

FIXTURE_METRIC_NAME = "repeat_guest_rate"
FIXTURE_START_DATE = date(2025, 1, 1)
FIXTURE_DAYS = 180

_FIXTURE_DIMENSIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("hotel", ("resort", "city")),
    ("market_segment", ("direct", "corporate", "online")),
    ("customer_type", ("transient", "contract")),
)

_DIMENSION_OFFSETS: dict[tuple[str, str], float] = {
    ("hotel", "resort"): 0.015,
    ("hotel", "city"): -0.012,
    ("market_segment", "direct"): 0.010,
    ("market_segment", "corporate"): -0.008,
    ("market_segment", "online"): 0.004,
    ("customer_type", "transient"): 0.006,
    ("customer_type", "contract"): -0.006,
}

_DIMENSION_OBS_COUNTS: dict[tuple[str, str], int] = {
    ("hotel", "resort"): 96,
    ("hotel", "city"): 88,
    ("market_segment", "direct"): 78,
    ("market_segment", "corporate"): 70,
    ("market_segment", "online"): 74,
    ("customer_type", "transient"): 84,
    ("customer_type", "contract"): 68,
}


def stable_series() -> pd.DataFrame:
    """Return a deterministic 180-day canonical fixture with a flat trend."""

    return _build_fixture(
        demo_id="clubmed_repeat_guest_rate_stable",
        base_rate=0.42,
        trend_step=0.0,
        wave_scale=0.004,
        wave_period=14,
    )


def structural_decline() -> pd.DataFrame:
    """Return a deterministic 180-day canonical fixture with a negative slope."""

    return _build_fixture(
        demo_id="clubmed_repeat_guest_rate_structural_decline",
        base_rate=0.46,
        trend_step=-0.0008,
        wave_scale=0.002,
        wave_period=10,
    )


def segment_shift() -> pd.DataFrame:
    """Return a fixture where the global dip aligns with decline in two segment series."""

    return _build_fixture(
        demo_id="clubmed_repeat_guest_rate_segment_shift",
        base_rate=0.44,
        trend_step=-0.00045,
        wave_scale=0.0025,
        wave_period=12,
        segment_default_trend_step=0.0,
        segment_trend_overrides={
            ("hotel", "resort"): -0.00095,
            ("market_segment", "corporate"): -0.00085,
        },
    )


def temporary_dip() -> pd.DataFrame:
    """Return a fixture with a one-time dip followed by recovery."""

    return _build_fixture(
        demo_id="clubmed_repeat_guest_rate_temporary_dip",
        base_rate=0.43,
        trend_step=0.0,
        wave_scale=0.0015,
        wave_period=16,
        day_adjustments=_temporary_dip_adjustments(),
    )


def demo_registry_fixture() -> pd.DataFrame:
    """Return canonical demo registry metadata for the Club Med proxy demo."""

    return pd.DataFrame(
        [
            {
                "demo_id": "clubmed_repeat_guest_rate",
                "demo_label": "Club Med Repeat Guest Rate",
                "target_account": "Club Med",
                "target_vertical": "tourism",
                "scenario_label": "Repeat guest rate diagnostic demo",
                "primary_metric": "repeat_guest_rate",
                "public_data_source": "Kaggle hotel bookings proxy dataset",
                "disclaimer_text": "Uses public proxy data for deterministic demo analysis only.",
                "default_dimension_name": "hotel",
            }
        ]
    )


def semantic_mapping_fixture() -> pd.DataFrame:
    """Return canonical semantic mapping metadata for the Club Med proxy demo."""

    rows = [
        _semantic_mapping_row(
            field_type="metric",
            raw_key="repeat_guest_rate",
            display_label="Repeat Guest Rate",
            business_definition="Share of bookings attributed to returning guests.",
            llm_hint="Describe retention movement without causal claims.",
            sort_order=1,
        ),
        _semantic_mapping_row(
            field_type="dimension",
            raw_key="hotel",
            display_label="Hotel Type",
            business_definition="Booking slice by hotel category.",
            llm_hint="Use as a segment axis for comparison.",
            sort_order=10,
        ),
        _semantic_mapping_row(
            field_type="dimension",
            raw_key="market_segment",
            display_label="Market Segment",
            business_definition="Booking slice by demand segment.",
            llm_hint="Use as a segment axis for comparison.",
            sort_order=11,
        ),
        _semantic_mapping_row(
            field_type="dimension",
            raw_key="customer_type",
            display_label="Customer Type",
            business_definition="Booking slice by customer relationship type.",
            llm_hint="Use as a segment axis for comparison.",
            sort_order=12,
        ),
        _semantic_mapping_row(
            field_type="dimension_value",
            raw_key="all",
            display_label="All",
            business_definition="Global aggregate across all eligible bookings.",
            llm_hint="Use for the global benchmark series.",
            sort_order=20,
        ),
        _semantic_mapping_row(
            field_type="dimension_value",
            raw_key="resort",
            display_label="Resort",
            business_definition="Resort-oriented hotel slice.",
            llm_hint="Compare to other hotel slices.",
            sort_order=21,
        ),
        _semantic_mapping_row(
            field_type="dimension_value",
            raw_key="city",
            display_label="City",
            business_definition="City-oriented hotel slice.",
            llm_hint="Compare to other hotel slices.",
            sort_order=22,
        ),
        _semantic_mapping_row(
            field_type="dimension_value",
            raw_key="direct",
            display_label="Direct",
            business_definition="Direct booking demand segment.",
            llm_hint="Compare to other market segments.",
            sort_order=23,
        ),
        _semantic_mapping_row(
            field_type="dimension_value",
            raw_key="corporate",
            display_label="Corporate",
            business_definition="Corporate booking demand segment.",
            llm_hint="Compare to other market segments.",
            sort_order=24,
        ),
        _semantic_mapping_row(
            field_type="dimension_value",
            raw_key="online",
            display_label="Online",
            business_definition="Online booking demand segment.",
            llm_hint="Compare to other market segments.",
            sort_order=25,
        ),
        _semantic_mapping_row(
            field_type="dimension_value",
            raw_key="transient",
            display_label="Transient",
            business_definition="Transient customer relationship slice.",
            llm_hint="Compare to other customer types.",
            sort_order=26,
        ),
        _semantic_mapping_row(
            field_type="dimension_value",
            raw_key="contract",
            display_label="Contract",
            business_definition="Contract customer relationship slice.",
            llm_hint="Compare to other customer types.",
            sort_order=27,
        ),
    ]
    return pd.DataFrame(rows)


def _build_fixture(
    *,
    demo_id: str,
    base_rate: float,
    trend_step: float,
    wave_scale: float,
    wave_period: int,
    segment_default_trend_step: float | None = None,
    segment_trend_overrides: dict[tuple[str, str], float] | None = None,
    day_adjustments: dict[int, float] | None = None,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    default_segment_trend_step = (
        trend_step if segment_default_trend_step is None else segment_default_trend_step
    )
    segment_trend_overrides = segment_trend_overrides or {}
    day_adjustments = day_adjustments or {}
    for day_index in range(FIXTURE_DAYS):
        day = FIXTURE_START_DATE + timedelta(days=day_index)
        global_rate = _metric_value(
            base_rate=base_rate,
            trend_step=trend_step,
            day_index=day_index,
            wave_scale=wave_scale,
            wave_period=wave_period,
            offset=0.0,
            day_adjustment=day_adjustments.get(day_index, 0.0),
        )
        rows.append(
            _make_row(
                demo_id=demo_id,
                day=day,
                dimension_name="all",
                dimension_value="all",
                slice_level="global",
                metric_value=global_rate,
                obs_count=150,
            )
        )
        for dimension_name, values in _FIXTURE_DIMENSIONS:
            for dimension_value in values:
                rows.append(
                    _make_row(
                        demo_id=demo_id,
                        day=day,
                        dimension_name=dimension_name,
                        dimension_value=dimension_value,
                        slice_level="segment",
                        metric_value=_metric_value(
                            base_rate=base_rate,
                            trend_step=segment_trend_overrides.get(
                                (dimension_name, dimension_value), default_segment_trend_step
                            ),
                            day_index=day_index,
                            wave_scale=wave_scale,
                            wave_period=wave_period,
                            offset=_DIMENSION_OFFSETS[(dimension_name, dimension_value)],
                            day_adjustment=day_adjustments.get(day_index, 0.0),
                        ),
                        obs_count=_DIMENSION_OBS_COUNTS[(dimension_name, dimension_value)],
                    )
                )
    return pd.DataFrame(rows)


def _make_row(
    *,
    demo_id: str,
    day: date,
    dimension_name: str,
    dimension_value: str,
    slice_level: str,
    metric_value: float,
    obs_count: int,
) -> dict[str, object]:
    numerator = round(metric_value * obs_count, 6)
    denominator = float(obs_count)
    return {
        "demo_id": demo_id,
        "date_day": day,
        "metric_name": FIXTURE_METRIC_NAME,
        "metric_value": metric_value,
        "dimension_name": dimension_name,
        "dimension_value": dimension_value,
        "slice_level": slice_level,
        "obs_count": obs_count,
        "metric_numerator": numerator,
        "metric_denominator": denominator,
    }


def _metric_value(
    *,
    base_rate: float,
    trend_step: float,
    day_index: int,
    wave_scale: float,
    wave_period: int,
    offset: float,
    day_adjustment: float,
) -> float:
    wave_position = (day_index % wave_period) - (wave_period / 2)
    wave_component = wave_scale * (wave_position / wave_period)
    value = base_rate + (trend_step * day_index) + wave_component + offset + day_adjustment
    return round(value, 6)


def _temporary_dip_adjustments() -> dict[int, float]:
    adjustments: dict[int, float] = {}
    for day_index in range(FIXTURE_DAYS):
        if 70 <= day_index <= 84:
            midpoint = 77
            distance = abs(day_index - midpoint)
            adjustments[day_index] = -0.05 + (distance * 0.004)
        elif 85 <= day_index <= 96:
            adjustments[day_index] = -0.006 + ((day_index - 85) * 0.0005)
    return adjustments


def _semantic_mapping_row(
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
