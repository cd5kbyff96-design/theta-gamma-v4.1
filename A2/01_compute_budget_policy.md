# Compute Budget Policy — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26
**Governing limits:** `A0/02_operating_limits.yaml`

---

## 1. Purpose

This policy prevents budget drift — the gradual, undetected overspend that occurs when
training experiments compound without cost visibility. It enforces hard ceilings, automated
downgrades, and kill-switches while preserving the velocity needed to hit milestone gates
G1–G4 defined in `A1/02_gate_definitions.yaml`.

## 2. Budget Envelope

| Parameter | Value | Source |
|-----------|-------|--------|
| Monthly compute cap | $500 | `02_operating_limits.yaml` |
| Daily compute cap | $50 | `02_operating_limits.yaml` |
| Single-action cap | $50 | `02_operating_limits.yaml` |
| Alert threshold | 80% of any cap | `02_operating_limits.yaml` |
| Max experiment runtime | 24 hours | `02_operating_limits.yaml` |

### 2.1 Budget Allocation by Activity

| Activity | Monthly Allocation | % of Cap | Flexibility |
|----------|-------------------|----------|-------------|
| Training runs (G1–G3 progression) | $300 | 60% | Can borrow up to $50 from eval |
| Eval harness (all suites) | $75 | 15% | Fixed |
| Load testing / perf benchmarks (G4) | $50 | 10% | Fixed |
| Ephemeral dev environments | $40 | 8% | Can shrink to $20 |
| CI / build / misc | $25 | 5% | Fixed |
| Reserve (unplanned) | $10 | 2% | Emergency only |

### 2.2 Budget Periods

- **Monthly cycle:** 1st to last day of calendar month
- **Unused budget does NOT roll over** — each month starts at $0 spent
- **Mid-month checkpoint:** Mandatory spend review at day 15

## 3. Cost Tracking Requirements

### 3.1 Real-Time Tracking

Every compute action must emit a cost event:

```
{
  "timestamp": "ISO-8601",
  "action_type": "training|eval|load_test|infra|ci",
  "resource": "gpu_type:count x hours",
  "estimated_cost_usd": 0.00,
  "cumulative_daily_usd": 0.00,
  "cumulative_monthly_usd": 0.00,
  "experiment_id": "string",
  "budget_category": "training|eval|perf|infra|ci|reserve"
}
```

### 3.2 Cost Attribution

- Every training run must have an `experiment_id` linking to a hypothesis
- Orphan compute (no experiment_id) is flagged as S3 failure signal
- Cost is attributed at the experiment level for ROI analysis

## 4. Alert Thresholds

| Level | Trigger | Action |
|-------|---------|--------|
| **Info** | Daily spend > $30 (60% of daily cap) | Log to dashboard |
| **Warning** | Daily spend > $40 (80% of daily cap) | Notify team channel |
| **Critical** | Daily spend > $48 (96% of daily cap) | Auto-pause non-essential jobs |
| **Kill** | Daily spend >= $50 (100% of daily cap) | Hard-stop ALL compute |
| **Info** | Monthly spend > $300 (60% of monthly cap) | Log to dashboard |
| **Warning** | Monthly spend > $400 (80% of monthly cap) | Notify team + trigger downgrade eval |
| **Critical** | Monthly spend > $475 (95% of monthly cap) | Auto-downgrade to cheapest tier |
| **Kill** | Monthly spend >= $500 (100% of monthly cap) | Hard-stop ALL compute for month |

## 5. Kill-Switch Thresholds

Kill-switches are **non-negotiable hard stops** that cannot be overridden autonomously.
Restarting after a kill-switch requires human approval (T3 per autonomy contract).

| Kill-Switch | Trigger | Effect | Restart Requires |
|-------------|---------|--------|-----------------|
| **KS-DAILY** | Daily spend >= $50 | Terminate all running jobs, block new launches | Human approval + next calendar day |
| **KS-MONTHLY** | Monthly spend >= $500 | Terminate all running jobs for remainder of month | Human approval + budget amendment |
| **KS-RUNAWAY** | Single experiment > $50 | Terminate that experiment | Human approval + cost justification |
| **KS-DURATION** | Any job running > 24h | Terminate that job | Human approval + runtime extension justification |
| **KS-REGRESSION** | Cost per gate-progress-point > 3x historical average | Pause training pipeline | Human review of training efficiency |
| **KS-ORPHAN** | > $20 cumulative orphan compute in a day | Block new unattributed jobs | Assign experiment_ids to orphaned jobs |

## 6. Experiment Governance

### 6.1 Pre-Launch Cost Estimate

Before any training run launches, it must produce:

- Estimated cost (GPU type x count x hours x rate)
- Budget category and remaining budget in that category
- Expected gate progress (which gate, estimated metric improvement)
- Kill conditions (max cost, max runtime, min metric improvement to justify continuation)

### 6.2 Checkpoint-Based Cost Gates

Training runs must checkpoint and evaluate cost-effectiveness at intervals:

| Checkpoint | Timing | Decision |
|-----------|--------|----------|
| Early-exit check | 10% of estimated runtime | If loss not decreasing, terminate |
| Mid-run check | 50% of estimated runtime | If metric improvement < 25% of target, evaluate downgrade |
| Late-run check | 80% of estimated runtime | If metric improvement < 75% of target, log for review |

### 6.3 Cost-per-Point Tracking

Track the marginal cost to improve cross_modal_accuracy by 1 percentage point:

```
cost_per_point = experiment_cost_usd / delta_cross_modal_accuracy_pp
```

- **Healthy:** < $15/pp
- **Elevated:** $15–$30/pp — evaluate optimization opportunities
- **Unsustainable:** > $30/pp — trigger KS-REGRESSION review

## 7. Downgrade Cascade

When budget pressure triggers alerts, the system follows the downgrade cascade
defined in `03_auto_downgrade_rules.md`:

```
FSDP/Lightning (full performance)
    ↓ at 80% monthly cap
DeepSpeed ZeRO-2/3 (reduced memory, similar throughput)
    ↓ at 90% monthly cap
Compressed fallback (quantized, reduced batch)
    ↓ at 95% monthly cap
Eval-only mode (no training, only run evals on existing checkpoints)
    ↓ at 100% monthly cap
Full stop
```

## 8. Monthly Review Process

At the end of each budget month:

1. **Spend report:** Total spend by category vs allocation
2. **Efficiency report:** Cost-per-point trend, waste analysis
3. **Gate progress report:** Which gates advanced, at what cost
4. **Next month plan:** Proposed allocation adjustments based on trajectory
5. **Anomaly report:** Any kill-switch activations, orphan compute, overruns

## 9. Policy Amendments

Changes to this policy follow the amendment process in `A0/00_autonomy_contract.md` Section 11.
Budget cap increases above $500/month require human approval (T3).
