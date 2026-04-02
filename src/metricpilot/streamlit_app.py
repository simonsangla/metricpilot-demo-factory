"""Streamlit UI for the compact MetricPilot diagnostic workflow."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from metricpilot.adapters.clubmed import build_clubmed_proxy_tables
from metricpilot.concern_classifier import classify_decomposition
from metricpilot.contracts import ClassificationResult, NarrativeOutput, SegmentContribution, ValidationResult
from metricpilot.narrative_contract import build_narrative_output
from metricpilot.schema_validator import validate_canonical_frames
from metricpilot.segment_scanner import scan_segments
from metricpilot.trend_decomposer import decompose_timeseries


def build_diagnostic_view_model(csv_path: str | Path) -> dict[str, object]:
    """Run the validated local workflow and return deterministic render data."""

    metric_timeseries, demo_registry, semantic_mapping = build_clubmed_proxy_tables(csv_path)
    validation = validate_canonical_frames(
        metric_timeseries=metric_timeseries,
        demo_registry=demo_registry,
        semantic_mapping=semantic_mapping,
    )
    if not validation.ok:
        raise ValueError("; ".join(validation.errors))

    global_series = (
        metric_timeseries.query("dimension_name == 'all' and dimension_value == 'all'")
        .sort_values("date_day")
        .set_index("date_day")["metric_value"]
    )
    classification = classify_decomposition(decompose_timeseries(global_series))
    segment_contributions = scan_segments(metric_timeseries, target_metric="repeat_guest_rate")
    narrative = build_narrative_output(
        classification=classification,
        segment_contributions=segment_contributions,
    )
    return {
        "demo_registry": demo_registry.iloc[0].to_dict(),
        "validation": validation,
        "classification": classification,
        "narrative": narrative,
        "segment_contributions": _segment_dataframe(segment_contributions),
        "global_series": global_series.reset_index(name="metric_value"),
    }


def render_streamlit_app(default_csv_path: str = "hotel_bookings.csv") -> None:
    """Render the compact local Streamlit diagnostic page."""

    st.set_page_config(page_title="MetricPilot Demo Factory", layout="wide")
    st.title("MetricPilot Demo Factory")
    st.caption("Club Med repeat guest rate diagnostic workflow")

    csv_path = st.text_input("Local hotel_bookings.csv path", value=default_csv_path)
    run_clicked = st.button("Run diagnostic")

    if not run_clicked:
        st.info("Provide a local hotel_bookings.csv path and run the diagnostic workflow.")
        return

    try:
        view_model = build_diagnostic_view_model(csv_path)
    except Exception as exc:  # pragma: no cover - exercised via Streamlit rendering
        st.error(f"Diagnostic workflow failed: {exc}")
        return

    _render_view_model(view_model)


def _render_view_model(view_model: dict[str, object]) -> None:
    demo_registry = view_model["demo_registry"]
    classification = view_model["classification"]
    narrative = view_model["narrative"]
    segment_contributions = view_model["segment_contributions"]
    global_series = view_model["global_series"]

    st.subheader(str(demo_registry["demo_label"]))
    st.write(f"Account: {demo_registry['target_account']}")
    st.write(f"Metric: {demo_registry['primary_metric']}")

    st.subheader("Diagnostic summary")
    st.metric("Concern level", _concern_label(classification))
    st.write(f"Confidence: {narrative.confidence}")
    st.write(f"Finding: {narrative.finding}")
    st.write(f"Business meaning: {narrative.business_meaning}")

    st.subheader("Caveats")
    for caveat in narrative.caveats:
        st.write(f"- {caveat}")

    st.subheader("Top segment changes")
    st.dataframe(segment_contributions, width="stretch")

    st.subheader("Global KPI series")
    st.dataframe(global_series, width="stretch")


def _segment_dataframe(segment_contributions: list[SegmentContribution]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "dimension_name": item.dimension_name,
                "dimension_value": item.dimension_value,
                "contribution_delta": item.contribution_delta,
                "obs_count": item.obs_count,
                "slope": item.slope,
            }
            for item in segment_contributions
        ]
    )


def _concern_label(classification: ClassificationResult) -> str:
    return classification.level.value.replace("_", " ").title()


if __name__ == "__main__":
    render_streamlit_app()
