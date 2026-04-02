# Module Specification

## 1. schema_validator
Input:
- metric_timeseries dataframe
- demo_registry dataframe
- semantic_mapping dataframe

Output:
- pass/fail
- typed error list

## 2. trend_decomposer
Input:
- one KPI time series

Output:
- trend
- seasonal
- residual
- expected baseline stats

Method:
- STL decomposition

## 3. concern_classifier
Input:
- decomposed series
- robust slope result
- change-point result

Output:
- `not_concerning` / `watch` / `concerning`
- evidence fields
- confidence note

Method:
- STL residual rules
- Theil-Sen slope
- change-point detection

## 4. segment_scanner
Input:
- filtered metric_timeseries for segment rows
- target KPI
- analysis window

Output:
- ranked contributing segments
- contribution stats
- threshold notes

Rules:
- enforce minimum denominator / obs_count
- descriptive contribution only
- no causal wording

## 5. narrative_interpreter_contract
Input:
- structured stats summary JSON

Output schema:
- `finding`
- `confidence`
- `business_meaning`
- `caveats`
