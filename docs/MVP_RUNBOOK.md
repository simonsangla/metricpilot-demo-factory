# MVP Runbook

## Purpose

This runbook is the smallest complete workflow for running and verifying the MetricPilot Demo Factory MVP locally.

## Preconditions

- Python 3.12+
- A local `hotel_bookings.csv` compatible with the Club Med proxy adapter spec

## Install

```bash
pip install -e .
```

## Validate

Run the full repo validation:

```bash
pytest
```

Expected result:

- full suite green

## Launch the app

```bash
streamlit run src/metricpilot/streamlit_app.py
```

Expected result:

- Streamlit serves a local page
- the page asks for a `hotel_bookings.csv` path

## Execute one diagnostic run

1. Enter a local CSV path.
2. Click `Run diagnostic`.
3. Verify the page renders:
   - demo metadata
   - concern level
   - deterministic narrative
   - top segment changes
   - global KPI series table

## Acceptance recap

The MVP is considered frozen when all of the following hold:

- `pytest` is green
- adapter output passes schema validation
- global + per-segment outputs are present
- narrative output remains deterministic and non-causal
- Streamlit app starts locally and executes the compact workflow

## Known limits

- Club Med / tourism only
- `repeat_guest_rate` only
- local run only
- no persistence
- no auth
- no deployment target
- no visual design pass beyond the minimal Streamlit shell
