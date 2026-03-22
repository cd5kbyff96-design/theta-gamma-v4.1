# PKT-OPS-005: Execute Pilot Readiness Training Run (G3+G4 Target)

**Priority:** P0
**Domain:** OPS
**Estimated Effort:** 2d
**Depends On:** PKT-TRAIN-006, PKT-EVAL-005, PKT-EVAL-003
**Source Artifacts:** A1/02_gate_definitions.yaml (G3, G4)

## Objective
Execute the final training run targeting Gate G3 (accuracy >= 70%) and simultaneously evaluate Gate G4 (latency p95 <= 100ms) for pilot readiness.

## Inputs
- G2-passing checkpoint from PKT-TRAIN-006
- Full eval harness
- Latency benchmark suite
- Budget tracking

## Commands
1. Resume training from best G2 checkpoint
2. Run full eval harness at each checkpoint
3. Run latency benchmark on each exported model
4. Monitor all G3 criteria (accuracy, F1, consistency, retrieval, robustness, OOD, calibration, safety)
5. Monitor G4 criteria (p50, p95, p99 latency, QPS, GPU memory)
6. Track cost-per-point and budget
7. Request human sign-off when G3 automated criteria pass
8. Continue until both G3 and G4 pass or stop conditions met

## Tests
| Test | Command | Expected |
|------|---------|----------|
| G3 gate test | Run cross-modal accuracy eval over 5 runs | cross_modal_accuracy >= 70% with stddev <= 3pp = pass |
| G4 gate test | Run latency benchmark over 5 runs | p95 latency <= 100ms = pass |
| Safety test | Run safety classifier on model outputs | safety_violation_rate <= 0.1% = pass |
| Combined test | Verify G3 and G4 results together | Both G3 AND G4 pass simultaneously = pass |

## Done Definition
Both G3 and G4 gates pass. Human sign-off obtained for G3. Model is pilot-ready.

## Stop Condition
If cumulative project cost exceeds budget cap, or if G3 accuracy plateaus below 65% for 5 consecutive runs, or if latency cannot be brought below 120ms after optimization attempts.

## Notes
This is the final packet before pilot deployment. G3 requires human sign-off in addition to automated criteria. G4 is fully automated. Both gates must pass simultaneously on the same model checkpoint.
