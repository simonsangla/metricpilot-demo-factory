# Claude Code Handoff

## Objective

Take over the next pass focused on app design quality, without changing the frozen MVP scope.

## Frozen MVP baseline

- All phases through `T7.2` are complete in [docs/TASK_LIST.md](docs/TASK_LIST.md)
- Full `pytest` suite is green
- Approved shell is Streamlit
- Current app entrypoint is [streamlit_app.py](../src/metricpilot/streamlit_app.py)

## What must stay fixed

- Club Med / tourism only
- `repeat_guest_rate` only
- existing adapter, analytics, and narrative modules remain the data/logic source
- no causal wording
- no raw source-column leakage outside canonical adapter surfaces
- no new persistence, auth, API, or deployment scope unless explicitly requested later

## Recommended design focus

- improve information hierarchy and visual clarity in the Streamlit page
- make the compact diagnostic workflow easier to scan
- keep global classification, segment ranking, and narrative visible without adding new flows
- keep the app single-page unless a later plan change explicitly expands scope

## Recommended working order

1. Review [streamlit_app.py](../src/metricpilot/streamlit_app.py)
2. Preserve the existing workflow contract
3. Improve presentation only after confirming `pytest` stays green
4. Keep any new labels or copy non-causal

## Minimal acceptance bar for the design pass

- app still runs with `streamlit run src/metricpilot/streamlit_app.py`
- app still uses the same validated backend surfaces
- app still renders one compact workflow
- existing tests remain green, with additional UI-focused tests only if they are deterministic

## Non-goals for the handoff

- reworking the analytical engine
- changing the KPI or vertical
- introducing recommendations or speculative explanations
- building a broader product shell around the MVP
