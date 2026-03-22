# PKT-TRAIN-001: Implement FSDP Training Loop (T1 Tier)

**Priority:** P0
**Domain:** TRAIN
**Estimated Effort:** 2d
**Depends On:** PKT-INFRA-001, PKT-INFRA-003, PKT-DATA-001
**Source Artifacts:** A2/02_training_tier_matrix.csv, A2/03_auto_downgrade_rules.md

## Objective
Implement the T1-Full-FSDP training loop using Lightning Fabric with full sharding, bf16 mixed precision, and checkpoint integration.

## Inputs
- GPU environment from PKT-INFRA-001
- Experiment tracker from PKT-INFRA-003
- Data pipeline from PKT-DATA-001
- Model architecture specification

## Commands
1. Implement model architecture with cross-modal encoders
2. Configure FSDP with FULL_SHARD strategy
3. Set up bf16 mixed precision via Lightning Fabric
4. Integrate data loader from PKT-DATA-001
5. Implement gradient accumulation
6. Add checkpoint save/load hooks with hash validation
7. Integrate metric logging for all training metrics (M-MQ-001 through M-MQ-004)
8. Add cost event emission per training step
9. Run 100-step smoke test on real data

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Smoke test | Run 100 training steps on real data | 100 steps complete without error |
| Loss decrease test | Compare loss at step 1 vs step 100 | Training loss at step 100 < loss at step 1 |
| Checkpoint test | Save at step 50, resume at step 50 | Loss continues decreasing after resume |
| Multi-GPU test | Monitor GPU utilization during training | All 4 GPUs utilized > 80% |
| Metric logging test | Verify metric outputs after 100 steps | All 4 training metrics (M-MQ-001 through M-MQ-004) logged |

## Done Definition
T1-Full-FSDP training loop runs end-to-end, loss decreases, checkpointing works, metrics are logged, cost events emitted.

## Stop Condition
If model fails to fit in 4xA100-80GB memory after FSDP optimization or training loss diverges within first 100 steps.

## Notes
This is the primary training tier. All other tiers (T2, T3) depend on the interface established here.
