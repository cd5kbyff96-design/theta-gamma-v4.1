# Evaluation Harness Plan — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26

---

## 1. Overview

The evaluation harness is the automated system that collects metrics defined in `01_metric_dictionary.yaml` and evaluates them against gate criteria in `02_gate_definitions.yaml`. It runs as part of the training and CI pipeline, producing structured reports that drive gate pass/fail decisions.

## 2. Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Eval Orchestrator                 │
│         (triggers evals, aggregates results)        │
├──────────┬──────────┬──────────┬────────────────────┤
│ Cross-   │ Per-     │ Latency  │ Safety &           │
│ Modal    │ Modality │ & Perf   │ Robustness         │
│ Suite    │ Suite    │ Suite    │ Suite              │
├──────────┴──────────┴──────────┴────────────────────┤
│              Metric Collector & Storage             │
├─────────────────────────────────────────────────────┤
│              Gate Evaluator & Reporter              │
└─────────────────────────────────────────────────────┘
```

### 2.1 Components

| Component | Responsibility |
|-----------|---------------|
| **Eval Orchestrator** | Schedules and coordinates eval suite execution, manages dependencies between suites |
| **Cross-Modal Suite** | Runs M-CM-001 through M-CM-004 evaluations |
| **Per-Modality Suite** | Runs M-MOD-001 through M-MOD-004 evaluations |
| **Latency & Perf Suite** | Runs M-LAT-001 through M-THR-001 and M-RES-001 benchmarks |
| **Safety & Robustness Suite** | Runs M-ROB-001 through M-SAF-001 evaluations |
| **Metric Collector** | Ingests results from all suites, validates schema, stores in metric store |
| **Gate Evaluator** | Applies gate definitions to collected metrics, produces pass/fail verdicts |
| **Reporter** | Generates human-readable reports, sends notifications, updates dashboards |

## 3. Eval Suite Specifications

### 3.1 Cross-Modal Suite

**Trigger:** End of each training run or on-demand
**Runtime budget:** 60 minutes max
**Dataset:** Cross-modal benchmark set (held out from training)

| Eval | Dataset Size | Modality Pairs | Method |
|------|-------------|----------------|--------|
| Accuracy (M-CM-001) | 10,000 samples | text-image, text-audio, image-audio | Top-1 classification accuracy |
| F1 (M-CM-002) | Same 10,000 | Same | Weighted F1 per class |
| Consistency (M-CM-003) | 5,000 paired samples | Same semantic content, different modalities | Agreement rate |
| Retrieval Recall@10 (M-CM-004) | 5,000 queries | Each query modality vs each target modality | Recall in top-10 retrieved |

### 3.2 Per-Modality Suite

**Trigger:** Alongside cross-modal suite
**Runtime budget:** 30 minutes max

| Eval | Dataset Size | Method |
|------|-------------|--------|
| Text accuracy (M-MOD-001) | 5,000 text-only samples | Standard classification accuracy |
| Image accuracy (M-MOD-002) | 5,000 image-only samples | Standard classification accuracy |
| Audio accuracy (M-MOD-003) | 5,000 audio-only samples | Standard classification accuracy |
| Modality gap (M-MOD-004) | Derived | max pairwise difference |

### 3.3 Latency & Performance Suite

**Trigger:** Per build (after model export/optimization)
**Runtime budget:** 45 minutes max
**Infrastructure:** Production-equivalent hardware

| Eval | Method | Load Profile |
|------|--------|-------------|
| Latency p50/p95/p99 (M-LAT-*) | 10,000 inference requests | Ramp from 10 to 200 QPS over 10 min, sustain peak 5 min |
| Throughput (M-THR-001) | Same load test | Measured at sustained peak |
| GPU memory (M-RES-001) | nvidia-smi sampling during load test | Peak across run |

### 3.4 Safety & Robustness Suite

**Trigger:** End of each training run
**Runtime budget:** 90 minutes max

| Eval | Dataset Size | Method |
|------|-------------|--------|
| Adversarial robustness (M-ROB-001) | 2,000 samples | PGD attack (image ε=8/255), character perturbation (text) |
| OOD detection (M-ROB-002) | 3,000 in-dist + 3,000 OOD | AUROC on model confidence scores |
| Calibration (M-ROB-003) | 5,000 samples | 15-bin ECE |
| Safety violations (M-SAF-001) | 5,000 adversarial + benign prompts | Safety classifier flagging rate |

## 4. Data Management

### 4.1 Eval Datasets

- **Storage:** Versioned in object storage with content hashes
- **Isolation:** Eval datasets are never included in training data
- **Versioning:** Each dataset version is immutable; new versions get new IDs
- **Contamination check:** Automated dedup check against training data before each eval

### 4.2 Metric Storage

- **Format:** Structured JSON per eval run, indexed by run ID and timestamp
- **Retention:** All metric history retained indefinitely
- **Schema:** Validated against `01_metric_dictionary.yaml` on ingestion
- **Access:** Read-only for all components except Metric Collector

## 5. Execution Modes

| Mode | Trigger | Suites Run | Gate Evaluation |
|------|---------|------------|-----------------|
| **Full** | End of training run | All 4 suites | All applicable gates |
| **Quick** | Per commit on feature branch | Cross-modal + per-modality only | G1 only (sanity check) |
| **Perf-only** | Per build/optimization change | Latency & perf only | G4 only |
| **Safety-only** | On-demand or pre-pilot | Safety & robustness only | G3 safety criteria only |
| **Regression** | Nightly | All 4 suites against previous best | Delta metrics only (M-REG-*) |

## 6. Gate Evaluation Logic

```
for each gate in [G1, G2, G3, G4]:
    if gate.dependencies not all passed:
        skip gate (not yet eligible)

    results = []
    for each criterion in gate.criteria:
        metric_values = fetch_metric(criterion.metric_id, criterion.window)
        passed = evaluate(metric_values, criterion.operator, criterion.threshold)
        results.append(passed)

    gate_passed = all(results)

    if gate_passed:
        record_pass(gate, timestamp)
        if gate.id == "G3":
            request_human_signoff()
    else:
        record_fail(gate, timestamp)
        consecutive_fails = count_consecutive_fails(gate)
        if consecutive_fails >= 2:
            execute_rollback(gate.rollback)
        else:
            notify(gate.on_fail.notification)
```

## 7. Reporting

### 7.1 Per-Run Report

Generated after every eval run. Contains:
- Run metadata (ID, timestamp, checkpoint, configuration)
- All metric values with comparison to previous run
- Gate status for all eligible gates
- Regression deltas highlighted if negative
- Visualization: trend charts for primary metrics

### 7.2 Gate Status Dashboard

Live dashboard showing:
- Current status of each gate (not-started / in-progress / passed / failed)
- Historical pass/fail timeline
- Metric trends with threshold lines overlaid
- Time-to-gate estimates based on current trajectory

### 7.3 Failure Report

Generated on any gate failure. Contains:
- Which criteria failed and by how much
- Historical context (was this metric trending down?)
- Suggested investigation areas based on failure pattern
- Link to rollback actions if consecutive failure threshold reached

## 8. CI Integration

- **Training pipeline:** Full eval triggered at end of each training run
- **Feature branches:** Quick eval on PR creation and update
- **Build pipeline:** Perf-only eval on model export
- **Nightly:** Regression eval against best-known checkpoint
- **Pre-deploy:** Full eval required; results attached to deployment request

## 9. Reproducibility

- Every eval run captures: code version (git SHA), dataset version, model checkpoint hash, hardware spec, random seeds
- Eval results include a `reproduce` command that re-runs the exact evaluation
- Metric storage includes raw per-sample predictions for post-hoc analysis
