# Test Plan

## Required fixture cases
1. Stable series -> `not_concerning`
2. Temporary dip -> `watch` or `not_concerning`
3. Structural decline -> `concerning`
4. Segment-driven deterioration -> global concern + ranked contributors

## Assertions
- schema validation passes on valid fixtures
- schema validation fails on malformed fixtures
- STL decomposition returns expected component lengths
- robust slope sign matches known scenario direction
- change-point detection fires only where expected
- concern classifier matches fixture expectations
- segment scanner returns non-empty ranked output for segment shift case
- interpretation payload conforms to schema
