# Validation Evidence Checklist — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26
**Usage:** Structured by milestone. Check off each item as evidence is collected. All items in a milestone must be checked before that milestone is considered validated.

---

## How to Use This Checklist

1. Work through each milestone section sequentially (G1 → G2 → G3/G4 → Pilot)
2. For each evidence item, check the box when the artifact exists and is verified
3. Record the location (file path, URL, or system) where the evidence is stored
4. A milestone is validated only when ALL items in that section are checked
5. Carry forward any evidence gaps as blockers in the blocker report template

---

## Milestone 1: G1 — Baseline Cross-Modal (40–50%)

### 1.1 Training Evidence

- [ ] **Training configuration** — Hyperparameters, architecture, optimizer settings
  - Location: _______________
- [ ] **Training logs** — Loss curves (training + validation) for full run
  - Location: _______________
- [ ] **Checkpoint manifest** — List of all checkpoints with timestamps and metrics
  - Location: _______________
- [ ] **Compute cost report** — Total cost of training run(s) to reach G1
  - Location: _______________
- [ ] **Tier history** — Record of training tier used (T1/T2/T3) with transitions
  - Location: _______________

### 1.2 Evaluation Evidence

- [ ] **Cross-modal accuracy report** — M-CM-001 >= 40% (mean of 3 runs)
  - Measured value: _____ | Location: _______________
- [ ] **Cross-modal F1 report** — M-CM-002 >= 0.38 (mean of 3 runs)
  - Measured value: _____ | Location: _______________
- [ ] **Validation loss trend** — Decreasing slope over last 5 epochs
  - Slope value: _____ | Location: _______________
- [ ] **Floor guard verification** — All 3 individual runs >= 35% accuracy
  - Run values: _____, _____, _____ | Location: _______________

### 1.3 Data Evidence

- [ ] **Training dataset manifest** — Dataset version, size, modality distribution
  - Location: _______________
- [ ] **Eval dataset manifest** — Held-out dataset version, size, no contamination
  - Location: _______________
- [ ] **Contamination check result** — Zero overlap between train and eval
  - Location: _______________

### 1.4 Gate Evidence

- [ ] **Gate evaluator output** — G1 PASS verdict with all criteria results
  - Location: _______________
- [ ] **No consecutive failures** — Failure history shows no 2x consecutive G1 fail
  - Location: _______________

**Milestone 1 Status:** [ ] VALIDATED / [ ] INCOMPLETE (gaps: _______________)

---

## Milestone 2: G2 — Mid-Tier Cross-Modal (60–70%)

### 2.1 Training Evidence

- [ ] **Training configuration** — Updated hyperparameters from G1 checkpoint
  - Location: _______________
- [ ] **Training logs** — Loss curves for G1→G2 training
  - Location: _______________
- [ ] **Checkpoint manifest** — All G2-phase checkpoints
  - Location: _______________
- [ ] **Compute cost report** — Incremental cost from G1 to G2
  - Location: _______________
- [ ] **Cost-per-point analysis** — $/pp trend during G2 training
  - Location: _______________

### 2.2 Evaluation Evidence

- [ ] **Cross-modal accuracy report** — M-CM-001 >= 60% (mean of 3 runs)
  - Measured value: _____ | Location: _______________
- [ ] **Cross-modal F1 report** — M-CM-002 >= 0.58
  - Measured value: _____ | Location: _______________
- [ ] **Cross-modal consistency** — M-CM-003 >= 55%
  - Measured value: _____ | Location: _______________
- [ ] **Modality gap** — M-MOD-004 <= 15pp (all 3 runs)
  - Max gap value: _____ | Location: _______________
- [ ] **Adversarial robustness** — M-ROB-001 >= 40%
  - Measured value: _____ | Location: _______________
- [ ] **Per-modality accuracy breakdown** — M-MOD-001, 002, 003 values
  - Text: _____, Image: _____, Audio: _____ | Location: _______________

### 2.3 Gate Evidence

- [ ] **Gate evaluator output** — G2 PASS verdict with all criteria results
  - Location: _______________
- [ ] **No consecutive failures** — Failure history clean
  - Location: _______________

**Milestone 2 Status:** [ ] VALIDATED / [ ] INCOMPLETE (gaps: _______________)

---

## Milestone 3: G3 — Pilot Readiness (>=70%) + G4 — Latency (<100ms)

### 3.1 G3 Training Evidence

- [ ] **Training configuration** — Final training config
  - Location: _______________
- [ ] **Training logs** — Full loss curves G2→G3
  - Location: _______________
- [ ] **Final checkpoint** — Checkpoint selected for pilot deployment
  - Checkpoint ID: _____ | Location: _______________

### 3.2 G3 Evaluation Evidence

- [ ] **Cross-modal accuracy** — M-CM-001 >= 70% (mean of 5 runs, stddev <= 3pp)
  - Mean: _____, Stddev: _____ | Location: _______________
- [ ] **Cross-modal F1** — M-CM-002 >= 0.68
  - Measured: _____ | Location: _______________
- [ ] **Cross-modal consistency** — M-CM-003 >= 65%
  - Measured: _____ | Location: _______________
- [ ] **Retrieval Recall@10** — M-CM-004 >= 0.60
  - Measured: _____ | Location: _______________
- [ ] **Modality gap** — M-MOD-004 <= 10pp (all 5 runs)
  - Max gap: _____ | Location: _______________
- [ ] **Adversarial robustness** — M-ROB-001 >= 50%
  - Measured: _____ | Location: _______________
- [ ] **OOD detection** — M-ROB-002 >= 0.85
  - Measured: _____ | Location: _______________
- [ ] **Calibration** — M-ROB-003 <= 0.05
  - Measured: _____ | Location: _______________
- [ ] **Safety violation rate** — M-SAF-001 <= 0.1%
  - Measured: _____ | Location: _______________
- [ ] **Stability verification** — All 5 individual runs >= 65% (floor guard)
  - Run values: _____, _____, _____, _____, _____ | Location: _______________

### 3.3 G4 Performance Evidence

- [ ] **Latency p50** — M-LAT-001 <= 50ms (mean of 5 load tests)
  - Measured: _____ms | Location: _______________
- [ ] **Latency p95** — M-LAT-002 <= 100ms (mean of 5 load tests, no run > 120ms)
  - Mean: _____ms, Max single: _____ms | Location: _______________
- [ ] **Latency p99** — M-LAT-003 <= 200ms
  - Measured: _____ms | Location: _______________
- [ ] **Throughput** — M-THR-001 >= 100 QPS
  - Measured: _____ QPS | Location: _______________
- [ ] **GPU memory** — M-RES-001 <= 16 GB
  - Measured: _____ GB | Location: _______________
- [ ] **Load test configuration** — Documented load profile (ramp, sustain, duration)
  - Location: _______________

### 3.4 Gate Evidence

- [ ] **G3 gate evaluator output** — PASS verdict
  - Location: _______________
- [ ] **G4 gate evaluator output** — PASS verdict
  - Location: _______________
- [ ] **Human sign-off for G3** — Obtained (G3 requires T3 approval)
  - Approved by: _____, Date: _____ | Location: _______________

### 3.5 Cost Evidence

- [ ] **Total project compute cost** — Within $500/month budget
  - Total spent: $_____ | Location: _______________
- [ ] **Cost-per-point trend** — Final $/pp value
  - Final value: $_____ /pp | Location: _______________
- [ ] **Kill-switch history** — Record of any kill-switch activations
  - Activations: _____ | Location: _______________

**Milestone 3 Status:** [ ] VALIDATED / [ ] INCOMPLETE (gaps: _______________)

---

## Milestone 4: Pilot Deployment

### 4.1 Pre-Deployment Evidence

- [ ] **Pilot SOW executed** — Signed by both parties
  - Location: _______________
- [ ] **Data handling agreement** — DPA or DUA signed
  - Location: _______________
- [ ] **Deployment environment validated** — Endpoint live and responding
  - Endpoint URL: _____ | Location: _______________
- [ ] **Integration guide delivered** — D2 from SOW accepted by partner
  - Location: _______________
- [ ] **Benchmark dataset received** — D4 from SOW
  - Samples: _____, Size: _____ | Location: _______________

### 4.2 Monitored Operation Evidence

- [ ] **Weekly status reports** — All delivered on time
  - Reports: _____ / _____ delivered | Location: _______________
- [ ] **Uptime log** — >= 99.0% during monitored period
  - Measured: _____% | Location: _______________
- [ ] **Incident log** — All incidents documented and resolved
  - Total incidents: _____, Unresolved: _____ | Location: _______________

### 4.3 Pilot Evaluation Evidence

- [ ] **Pilot scorecard completed** — All sections filled, verdict recorded
  - Verdict: _____ | Location: _______________
- [ ] **Partner feedback survey** — Completed, average >= 3.5/5.0
  - Average: _____ | Location: _______________
- [ ] **Final pilot report** — D7 from SOW delivered
  - Location: _______________

**Milestone 4 Status:** [ ] VALIDATED / [ ] INCOMPLETE (gaps: _______________)

---

## Summary

| Milestone | Status | Evidence Items | Completed | Gaps |
|-----------|--------|---------------|-----------|------|
| G1 Baseline | [ ] VALIDATED | 14 | [___] | |
| G2 Mid-Tier | [ ] VALIDATED | 13 | [___] | |
| G3+G4 Pilot Ready | [ ] VALIDATED | 22 | [___] | |
| Pilot Deployment | [ ] VALIDATED | 11 | [___] | |
| **Total** | | **60** | **[___]** | |
