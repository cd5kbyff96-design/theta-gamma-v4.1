# PKT-TRAIN-004: Implement Pruning Compressed Training (T3 Fallback)

**Priority:** P2
**Domain:** TRAIN
**Estimated Effort:** 1d
**Depends On:** PKT-TRAIN-002
**Source Artifacts:** A2/02_training_tier_matrix.csv, A2/03_auto_downgrade_rules.md

## Objective
Implement magnitude pruning (30% sparsity) as fallback compression strategy when QLoRA causes unacceptable accuracy loss.

## Inputs
- DeepSpeed training loop from PKT-TRAIN-002
- Pruning library
- Sparsity target (30%)

## Commands
1. Implement magnitude-based weight pruning at 30% sparsity
2. Apply structured pruning to linear layers
3. Fine-tune pruned model for 500 steps
4. Configure single GPU with DeepSpeed ZeRO-2
5. Compare accuracy to full-precision and QLoRA baselines on 1K eval samples
6. Benchmark inference latency of pruned model

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Sparsity test | Count zero weights in pruned model | Model has 30% zero weights |
| Training test | Run 500 fine-tuning steps on pruned model | 500 steps complete without error |
| Accuracy test | Evaluate on 1K samples vs full-precision baseline | Accuracy within 10pp of full-precision baseline |
| Latency test | Benchmark pruned model inference vs full-precision | Pruned inference latency <= full-precision latency |

## Done Definition
Pruned model trains on single GPU, achieves within 10pp of baseline accuracy, inference latency is equal or better.

## Stop Condition
If pruning causes > 15pp accuracy loss even after fine-tuning.

## Notes
This is a fallback for PKT-TRAIN-003. Only execute if QLoRA accuracy degradation exceeds the 12pp hard stop threshold.
