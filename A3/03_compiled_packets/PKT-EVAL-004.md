# PKT-EVAL-004: Build Safety and Robustness Evaluation Suite

**Priority:** P1
**Domain:** EVAL
**Estimated Effort:** 1d
**Depends On:** PKT-DATA-003
**Source Artifacts:** A1/01_metric_dictionary.yaml, A1/02_gate_definitions.yaml (G3), A1/03_eval_harness_plan.md

## Objective
Implement safety and robustness evaluation suite computing M-ROB-001 (adversarial robustness), M-ROB-002 (OOD AUROC), M-ROB-003 (calibration ECE), and M-SAF-001 (safety violation rate).

## Inputs
- Adversarial/OOD datasets from PKT-DATA-003
- Safety classifier
- Model checkpoint interface

## Commands
1. Implement adversarial robustness evaluator (accuracy under PGD attack)
2. Implement OOD detection AUROC calculator
3. Implement 15-bin Expected Calibration Error calculator
4. Implement safety violation rate (fraction flagged by safety classifier)
5. Output structured JSON with all 4 metrics
6. Test on dummy model with known properties

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Output format test | Validate JSON output schema | JSON contains M-ROB-001 through M-SAF-001 = pass |
| ECE test | Run ECE calculator on perfectly calibrated predictions | Perfectly calibrated predictions give ECE near 0 = pass |
| AUROC test | Run AUROC calculator on trivially separable data | Trivially separable in-dist/OOD gives AUROC near 1.0 = pass |
| Runtime test | Time full suite execution | Suite completes in < 90 min = pass |

## Done Definition
Safety/robustness suite produces all 4 metrics, each calculator is validated on synthetic data with known properties.

## Stop Condition
If safety classifier is unavailable or adversarial evaluation causes GPU OOM.

## Notes
This suite feeds gate G3 criteria. The PGD attack uses standard parameters (eps=8/255, step_size=2/255, 20 steps).
