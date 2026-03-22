# PKT-DATA-004: Implement Data Contamination Checker

**Priority:** P1
**Domain:** DATA
**Estimated Effort:** 4h
**Depends On:** PKT-DATA-001, PKT-DATA-002
**Source Artifacts:** A1/03_eval_harness_plan.md, A1/04_failure_signals.md

## Objective
Build automated dedup/contamination checker that verifies zero overlap between training and eval datasets before every evaluation run.

## Inputs
- Training dataset hashes
- Eval dataset hashes
- Dedup algorithm specification

## Commands
1. Implement content-hash-based dedup checker
2. Implement fuzzy matching for near-duplicates (cosine similarity > 0.95)
3. Integrate checker into eval harness pre-run hook
4. Add contamination failure signal (S1 Critical)
5. Test with known-contaminated and clean datasets

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Clean test | Run checker on non-overlapping datasets | 0 contamination reported |
| Contaminated test | Run checker on dataset with 5% planted overlap | Contamination flagged |
| Fuzzy test | Run near-duplicate detection on paraphrased content | Near-duplicates caught |
| Performance test | Run checker on 100K samples and measure wall time | Completes in < 5 minutes |

## Done Definition
Contamination checker runs before every eval, catches exact and near-duplicate contamination, integrated into eval harness.

## Stop Condition
If fuzzy matching produces > 5% false positive rate that cannot be tuned.

## Notes
The contamination checker is a critical guardrail. Contamination failure is classified as S1 Critical because it invalidates all evaluation results.
