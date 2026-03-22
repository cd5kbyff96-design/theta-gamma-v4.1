# PKT-EVAL-005: Implement Gate Evaluator

**Priority:** P0
**Domain:** EVAL
**Estimated Effort:** 8h
**Depends On:** PKT-EVAL-001, PKT-EVAL-002, PKT-EVAL-003, PKT-EVAL-004
**Source Artifacts:** A1/02_gate_definitions.yaml

## Objective
Build the gate evaluator that applies G1-G4 gate criteria to collected metrics and produces pass/fail verdicts with rollback triggering.

## Inputs
- All eval suite results
- Gate definitions YAML
- Metric history store

## Commands
1. Parse gate definitions from YAML
2. Implement rolling window aggregation (3-run and 5-run windows)
3. Implement threshold comparison with floor guards
4. Implement composite pass rule (all criteria must pass)
5. Implement consecutive failure counter
6. Implement rollback trigger on 2 consecutive failures
7. Generate structured gate status report
8. Test with simulated metric histories

## Tests
| Test | Command | Expected |
|------|---------|----------|
| G1 pass test | Run gate evaluator with metrics above threshold | Simulated metrics above threshold, gate passes = pass |
| G1 fail test | Run gate evaluator with one metric below threshold | One metric below threshold, gate fails = pass |
| Floor guard test | Run gate evaluator with mean passing but one run below floor | Mean passes but one run below floor, gate fails = pass |
| Consecutive failure test | Run gate evaluator with 2 consecutive failures | 2 consecutive fails triggers rollback = pass |
| G3 stability test | Run gate evaluator with stddev > 3pp | Stddev > 3pp causes fail even with mean above 70% = pass |

## Done Definition
Gate evaluator correctly evaluates all G1-G4 gates, applies floor guards, detects consecutive failures, triggers rollback actions.

## Stop Condition
If gate definition YAML parsing fails or rolling window logic produces incorrect aggregations.

## Notes
The gate evaluator is the central decision point for training progression. Rollback triggers must be reliable to prevent wasted compute.
