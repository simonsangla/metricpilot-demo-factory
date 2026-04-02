# Architecture

Raw public dataset -> adapter -> canonical tables -> deterministic engine -> interpretation layer -> UI later

## Locked foundation sequence
1. Define contracts
2. Generate schema-native fixtures
3. Build and validate modules on fixtures
4. Add adapter spec
5. Integrate Club Med public dataset adapter
6. Build UI only after module validation

## Data contract layer
Tables:
- `metric_timeseries`
- `demo_registry`
- `semantic_mapping`

## Analytical engine
Modules:
- schema validator
- trend decomposer
- concern classifier
- segment scanner
- narrative interpretation contract

## Analysis core
- STL decomposition
- Theil-Sen slope estimation
- change-point detection
- concern classification: `not_concerning` / `watch` / `concerning`
- segment ranking by contribution to deterioration

## Forbidden in v1
- "root cause"
- causality claims
- full autonomous recommendation layer
