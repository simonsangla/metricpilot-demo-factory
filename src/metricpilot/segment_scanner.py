"""Deterministic ranking of segment-level KPI deterioration signals."""

from __future__ import annotations

import pandas as pd
from scipy.stats import theilslopes

from metricpilot.contracts import SegmentContribution

DEFAULT_MIN_OBS_COUNT = 30
DEFAULT_MIN_DENOMINATOR = 30.0
WINDOW_DAYS = 30


def scan_segments(
    metric_timeseries: pd.DataFrame,
    *,
    target_metric: str,
    min_obs_count: int = DEFAULT_MIN_OBS_COUNT,
    min_denominator: float = DEFAULT_MIN_DENOMINATOR,
) -> list[SegmentContribution]:
    """Return ranked segment-level deterioration statistics for one KPI."""

    segment_rows = metric_timeseries.loc[
        (metric_timeseries["metric_name"] == target_metric)
        & (metric_timeseries["slice_level"] == "segment")
    ].copy()

    if segment_rows.empty:
        return []

    results: list[SegmentContribution] = []
    grouped = segment_rows.sort_values("date_day").groupby(
        ["dimension_name", "dimension_value"],
        sort=True,
    )

    for (dimension_name, dimension_value), frame in grouped:
        if (frame["obs_count"] < min_obs_count).any():
            continue
        if (frame["metric_denominator"] < min_denominator).any():
            continue

        values = frame["metric_value"].astype(float).reset_index(drop=True)
        slope, _, _, _ = theilslopes(values.to_numpy(), range(len(values)))
        contribution_delta = float(values.iloc[-WINDOW_DAYS:].mean() - values.iloc[:WINDOW_DAYS].mean())
        results.append(
            SegmentContribution(
                dimension_name=dimension_name,
                dimension_value=dimension_value,
                contribution_delta=contribution_delta,
                obs_count=int(frame["obs_count"].min()),
                slope=float(slope),
            )
        )

    return sorted(results, key=lambda item: (item.contribution_delta, item.dimension_name, item.dimension_value))
