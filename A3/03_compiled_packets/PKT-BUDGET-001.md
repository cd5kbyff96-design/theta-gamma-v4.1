# PKT-BUDGET-001: Implement Cost-Per-Point Tracker

**Priority:** P1
**Domain:** BUDGET
**Estimated Effort:** 4h
**Depends On:** PKT-INFRA-004, PKT-EVAL-005
**Source Artifacts:** A2/01_compute_budget_policy.md

## Objective
Build the cost-per-point tracker that computes the marginal USD cost per percentage-point improvement in cross-modal accuracy.

## Inputs
- Cost event stream from PKT-INFRA-004
- Gate evaluator results from PKT-EVAL-005

## Commands
1. Implement cost-per-point calculation (experiment_cost_usd / delta_cross_modal_accuracy_pp)
2. Add rolling average over last 3 experiments
3. Classify health: healthy < $15/pp, elevated $15-30/pp, unsustainable > $30/pp
4. Integrate with KS-REGRESSION trigger (> 3x historical avg)
5. Log to experiment tracker and dashboard
6. Test with simulated experiment cost/accuracy pairs

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Calculation test | Provide known cost and accuracy delta | Correct cost-per-point is produced = pass |
| Classification test | Submit $10/pp, $20/pp, $35/pp values | $10/pp classified healthy, $20/pp elevated, $35/pp unsustainable = pass |
| KS-REGRESSION test | Submit cost-per-point > 3x historical average | Kill-switch signal is triggered = pass |

## Done Definition
Cost-per-point is calculated per experiment, health classification works, KS-REGRESSION integration is functional.

## Stop Condition
If accuracy deltas are consistently zero (no gate progress to measure cost against).

## Notes
Rolling average window of 3 experiments is intentionally small to remain responsive to cost spikes during early-stage training.
