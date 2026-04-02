# Canonical Schema

## 1. metric_timeseries

| Column | Type | Required | Meaning |
|---|---|---:|---|
| demo_id | string | yes | Scenario/demo identifier |
| date_day | date | yes | Daily date used for time-series analysis |
| metric_name | string | yes | KPI identifier, e.g. `repeat_guest_rate` |
| metric_value | float | yes | Aggregated KPI value |
| dimension_name | string | yes | Allowed analytic dimension |
| dimension_value | string | yes | Segment value inside the chosen dimension |
| slice_level | string | yes | `global` or `segment` |
| obs_count | int | yes | Number of raw observations behind the aggregate |
| metric_numerator | float | yes | KPI numerator |
| metric_denominator | float | yes | KPI denominator |

### Allowed v1 dimensions
- `all`
- `hotel`
- `market_segment`
- `distribution_channel`
- `customer_type`
- `deposit_type`
- `country_top`

### Rules
- `all` must use `dimension_value = "all"` and `slice_level = "global"`
- `country_top` must bucket to top N countries + `OTHER`
- small segments must be filtered using denominator/volume thresholds
- app code must not depend on raw Kaggle columns

## 2. demo_registry

| Column | Type | Required | Meaning |
|---|---|---:|---|
| demo_id | string | yes | Join key |
| demo_label | string | yes | User-facing demo label |
| target_account | string | yes | Prospect/account name |
| target_vertical | string | yes | Industry context |
| scenario_label | string | yes | Scenario title |
| primary_metric | string | yes | Primary KPI |
| public_data_source | string | yes | Public proxy dataset label |
| disclaimer_text | string | yes | Proxy-data disclaimer |
| default_dimension_name | string | yes | Default segment axis |

## 3. semantic_mapping

| Column | Type | Required | Meaning |
|---|---|---:|---|
| field_type | string | yes | `metric`, `dimension`, or `dimension_value` |
| raw_key | string | yes | Raw internal key |
| display_label | string | yes | Friendly label |
| business_definition | string | yes | Meaning in business language |
| llm_hint | string | yes | Interpretation hint |
| sort_order | int | yes | Display ordering |
| is_active | bool | yes | Active flag |
