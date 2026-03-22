# Pilot Scorecard Template — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26
**Usage:** Copy-paste ready. Fill in measured values during pilot evaluation.

---

## PILOT SCORECARD

| Field | Value |
|-------|-------|
| **Pilot ID** | PLT-[YYYY]-[NNN] |
| **Partner** | [PARTNER_ORGANIZATION] |
| **SOW Reference** | SOW-TG-[YYYY]-[NNN] |
| **Model Version** | Theta-Gamma v[VERSION] |
| **Pilot Period** | [START_DATE] to [END_DATE] |
| **Evaluator** | [NAME], [TITLE] |
| **Evaluation Date** | [YYYY-MM-DD] |

---

## Section 1: Cross-Modal Performance

| # | Criterion | Metric ID | Target | Measured | Pass/Fail | Notes |
|---|-----------|-----------|--------|----------|-----------|-------|
| 1.1 | Cross-modal accuracy | M-CM-001 | >= 70.0% | [___]% | [ ] PASS / [ ] FAIL | |
| 1.2 | Cross-modal F1 | M-CM-002 | >= 0.68 | [___] | [ ] PASS / [ ] FAIL | |
| 1.3 | Cross-modal consistency | M-CM-003 | >= 65.0% | [___]% | [ ] PASS / [ ] FAIL | |
| 1.4 | Retrieval Recall@10 | M-CM-004 | >= 0.60 | [___] | [ ] PASS / [ ] FAIL | |
| 1.5 | Max modality gap | M-MOD-004 | <= 10.0pp | [___]pp | [ ] PASS / [ ] FAIL | |

**Section 1 Result:** [___] / 5 criteria passed

---

## Section 2: Latency & Throughput

| # | Criterion | Metric ID | Target | Measured | Pass/Fail | Notes |
|---|-----------|-----------|--------|----------|-----------|-------|
| 2.1 | Inference latency (p50) | M-LAT-001 | <= 50ms | [___]ms | [ ] PASS / [ ] FAIL | |
| 2.2 | Inference latency (p95) | M-LAT-002 | <= 100ms | [___]ms | [ ] PASS / [ ] FAIL | |
| 2.3 | Inference latency (p99) | M-LAT-003 | <= 200ms | [___]ms | [ ] PASS / [ ] FAIL | |
| 2.4 | Throughput (QPS) | M-THR-001 | >= [TARGET] QPS | [___] QPS | [ ] PASS / [ ] FAIL | |
| 2.5 | GPU memory peak | M-RES-001 | <= 16 GB | [___] GB | [ ] PASS / [ ] FAIL | |

**Section 2 Result:** [___] / 5 criteria passed

---

## Section 3: Reliability & Operations

| # | Criterion | Target | Measured | Pass/Fail | Notes |
|---|-----------|--------|----------|-----------|-------|
| 3.1 | Uptime during monitored operation | >= 99.0% | [___]% | [ ] PASS / [ ] FAIL | |
| 3.2 | API error rate | <= 1.0% | [___]% | [ ] PASS / [ ] FAIL | |
| 3.3 | Incidents during pilot (S1/S2) | 0 unresolved | [___] total / [___] unresolved | [ ] PASS / [ ] FAIL | |
| 3.4 | Mean time to recovery (MTTR) | <= 4 hours | [___]h | [ ] PASS / [ ] FAIL | |
| 3.5 | Weekly reports delivered on time | 100% | [___]% | [ ] PASS / [ ] FAIL | |

**Section 3 Result:** [___] / 5 criteria passed

---

## Section 4: Safety & Robustness

| # | Criterion | Metric ID | Target | Measured | Pass/Fail | Notes |
|---|-----------|-----------|--------|----------|-----------|-------|
| 4.1 | Safety violation rate | M-SAF-001 | <= 0.1% | [___]% | [ ] PASS / [ ] FAIL | |
| 4.2 | Adversarial robustness | M-ROB-001 | >= 50.0% | [___]% | [ ] PASS / [ ] FAIL | |
| 4.3 | OOD detection AUROC | M-ROB-002 | >= 0.85 | [___] | [ ] PASS / [ ] FAIL | |
| 4.4 | Calibration ECE | M-ROB-003 | <= 0.05 | [___] | [ ] PASS / [ ] FAIL | |

**Section 4 Result:** [___] / 4 criteria passed

---

## Section 5: Partner Feedback

| # | Question | Rating (1-5) | Comments |
|---|----------|-------------|----------|
| 5.1 | Overall model quality | [___] | |
| 5.2 | Ease of integration | [___] | |
| 5.3 | Documentation quality | [___] | |
| 5.4 | Technical support responsiveness | [___] | |
| 5.5 | Relevance to your use cases | [___] | |
| 5.6 | Likelihood to adopt post-pilot | [___] | |

**Section 5 Average:** [___] / 5.0
**Pass Threshold:** >= 3.5 / 5.0

| Feedback pass/fail | [ ] PASS (avg >= 3.5) / [ ] FAIL (avg < 3.5) |

---

## Overall Verdict

### Scoring Summary

| Section | Criteria Passed | Total | Weight |
|---------|----------------|-------|--------|
| 1. Cross-Modal Performance | [___] | 5 | 30% |
| 2. Latency & Throughput | [___] | 5 | 25% |
| 3. Reliability & Operations | [___] | 5 | 20% |
| 4. Safety & Robustness | [___] | 4 | 15% |
| 5. Partner Feedback | [pass/fail] | 1 | 10% |

### Mandatory Pass Criteria

These criteria MUST pass regardless of overall score:

| # | Mandatory Criterion | Result |
|---|-------------------|--------|
| M1 | Cross-modal accuracy (1.1) >= 70% | [ ] PASS / [ ] FAIL |
| M2 | Inference latency p95 (2.2) <= 100ms | [ ] PASS / [ ] FAIL |
| M3 | Safety violation rate (4.1) <= 0.1% | [ ] PASS / [ ] FAIL |
| M4 | Uptime (3.1) >= 99.0% | [ ] PASS / [ ] FAIL |

### Overall Result

```
[ ] PASS       — All mandatory criteria met AND >= 75% of total criteria passed
[ ] COND. PASS — All mandatory criteria met AND >= 60% of total criteria passed
                 Remediation plan required for failed criteria.
[ ] FAIL       — Any mandatory criterion failed OR < 60% of total criteria passed
```

**Overall Result:** [PASS / CONDITIONAL PASS / FAIL]

### Remediation Plan (if Conditional Pass)

| Failed Criterion | Gap | Remediation Action | Owner | Target Date |
|-----------------|-----|-------------------|-------|-------------|
| [criterion] | [target vs actual] | [action] | [name] | [date] |

---

## Signatures

| | Provider | Partner |
|---|---------|---------|
| **Name** | [NAME] | [NAME] |
| **Title** | [TITLE] | [TITLE] |
| **Date** | [YYYY-MM-DD] | [YYYY-MM-DD] |
| **Agrees with scorecard** | [ ] Yes / [ ] Disputed | [ ] Yes / [ ] Disputed |

**Dispute Notes (if any):**
[Free text for either party to note disagreements with measured values]
