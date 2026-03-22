# PKT-BUDGET-003: Implement Checkpoint Cost Gates

**Priority:** P2
**Domain:** BUDGET
**Estimated Effort:** 4h
**Depends On:** PKT-INFRA-004, PKT-BUDGET-001
**Source Artifacts:** A2/01_compute_budget_policy.md

## Objective
Implement mid-run cost checkpoints at 10%, 50%, and 80% of estimated runtime that evaluate whether to continue, downgrade, or terminate the run.

## Inputs
- Cost event stream
- Cost-per-point tracker from PKT-BUDGET-001
- Estimated runtime
- Current metric improvement

## Commands
1. Implement 10% checkpoint (early-exit if loss not decreasing)
2. Implement 50% checkpoint (downgrade eval if improvement < 25% target)
3. Implement 80% checkpoint (log warning if improvement < 75% target)
4. Wire checkpoints into training loop callback
5. Test with simulated training scenarios

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Early-exit test | Simulate flat loss at 10% runtime | Termination is triggered = pass |
| Mid-run test | Simulate insufficient improvement at 50% runtime | Downgrade signal is triggered = pass |
| Normal test | Simulate healthy progress through all checkpoints | Continuation is allowed at all checkpoints = pass |
| Callback test | Run training with known estimated runtime | Checkpoints fire at correct runtime percentages = pass |

## Done Definition
Training runs are automatically evaluated at 10%, 50%, and 80% of runtime. Underperforming runs are terminated or downgraded.

## Stop Condition
If runtime estimation is too inaccurate (> 50% error) to calculate meaningful checkpoint percentages.

## Notes
The 10% checkpoint is the most aggressive gate and is designed to catch clearly failing runs early. The 50% and 80% checkpoints are progressively more lenient.
