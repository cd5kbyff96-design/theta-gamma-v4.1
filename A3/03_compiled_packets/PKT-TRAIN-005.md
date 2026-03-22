# PKT-TRAIN-005: Execute Baseline Training Run (G1 Target)

**Priority:** P0
**Domain:** TRAIN
**Estimated Effort:** 2d
**Depends On:** PKT-TRAIN-001, PKT-DATA-001, PKT-EVAL-001
**Source Artifacts:** A1/02_gate_definitions.yaml (G1), A2/01_compute_budget_policy.md

## Objective
Execute the first full training run targeting Gate G1 baseline (cross-modal accuracy >= 40%) using T1-Full-FSDP tier.

## Inputs
- T1 training loop from PKT-TRAIN-001
- Full training dataset
- Eval harness from PKT-EVAL-001
- Cost tracking from PKT-INFRA-004

## Commands
1. Configure hyperparameters (learning rate, batch size, epochs)
2. Start training run with experiment_id logged
3. Monitor training loss per epoch
4. Run eval harness at each checkpoint
5. Monitor cost-per-point metric
6. Checkpoint every epoch
7. Evaluate G1 gate criteria after each eval run
8. Continue until G1 passes or budget/stop conditions met

## Tests
| Test | Command | Expected |
|------|---------|----------|
| G1 gate test | Run eval harness over 3 consecutive eval runs | cross_modal_accuracy >= 40% over 3 eval runs |
| Loss trend test | Plot validation loss over training epochs | Validation loss shows decreasing trend over 5 epochs |
| F1 test | Compute cross-modal F1 from eval harness | cross_modal_f1 >= 0.38 |
| Cost test | Query cumulative cost from cost tracker | Total run cost < $150 |

## Done Definition
G1 gate passes -- cross-modal accuracy >= 40%, F1 >= 0.38, validation loss decreasing, all within budget.

## Stop Condition
If training cost exceeds $150 without reaching 35% accuracy, or if loss diverges, or if KS-RUNAWAY triggers.

## Notes
G1 is the first quality gate. Passing G1 unlocks continued training toward G2 in PKT-TRAIN-006.
