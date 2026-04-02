"""Deterministic concern classification from decomposed KPI series."""

from __future__ import annotations

import numpy as np
import ruptures as rpt
from scipy.stats import theilslopes

from metricpilot.contracts import ClassificationResult, ConcernLevel, DecompositionResult

DECLINE_SLOPE_THRESHOLD = -0.0005
WATCH_SLOPE_THRESHOLD = -0.00015
CONCERNING_DRAWDOWN_THRESHOLD = -0.05
WATCH_DRAWDOWN_THRESHOLD = -0.01
RECOVERY_THRESHOLD = 0.005
CHANGE_POINT_PENALTY = 3.0


def classify_decomposition(decomposition: DecompositionResult) -> ClassificationResult:
    """Classify trend concern using Theil-Sen slope and change-point evidence."""

    trend = decomposition.trend.astype(float).reset_index(drop=True)
    positions = np.arange(len(trend), dtype=float)
    slope, intercept, lower_slope, upper_slope = theilslopes(trend.to_numpy(), positions)
    change_points = _detect_change_points(trend.to_numpy())

    start_level = float(trend.iloc[0])
    end_level = float(trend.iloc[-1])
    trough_level = float(trend.min())
    drawdown = trough_level - start_level
    recovery = end_level - trough_level

    if slope <= DECLINE_SLOPE_THRESHOLD or (
        change_points
        and drawdown <= CONCERNING_DRAWDOWN_THRESHOLD
        and recovery <= RECOVERY_THRESHOLD
    ):
        level = ConcernLevel.CONCERNING
        evidence_text = "Trend remains materially below the starting level across the analysis window."
    elif (
        slope <= WATCH_SLOPE_THRESHOLD
        or (change_points and drawdown <= WATCH_DRAWDOWN_THRESHOLD and recovery >= RECOVERY_THRESHOLD)
    ):
        level = ConcernLevel.WATCH
        evidence_text = "Trend shows a detectable shift that warrants monitoring."
    else:
        level = ConcernLevel.NOT_CONCERNING
        evidence_text = "Trend remains stable within the monitored range."

    return ClassificationResult(
        level=level,
        slope=float(slope),
        slope_ci=(float(lower_slope), float(upper_slope)),
        change_points=change_points,
        evidence_text=evidence_text,
    )


def _detect_change_points(trend: np.ndarray) -> list[int]:
    if len(trend) < 3:
        return []
    result = rpt.Pelt(model="rbf").fit(trend).predict(pen=CHANGE_POINT_PENALTY)
    return [int(point) for point in result if point < len(trend)]
