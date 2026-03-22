# PKT-INFRA-001: Provision GPU Training Environment

**Priority:** P0
**Domain:** INFRA
**Estimated Effort:** 1d
**Depends On:** None
**Source Artifacts:** A0/02_operating_limits.yaml, A2/02_training_tier_matrix.csv

## Objective
Provision a 4xA100-80GB training environment with PyTorch, CUDA, and FSDP support for T1-Full tier.

## Inputs
- Cloud provider credentials
- A2 training tier matrix
- CUDA 12.x compatible base image

## Commands
1. Create VM instance with 4xA100-80GB GPUs
2. Install CUDA 12.x toolkit
3. Install PyTorch 2.x with FSDP support
4. Install Lightning Fabric
5. Install DeepSpeed as fallback
6. Configure NCCL for multi-GPU communication
7. Run NCCL all-reduce benchmark
8. Validate GPU-to-GPU bandwidth

## Tests
| Test | Command | Expected |
|------|---------|----------|
| GPU count check | `nvidia-smi --list-gpus \| wc -l` | 4 GPUs detected = pass |
| NCCL benchmark | `all_reduce_perf -b 8 -e 128M -f 2 -g 4` | Bandwidth > 100 GB/s = pass |
| PyTorch FSDP smoke test | `python fsdp_smoke_test.py --steps 10` | Dummy model trains 10 steps without error = pass |

## Done Definition
4xA100-80GB environment is running, all frameworks installed, NCCL benchmark passes, FSDP smoke test completes.

## Stop Condition
If GPU provisioning fails after 3 attempts or cloud quota is insufficient, stop and escalate.

## Notes
T1-Full tier requires the full 4xA100-80GB configuration. Lower tiers may use fewer GPUs or smaller instances per the training tier matrix.
