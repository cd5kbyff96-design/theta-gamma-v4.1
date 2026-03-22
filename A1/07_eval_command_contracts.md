# Eval Command Contracts — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-27

---

## 1. Purpose

This document defines the canonical command templates for all benchmark, evaluation, and regression runs. Every eval invocation must use these templates to ensure reproducibility and auditability.

---

## 2. Environment Prerequisites

```bash
# Required environment variables
export THETA_GAMMA_ROOT=/opt/theta-gamma
export EVAL_DATA_ROOT=/data/eval/golden
export METRIC_STORE_URL=http://metrics.internal:8080
export CHECKPOINT_DIR=/checkpoints/theta-gamma
export RESULTS_DIR=/results/eval
```

---

## 3. Cross-Modal Benchmark Commands

### 3.1 Cross-Modal Accuracy (M-CM-001)

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/cross_modal_accuracy.py \
  --checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --dataset ${EVAL_DATA_ROOT}/DS-CM-BENCH-001 \
  --dataset-hash a3f7c9e1d42b8f6a50e3d19c7b4a28f6e1d530c9b72e4a81f6d3c950b7e2a14d \
  --modality-pairs text-image,text-audio,image-audio \
  --batch-size 64 \
  --num-workers 4 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/cross_modal_accuracy \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --seed 42
```

**Expected output:** JSON with `accuracy`, `per_class_accuracy`, `confusion_matrix`
**Timeout:** 60 minutes
**Gate references:** G1, G2, G3

### 3.2 Cross-Modal F1 (M-CM-002)

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/cross_modal_f1.py \
  --checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --dataset ${EVAL_DATA_ROOT}/DS-CM-BENCH-001 \
  --dataset-hash a3f7c9e1d42b8f6a50e3d19c7b4a28f6e1d530c9b72e4a81f6d3c950b7e2a14d \
  --weighting frequency \
  --batch-size 64 \
  --num-workers 4 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/cross_modal_f1 \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --seed 42
```

**Expected output:** JSON with `f1_weighted`, `precision`, `recall`, `per_class_f1`
**Timeout:** 60 minutes
**Gate references:** G1, G2, G3

### 3.3 Cross-Modal Consistency (M-CM-003)

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/cross_modal_consistency.py \
  --checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --dataset ${EVAL_DATA_ROOT}/DS-CM-CONSIST-001 \
  --dataset-hash b8d4e2f71a9c3b5d60f4e28a7c5b39g7f2e641d0c83f5b92g7e4d061c8f3b25e \
  --batch-size 32 \
  --num-workers 4 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/cross_modal_consistency \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --seed 42
```

**Expected output:** JSON with `consistency_rate`, `per_pair_consistency`
**Timeout:** 30 minutes
**Gate references:** G2, G3

### 3.4 Cross-Modal Retrieval Recall@K (M-CM-004)

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/retrieval_recall_at_k.py \
  --checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --dataset ${EVAL_DATA_ROOT}/DS-CM-RETRIEVAL-001 \
  --dataset-hash c9e5f3a82b0d4c6e71a5f39b8d6c40h8a3f752e1d94a6c03h8f5e172d9a4c36f \
  --k 10 \
  --batch-size 32 \
  --num-workers 4 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/retrieval_recall \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --seed 42
```

**Expected output:** JSON with `recall_at_10`, `recall_at_5`, `recall_at_1`, `mrr`
**Timeout:** 30 minutes
**Gate references:** G3

---

## 4. Per-Modality Eval Commands

### 4.1 Text Accuracy (M-MOD-001)

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/text_accuracy.py \
  --checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --dataset ${EVAL_DATA_ROOT}/DS-MOD-TEXT-001 \
  --dataset-hash d0f6a4b93c1e5d7f82b6a40c9e7d51i9b4a863f2e05b7d14i9a6f283e0b5d47a \
  --batch-size 128 \
  --num-workers 4 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/text_accuracy \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --seed 42
```

### 4.2 Image Accuracy (M-MOD-002)

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/image_accuracy.py \
  --checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --dataset ${EVAL_DATA_ROOT}/DS-MOD-IMAGE-001 \
  --dataset-hash e1a7b5c04d2f6e8a93c7b51d0f8e62j0c5b974a3f16c8e25j0b7a394f1c6e58b \
  --batch-size 64 \
  --num-workers 4 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/image_accuracy \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --seed 42
```

### 4.3 Audio Accuracy (M-MOD-003)

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/audio_accuracy.py \
  --checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --dataset ${EVAL_DATA_ROOT}/DS-MOD-AUDIO-001 \
  --dataset-hash f2b8c6d15e3a7f9b04d8c62e1a9f73k1d6c085b4a27d9f36k1c8b405a2d7f69c \
  --batch-size 64 \
  --num-workers 4 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/audio_accuracy \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --seed 42
```

**Per-modality shared properties:**
- **Expected output:** JSON with `accuracy`, `per_class_accuracy`
- **Timeout:** 30 minutes per modality
- **Gate references:** G2 (modality_gap_max), G3 (modality_gap_max)

---

## 5. Latency & Performance Commands

### 5.1 Latency Benchmark (M-LAT-001, M-LAT-002, M-LAT-003)

```bash
python ${THETA_GAMMA_ROOT}/perf_harness/latency_bench.py \
  --model-endpoint http://model-server.internal:8000/predict \
  --dataset ${EVAL_DATA_ROOT}/DS-PERF-LOAD-001 \
  --dataset-hash f8b4c2d71e9a3f5b60d4c28e7a5f39q7d2c641b0e83f5c92q7c4d061e8a3f25b \
  --ramp-start-qps 10 \
  --ramp-end-qps 200 \
  --ramp-duration-sec 600 \
  --sustain-duration-sec 300 \
  --num-requests 10000 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/latency \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID}
```

**Expected output:** JSON with `p50_ms`, `p95_ms`, `p99_ms`, `mean_ms`, `max_ms`
**Timeout:** 45 minutes
**Gate references:** G4

### 5.2 Throughput Benchmark (M-THR-001)

```bash
python ${THETA_GAMMA_ROOT}/perf_harness/throughput_bench.py \
  --model-endpoint http://model-server.internal:8000/predict \
  --dataset ${EVAL_DATA_ROOT}/DS-PERF-LOAD-001 \
  --dataset-hash f8b4c2d71e9a3f5b60d4c28e7a5f39q7d2c641b0e83f5c92q7c4d061e8a3f25b \
  --target-qps 200 \
  --duration-sec 300 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/throughput \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID}
```

**Expected output:** JSON with `sustained_qps`, `peak_qps`, `error_rate`
**Timeout:** 15 minutes
**Gate references:** G4

### 5.3 GPU Memory Profiling (M-RES-001)

```bash
python ${THETA_GAMMA_ROOT}/perf_harness/gpu_profiler.py \
  --model-endpoint http://model-server.internal:8000/predict \
  --dataset ${EVAL_DATA_ROOT}/DS-PERF-LOAD-001 \
  --dataset-hash f8b4c2d71e9a3f5b60d4c28e7a5f39q7d2c641b0e83f5c92q7c4d061e8a3f25b \
  --num-requests 1000 \
  --sample-interval-ms 100 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/gpu_profile \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID}
```

**Expected output:** JSON with `peak_memory_gb`, `mean_memory_gb`, `utilization_pct`
**Timeout:** 15 minutes
**Gate references:** G4

---

## 6. Safety & Robustness Commands

### 6.1 Adversarial Robustness (M-ROB-001)

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/adversarial_eval.py \
  --checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --dataset ${EVAL_DATA_ROOT}/DS-ADV-ROBUST-001 \
  --dataset-hash a3c9d7e26f4b8a0c15e9d73f2b0a84l2e7d196c5b38e0a47l2d9c516b3e8a70d \
  --attack-type pgd \
  --epsilon-image 0.03137 \
  --text-perturbation char_swap \
  --batch-size 32 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/adversarial \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --seed 42
```

**Expected output:** JSON with `robust_accuracy`, `per_attack_accuracy`, `clean_accuracy`
**Timeout:** 90 minutes
**Gate references:** G2, G3

### 6.2 OOD Detection (M-ROB-002)

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/ood_detection.py \
  --checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --in-dist-dataset ${EVAL_DATA_ROOT}/DS-OOD-INDIST-001 \
  --in-dist-hash b4d0e8f37a5c9b1d26f0e84a3c1b95m3f8e207d6c49f1b58m3e0d627c4f9b81e \
  --ood-dataset ${EVAL_DATA_ROOT}/DS-OOD-OUT-001 \
  --ood-hash c5e1f9a48b6d0c2e37a1f95b4d2c06n4a9f318e7d50a2c69n4f1e738d5a0c92f \
  --batch-size 64 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/ood_detection \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --seed 42
```

**Expected output:** JSON with `auroc`, `fpr_at_95_tpr`, `detection_accuracy`
**Timeout:** 30 minutes
**Gate references:** G3

### 6.3 Calibration (M-ROB-003)

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/calibration.py \
  --checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --dataset ${EVAL_DATA_ROOT}/DS-CALIB-001 \
  --dataset-hash e7a3b1c60d8f2e4a59c3b17d6f4e28p6c1b530a9f72c4e81p6b3a950f7c2e14b \
  --num-bins 15 \
  --batch-size 64 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/calibration \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --seed 42
```

**Expected output:** JSON with `ece`, `mce`, `reliability_diagram_path`
**Timeout:** 15 minutes
**Gate references:** G3

### 6.4 Safety Violations (M-SAF-001)

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/safety_classifier.py \
  --checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --dataset ${EVAL_DATA_ROOT}/DS-SAFETY-001 \
  --dataset-hash d6f2a0b59c7e1d3f48b2a06c5e3d17o5b0a429f8e61b3d70o5a2f849e6b1d03a \
  --batch-size 32 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/safety \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --seed 42
```

**Expected output:** JSON with `violation_rate`, `per_category_violations`, `flagged_samples`
**Timeout:** 60 minutes
**Gate references:** G3

---

## 7. Regression Commands

### 7.1 Cross-Modal Regression Check (M-REG-001)

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/regression_check.py \
  --current-checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --baseline-predictions ${EVAL_DATA_ROOT}/DS-REG-BASELINE-001 \
  --baseline-hash a9c5d3e82f0b4a6c71e5d39f8a6c40r8e3d752c1f94b6a03r8d5c172f9b4a36c \
  --metric cross_modal_accuracy \
  --regression-threshold -5.0 \
  --dataset ${EVAL_DATA_ROOT}/DS-CM-BENCH-001 \
  --dataset-hash a3f7c9e1d42b8f6a50e3d19c7b4a28f6e1d530c9b72e4a81f6d3c950b7e2a14d \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/regression \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --seed 42
```

**Expected output:** JSON with `delta`, `current_value`, `baseline_value`, `regressed` (bool)
**Timeout:** 60 minutes

### 7.2 Latency Regression Check (M-REG-002)

```bash
python ${THETA_GAMMA_ROOT}/perf_harness/latency_regression.py \
  --model-endpoint http://model-server.internal:8000/predict \
  --previous-results ${RESULTS_DIR}/${PREVIOUS_RUN_ID}/latency \
  --dataset ${EVAL_DATA_ROOT}/DS-PERF-LOAD-001 \
  --dataset-hash f8b4c2d71e9a3f5b60d4c28e7a5f39q7d2c641b0e83f5c92q7c4d061e8a3f25b \
  --regression-threshold-ms 20 \
  --output-dir ${RESULTS_DIR}/${RUN_ID}/latency_regression \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID}
```

**Expected output:** JSON with `delta_p50_ms`, `delta_p95_ms`, `regressed` (bool)
**Timeout:** 45 minutes

---

## 8. Composite / Suite Commands

### 8.1 Full Eval Suite

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/run_suite.py \
  --mode full \
  --checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --eval-data-root ${EVAL_DATA_ROOT} \
  --model-endpoint http://model-server.internal:8000/predict \
  --output-dir ${RESULTS_DIR}/${RUN_ID} \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --gate-definitions ${THETA_GAMMA_ROOT}/config/02_gate_definitions.yaml \
  --seed 42 \
  --parallel-suites 2
```

**Timeout:** 180 minutes
**Runs:** All suites, evaluates all applicable gates

### 8.2 Quick Eval (Feature Branch)

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/run_suite.py \
  --mode quick \
  --checkpoint ${CHECKPOINT_DIR}/${CHECKPOINT_ID} \
  --eval-data-root ${EVAL_DATA_ROOT} \
  --output-dir ${RESULTS_DIR}/${RUN_ID} \
  --metric-store ${METRIC_STORE_URL} \
  --run-id ${RUN_ID} \
  --gate-definitions ${THETA_GAMMA_ROOT}/config/02_gate_definitions.yaml \
  --seed 42
```

**Timeout:** 90 minutes
**Runs:** Cross-modal + per-modality suites, evaluates G1 only

### 8.3 Nightly Regression

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/run_suite.py \
  --mode regression \
  --checkpoint ${CHECKPOINT_DIR}/latest \
  --baseline-run-id ${BEST_KNOWN_RUN_ID} \
  --eval-data-root ${EVAL_DATA_ROOT} \
  --model-endpoint http://model-server.internal:8000/predict \
  --output-dir ${RESULTS_DIR}/nightly-$(date +%Y%m%d) \
  --metric-store ${METRIC_STORE_URL} \
  --run-id nightly-$(date +%Y%m%d) \
  --gate-definitions ${THETA_GAMMA_ROOT}/config/02_gate_definitions.yaml \
  --seed 42
```

**Timeout:** 180 minutes
**Runs:** All suites against previous best, produces delta metrics

---

## 9. Data Integrity Verification

Before any eval run, verify dataset integrity:

```bash
python ${THETA_GAMMA_ROOT}/eval_harness/verify_datasets.py \
  --manifest ${THETA_GAMMA_ROOT}/config/06_golden_dataset_manifest.csv \
  --data-root ${EVAL_DATA_ROOT} \
  --check-hashes \
  --check-contamination --training-data-index ${TRAINING_DATA_INDEX}
```

**Expected output:** Per-dataset `PASS`/`FAIL` for hash and contamination checks
**Timeout:** 30 minutes
**Policy:** Any `FAIL` blocks the eval run

---

## 10. Command Contract Rules

1. **Hash verification:** Every command that references a dataset must include a `--dataset-hash` flag matching `06_golden_dataset_manifest.csv`
2. **Seed pinning:** All eval commands must set `--seed 42` for reproducibility
3. **Metric store:** All commands must push results to the metric store via `--metric-store`
4. **Run ID:** Every invocation must carry a unique `--run-id` for traceability
5. **Output isolation:** Results go to `${RESULTS_DIR}/${RUN_ID}/` — never overwrite previous runs
6. **Timeout enforcement:** Commands exceeding their timeout are killed and logged as failures
