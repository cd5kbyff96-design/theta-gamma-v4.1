# PKT-EVAL-002: Build Per-Modality Evaluation Suite

**Priority:** P1
**Domain:** EVAL
**Estimated Effort:** 4h
**Depends On:** PKT-DATA-002
**Source Artifacts:** A1/01_metric_dictionary.yaml, A1/03_eval_harness_plan.md

## Objective
Implement per-modality evaluation suite computing M-MOD-001 (text accuracy), M-MOD-002 (image accuracy), M-MOD-003 (audio accuracy), and M-MOD-004 (max modality gap).

## Inputs
- Per-modality eval datasets from PKT-DATA-002 (5K each)
- Metric definitions

## Commands
1. Implement text-only accuracy evaluator (M-MOD-001)
2. Implement image-only accuracy evaluator (M-MOD-002)
3. Implement audio-only accuracy evaluator (M-MOD-003)
4. Implement max modality gap calculator (M-MOD-004)
5. Output structured JSON results
6. Integrate with experiment tracking
7. Test on dummy model

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Output format test | Validate JSON output schema | JSON contains M-MOD-001 through M-MOD-004 = pass |
| Gap calculation test | Run gap calculator with known accuracies | Known accuracies produce correct max gap = pass |
| Runtime test | Time full suite execution | Suite completes in < 30 min = pass |

## Done Definition
Per-modality suite runs, produces all 4 per-modality metrics, modality gap is calculated correctly.

## Stop Condition
If any modality eval consistently produces errors due to data format issues.

## Notes
The modality gap metric (M-MOD-004) is critical for identifying imbalanced performance across text, image, and audio modalities.
