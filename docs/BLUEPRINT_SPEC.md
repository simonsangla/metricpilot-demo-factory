# Blueprint Specification

## Goal
Create a reusable demo engine, not a one-off prospect dashboard.

## v1 target
Club Med tourism proxy only.

## Core promise
"I reduce time-to-diagnosis for KPI deterioration by separating normal variation from concerning structural shifts and surfacing likely contributing segments."

## Engine boundaries
- One KPI first: `repeat_guest_rate`
- One fact table
- Metadata tables for demo context and semantic control
- Deterministic analysis before UI
- Interpretation only after stats are proven

## Main risks
- coding against raw dataset shape
- overclaiming root cause
- building UI before module proof
- segment-noise explosion
- scope drift into multi-vertical platform

## First sacrifice if drift starts
Cut semantic richness before cutting analytical proof.
Cut extra dimensions before cutting concern classification.
