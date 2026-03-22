# PKT-TRAIN-006: Execute Mid-Tier Training Run (G2 Target)

**Priority:** P0
**Domain:** TRAIN
**Estimated Effort:** 2d
**Depends On:** PKT-TRAIN-005, PKT-EVAL-002
**Source Artifacts:** A1/02_gate_definitions.yaml (G2), A2/01_compute_budget_policy.md

## Objective
Continue training from G1 checkpoint toward Gate G2 (cross-modal accuracy >= 60%) with modality balance monitoring.

## Inputs
- G1-passing checkpoint from PKT-TRAIN-005
- Updated training config
- G2 eval criteria

## Commands
1. Resume training from best G1 checkpoint
2. Adjust learning rate schedule for continued training
3. Monitor modality gap (must stay <= 15pp)
4. Monitor adversarial robustness (must reach >= 40%)
5. Run eval harness at each checkpoint
6. Monitor budget and tier -- downgrade if triggered
7. Evaluate G2 gate criteria after each eval run
8. Continue until G2 passes or stop conditions met

## Tests
| Test | Command | Expected |
|------|---------|----------|
| G2 gate test | Run eval harness over 3 consecutive eval runs | cross_modal_accuracy >= 60% over 3 eval runs |
| Modality balance test | Compute per-modality accuracy gap | Max modality gap <= 15pp |
| Robustness test | Run adversarial eval suite | adversarial_robustness >= 40% |
| Consistency test | Compute cross-modal consistency metric | cross_modal_consistency >= 55% |
| Cost test | Query cumulative cost since G1 | Cumulative cost from G1 < $200 |

## Done Definition
G2 gate passes -- accuracy >= 60%, modality gap <= 15pp, robustness >= 40%, consistency >= 55%.

## Stop Condition
If cost exceeds $200 beyond G1 without reaching 55% accuracy, or if modality gap exceeds 25pp persistently, or if KS-MONTHLY triggers.

## Notes
G2 introduces modality balance and adversarial robustness requirements beyond raw accuracy. Budget monitoring must account for potential tier downgrade triggers.
