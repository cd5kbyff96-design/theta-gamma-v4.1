# PKT-TRAIN-002: Implement DeepSpeed Training Loop (T1/T2 Tiers)

**Priority:** P0
**Domain:** TRAIN
**Estimated Effort:** 1d
**Depends On:** PKT-TRAIN-001
**Source Artifacts:** A2/02_training_tier_matrix.csv, A2/03_auto_downgrade_rules.md

## Objective
Implement DeepSpeed ZeRO-2 and ZeRO-3 training loops as alternatives/downgrades to FSDP, using the same Lightning Fabric interface.

## Inputs
- FSDP training loop from PKT-TRAIN-001 (shared interface)
- DeepSpeed configuration

## Commands
1. Create DeepSpeed ZeRO-3 config for T1-Full-DeepSpeed (4 GPU)
2. Create DeepSpeed ZeRO-2 config for T2-Efficient (2 GPU)
3. Swap Lightning strategy parameter to DeepSpeedStrategy
4. Validate checkpoint compatibility between FSDP and DeepSpeed formats
5. Run 100-step smoke test on ZeRO-3 (4 GPU)
6. Run 100-step smoke test on ZeRO-2 (2 GPU)
7. Benchmark throughput comparison: FSDP vs ZeRO-3 vs ZeRO-2

## Tests
| Test | Command | Expected |
|------|---------|----------|
| ZeRO-3 smoke test | Run 100 training steps with ZeRO-3 on 4 GPUs | 100 steps complete, loss decreasing |
| ZeRO-2 smoke test | Run 100 training steps with ZeRO-2 on 2 GPUs | 100 steps complete, loss decreasing |
| Checkpoint cross-load test | Load FSDP checkpoint in DeepSpeed runtime | FSDP checkpoint loads in DeepSpeed without error |
| Throughput test | Compare samples/sec across all strategies | ZeRO-2 throughput >= 50% of FSDP throughput |

## Done Definition
DeepSpeed ZeRO-2 and ZeRO-3 training loops work via Lightning strategy swap, checkpoints are cross-compatible, throughput is benchmarked.

## Stop Condition
If DeepSpeed checkpoint format is incompatible with FSDP and conversion takes > 4h to implement.

## Notes
ZeRO-3 serves as the direct FSDP alternative at T1; ZeRO-2 is the T2-Efficient tier for reduced GPU count.
