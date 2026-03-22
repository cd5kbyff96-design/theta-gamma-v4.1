# Quality Report — Phase A2: Compute Budget & Downgrade Rules

**Generated:** 2026-02-27
**Phase:** A2
**Status:** PASS

---

## 1. File Manifest

| File | Status | Description |
|------|--------|-------------|
| `01_compute_budget_policy.md` | PASS | Budget envelope, alert thresholds, 6 kill-switches, experiment governance |
| `02_training_tier_matrix.csv` | PASS | 12 tiers with stack, cost band, entry/exit criteria |
| `03_auto_downgrade_rules.md` | PASS | 4 downgrade rules, 3 upgrade rules, Ray scaling policies, FSDP/DeepSpeed selection |
| `04_runway_burn_dashboard_spec.md` | PASS | 7-panel dashboard with data sources, alerting, derived metrics |
| `05_budget_guardrails.yaml` | PASS | Machine-readable guardrails: caps, hard stops, alert thresholds, downgrade order |
| `06_compute_exception_policy.md` | PASS | 5 exception types with approval flows, limits, tracking, post-review |
| `99_quality_report.md` | PASS | This file — gate-by-gate evidence |

## 2. Quality Gate Results

### Core Gates

| Gate | Requirement | Actual | Status | Evidence File | Evidence Section | Note |
|------|-------------|--------|--------|---------------|-----------------|------|
| Clear downgrade rules before cap breach | Rules trigger before 100% | D1 at 80%, D2 at 90%, D3 at 95%, D4 at 100% | PASS | `03_auto_downgrade_rules.md` | §3 Rules D1–D4 | All triggers fire before budget breach |
| Explicit kill-switch thresholds | Defined and non-negotiable | 6 kill-switches with specific USD thresholds | PASS | `01_compute_budget_policy.md` | §5 Kill-Switch Thresholds | KS-DAILY=$50, KS-MONTHLY=$500, KS-RUNAWAY=$50, KS-DURATION=24h, KS-REGRESSION=3x avg, KS-ORPHAN=$20 |
| Kill-switches consistent across docs | Budget policy = downgrade rules = guardrails | All 3 documents agree | PASS | `05_budget_guardrails.yaml` + `01_compute_budget_policy.md` + `03_auto_downgrade_rules.md` | hard_stop_usd, §5, §8 | Values cross-referenced |
| Every tier has entry + exit criteria | All 12 tiers | 12/12 have both columns populated | PASS | `02_training_tier_matrix.csv` | All rows | CSV columns 4 and 5 |
| Downgrade cascade covers FSDP -> DeepSpeed -> compressed | Full path defined | T1-FSDP -> T2-ZeRO2 -> T3-QLoRA/Pruned -> T4-Eval -> T5-Stop | PASS | `03_auto_downgrade_rules.md` | §2 Cascade Overview | Complete path with Lightning integration |
| Ray scaling policies defined | Scale-up and scale-down | 3 scale-up conditions, 3 scale-down conditions, spot policies | PASS | `03_auto_downgrade_rules.md` | §5 Ray Scaling Policies | Scale-up requires T3 approval |
| Budget aligns with A0 operating limits | $500/mo, $50/day, $50/action | All thresholds match | PASS | `05_budget_guardrails.yaml` | monthly_cap_usd, daily_cap_usd, single_action_cap_usd | Matches `A0/02_operating_limits.yaml` |

### Enforcement Addon Gates

| Gate | Requirement | Actual | Status | Evidence File | Evidence Section | Note |
|------|-------------|--------|--------|---------------|-----------------|------|
| Hard stop exists before budget breach | Hard stop fires at or before 100% cap | KS-DAILY at $50 (100%), KS-MONTHLY at $500 (100%) fire AT cap, preventing breach | PASS | `05_budget_guardrails.yaml` | hard_stop_usd | Critical alert at 96%/95% provides pre-breach warning; hard stop at 100% prevents overspend |
| Downgrade path defined for each high-cost workload | Every T1/T2 tier has a downgrade target | T1-FSDP -> T2-ZeRO2, T1-DeepSpeed -> T2-ZeRO2, T2-ZeRO2 -> T3-QLoRA, T1-Ray -> base tier, T1-Spot -> T2-Spot | PASS | `05_budget_guardrails.yaml` + `03_auto_downgrade_rules.md` | auto_downgrade_order, §3 Rules D1–D4 | All high-cost tiers have explicit downgrade targets |
| Budget guardrails YAML has required keys | monthly_cap_usd, hard_stop_usd, alert_thresholds, auto_downgrade_order | All 4 present | PASS | `05_budget_guardrails.yaml` | Top-level keys | Plus cost_per_point_thresholds, orphan_compute, budget_allocation, experiment_limits |
| Exception policy defines controlled overspend | Exceptions bounded and time-limited | 5 exception types with max overspend, duration, approval, auto-expiry | PASS | `06_compute_exception_policy.md` | §2 Exception Types | Max cumulative overspend: $150/mo (30% of cap); absolute ceiling: $600 |

## 3. Downgrade Coverage Summary

| Transition | Rule | Trigger | Autonomy |
|-----------|------|---------|----------|
| T1 -> T2 | D1 | 80% monthly cap or $15/pp | T1 (log & proceed) |
| T2 -> T3 | D2 | 90% monthly cap or $25/pp | T2 (notify & proceed) |
| T3 -> T4 | D3 | 95% monthly cap | T2 (notify & proceed) |
| T4 -> T5 | D4 | 100% monthly cap | Automatic (kill-switch) |
| T2 -> T1 | U1 | Spend < 50% with 10+ days left | T1 |
| T3 -> T2 | U2 | Spend < 60% with 10+ days left | T1 |
| T4/T5 -> Any | U3 | New month or human approval | T3 |

## 4. Kill-Switch Summary

| Switch | Threshold | Scope | Restart |
|--------|-----------|-------|---------|
| KS-DAILY | $50/day | All jobs | Next day + human |
| KS-MONTHLY | $500/month | All jobs | Next month + human |
| KS-RUNAWAY | $50/experiment | Single experiment | Human + justification |
| KS-DURATION | 24h runtime | Single job | Human + extension |
| KS-REGRESSION | 3x avg cost/pp | Training pipeline | Human review |
| KS-ORPHAN | $20 orphan/day | Unattributed jobs | Assign experiment_ids |

## 5. High-Cost Workload Downgrade Paths

| Workload | Cost Band | Downgrade Target | Savings |
|----------|-----------|-----------------|---------|
| T1-Full-FSDP (4xA100) | $35-50/day | T2-Efficient-ZeRO2 (2xA100) | ~40-50% |
| T1-Full-DeepSpeed (4xA100) | $35-50/day | T2-Efficient-ZeRO2/3 (2xA100) | ~40-50% |
| T1-Ray-Scaled (8xA100) | $50-100/day | T1-Full (4xA100) | ~50% |
| T2-Efficient (2xA100) | $20-35/day | T3-Compressed (1xA100) | ~40-60% |
| T1-Spot-FSDP (4xA100 spot) | $15-30/day | T2-Spot-ZeRO2 (2xA100 spot) | ~40-50% |

## 6. Cross-Reference Validation

- Budget caps ($500/mo, $50/day) match `A0/02_operating_limits.yaml`
- Downgrade rules reference gate metrics from `A1/01_metric_dictionary.yaml`
- Kill-switch thresholds consistent across `01_compute_budget_policy.md`, `03_auto_downgrade_rules.md`, and `05_budget_guardrails.yaml`
- Dashboard panels cover all data streams in budget policy and downgrade rules
- Rollback guards in downgrade rules align with failure signal thresholds from `A1/04_failure_signals.md`
- Exception policy respects autonomy tiers from `A0/00_autonomy_contract.md`
- Budget guardrails YAML is machine-readable for pipeline consumption

## 7. Top Blockers

None. All core and addon quality gates pass.
