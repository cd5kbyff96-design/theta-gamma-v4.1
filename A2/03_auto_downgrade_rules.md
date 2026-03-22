# Auto-Downgrade Rules — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26
**References:** `01_compute_budget_policy.md`, `02_training_tier_matrix.csv`

---

## 1. Purpose

This document defines the automated rules that downgrade the training stack when budget
pressure approaches cap limits. Downgrades preserve milestone velocity by continuing
training at reduced cost rather than halting entirely. Upgrades are also defined for when
budget pressure subsides.

## 2. Downgrade Cascade Overview

```
┌──────────────────────────────────────────────────────────┐
│  T1-Full-FSDP / T1-Full-DeepSpeed                       │
│  4xA100-80GB | full batch | $35-50/day                   │
│  DEFAULT TIER                                            │
├──────────────────────┬───────────────────────────────────┤
│  Trigger: 80% cap    │  OR cost/pp > $15                 │
│          ▼           │                                   │
│  T2-Efficient-ZeRO2/3                                    │
│  2xA100-80GB | 75% batch | $20-35/day                    │
├──────────────────────┬───────────────────────────────────┤
│  Trigger: 90% cap    │  OR cost/pp > $25                 │
│          ▼           │                                   │
│  T3-Compressed (QLoRA or Pruned)                         │
│  1xA100-80GB | 50% batch | $8-20/day                     │
├──────────────────────┬───────────────────────────────────┤
│  Trigger: 95% cap    │                                   │
│          ▼           │                                   │
│  T4-Eval-Only                                            │
│  1xA100-40GB/A10 | no training | $2-8/day                │
├──────────────────────┬───────────────────────────────────┤
│  Trigger: 100% cap   │  (KS-MONTHLY kill-switch)         │
│          ▼           │                                   │
│  T5-Full-Stop                                            │
│  $0/day                                                  │
└──────────────────────────────────────────────────────────┘
```

## 3. Downgrade Rules

### Rule D1: T1 -> T2 (Full -> Efficient)

**Trigger conditions (ANY):**
- Monthly spend >= 80% of $500 cap ($400)
- Daily spend >= 80% of $50 cap ($40) for 2 consecutive days
- Cost-per-point exceeds $15/pp over last 3 training runs
- GPU utilization < 40% average over 4 hours (resource waste)

**Execution:**
1. Complete current training step (do not interrupt mid-step)
2. Save checkpoint with full optimizer state
3. Log downgrade event: `{from: T1, to: T2, reason: <trigger>, timestamp: ISO-8601}`
4. Reconfigure job:
   - Reduce GPU count: 4 -> 2
   - Switch to DeepSpeed ZeRO-2 (or ZeRO-3 if model doesn't fit)
   - Reduce batch size to 75% of T1 batch size
   - Adjust learning rate: scale linearly with batch size reduction
   - Enable gradient accumulation to approximate effective batch size
5. Resume from checkpoint
6. Run quick eval (cross-modal accuracy only) after 100 steps to verify no catastrophic degradation

**Rollback guard:** If cross_modal_accuracy drops > 5pp within 500 steps of downgrade, revert to T1 and log anomaly.

**Autonomy tier:** T1 — log and proceed (per `A0/00_autonomy_contract.md`)

### Rule D2: T2 -> T3 (Efficient -> Compressed)

**Trigger conditions (ANY):**
- Monthly spend >= 90% of $500 cap ($450)
- Daily spend >= 90% of $50 cap ($45) for 2 consecutive days
- Cost-per-point exceeds $25/pp over last 3 training runs

**Execution:**
1. Complete current training step
2. Save checkpoint with full optimizer state
3. Log downgrade event
4. Select compression strategy:
   - **QLoRA path (default):** Quantize base model to 4-bit NF4, add LoRA adapters (rank 64, alpha 128)
   - **Pruning path (fallback):** Apply magnitude pruning at 30% sparsity if QLoRA causes > 8pp accuracy drop
5. Reconfigure job:
   - Reduce GPU count: 2 -> 1
   - Apply selected compression
   - Reduce batch size to 50% of T1 batch size
   - Reduce learning rate by 50% (compressed models are more sensitive)
6. Resume from checkpoint (QLoRA) or fine-tune from pruned model
7. Run quick eval after 200 steps

**Rollback guard:** If cross_modal_accuracy drops > 10pp within 1000 steps, revert to T2.

**QLoRA -> Pruning fallback:** If QLoRA accuracy is > 8pp below T2 baseline after 500 steps, switch to pruning path automatically.

**Autonomy tier:** T2 — notify and proceed

### Rule D3: T3 -> T4 (Compressed -> Eval-Only)

**Trigger conditions (ANY):**
- Monthly spend >= 95% of $500 cap ($475)
- All training budget categories exhausted
- 3 consecutive training runs show no gate progress

**Execution:**
1. Save final checkpoint
2. Terminate all training jobs
3. Log downgrade event
4. Switch to eval-only mode:
   - Run eval harness on all existing checkpoints
   - Identify best checkpoint per gate
   - Generate cost-efficiency report
5. Reduce infrastructure to minimum inference-capable setup

**Autonomy tier:** T2 — notify and proceed

### Rule D4: T4 -> T5 (Eval-Only -> Full Stop)

**Trigger conditions:**
- Monthly spend >= 100% of $500 cap ($500)
- KS-MONTHLY kill-switch activated

**Execution:**
1. Terminate ALL running jobs immediately
2. Save any in-progress eval results
3. Log downgrade event
4. Block all new compute launches until next budget period or human override

**Autonomy tier:** Automatic (kill-switch is non-negotiable)

## 4. Upgrade Rules

### Rule U1: T2 -> T1 (Efficient -> Full)

**Trigger conditions (ALL required):**
- Monthly spend drops below 50% of cap ($250) with >= 10 days remaining
- No active budget alerts
- Current gate has not yet passed (training still needed)

**Execution:**
1. Save checkpoint
2. Log upgrade event
3. Reconfigure to T1 settings (4 GPU, full batch)
4. Resume from checkpoint
5. Monitor spend rate for 24h — if projected to hit 80% cap, auto-downgrade again

### Rule U2: T3 -> T2 (Compressed -> Efficient)

**Trigger conditions (ALL required):**
- Monthly spend drops below 60% of cap ($300) with >= 10 days remaining
- No active budget alerts
- Compressed training is showing diminishing returns (cost-per-point > $20/pp at T3)

**Execution:**
1. Merge LoRA adapters (if QLoRA) or remove pruning masks
2. Save merged checkpoint
3. Log upgrade event
4. Reconfigure to T2 settings
5. Resume from merged checkpoint

### Rule U3: T4/T5 -> Any Training Tier

**Trigger conditions:**
- New budget month begins, OR
- Human approves budget amendment (T3 per autonomy contract)

**Execution:**
1. Evaluate remaining monthly budget
2. Select highest affordable tier
3. Resume from best known checkpoint
4. Log upgrade event

## 5. Ray Scaling Policies

### 5.1 Scale-Up Policy (Ray Train)

**When to scale beyond default GPU count:**

| Condition | Action | Max Scale |
|-----------|--------|-----------|
| Gate deadline < 5 days AND current tier insufficient | Request T1-Ray-Scaled (8 GPU) | 2x default |
| Cost-per-point < $5/pp AND monthly budget < 40% spent | Allow opportunistic scaling | 2x default |
| Hyperparameter sweep with > 8 configurations | Use Ray Tune with 2 concurrent trials | 2x default |

**All scale-up requires human pre-approval (T3)** — per `02_training_tier_matrix.csv`.

### 5.2 Scale-Down Policy (Ray Train)

| Condition | Action |
|-----------|--------|
| Scaled job running > 6h without metric improvement | Terminate and revert to base tier |
| Daily spend projected to exceed $80 at current rate | Scale down to base GPU count |
| Spot instance preemption rate > 3/hour | Switch to on-demand at lower GPU count |

**Scale-down is autonomous (T1)** — log and proceed.

### 5.3 Spot Instance Policies

| Policy | Rule |
|--------|------|
| Spot eligibility | Only for workloads that checkpoint every 30 minutes |
| Preemption handling | Resume from latest checkpoint on new spot or on-demand instance |
| Availability threshold | Require > 80% spot availability in region before starting |
| Fallback | If spot unavailable for > 30 min, fall back to on-demand at same or lower tier |
| Cost savings target | Spot must be >= 40% cheaper than on-demand to justify preemption risk |

## 6. FSDP vs DeepSpeed Selection

### 6.1 Default Selection Logic

```
if model fits in 4xA100 with FSDP:
    use T1-Full-FSDP (simpler, fewer config knobs)
elif model requires activation checkpointing or offloading:
    use T1-Full-DeepSpeed (ZeRO-3 + offload)
elif downgrading to T2:
    use DeepSpeed ZeRO-2 (better memory efficiency at 2 GPU)
elif downgrading to T3:
    use DeepSpeed ZeRO-2 + QLoRA (single GPU)
```

### 6.2 Lightning Integration

- All tiers use Lightning Fabric as the training loop abstraction
- Tier changes only modify the `strategy` parameter:
  - T1-FSDP: `FSDPStrategy(sharding_strategy="FULL_SHARD")`
  - T1-DeepSpeed: `DeepSpeedStrategy(stage=3)`
  - T2: `DeepSpeedStrategy(stage=2)`
  - T3: `DeepSpeedStrategy(stage=2)` + QLoRA/pruning applied at model level
- This minimizes code changes during tier transitions

## 7. Downgrade Decision Log Format

Every downgrade/upgrade must log:

```yaml
- timestamp: "ISO-8601"
  direction: downgrade|upgrade
  from_tier: T1|T2|T3|T4|T5
  to_tier: T1|T2|T3|T4|T5
  rule: D1|D2|D3|D4|U1|U2|U3
  trigger_reason: "monthly spend at 82% ($410)"
  monthly_spend_at_trigger: 410.00
  daily_spend_at_trigger: 42.00
  checkpoint_id: "ckpt-20260226-1430"
  cross_modal_accuracy_at_trigger: 52.3
  cost_per_point_at_trigger: 18.5
  rollback_guard_active: true
  autonomy_tier: T1|T2
```

## 8. Kill-Switch Integration

Kill-switches from `01_compute_budget_policy.md` override all downgrade rules:

| Kill-Switch | Effect on Tier |
|-------------|---------------|
| KS-DAILY | Pause current tier until next calendar day |
| KS-MONTHLY | Force to T5-Full-Stop |
| KS-RUNAWAY | Terminate specific experiment, keep tier |
| KS-DURATION | Terminate specific job, keep tier |
| KS-REGRESSION | Pause training, trigger efficiency review |
| KS-ORPHAN | Block unattributed jobs, keep tier |

Kill-switches take precedence over downgrade cascade — the system cannot "downgrade around" a kill-switch.
