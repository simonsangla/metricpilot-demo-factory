# MetricPilot Demo Factory — Task List

> **Role of this file:** Granular task tracker. ChatGPT (brain) updates status after each executor report. Executor references task IDs when reporting.

---

## Status Legend

| Status | Meaning |
|--------|---------|
| `TODO` | Not started |
| `IN_PROGRESS` | Executor is working on it |
| `DONE` | Completed and verified by brain |
| `BLOCKED` | Cannot proceed — dependency or issue |
| `CUT` | Removed from scope (see sacrifice order in EXECUTION_PLAN.md) |

---

## Phase 0 — Repo Skeleton

| ID | Task | Status | Depends On | Acceptance Criteria |
|----|------|--------|------------|---------------------|
| T0.1 | Create `pyproject.toml` with pinned deps: `pandas>=2.0`, `statsmodels>=0.14`, `ruptures>=1.1`, `scipy>=1.11`, `pytest>=7.0`. Use `src` layout. | DONE | — | `pip install -e .` succeeds |
| T0.2 | Create package skeleton: `src/metricpilot/__init__.py`, empty module stubs (`contracts.py`, `fixtures.py`, `schema_validator.py`, `trend_decomposer.py`, `concern_classifier.py`, `segment_scanner.py`, `narrative_contract.py`), `tests/conftest.py`, `tests/test_*.py` stubs | DONE | T0.1 | `python -c "import metricpilot"` succeeds |

**Phase 0 gate:** `pip install -e .` + `import metricpilot` both succeed.

---

## Phase 1 — Contracts

| ID | Task | Status | Depends On | Acceptance Criteria |
|----|------|--------|------------|---------------------|
| T1.1 | Implement `contracts.py`: `MetricTimeseriesRow`, `DemoRegistryRow`, `SemanticMappingRow` dataclasses matching CANONICAL_SCHEMA.md | DONE | T0.2 | Dataclasses importable, fields match schema |
| T1.2 | Add `ConcernLevel` enum (`NOT_CONCERNING`, `WATCH`, `CONCERNING`) to contracts | DONE | T1.1 | Enum importable |
| T1.3 | Add `DecompositionResult` dataclass (trend, seasonal, residual, observed) | DONE | T1.1 | Dataclass importable |
| T1.4 | Add `ClassificationResult` dataclass (level, slope, slope_ci, change_points, evidence_text) | DONE | T1.2 | Dataclass importable |
| T1.5 | Add `SegmentContribution` dataclass (dimension_name, dimension_value, contribution_delta, obs_count, slope) | DONE | T1.1 | Dataclass importable |
| T1.6 | Add `NarrativeOutput` dataclass (finding, confidence, business_meaning, caveats) | DONE | T1.1 | Dataclass importable |
| T1.7 | Add `AnalysisSummary` dataclass — engine output contract linking ClassificationResult + list[SegmentContribution] | DONE | T1.4, T1.5 | Dataclass importable |
| T1.8 | Add `ALLOWED_DIMENSIONS` frozen list: `all`, `hotel`, `market_segment`, `distribution_channel`, `customer_type`, `deposit_type`, `country_top` | DONE | T1.1 | Constant importable, is a frozenset or tuple |
| T1.9 | Add `ValidationResult` dataclass (ok: bool, errors: list[str]) | DONE | T1.1 | Dataclass importable |

**Phase 1 gate:** All contracts importable. `python -c "from metricpilot.contracts import *"` succeeds. No logic, pure types.

---

## Phase 2 — Fixtures

| ID | Task | Status | Depends On | Acceptance Criteria |
|----|------|--------|------------|---------------------|
| T2.1 | Implement `stable_series()` fixture: 180 days, daily grain, global + 3 dimensions x 2-3 values, flat trend + noise, `obs_count >= 50` | DONE | T1.* | Returns DataFrame, columns match schema, 180 unique dates |
| T2.2 | Implement `structural_decline()` fixture: 180 days, steady negative slope across all segments | DONE | T2.1 | Returns DataFrame, clear negative trend visible |
| T2.3 | Implement `segment_shift()` fixture: 180 days, global dip driven by 1-2 segments declining, others stable | DONE | T2.1 | Returns DataFrame, identifiable segment-driven deterioration |
| T2.4 | Implement `temporary_dip()` fixture: 180 days, one-time dip with recovery | DONE | T2.1 | Returns DataFrame, dip visible but trend recovers |
| T2.5 | Add `demo_registry_fixture()` and `semantic_mapping_fixture()` returning conformant DataFrames | DONE | T1.* | Returns DataFrames matching schema |

**Phase 2 gate:** All 4 time-series fixtures + metadata fixtures pass schema_validator (validated in Phase 3).

---

## Phase 3 — Core Analytics

| ID | Task | Status | Depends On | Acceptance Criteria |
|----|------|--------|------------|---------------------|
| T3.1 | Implement `schema_validator.py`: column presence, types, dimension allowlist, global row rules, ratio tolerance, demo_id consistency | DONE | T1.9, T1.8 | Function callable, returns ValidationResult |
| T3.2 | Write `tests/test_schema_validator.py`: valid fixture passes, missing column fails, bad dimension fails, wrong global dimension_value fails, mismatched ratio fails | DONE | T3.1, T2.1 | `pytest tests/test_schema_validator.py` green |
| T3.3 | Implement `trend_decomposer.py`: STL wrapper (period=7), returns DecompositionResult, raises InsufficientDataError if len < 14 | DONE | T1.3 | Function callable, returns DecompositionResult |
| T3.4 | Write `tests/test_trend_decomposer.py`: component shapes match input, stable fixture → flat trend, short series → error | DONE | T3.3, T2.1 | `pytest tests/test_trend_decomposer.py` green |
| T3.5 | Implement `concern_classifier.py`: Theil-Sen slope on trend, change-point via ruptures.Pelt, classification logic (NOT_CONCERNING / WATCH / CONCERNING) | DONE | T1.4, T3.3 | Function callable, returns ClassificationResult |
| T3.6 | Write `tests/test_concern_classifier.py`: stable→NOT_CONCERNING, decline→CONCERNING, dip→WATCH or NOT_CONCERNING | DONE | T3.5, T2.* | `pytest tests/test_concern_classifier.py` green |
| T3.7 | Implement `segment_scanner.py`: filter by min obs_count/denominator (30), Theil-Sen per segment, rank by contribution_delta | DONE | T1.5 | Function callable, returns list[SegmentContribution] |
| T3.8 | Write `tests/test_segment_scanner.py`: segment_shift fixture → top contributor matches injected segment, stable → no extreme contributors, small segments filtered | DONE | T3.7, T2.* | `pytest tests/test_segment_scanner.py` green |

**Phase 3 gate:** `pytest tests/` all green.

---

## Phase 4 — Integration Validation

| ID | Task | Status | Depends On | Acceptance Criteria |
|----|------|--------|------------|---------------------|
| T4.1 | Write `tests/test_integration.py`: full chain `stable_series` → validator → decomposer → classifier → scanner. Assert NOT_CONCERNING. | DONE | T3.* | Test green |
| T4.2 | Add integration test: `structural_decline` → validator → decomposer → classifier → scanner. Assert CONCERNING. | DONE | T4.1 | Test green |
| T4.3 | Add integration test: `segment_shift` → full chain → CONCERNING + scanner identifies injected segment | DONE | T4.1 | Test green |
| T4.4 | Add guard test: grep `src/metricpilot/` for raw Kaggle column names — must find zero matches | DONE | T3.* | Test green |
| T4.5 | Add integration test: `temporary_dip` → validator → decomposer → classifier → scanner. Assert WATCH or NOT_CONCERNING. | DONE | T4.1 | Test green |

**Phase 4 gate:** All analytical integration + source-contract guard tests green. **This gate unlocks Phase 5 and Phase 6 work, and is still required before Phase 7.**

---

## Phase 5 — Club Med Adapter

| ID | Task | Status | Depends On | Acceptance Criteria |
|----|------|--------|------------|---------------------|
| T5.1 | Create `src/metricpilot/adapters/clubmed.py`: load `hotel_bookings.csv`, build `date_day` from arrival parts, compute `repeat_guest_rate` (numerator/denominator) | DONE | T4.* | Function callable |
| T5.2 | Implement global series: aggregate all bookings per day → one `metric_timeseries` row per date with `slice_level=global`, `dimension_name=all`, `dimension_value=all` | DONE | T5.1 | Output has global rows |
| T5.3 | Implement segment series: per-day aggregation for each allowed dimension/value pair, `slice_level=segment` | DONE | T5.1 | Output has segment rows for all allowed dimensions |
| T5.4 | Implement `country_top` bucketing: top 10 countries + OTHER | DONE | T5.3 | country_top dimension present, OTHER bucket exists |
| T5.5 | Generate `demo_registry` row and `semantic_mapping` rows for Club Med demo | DONE | T5.1 | DataFrames match schema |
| T5.6 | Write `tests/test_adapter_clubmed.py`: output passes schema_validator, has global + segment rows, no raw Kaggle columns in output, country_top has OTHER | DONE | T5.* | `pytest tests/test_adapter_clubmed.py` green |

**Phase 5 gate:** Adapter output passes schema_validator. Zero Kaggle column names in `src/metricpilot/`.

---

## Phase 6 — Narrative Interpreter

| ID | Task | Status | Depends On | Acceptance Criteria |
|----|------|--------|------------|---------------------|
| T6.1 | Implement `narrative_contract.py`: template-based narrative from ClassificationResult + list[SegmentContribution] → NarrativeOutput | DONE | T1.6, T4.* | Function callable, returns NarrativeOutput |
| T6.2 | Write `tests/test_narrative.py`: output schema valid, no banned phrases, concerning output mentions deterioration, different outputs for different concern levels | DONE | T6.1 | `pytest tests/test_narrative.py` green |

**Phase 6 gate:** Narrative output conforms to schema, zero banned phrases.

---

## Phase 7 — UI

| ID | Task | Status | Depends On | Acceptance Criteria |
|----|------|--------|------------|---------------------|
| T7.1 | Document the chosen UI shell (Streamlit / Gradio / custom) with constraint fit, implementation rationale, and acceptance criteria for `T7.2`. | DONE | T4.*, T5.*, T6.* | Decision documented in repo plan docs |
| T7.2 | Build compact diagnostic workflow using the approved shell and existing validated analytics, adapter, and narrative surfaces. | DONE | T7.1 | App runs locally using the documented Streamlit workflow |

---

## Progress Tracker

| Phase | Total Tasks | Done | Remaining | Status |
|-------|-------------|------|-----------|--------|
| 0 — Skeleton | 2 | 2 | 0 | DONE |
| 1 — Contracts | 9 | 9 | 0 | DONE |
| 2 — Fixtures | 5 | 5 | 0 | DONE |
| 3 — Analytics | 8 | 8 | 0 | DONE |
| 4 — Integration | 5 | 5 | 0 | DONE |
| 5 — Adapter | 6 | 6 | 0 | DONE |
| 6 — Narrative | 2 | 2 | 0 | DONE |
| 7 — UI | 2 | 2 | 0 | DONE |
| **Total** | **39** | **39** | **0** | |

---

## Change Log

| Date | Change | By |
|------|--------|----|
| 2026-04-02 | Initial plan and task list created | Claude (reviewer) |
