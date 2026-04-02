"""Deterministic narrative generation from analytical outputs."""

from __future__ import annotations

from metricpilot.contracts import ClassificationResult, ConcernLevel, NarrativeOutput, SegmentContribution


def build_narrative_output(
    *,
    classification: ClassificationResult,
    segment_contributions: list[SegmentContribution],
) -> NarrativeOutput:
    """Render a compact narrative summary from verified analytical outputs."""

    top_segment = segment_contributions[0] if segment_contributions else None
    confidence = _confidence_label(classification)
    finding, business_meaning = _narrative_lines(classification, top_segment)
    caveats = _build_caveats(classification, top_segment, segment_contributions)

    return NarrativeOutput(
        finding=finding,
        confidence=confidence,
        business_meaning=business_meaning,
        caveats=caveats,
    )


def _narrative_lines(
    classification: ClassificationResult,
    top_segment: SegmentContribution | None,
) -> tuple[str, str]:
    if classification.level is ConcernLevel.CONCERNING:
        finding = "Repeat guest rate shows clear deterioration across the observed period."
        business_meaning = (
            "The current pattern signals a sustained retention decline that merits prompt attention."
        )
    elif classification.level is ConcernLevel.WATCH:
        finding = "Repeat guest rate shows a shift that should stay under close monitoring."
        business_meaning = "The current pattern is not stable enough to ignore and should be monitored."
    else:
        finding = "Repeat guest rate remains stable within the observed period."
        business_meaning = "The current pattern stays within a stable range for retention monitoring."

    if top_segment is None:
        return finding, business_meaning

    segment_label = _segment_label(top_segment)
    if classification.level is ConcernLevel.CONCERNING:
        business_meaning = (
            f"{business_meaning} The largest segment change appears in {segment_label}."
        )
    elif classification.level is ConcernLevel.WATCH:
        business_meaning = (
            f"{business_meaning} The largest segment shift appears in {segment_label}."
        )
    else:
        business_meaning = (
            f"{business_meaning} The largest segment movement remains limited, including {segment_label}."
        )
    return finding, business_meaning


def _build_caveats(
    classification: ClassificationResult,
    top_segment: SegmentContribution | None,
    segment_contributions: list[SegmentContribution],
) -> list[str]:
    caveats = [
        f"Analytical evidence: {classification.evidence_text}",
        f"Detected change points: {len(classification.change_points)}",
    ]
    if top_segment is not None:
        caveats.append(
            f"Largest segment change observed in {_segment_label(top_segment)} with delta {top_segment.contribution_delta:.3f}."
        )
    else:
        caveats.append("No segment-level movement exceeded the ranking threshold.")
    if len(segment_contributions) > 1:
        caveats.append(f"Ranked segment count: {len(segment_contributions)}.")
    return caveats


def _confidence_label(classification: ClassificationResult) -> str:
    if classification.level is ConcernLevel.CONCERNING:
        return "high confidence"
    if classification.level is ConcernLevel.WATCH:
        return "moderate confidence"
    return "stable confidence"


def _segment_label(segment: SegmentContribution) -> str:
    return f"{segment.dimension_name} {segment.dimension_value}".replace("_", " ")
