# Recovery State Machine — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26
**References:** `A1/04_failure_signals.md`, `A2/03_auto_downgrade_rules.md`, `A3/04_packet_index.csv`

---

## 1. Purpose

This document defines a deterministic state machine for recovering from failed runs,
failed tests, and stalled delivery. Every failure mode transitions through defined
states with bounded retries, mandatory fallbacks, and escalation on the third
consecutive failure.

## 2. State Definitions

```
┌──────────┐
│  HEALTHY  │◄──────────────────────────────────────────────┐
│           │  (all metrics nominal, pipeline progressing)  │
└────┬──────┘                                               │
     │ failure detected                                     │
     ▼                                                      │
┌──────────┐                                                │
│ DETECTED │  (failure signal fires, clock starts)          │
│          │                                                │
└────┬──────┘                                               │
     │ triage complete                                      │
     ▼                                                      │
┌──────────┐    success    ┌───────────┐                    │
│ RETRY-1  │──────────────►│ RECOVERED │────────────────────┘
│ same path│               └───────────┘
└────┬──────┘
     │ failure
     ▼
┌──────────┐    success    ┌───────────┐
│ RETRY-2  │──────────────►│ RECOVERED │────────────────────┐
│ fallback │               └───────────┘                    │
└────┬──────┘                                               │
     │ failure                                              │
     ▼                                                      │
┌──────────┐                                                │
│ ESCALATED│  (human required, pipeline paused)             │
│          │                                                │
└────┬──────┘                                               │
     │ human resolves                                       │
     ▼                                                      │
┌───────────┐                                               │
│ RECOVERED │───────────────────────────────────────────────┘
└───────────┘
```

### State Descriptions

| State | Description | Max Duration | Auto-Transition |
|-------|-------------|-------------|-----------------|
| **HEALTHY** | Pipeline operating normally. All metrics within thresholds. | Indefinite | To DETECTED on failure signal |
| **DETECTED** | Failure signal received. Triage in progress. Incident record created. | 30 min | To RETRY-1 after triage |
| **RETRY-1** | Retry using same configuration path. Clock running on SLA. | Per SLA (see §4) | To RECOVERED on success, RETRY-2 on failure |
| **RETRY-2** | Retry using fallback path from `02_retry_policy.yaml`. | Per SLA | To RECOVERED on success, ESCALATED on failure |
| **ESCALATED** | Pipeline paused. Human intervention required. Incident promoted. | Unbounded (human) | To RECOVERED on human resolution |
| **RECOVERED** | Issue resolved. Post-mortem logged. Return to HEALTHY. | 15 min (cooldown) | To HEALTHY after cooldown |

## 3. Failure Mode Registry

Every failure mode has: owner, SLA, escalation target, retry path, fallback path.

### 3.1 Training Failures

| ID | Failure Mode | Severity | Owner | SLA | Retry Path | Fallback Path | Escalation Target |
|----|-------------|----------|-------|-----|-----------|---------------|-------------------|
| FM-TR-01 | Loss divergence | S1 | ML Engineer | Immediate | Revert checkpoint + halve LR | Revert 2 checkpoints + halve LR + reduce batch | Tech Lead |
| FM-TR-02 | Validation loss plateau | S2 | ML Engineer | 4h | Apply LR decay schedule | Switch optimizer (Adam→AdamW) + add warmup | Tech Lead |
| FM-TR-03 | Overfitting | S2 | ML Engineer | 4h | Increase dropout + weight decay | Increase data augmentation + check contamination | Tech Lead |
| FM-TR-04 | Gradient explosion | S1 | ML Engineer | Immediate | Skip batch + apply gradient clipping | Reduce LR by 75% + enable fp32 accumulation | Tech Lead |
| FM-TR-05 | Gradient vanishing | S2 | ML Engineer | 4h | Check activations + reinit affected layers | Switch activation function + adjust init scheme | Tech Lead |
| FM-TR-06 | NaN/Inf in loss | S1 | ML Engineer | Immediate | Revert checkpoint + enable loss scaling | Revert 2 checkpoints + switch to fp32 training | Tech Lead |

### 3.2 Cross-Modal Failures

| ID | Failure Mode | Severity | Owner | SLA | Retry Path | Fallback Path | Escalation Target |
|----|-------------|----------|-------|-----|-----------|---------------|-------------------|
| FM-CM-01 | Accuracy regression (>5pp) | S2 | ML Engineer | 4h | Revert to previous checkpoint | Revert to best-known checkpoint + analyze data | Tech Lead |
| FM-CM-02 | Modality imbalance (>20pp gap) | S2 | Data Engineer | 4h | Adjust modality sampling ratios | Rebalance training data + modality-specific LR | Tech Lead |
| FM-CM-03 | Consistency collapse (<30%) | S1 | ML Engineer | Immediate | Halt + inspect representation space | Revert to pre-collapse checkpoint + review loss fn | Architect |
| FM-CM-04 | Retrieval degradation (>0.15 drop) | S3 | ML Engineer | 24h | Re-index embeddings | Retrain embedding projection layer | Tech Lead |

### 3.3 Latency & Performance Failures

| ID | Failure Mode | Severity | Owner | SLA | Retry Path | Fallback Path | Escalation Target |
|----|-------------|----------|-------|-----|-----------|---------------|-------------------|
| FM-LT-01 | Latency spike (p95 >150ms) | S2 | Infra Engineer | 4h | Profile + remove unoptimized ops | Apply quantization (int8) for inference | Tech Lead |
| FM-LT-02 | Latency regression (>+20ms) | S3 | Infra Engineer | 24h | Bisect recent changes | Revert to last passing build | Tech Lead |
| FM-LT-03 | Throughput collapse (<50 QPS) | S1 | Infra Engineer | Immediate | Check GPU util + restart server | Reduce model size + horizontal scaling | Architect |
| FM-LT-04 | GPU memory overflow (>90%) | S2 | Infra Engineer | 4h | Reduce batch size | Apply gradient checkpointing + model pruning | Tech Lead |

### 3.4 Safety & Robustness Failures

| ID | Failure Mode | Severity | Owner | SLA | Retry Path | Fallback Path | Escalation Target |
|----|-------------|----------|-------|-----|-----------|---------------|-------------------|
| FM-SF-01 | Safety violation spike (>1%) | S1 | Safety Engineer | Immediate | Quarantine checkpoint + inspect data | Revert to last safe checkpoint + retrain safety head | Safety Lead + Legal |
| FM-SF-02 | Adversarial robustness drop (<25%) | S2 | ML Engineer | 4h | Increase adversarial training weight | Add stronger PGD steps + data augmentation | Tech Lead |
| FM-SF-03 | Calibration degradation (ECE >0.10) | S3 | ML Engineer | 24h | Re-calibrate with temperature scaling | Platt scaling on validation set | Tech Lead |
| FM-SF-04 | OOD detection failure (AUROC <0.70) | S2 | ML Engineer | 4h | Review OOD detection method | Switch to energy-based OOD detection | Tech Lead |

### 3.5 Data Pipeline Failures

| ID | Failure Mode | Severity | Owner | SLA | Retry Path | Fallback Path | Escalation Target |
|----|-------------|----------|-------|-----|-----------|---------------|-------------------|
| FM-DP-01 | Data staleness (>90 days) | S3 | Data Engineer | 24h | Investigate pipeline + restart ingestion | Switch to backup data source | Tech Lead |
| FM-DP-02 | Modality coverage drop | S3 | Data Engineer | 24h | Check per-modality sources | Backfill from alternative sources | Tech Lead |
| FM-DP-03 | Data contamination (eval in train) | S1 | Data Engineer | Immediate | Halt eval + quarantine data | Rebuild eval dataset from scratch | Tech Lead + Safety Lead |

### 3.6 Infrastructure & Budget Failures

| ID | Failure Mode | Severity | Owner | SLA | Retry Path | Fallback Path | Escalation Target |
|----|-------------|----------|-------|-----|-----------|---------------|-------------------|
| FM-IF-01 | Compute cost overrun (>80% cap) | S2 | Infra Engineer | 4h | Auto-downgrade tier (D1/D2) | Switch to spot instances | Budget Owner |
| FM-IF-02 | Checkpoint corruption | S1 | Infra Engineer | Immediate | Load previous valid checkpoint | Rebuild from 2nd-most-recent valid checkpoint | Tech Lead |
| FM-IF-03 | Kill-switch tripped | S1 | Infra Engineer | Immediate | Follow kill-switch restart procedure | Request budget amendment (T3) | Budget Owner |

### 3.7 Gate Failures

| ID | Failure Mode | Severity | Owner | SLA | Retry Path | Fallback Path | Escalation Target |
|----|-------------|----------|-------|-----|-----------|---------------|-------------------|
| FM-GT-01 | G1 gate failure | S2 | ML Engineer | 12h | Retry with same config (max 3 retries) | Hyperparameter sweep + architecture review | Architect |
| FM-GT-02 | G2 gate failure | S2 | ML Engineer | 24h | Retry + modality balance diagnostic | Revert to G1 checkpoint + revised training plan | Architect |
| FM-GT-03 | G3 gate failure | S2 | ML Engineer | 48h | Retry + full diagnostic suite | Revert to G2 checkpoint + architecture review | Architect + Stakeholders |
| FM-GT-04 | G4 gate failure | S2 | Infra Engineer | 24h | Profiling + optimization pass | Quantization + pruning + hardware evaluation | Architect |
| FM-GT-05 | 2 consecutive gate failures (any) | S1 | ML Engineer | Immediate | Execute gate rollback per A1 | Full pipeline halt + architecture review meeting | Architect + Stakeholders |

### 3.8 Delivery Stalls

| ID | Failure Mode | Severity | Owner | SLA | Retry Path | Fallback Path | Escalation Target |
|----|-------------|----------|-------|-----|-----------|---------------|-------------------|
| FM-DL-01 | No gate progress for 7 days | S2 | Tech Lead | 4h | Analyze cost-per-point trends | Scope reduction or target adjustment review | Stakeholders |
| FM-DL-02 | Packet blocked >48h | S2 | Packet Owner | 4h | Unblock dependency or find workaround | Rescope packet or split into sub-packets | Tech Lead |
| FM-DL-03 | Budget exhausted mid-month | S1 | Budget Owner | Immediate | Switch to T4-Eval-Only | Emergency budget amendment request | Stakeholders |
| FM-DL-04 | Critical path packet fails | S1 | Packet Owner | Immediate | Retry packet with revised approach | Escalate with blocker report | Tech Lead + Architect |

## 4. SLA Definitions

| SLA Class | Max Triage | Max Retry-1 | Max Retry-2 | Max Total Resolution |
|-----------|-----------|-------------|-------------|---------------------|
| Immediate (S1) | 15 min | 1h | 2h | 4h before escalation |
| 4-hour (S2) | 30 min | 4h | 8h | 24h before escalation |
| 24-hour (S3) | 1h | 24h | 48h | 72h before escalation |

## 5. State Transition Rules

### 5.1 HEALTHY → DETECTED
- **Trigger:** Any failure signal fires (from A1/04_failure_signals.md or runtime detection)
- **Actions:** Create incident record, start SLA clock, notify owner
- **Timeout:** Auto-triage after 30 min if owner hasn't responded

### 5.2 DETECTED → RETRY-1
- **Trigger:** Triage complete, retry path identified
- **Actions:** Execute retry path from §3, log attempt, monitor metrics
- **Constraint:** Must use same-path retry (not fallback)

### 5.3 RETRY-1 → RECOVERED (success)
- **Trigger:** Retry succeeds (failure signal clears, metrics return to threshold)
- **Actions:** Log resolution, update incident record, enter 15-min cooldown

### 5.4 RETRY-1 → RETRY-2 (failure)
- **Trigger:** Same-path retry fails or times out
- **Actions:** Switch to fallback path from §3, log failure, escalate awareness

### 5.5 RETRY-2 → RECOVERED (success)
- **Trigger:** Fallback retry succeeds
- **Actions:** Log resolution, document why fallback was needed

### 5.6 RETRY-2 → ESCALATED (failure — MANDATORY)
- **Trigger:** Fallback retry fails (THIRD FAILURE overall)
- **Actions:** Pause pipeline, notify escalation target, create blocker report
- **Constraint:** **This transition is mandatory and cannot be bypassed.** Third failure always escalates.

### 5.7 ESCALATED → RECOVERED
- **Trigger:** Human resolves issue
- **Actions:** Log human decision, update incident, schedule post-mortem

## 6. Concurrency Rules

- Multiple failure modes can be active simultaneously
- Each runs its own independent state machine instance
- If 3+ S1 failures are active simultaneously: halt entire pipeline, escalate all to Architect
- S1 failures take priority for resource allocation over S2/S3
- A single resource (GPU, person) cannot be assigned to more than 2 active recoveries

## 7. Post-Recovery Actions

After every RECOVERED → HEALTHY transition:

1. **Incident record closed** with root cause, resolution, and time-to-resolve
2. **Post-mortem** scheduled if S1 or if total resolution exceeded SLA
3. **Prevention ticket** created if root cause is preventable
4. **State machine updated** if new failure mode was discovered
5. **15-minute cooldown** before declaring HEALTHY (prevents flapping)
