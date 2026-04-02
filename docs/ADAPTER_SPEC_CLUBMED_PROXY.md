# Club Med Proxy Adapter Spec

## Raw source
Kaggle dataset:
- `qucwang/hotel-bookings-analysis-dataset`
- file: `hotel_bookings.csv`

## Adapter responsibility
Transform raw booking rows into canonical tables.

## Raw fields expected
- `arrival_date_year`
- `arrival_date_month`
- `arrival_date_day_of_month`
- `hotel`
- `market_segment`
- `distribution_channel`
- `country`
- `customer_type`
- `deposit_type`
- `is_repeated_guest`

## Derived fields
- `date_day` = normalized date from arrival parts
- `repeat_guest_rate`:
  - numerator = count where `is_repeated_guest == 1`
  - denominator = total booking count
  - value = numerator / denominator

## Segment handling
Build:
- one global series
- one series per allowed dimension/value pair
- bucket top-N countries into `country_top`, rest = `OTHER`

## Deferred
- multi-KPI support
- cancellation-rate implementation
