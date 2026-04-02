# Prompt for Claude — Review and Roadmap

Review all files in this repo/folder and act as a strict technical reviewer.

Mission:
Produce a deterministic execution roadmap for the MetricPilot Demo Factory foundation phase.

Required stance:
- ARCH-FIRST
- fixture-first
- no UI until analytical chain is validated
- no fake claims
- no root-cause language
- reduce scope if drift appears

What to review:
- docs/PROJECT_CONTEXT.md
- docs/ARCHITECTURE.md
- docs/CANONICAL_SCHEMA.md
- docs/APP_SPEC.md
- docs/MODULE_SPEC.md
- docs/TEST_PLAN.md
- docs/ADAPTER_SPEC_CLUBMED_PROXY.md
- docs/PROSPECT_LIST.md
- docs/ROADMAP_SEED.md

Required output:
1. architecture review
2. risk review
3. recommended execution order
4. module-by-module implementation plan
5. test strategy
6. what to cut if drift starts
7. what should stay blocked until later
8. exact first 10 implementation tasks

Hard constraints:
- Club Med tourism only for v1
- first KPI = repeat_guest_rate
- global KPI + per-segment scan
- STL + Theil-Sen + change-point detection
- no separate driver table in v1
- no UI yet
