"""Narrative contract coverage for Phase 6 deterministic output generation."""

from __future__ import annotations

from metricpilot.contracts import (
    ClassificationResult,
    ConcernLevel,
    NarrativeOutput,
    SegmentContribution,
)
from metricpilot.narrative_contract import build_narrative_output

_BANNED_PHRASES = ("root cause", "caused by", "driven by", "due to")


def test_build_narrative_output_returns_contract_shape() -> None:
    output = build_narrative_output(
        classification=_classification(ConcernLevel.WATCH),
        segment_contributions=[_segment("hotel", "resort", -0.042)],
    )

    assert isinstance(output, NarrativeOutput)
    assert output.finding
    assert output.confidence
    assert output.business_meaning
    assert isinstance(output.caveats, list)
    assert output.caveats


def test_build_narrative_output_avoids_banned_phrases_and_mentions_deterioration_for_concerning() -> None:
    output = build_narrative_output(
        classification=_classification(ConcernLevel.CONCERNING, slope=-0.0008, change_points=[30, 60]),
        segment_contributions=[
            _segment("hotel", "resort", -0.12),
            _segment("market_segment", "corporate", -0.09),
        ],
    )

    combined_text = " ".join(
        [output.finding, output.confidence, output.business_meaning, *output.caveats]
    ).lower()

    assert "deterioration" in combined_text
    assert "hotel resort" in combined_text or "hotel= resort" in combined_text or "hotel resort" in combined_text.replace("_", " ")
    for phrase in _BANNED_PHRASES:
        assert phrase not in combined_text


def test_build_narrative_output_varies_by_concern_level() -> None:
    not_concerning = build_narrative_output(
        classification=_classification(ConcernLevel.NOT_CONCERNING, slope=0.0, change_points=[]),
        segment_contributions=[],
    )
    watch = build_narrative_output(
        classification=_classification(ConcernLevel.WATCH, slope=-0.0001, change_points=[65]),
        segment_contributions=[_segment("customer_type", "contract", -0.011)],
    )
    concerning = build_narrative_output(
        classification=_classification(ConcernLevel.CONCERNING, slope=-0.0008, change_points=[30, 60]),
        segment_contributions=[_segment("hotel", "resort", -0.12)],
    )

    assert len({not_concerning.finding, watch.finding, concerning.finding}) == 3
    assert "stable" in not_concerning.finding.lower()
    assert "monitor" in watch.business_meaning.lower()
    assert "deterioration" in concerning.finding.lower() or "deterioration" in concerning.business_meaning.lower()


def _classification(
    level: ConcernLevel,
    *,
    slope: float = -0.0002,
    change_points: list[int] | None = None,
) -> ClassificationResult:
    return ClassificationResult(
        level=level,
        slope=slope,
        slope_ci=(slope - 0.0001, slope + 0.0001),
        change_points=change_points or [],
        evidence_text="Deterministic analytical summary.",
    )


def _segment(dimension_name: str, dimension_value: str, contribution_delta: float) -> SegmentContribution:
    return SegmentContribution(
        dimension_name=dimension_name,
        dimension_value=dimension_value,
        contribution_delta=contribution_delta,
        obs_count=80,
        slope=contribution_delta / 100,
    )
