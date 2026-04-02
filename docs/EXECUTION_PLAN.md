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
[UI] — BLOCKED until engine is proven
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
**Gate:** Full-chain integration tests pass (fixture → validator → decomposer → classifier → scanner → narrative). This gate unlocks UI and adapter work.

### Phase 5 — Club Med Adapter
**Gate:** Adapter output passes schema_validator. No Kaggle column names leak into app code.

### Phase 6 — Narrative Interpreter
**Gate:** Template narrative passes banned-phrase test. Output conforms to NarrativeOutput schema.

### Phase 7 — UI (BLOCKED)
**Gate:** Phase 4 fully green. Not before.

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

**Active phase:** Phase 0
**Last completed task:** — (none)
**Last updated:** 2026-04-02
**Blocked items:** Phase 7 (UI)

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
