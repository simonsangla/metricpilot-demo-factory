# MetricPilot Demo Factory — Execution Plan

> **Role of this file:** This is the master execution plan. ChatGPT reads this as the "brain" to issue instructions, review reports, enforce anti-drift, and update progress. The executor (Claude Code or other agent) implements tasks and returns reports. ChatGPT updates this file after each cycle.

---

## 1. Mission

Build a deterministic KPI diagnostic demo engine using public proxy data.
- **v1 vertical:** Club Med / tourism only
- **v1 KPI:** `repeat_guest_rate`
- **v1 scope:** analytical chain validation, no UI

---

## 2. Hard Constraints (never relax)

| ID | Constraint |
|----|-----------|
| HC-1 | Club Med tourism only for v1. No Lacoste, no retail. |
| HC-2 | First and only KPI = `repeat_guest_rate` |
| HC-3 | Global KPI + per-segment scan on every analysis run |
| HC-4 | STL decomposition + Theil-Sen slope + change-point detection |
| HC-5 | No separate driver table in v1 — scanner output is the contract |
| HC-6 | No UI until Phase 4 is fully green |
| HC-7 | No "root cause" language, no causality claims |
| HC-8 | No raw Kaggle column names in `src/metricpilot/` |
| HC-9 | Fixture-first: every module must pass on fixtures before adapter integration |
| HC-10 | ARCH-FIRST: contracts before code, tests before UI |

---

## 3. Architecture Summary

```
Raw Kaggle CSV
  |
  v
[Club Med Adapter] — transforms raw → canonical
  |
  v
[Canonical Tables]
  - metric_timeseries (fact)
  - demo_registry (metadata)
  - semantic_mapping (labels)
  |
  v
[Analytical Engine]
  - schema_validator
  - trend_decomposer (STL)
  - concern_classifier (Theil-Sen + change-point)
  - segment_scanner (ranked contributors)
  |
  v
[Narrative Interpreter] — deterministic template, no LLM
  |
  v
[UI] — unlocked after analytical, adapter, and narrative gates are green
```

---

## 4. Phases & Gate Rules

### Phase 0 — Repo Skeleton
**Gate:** `pip install -e .` succeeds, `import metricpilot` works.

### Phase 1 — Contracts
**Gate:** All dataclasses importable. Enum values match spec. No logic, pure types.

### Phase 2 — Fixtures
**Gate:** All 4 fixture generators produce DataFrames that pass schema_validator.

### Phase 3 — Core Analytics
**Gate:** All unit tests green for: schema_validator, trend_decomposer, concern_classifier, segment_scanner.

### Phase 4 — Integration Validation
**Gate:** Full-chain analytical integration tests pass (fixture → validator → decomposer → classifier → scanner). This gate unlocks Phase 5 and Phase 6 work. UI remains blocked until later gates are satisfied.

### Phase 5 — Club Med Adapter
**Gate:** Adapter output passes schema_validator. No Kaggle column names leak into app code.

### Phase 6 — Narrative Interpreter
**Gate:** Template narrative passes banned-phrase test, output conforms to NarrativeOutput schema, and concern-level outputs reflect the analytical classification without causal wording.

### Phase 7 — UI
**Gate:** Phase 4, Phase 5, and Phase 6 are green. This gate is now satisfied.

## 4A. Phase 7 UI Shell Decision

### Chosen shell
`Streamlit`

### Why Streamlit fits the current repo
- Lowest implementation overhead for a compact local diagnostic workflow.
- Maps directly onto the verified pipeline: load canonical tables, run analytical chain, render deterministic narrative.
- Supports fast local iteration without adding frontend build tooling, routing, or API glue.
- Keeps Phase 7 aligned with the repo's current single-user, local-run validation posture.

### Rejected alternatives
- `Gradio`
  - Better fit for prompt/demo interaction patterns than for a compact diagnostic dashboard with multiple structured outputs.
  - Adds less value than Streamlit for table-and-chart-heavy local inspection.
- `custom`
  - Requires unnecessary frontend/framework decisions, asset structure, and request wiring for the current scope.
  - Expands maintenance burden and implementation surface beyond the minimal Phase 7 goal.

### Constraint fit
- Preserves HC-1 and HC-2 by presenting only Club Med and `repeat_guest_rate`.
- Preserves HC-3 by requiring both global and per-segment outputs in one run.
- Preserves HC-5 by rendering existing scanner output directly, with no separate driver table.
- Preserves HC-7 by reusing the deterministic narrative layer and avoiding causal copy.
- Preserves HC-8 by consuming canonical adapter outputs only.
- Preserves HC-10 by building on already validated contracts, analytics, adapter, and narrative layers.

### Minimal T7.2 workflow outline
1. Load `hotel_bookings.csv` through the validated Club Med adapter.
2. Run schema validation on the canonical outputs and stop with deterministic errors if validation fails.
3. Run the analytical chain on the global KPI series and per-segment scanner output.
4. Render a compact local page with:
   - demo metadata header
   - global KPI classification summary
   - ranked segment table
   - deterministic narrative output
   - compact plots or tables for the global series only, if needed for readability

### Acceptance criteria for T7.2
- App starts locally with `streamlit run src/metricpilot/streamlit_app.py`.
- App loads the Club Med proxy dataset through the existing adapter path.
- App shows one diagnostic workflow for `repeat_guest_rate` only.
- App renders global classification, ranked segment output, and deterministic narrative in one run.
- App does not introduce new storage, auth, persistence, or deployment requirements.
- App copy contains no banned causal phrasing.

### Non-goals for Phase 7
- No deployment target selection.
- No authentication or multi-user support.
- No persistence layer or saved analyses.
- No styling system, design system migration, or multi-page app structure.
- No new KPIs, verticals, or recommendation engine behavior.

---

## 5. Anti-Drift Protocol

### For the Brain (ChatGPT)

Before issuing any instruction, check:

1. **Phase gate:** Is the current phase gate green? If not, do not advance.
2. **Constraint check:** Does the instruction violate any HC-* constraint? If yes, reject.
3. **Scope check:** Does the executor report mention anything outside v1 scope? If yes, flag and redirect.
4. **Quality check:** Does the executor report show tests passing? If not, fix before moving on.

### Drift detection triggers

| Signal | Action |
|--------|--------|
| Executor creates UI files | STOP. Reject. Phase 7 is blocked. |
| Executor uses raw Kaggle column names in `src/` | STOP. HC-8 violation. Revert. |
| Executor adds new KPIs beyond `repeat_guest_rate` | STOP. HC-2 violation. |
| Executor uses words: "root cause", "caused by", "driven by", "due to" in narrative output | STOP. HC-7 violation. |
| Executor adds a new vertical (retail, etc.) | STOP. HC-1 violation. |
| Executor skips fixtures and codes against raw data | STOP. HC-9 violation. |
| Tests fail and executor moves to next task | STOP. Fix first. |
| Executor adds a `driver_table` or `contribution_table` | STOP. HC-5 violation. |

### Recovery from drift

1. Identify which HC-* or phase gate was violated
2. Issue a corrective instruction referencing the specific constraint
3. Do not advance until the violation is resolved
4. Update TASK_LIST.md with a correction task if needed

---

## 6. Brain → Executor Instruction Format

Use this format when issuing instructions to the executor:

```
## FASTDEV INSTRUCTION

**Phase:** [current phase]
**Task:** [task ID from TASK_LIST.md]
**Objective:** [one sentence]

**Inputs:**
- [files to read / context needed]

**Expected output:**
- [files to create/modify]
- [tests to pass]

**Acceptance criteria:**
- [ ] [criterion 1]
- [ ] [criterion 2]

**Anti-drift reminders:**
- [relevant HC-* constraints for this task]
```

---

## 7. Executor → Brain Report Format

After each task, the executor returns:

```
## TASK REPORT

**Task:** [task ID]
**Status:** DONE | BLOCKED | PARTIAL
**Files created/modified:**
- [list]

**Tests run:**
- [test name]: PASS | FAIL
- [test name]: PASS | FAIL

**Decisions made:**
- [any non-trivial choices]

**Issues/blockers:**
- [if any]

**Next suggested task:** [task ID]
```

---

## 8. Brain Review Checklist

After receiving each executor report, ChatGPT checks:

- [ ] All acceptance criteria met?
- [ ] Tests listed and passing?
- [ ] No HC-* constraint violations in files created?
- [ ] No scope drift (new KPIs, new verticals, UI files, raw columns)?
- [ ] No banned language in narrative outputs?
- [ ] Task status updated in TASK_LIST.md?
- [ ] Phase gate still on track?

If all pass → mark task complete, issue next instruction.
If any fail → issue corrective instruction before advancing.

---

## 9. Sacrifice Order (if drift or time pressure)

Cut in this order (top = first to cut):

1. `semantic_mapping` richness — keep only `display_label`, drop `llm_hint`, `business_definition`
2. `country_top` dimension — reduces bucketing complexity
3. `narrative_contract` — defer entirely; `ClassificationResult` + `SegmentContribution` is proof enough
4. `deposit_type` dimension — low analytical value
5. `temporary_dip` fixture — hardest to calibrate

**Never cut:**
- schema_validator
- trend_decomposer
- concern_classifier
- segment_scanner
- `stable_series` and `structural_decline` fixtures

---

## 10. Current Status

**Active phase:** Phase 7
**Last completed task:** T6.2
**Last updated:** 2026-04-02
**Blocked items:** —

---

## 11. Reference Docs

| Doc | Purpose |
|-----|---------|
| `docs/PROJECT_CONTEXT.md` | Mission, scope, constraints |
| `docs/ARCHITECTURE.md` | Pipeline, modules, forbidden items |
| `docs/CANONICAL_SCHEMA.md` | Table definitions, allowed dimensions |
| `docs/APP_SPEC.md` | App goal, anti-drift rule |
| `docs/MODULE_SPEC.md` | Module I/O contracts |
| `docs/TEST_PLAN.md` | Required fixture cases and assertions |
| `docs/ADAPTER_SPEC_CLUBMED_PROXY.md` | Kaggle → canonical transform spec |
| `docs/BLUEPRINT_SPEC.md` | Engine boundaries, risk list |
| `docs/TASK_LIST.md` | Granular task tracker |
