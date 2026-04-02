# App Specification

## Foundation goal
Validate the analytical chain before building any UI.

## Future app goal
A compact diagnostic app that shows whether a KPI deterioration is real and what segments are most associated with it.

## Primary v1 use case
A prospect sees a tourism-focused proxy demo:
- daily repeat guest rate
- anomaly/trend judgment
- likely contributing segments
- business-readable interpretation

## User journey (post-foundation)
1. Select demo
2. Read scenario context
3. See KPI block
4. See trend/concerning judgment
5. Inspect segment contribution
6. Read plain-language interpretation
7. Optionally request the same analysis on real client data

## Anti-drift rule
No UI implementation starts until:
- fixture harness passes
- schema validator passes
- concern classifier passes known cases
- segment ranking passes known cases
