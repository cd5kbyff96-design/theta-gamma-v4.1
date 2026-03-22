# PKT-EVAL-003: Build Latency and Performance Benchmark Suite

**Priority:** P0
**Domain:** EVAL
**Estimated Effort:** 1d
**Depends On:** PKT-INFRA-001
**Source Artifacts:** A1/01_metric_dictionary.yaml, A1/02_gate_definitions.yaml (G4), A1/03_eval_harness_plan.md

## Objective
Implement load testing suite that measures M-LAT-001 (p50), M-LAT-002 (p95), M-LAT-003 (p99), M-THR-001 (QPS), and M-RES-001 (GPU memory peak).

## Inputs
- GPU environment from PKT-INFRA-001
- Model inference endpoint
- Load profile (10-200 QPS ramp, 10K requests)

## Commands
1. Implement inference server wrapper (batch inference endpoint)
2. Implement load generator (ramp 10->200 QPS over 10 min, sustain 5 min)
3. Implement latency percentile calculator (p50, p95, p99)
4. Implement throughput measurement at sustained peak
5. Implement GPU memory profiler (nvidia-smi sampling)
6. Output structured JSON with all 5 metrics
7. Run baseline benchmark on current model

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Latency test | Run latency percentile calculator | p50, p95, p99 are computed and positive = pass |
| Load test | Run load generator at target QPS | Generator reaches target QPS without client-side bottleneck = pass |
| Memory test | Run GPU memory profiler | GPU peak memory is captured accurately = pass |
| Runtime test | Time full benchmark execution | Full benchmark completes in < 45 min = pass |

## Done Definition
Performance suite produces p50/p95/p99 latency, QPS, GPU memory metrics. Load profile executes correctly.

## Stop Condition
If inference server cannot handle > 10 QPS or GPU memory profiling is unreliable.

## Notes
This suite directly feeds gate G4 criteria. The load profile ramp is designed to identify degradation thresholds.
