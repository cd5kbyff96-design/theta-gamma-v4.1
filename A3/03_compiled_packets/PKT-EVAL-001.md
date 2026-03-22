# PKT-EVAL-001: Build Cross-Modal Evaluation Suite

**Priority:** P0
**Domain:** EVAL
**Estimated Effort:** 1d
**Depends On:** PKT-DATA-002
**Source Artifacts:** A1/01_metric_dictionary.yaml, A1/02_gate_definitions.yaml, A1/03_eval_harness_plan.md

## Objective
Implement the cross-modal evaluation suite that computes M-CM-001 (accuracy), M-CM-002 (F1), M-CM-003 (consistency), and M-CM-004 (retrieval recall@10).

## Inputs
- Cross-modal eval dataset from PKT-DATA-002
- Metric definitions
- Model checkpoint interface

## Commands
1. Implement cross-modal accuracy evaluator (M-CM-001) on 10K samples
2. Implement weighted F1 evaluator (M-CM-002)
3. Implement consistency evaluator (M-CM-003) on 5K paired samples
4. Implement retrieval Recall@10 evaluator (M-CM-004) on 5K queries
5. Output structured JSON results per metric
6. Integrate with experiment tracking
7. Run on dummy/random model to verify plumbing

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Output format test | Validate JSON output schema | JSON output contains all 4 metric IDs (M-CM-001, M-CM-002, M-CM-003, M-CM-004) = pass |
| Dummy model test | Run eval suite on random model | Random model scores near chance level = pass |
| Determinism test | Run eval suite twice with same model+data | Same model+data produces identical metrics = pass |
| Runtime test | Time full suite execution | Full suite completes in < 60 min = pass |

## Done Definition
Cross-modal eval suite runs on any checkpoint, produces all 4 metrics in structured format, results log to experiment tracker.

## Stop Condition
If eval suite runtime exceeds 90 minutes on standard hardware or metric calculation produces NaN values.

## Notes
This is the foundational eval suite for the Theta-Gamma v4.1 cross-modal pipeline. All gate evaluations depend on these metrics.
