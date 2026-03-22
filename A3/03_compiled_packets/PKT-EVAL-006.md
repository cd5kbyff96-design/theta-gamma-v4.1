# PKT-EVAL-006: Implement Eval Orchestrator

**Priority:** P1
**Domain:** EVAL
**Estimated Effort:** 8h
**Depends On:** PKT-EVAL-005, PKT-DATA-004
**Source Artifacts:** A1/03_eval_harness_plan.md

## Objective
Build the eval orchestrator that coordinates eval suite execution, manages dependencies between suites, triggers gate evaluation, and generates reports.

## Inputs
- All 4 eval suites
- Gate evaluator
- Contamination checker
- Experiment tracker

## Commands
1. Implement orchestrator with 5 execution modes (full, quick, perf-only, safety-only, regression)
2. Implement suite dependency resolution
3. Run contamination checker before eval
4. Execute appropriate suites based on mode
5. Feed results to gate evaluator
6. Generate per-run eval report (metrics, gate status, regression deltas)
7. Integrate with CI triggers (end-of-training, per-commit, nightly)
8. Test full mode end-to-end

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Full mode test | Run orchestrator in full mode | All 4 suites run, gate evaluation completes = pass |
| Quick mode test | Run orchestrator in quick mode | Only cross-modal + per-modality run = pass |
| Contamination test | Run orchestrator with contaminated data | Orchestrator blocks eval if contamination detected = pass |
| Report test | Validate generated report | Report contains all metrics and gate verdicts = pass |

## Done Definition
Orchestrator runs all 5 execution modes correctly, contamination check precedes eval, gate evaluation runs automatically, reports are generated.

## Stop Condition
If suite coordination causes deadlocks or if contamination checker blocks all eval runs due to false positives.

## Notes
The orchestrator supports CI integration for automated eval at end-of-training, per-commit, and nightly schedules.
