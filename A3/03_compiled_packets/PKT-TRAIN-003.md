# PKT-TRAIN-003: Implement QLoRA Compressed Training (T3 Tier)

**Priority:** P1
**Domain:** TRAIN
**Estimated Effort:** 1d
**Depends On:** PKT-TRAIN-002
**Source Artifacts:** A2/02_training_tier_matrix.csv, A2/03_auto_downgrade_rules.md

## Objective
Implement QLoRA (4-bit NF4 quantization with LoRA adapters) training for the T3-Compressed tier on single GPU.

## Inputs
- DeepSpeed training loop from PKT-TRAIN-002
- QLoRA library (bitsandbytes + peft)
- LoRA config (rank=64, alpha=128)

## Commands
1. Quantize base model to 4-bit NF4 using bitsandbytes
2. Add LoRA adapters (rank=64, alpha=128) to attention layers
3. Configure DeepSpeed ZeRO-2 for single GPU
4. Reduce batch size to 50% of T1
5. Reduce learning rate to 50% of T1
6. Implement LoRA adapter merge for inference
7. Run 200-step smoke test
8. Compare accuracy to full-precision baseline on 1K eval samples

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Memory test | Monitor peak GPU memory during 200-step run | Peak GPU memory < 40GB on 1xA100-80GB |
| Training test | Run 200 training steps | 200 steps complete, loss decreasing |
| Accuracy test | Evaluate on 1K samples vs full-precision baseline | Accuracy within 8pp of full-precision baseline |
| Merge test | Compare merged model output to adapter model output | Merged model produces identical output to adapter model |

## Done Definition
QLoRA training works on single GPU, stays within memory budget, accuracy degradation is within 8pp, adapter merge produces valid model.

## Stop Condition
If QLoRA accuracy is > 12pp below full-precision baseline, switch to pruning path (PKT-TRAIN-004).

## Notes
T3-Compressed is the lowest-cost training tier. The 8pp accuracy threshold is a soft target; the 12pp hard stop triggers the pruning fallback.
