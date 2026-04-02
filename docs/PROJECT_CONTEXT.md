# Project Context

## Mission
Build a deterministic KPI diagnostic demo engine using public proxy datasets, starting with Club Med / tourism logic only.

## Immediate target
Club Med / Charlotte Bernin.

## v1 business story
Detect whether a drop in `repeat_guest_rate` is:
- normal variation
- a watch signal
- a concerning structural deterioration

Then surface the most likely contributing segments.

## Out of scope for foundation phase
- UI polish
- multi-source ingestion
- Snowflake-specific implementation
- recommendation engine
- chat over data
- causal claims / "root cause"

## Non-negotiable constraints
- ARCH-FIRST
- fixture-first, not raw-data-first
- one canonical fact table plus metadata tables
- tests before UI
- no fake claims
- no raw Kaggle schema leaking into app code
