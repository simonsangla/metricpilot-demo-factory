"""Fixture tests for the Phase 2 canonical series builders."""

from __future__ import annotations

import pandas as pd

from metricpilot.fixtures import (
    demo_registry_fixture,
    segment_shift,
    semantic_mapping_fixture,
    stable_series,
    structural_decline,
    temporary_dip,
)


def test_stable_series_matches_documented_shape() -> None:
    frame = stable_series()

    assert list(frame.columns) == [
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
    assert frame["date_day"].nunique() == 180
    assert frame["metric_name"].unique().tolist() == ["repeat_guest_rate"]
    assert set(frame["dimension_name"].unique()) == {
        "all",
        "hotel",
        "market_segment",
        "customer_type",
    }
    assert (frame["obs_count"] >= 50).all()
    assert (
        frame.query("dimension_name == 'all' and dimension_value == 'all' and slice_level == 'global'")
        .shape[0]
        == 180
    )


def test_stable_series_has_flat_global_trend() -> None:
    frame = stable_series()
    global_series = (
        frame.query("dimension_name == 'all'")
        .sort_values("date_day")
        .loc[:, "metric_value"]
        .reset_index(drop=True)
    )
    first_window = global_series.iloc[:30].mean()
    last_window = global_series.iloc[-30:].mean()

    assert abs(last_window - first_window) < 0.002


def test_structural_decline_has_negative_trend_for_every_series() -> None:
    frame = structural_decline()

    grouped = frame.sort_values("date_day").groupby(
        ["dimension_name", "dimension_value", "slice_level"], sort=True
    )

    for _, series_frame in grouped:
        values = series_frame["metric_value"].reset_index(drop=True)
        assert values.iloc[-30:].mean() < values.iloc[:30].mean()


def test_structural_decline_preserves_canonical_ratio_fields() -> None:
    frame = structural_decline()
    recomputed = (frame["metric_numerator"] / frame["metric_denominator"]).round(6)

    pd.testing.assert_series_equal(
        recomputed,
        frame["metric_value"],
        check_names=False,
    )


def test_segment_shift_is_deterministic_and_canonical() -> None:
    left = segment_shift()
    right = segment_shift()

    pd.testing.assert_frame_equal(left, right)
    assert left["date_day"].nunique() == 180
    assert left["metric_name"].unique().tolist() == ["repeat_guest_rate"]
    assert (
        left.query("dimension_name == 'all' and dimension_value == 'all' and slice_level == 'global'")
        .shape[0]
        == 180
    )


def test_segment_shift_has_global_dip_with_limited_declining_segments() -> None:
    frame = segment_shift()
    grouped = frame.sort_values("date_day").groupby(
        ["dimension_name", "dimension_value", "slice_level"], sort=True
    )

    declining_segments: list[tuple[str, str, str]] = []
    stable_segments: list[tuple[str, str, str]] = []

    for group_key, series_frame in grouped:
        values = series_frame["metric_value"].reset_index(drop=True)
        delta = values.iloc[-30:].mean() - values.iloc[:30].mean()
        if group_key[0] == "all":
            assert delta < -0.02
            continue
        if delta < -0.02:
            declining_segments.append(group_key)
        elif abs(delta) < 0.005:
            stable_segments.append(group_key)

    assert declining_segments == [
        ("hotel", "resort", "segment"),
        ("market_segment", "corporate", "segment"),
    ]
    assert len(stable_segments) == 5


def test_segment_shift_preserves_canonical_ratio_fields() -> None:
    frame = segment_shift()
    recomputed = (frame["metric_numerator"] / frame["metric_denominator"]).round(6)

    pd.testing.assert_series_equal(
        recomputed,
        frame["metric_value"],
        check_names=False,
    )


def test_temporary_dip_is_deterministic_and_canonical() -> None:
    left = temporary_dip()
    right = temporary_dip()

    pd.testing.assert_frame_equal(left, right)
    assert left["date_day"].nunique() == 180
    assert left["metric_name"].unique().tolist() == ["repeat_guest_rate"]


def test_temporary_dip_has_visible_dip_and_recovery() -> None:
    frame = temporary_dip().sort_values("date_day")
    global_series = (
        frame.query("dimension_name == 'all' and dimension_value == 'all'")
        .loc[:, "metric_value"]
        .reset_index(drop=True)
    )

    baseline = global_series.iloc[:30].mean()
    dip_window = global_series.iloc[72:83].mean()
    recovery_window = global_series.iloc[-30:].mean()

    assert dip_window < baseline - 0.02
    assert abs(recovery_window - baseline) < 0.005


def test_temporary_dip_preserves_canonical_ratio_fields() -> None:
    frame = temporary_dip()
    recomputed = (frame["metric_numerator"] / frame["metric_denominator"]).round(6)

    pd.testing.assert_series_equal(
        recomputed,
        frame["metric_value"],
        check_names=False,
    )


def test_demo_registry_fixture_matches_canonical_schema() -> None:
    frame = demo_registry_fixture()

    assert list(frame.columns) == [
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
    assert frame.shape == (1, 9)
    assert frame.loc[0, "demo_id"] == "clubmed_repeat_guest_rate"
    assert frame.loc[0, "primary_metric"] == "repeat_guest_rate"
    assert frame.loc[0, "target_account"] == "Club Med"
    assert frame.loc[0, "default_dimension_name"] == "hotel"


def test_semantic_mapping_fixture_matches_canonical_schema() -> None:
    frame = semantic_mapping_fixture()

    assert list(frame.columns) == [
        "field_type",
        "raw_key",
        "display_label",
        "business_definition",
        "llm_hint",
        "sort_order",
        "is_active",
    ]
    assert set(frame["field_type"].unique()) == {"metric", "dimension", "dimension_value"}
    assert frame["is_active"].tolist() == [True] * len(frame)
    assert frame["raw_key"].tolist() == [
        "repeat_guest_rate",
        "hotel",
        "market_segment",
        "customer_type",
        "all",
        "resort",
        "city",
        "direct",
        "corporate",
        "online",
        "transient",
        "contract",
    ]
