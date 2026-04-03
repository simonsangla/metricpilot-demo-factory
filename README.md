# MetricPilot Demo Factory

Deterministic MVP for a Club Med repeat guest rate diagnostic workflow built on public proxy data.

## MVP status

- Vertical: Club Med / tourism only
- KPI: `repeat_guest_rate` only
- Engine: schema validation, STL decomposition, Theil-Sen slope, change-point detection, segment scanning
- Adapter: Club Med proxy adapter from `hotel_bookings.csv` into canonical tables
- Narrative: deterministic template output only
- UI: compact local Streamlit app
- Test status: `pytest` green

## What is in the repo

- [docs/EXECUTION_PLAN.md](docs/EXECUTION_PLAN.md): final execution plan and UI-shell decision
- [docs/TASK_LIST.md](docs/TASK_LIST.md): completed task tracker
- [docs/MVP_RUNBOOK.md](docs/MVP_RUNBOOK.md): install, test, and run instructions
- [docs/CLAUDE_CODE_HANDOFF.md](docs/CLAUDE_CODE_HANDOFF.md): design-focused handoff for the next app pass

## Local workflow

1. Install dependencies:

```bash
pip install -e .
```

2. Run the full test suite:

```bash
pytest
```

3. Start the Streamlit app:

```bash
streamlit run src/metricpilot/streamlit_app.py
```

4. Provide a local path to `hotel_bookings.csv` in the UI and run the diagnostic.

## Current app behavior

The app runs one compact workflow only:

- load local `hotel_bookings.csv`
- transform it through the validated Club Med adapter
- validate canonical tables
- classify the global `repeat_guest_rate` series
- rank segment changes
- render deterministic narrative output

## Scope guardrails

- No extra KPIs
- No extra verticals
- No causal claims
- No auth, persistence, APIs, or deployment logic
- No multi-page UI

## Package layout

```text
docs/
src/metricpilot/
  adapters/clubmed.py
  schema_validator.py
  trend_decomposer.py
  concern_classifier.py
  segment_scanner.py
  narrative_contract.py
  streamlit_app.py
tests/
```
