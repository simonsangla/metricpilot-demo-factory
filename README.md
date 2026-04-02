# MetricPilot Demo Factory

Deterministic KPI diagnostic demo engine using public proxy datasets.

## v1 Scope

- **Vertical:** Club Med / tourism
- **KPI:** `repeat_guest_rate`
- **Method:** STL decomposition + Theil-Sen slope + change-point detection
- **Output:** Concern classification (`not_concerning` / `watch` / `concerning`) + ranked segment contributors

## Architecture

```
Raw Kaggle CSV → Club Med Adapter → Canonical Tables → Analytical Engine → Narrative Interpreter → UI (blocked)
```

## Project Structure

```
docs/                  # Architecture, specs, contracts, execution plan
sample_data/           # Example canonical CSVs
src/metricpilot/       # Source code (not yet created)
tests/                 # Test suite (not yet created)
```

## Key Docs

| Doc | Purpose |
|-----|---------|
| [EXECUTION_PLAN.md](docs/EXECUTION_PLAN.md) | Master plan with anti-drift protocol |
| [TASK_LIST.md](docs/TASK_LIST.md) | 39-task tracker across 7 phases |
| [CANONICAL_SCHEMA.md](docs/CANONICAL_SCHEMA.md) | Data contract definitions |
| [MODULE_SPEC.md](docs/MODULE_SPEC.md) | Module I/O contracts |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Pipeline and module layout |

## Status

**Phase 0** — Repo skeleton (not started)
