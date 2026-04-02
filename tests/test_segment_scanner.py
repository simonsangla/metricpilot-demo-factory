"""Segment scanner coverage for Phase 3 ranked segment analysis."""

from __future__ import annotations

import pandas as pd

from metricpilot.contracts import SegmentContribution
from metricpilot.fixtures import segment_shift, stable_series
from metricpilot.segment_scanner import scan_segments


def test_scan_segments_segment_shift_ranks_injected_top_contributor_first() -> None:
    results = scan_segments(segment_shift(), target_metric="repeat_guest_rate")

    assert results
    assert isinstance(results[0], SegmentContribution)
    assert (results[0].dimension_name, results[0].dimension_value) == ("hotel", "resort")
    assert results[0].contribution_delta < 0


def test_scan_segments_stable_fixture_has_no_extreme_contributors() -> None:
    results = scan_segments(stable_series(), target_metric="repeat_guest_rate")

    assert results
    assert max(abs(item.contribution_delta) for item in results) < 0.02


def test_scan_segments_filters_small_segments() -> None:
    frame = stable_series().copy()
    frame.loc[
        (frame["dimension_name"] == "market_segment") & (frame["dimension_value"] == "direct"),
        ["obs_count", "metric_denominator"],
    ] = [20, 20.0]

    results = scan_segments(frame, target_metric="repeat_guest_rate")

    assert all(
        not (item.dimension_name == "market_segment" and item.dimension_value == "direct")
        for item in results
    )
