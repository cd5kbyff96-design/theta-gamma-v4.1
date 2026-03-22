# Failure Signals — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26

---

## 1. Purpose

This document catalogs the failure signals that indicate problems during training, evaluation, and deployment of the Theta-Gamma model. Each signal includes detection criteria, severity, recommended response, and escalation path.

## 2. Signal Severity Levels

| Level | Label | Response Time | Action |
|-------|-------|--------------|--------|
| S1 | Critical | Immediate | Halt pipeline, escalate to human |
| S2 | High | < 4 hours | Block progression, notify team |
| S3 | Medium | < 24 hours | Log and investigate, continue cautiously |
| S4 | Low | Next review cycle | Log for trend analysis |

---

## 3. Training Failure Signals

### 3.1 Loss Divergence
- **Signal:** Training loss increases by > 50% over 100 steps
- **Severity:** S1 — Critical
- **Detection:** Automated monitoring of M-MQ-001 per-step values
- **Root causes:** Learning rate too high, data corruption, gradient explosion
- **Response:** Halt training, revert to last stable checkpoint, reduce learning rate by 50%
- **Escalation:** Immediate — training is wasting compute

### 3.2 Validation Loss Plateau
- **Signal:** Validation loss (M-MQ-002) does not improve for 10 consecutive epochs
- **Severity:** S2 — High
- **Detection:** Linear regression slope >= 0 over 10-epoch window
- **Root causes:** Insufficient model capacity, learning rate needs scheduling, data saturation
- **Response:** Trigger learning rate decay, evaluate data augmentation options
- **Escalation:** If plateau persists after LR adjustment, escalate for architecture review

### 3.3 Overfitting
- **Signal:** Overfitting gap (M-MQ-003) exceeds 0.5 nats and is increasing
- **Severity:** S2 — High
- **Detection:** M-MQ-003 > 0.5 AND positive slope over 5 epochs
- **Root causes:** Insufficient regularization, training data too small, data leakage
- **Response:** Increase dropout, add weight decay, check for train/eval data overlap
- **Escalation:** If gap continues growing after regularization adjustment

### 3.4 Gradient Explosion
- **Signal:** Gradient norm (M-MQ-004) exceeds 100x the running average
- **Severity:** S1 — Critical
- **Detection:** M-MQ-004 > 100 * EMA(M-MQ-004, window=1000)
- **Root causes:** Numerical instability, bad data batch, learning rate spike
- **Response:** Halt training, skip current batch, apply gradient clipping, resume from last stable step
- **Escalation:** Immediate if occurs more than twice in 1000 steps

### 3.5 Gradient Vanishing
- **Signal:** Gradient norm (M-MQ-004) drops below 1e-7 for 500 consecutive steps
- **Severity:** S2 — High
- **Detection:** M-MQ-004 < 1e-7 sustained
- **Root causes:** Dead neurons, poor initialization, activation function saturation
- **Response:** Check activation distributions, consider re-initialization of affected layers
- **Escalation:** If training makes zero progress for 1000 steps

### 3.6 NaN/Inf in Loss
- **Signal:** Training or validation loss contains NaN or Inf values
- **Severity:** S1 — Critical
- **Detection:** isnan() or isinf() check on loss values
- **Root causes:** Numerical overflow, division by zero, corrupted data
- **Response:** Immediate halt, revert to last clean checkpoint, enable mixed-precision safeguards
- **Escalation:** Immediate

---

## 4. Cross-Modal Failure Signals

### 4.1 Cross-Modal Accuracy Regression
- **Signal:** M-CM-001 drops by > 5pp compared to previous eval run
- **Severity:** S2 — High
- **Detection:** M-REG-001 < -5.0
- **Root causes:** Catastrophic forgetting, data distribution shift, training instability
- **Response:** Revert to previous checkpoint, investigate training data changes
- **Escalation:** If regression persists after checkpoint revert

### 4.2 Modality Imbalance
- **Signal:** M-MOD-004 (max modality gap) exceeds 20pp
- **Severity:** S2 — High
- **Detection:** Automated check on per-modality accuracy spread
- **Root causes:** Unbalanced training data, one modality encoder undertrained
- **Response:** Adjust modality sampling ratios, check per-modality data quality
- **Escalation:** If gap > 25pp or not improving after 3 training runs

### 4.3 Cross-Modal Consistency Collapse
- **Signal:** M-CM-003 drops below 30%
- **Severity:** S1 — Critical
- **Detection:** Cross-modal consistency eval
- **Root causes:** Shared representation space has collapsed, contrastive loss not working
- **Response:** Halt training, investigate representation space (t-SNE/UMAP), check loss function
- **Escalation:** Immediate — indicates fundamental architecture issue

### 4.4 Retrieval Performance Degradation
- **Signal:** M-CM-004 (Recall@10) drops by > 0.15 between consecutive runs
- **Severity:** S3 — Medium
- **Detection:** Delta check on retrieval eval
- **Root causes:** Embedding space drift, index staleness, data distribution change
- **Response:** Re-index embeddings, check for training data anomalies
- **Escalation:** If degradation persists after re-indexing

---

## 5. Latency & Performance Failure Signals

### 5.1 Latency Spike
- **Signal:** M-LAT-002 (p95 latency) exceeds 150ms (50% above threshold)
- **Severity:** S2 — High
- **Detection:** Load test harness
- **Root causes:** Model size increase, inefficient operator, memory pressure, hardware degradation
- **Response:** Profile inference path, check for unoptimized operations, verify hardware health
- **Escalation:** If latency cannot be brought below 100ms within 2 optimization cycles

### 5.2 Latency Regression
- **Signal:** M-REG-002 (latency delta) > +20ms compared to previous build
- **Severity:** S3 — Medium
- **Detection:** Automated delta check
- **Root causes:** New model layers, removed optimizations, dependency update
- **Response:** Bisect recent changes to identify latency regression source
- **Escalation:** If regression not identified within 24 hours

### 5.3 Throughput Collapse
- **Signal:** M-THR-001 drops below 50 QPS (50% below threshold)
- **Severity:** S1 — Critical
- **Detection:** Load test harness
- **Root causes:** Memory leak, deadlock, resource contention, infrastructure failure
- **Response:** Immediate investigation, check GPU utilization, memory patterns, and I/O
- **Escalation:** Immediate

### 5.4 GPU Memory Overflow
- **Signal:** M-RES-001 exceeds 90% of available GPU memory
- **Severity:** S2 — High
- **Detection:** GPU profiler during load test
- **Root causes:** Batch size too large, memory leak, model size increase
- **Response:** Reduce batch size, check for memory leaks, evaluate model pruning
- **Escalation:** If peak memory > available GPU memory (OOM risk)

---

## 6. Safety & Robustness Failure Signals

### 6.1 Safety Violation Spike
- **Signal:** M-SAF-001 exceeds 1.0% (10x threshold)
- **Severity:** S1 — Critical
- **Detection:** Safety classifier eval
- **Root causes:** Training data contamination, safety fine-tuning regression, adversarial data
- **Response:** Halt all deployment activity, quarantine checkpoint, investigate training data
- **Escalation:** Immediate — potential compliance/safety incident

### 6.2 Adversarial Robustness Drop
- **Signal:** M-ROB-001 drops below 25%
- **Severity:** S2 — High
- **Detection:** Adversarial eval suite
- **Root causes:** Overfitting to clean data, adversarial training weight too low
- **Response:** Increase adversarial training ratio, add stronger perturbations
- **Escalation:** If below 25% after retraining with adjusted adversarial weight

### 6.3 Calibration Degradation
- **Signal:** M-ROB-003 (ECE) exceeds 0.10 (2x threshold)
- **Severity:** S3 — Medium
- **Detection:** Calibration eval
- **Root causes:** Temperature scaling drift, distribution shift, overconfident predictions
- **Response:** Re-calibrate with temperature scaling, check confidence distributions
- **Escalation:** If ECE > 0.15 after recalibration

### 6.4 OOD Detection Failure
- **Signal:** M-ROB-002 (AUROC) drops below 0.70
- **Severity:** S2 — High
- **Detection:** OOD detection eval
- **Root causes:** In-distribution and OOD representations overlapping, feature space collapse
- **Response:** Review OOD detection method, check for distribution shift in eval data
- **Escalation:** If AUROC < 0.70 after method adjustment

---

## 7. Data Pipeline Failure Signals

### 7.1 Data Staleness
- **Signal:** M-DQ-002 exceeds 90 days
- **Severity:** S3 — Medium
- **Detection:** Data freshness check
- **Root causes:** Data pipeline stalled, upstream data source unavailable
- **Response:** Investigate data pipeline, check upstream source health
- **Escalation:** If data > 120 days stale

### 7.2 Modality Coverage Drop
- **Signal:** M-DQ-001 decreases compared to previous data refresh
- **Severity:** S3 — Medium
- **Detection:** Coverage check on data refresh
- **Root causes:** Data source for specific modality went offline, filtering too aggressive
- **Response:** Check per-modality data sources, adjust filtering thresholds
- **Escalation:** If any modality pair has zero coverage

### 7.3 Data Contamination
- **Signal:** Eval dataset samples found in training data
- **Severity:** S1 — Critical
- **Detection:** Automated dedup check before each eval
- **Root causes:** Data pipeline bug, incorrect data split
- **Response:** Halt eval, quarantine contaminated data, rebuild eval dataset
- **Escalation:** Immediate — all recent eval results may be invalid

---

## 8. Infrastructure Failure Signals

### 8.1 Compute Cost Overrun
- **Signal:** M-RES-003 exceeds 80% of monthly_compute_cap_usd
- **Severity:** S2 — High
- **Detection:** Cloud billing monitor
- **Root causes:** Runaway training, inefficient hyperparameter search, leaked resources
- **Response:** Audit running jobs, terminate idle resources, review training efficiency
- **Escalation:** At 90% of cap, halt non-essential compute

### 8.2 Checkpoint Corruption
- **Signal:** Checkpoint fails integrity check (hash mismatch or load failure)
- **Severity:** S1 — Critical
- **Detection:** Checkpoint validation on save and load
- **Root causes:** Storage failure, incomplete write, disk full
- **Response:** Revert to previous valid checkpoint, check storage health
- **Escalation:** Immediate if no valid recent checkpoint exists

---

## 9. Consecutive Failure Escalation Matrix

| Gate | 1st Failure | 2nd Consecutive | 3rd Consecutive |
|------|------------|-----------------|-----------------|
| G1 | Block + retry in 12h | Rollback to last improving checkpoint + hyperparameter review | Halt pipeline + architecture review |
| G2 | Block + retry in 24h | Rollback to best G1 checkpoint + modality balance diagnostic | Halt pipeline + stakeholder review |
| G3 | Block + retry in 48h | Rollback to best G2 checkpoint + full diagnostic suite | Halt pipeline + architecture review meeting |
| G4 | Block + retry in 24h | Rollback to last passing build + profiling | Halt pipeline + optimization sprint |

---

## 10. Signal Monitoring Summary

| Category | S1 (Critical) | S2 (High) | S3 (Medium) | S4 (Low) |
|----------|--------------|-----------|-------------|----------|
| Training | 3 | 3 | 0 | 0 |
| Cross-Modal | 1 | 2 | 1 | 0 |
| Latency/Perf | 1 | 2 | 1 | 0 |
| Safety/Robustness | 1 | 2 | 1 | 0 |
| Data Pipeline | 1 | 0 | 2 | 0 |
| Infrastructure | 1 | 1 | 0 | 0 |
| **Total** | **8** | **10** | **5** | **0** |
