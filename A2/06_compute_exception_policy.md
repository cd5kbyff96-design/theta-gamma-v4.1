# Compute Exception Policy — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-27
**References:** `01_compute_budget_policy.md`, `05_budget_guardrails.yaml`

---

## 1. Purpose

This policy defines how to request, approve, and track exceptions to the compute budget
guardrails. Exceptions are rare and time-bounded — they exist for cases where strict
adherence to budget caps would cause greater harm than a controlled, temporary overspend.

---

## 2. Exception Types

### EX-01: Budget Cap Override

**When:** A critical gate deadline is at risk and the remaining monthly budget is
insufficient to complete the necessary training runs.

| Field | Value |
|-------|-------|
| Approval | Human (T3 per autonomy contract) |
| Max overspend | 20% of monthly cap ($100 above $500) |
| Duration | Remainder of current budget month only |
| Reporting | Daily spend reports to budget owner |
| Auto-expire | End of calendar month — no carryover |

**Request must include:**
- Current gate status and distance to threshold
- Estimated cost to reach gate
- Evidence that downgrade tiers are insufficient
- Projected total spend with exception

### EX-02: Kill-Switch Temporary Suspension

**When:** A kill-switch (KS-DAILY, KS-RUNAWAY, KS-DURATION) has tripped but the
interrupted work is within minutes of completing a critical checkpoint.

| Field | Value |
|-------|-------|
| Approval | Human (T3) |
| Max extension | 30 minutes OR $10 additional, whichever comes first |
| Scope | Single job only — does not lift the switch for other jobs |
| Logging | Every minute of extension logged with cost |
| Auto-expire | After 30 minutes or $10 additional spend |

**Cannot be applied to:**
- KS-MONTHLY (non-negotiable)
- KS-REGRESSION (requires efficiency review, not more compute)
- KS-ORPHAN (requires attribution, not more compute)

### EX-03: Tier Lock (Prevent Downgrade)

**When:** The auto-downgrade system would trigger a tier change, but the current
training run is in a critical phase where switching tiers would cause checkpoint
incompatibility or significant metric regression.

| Field | Value |
|-------|-------|
| Approval | Human (T3) |
| Max duration | 48 hours |
| Condition | Must remain within daily cap (no compound exception) |
| Monitoring | Hourly cost check — if daily cap at risk, downgrade anyway |
| Auto-expire | After 48 hours or if daily cap is breached |

### EX-04: Scaled Compute Burst

**When:** A time-sensitive experiment (e.g., hyperparameter sweep before a gate
deadline) requires temporarily scaling beyond the default GPU allocation.

| Field | Value |
|-------|-------|
| Approval | Human (T3) |
| Max scale | 2x default GPU count (8 GPU max) |
| Max duration | 12 hours |
| Max cost | $100 for the burst period |
| Condition | Monthly spend < 60% of cap before burst starts |
| Auto-expire | After 12 hours, or if burst cost hits $100, or if monthly spend reaches 80% |

### EX-05: Eval Budget Reallocation

**When:** Training budget is exhausted but eval budget has surplus, and running
additional eval cycles on existing checkpoints would inform the next month's
training strategy.

| Field | Value |
|-------|-------|
| Approval | Autonomous (T1 — log and proceed) |
| Max reallocation | $25 from eval to training |
| Condition | Eval budget has >= $40 remaining |
| Direction | Eval -> training only (never training -> eval) |
| Logging | Reallocation logged as budget event |

---

## 3. Exception Request Process

### 3.1 Request Format

```yaml
exception_request:
  type: EX-01|EX-02|EX-03|EX-04|EX-05
  requester: pipeline|operator
  timestamp: "ISO-8601"
  justification: "string — why is this exception necessary"
  current_monthly_spend_usd: 0.00
  current_daily_spend_usd: 0.00
  requested_additional_usd: 0.00
  requested_duration_hours: 0
  gate_context: "which gate, current metric value, target"
  risk_assessment: "what happens if exception is denied"
  rollback_plan: "how to recover if exception causes problems"
```

### 3.2 Approval Flow

```
Exception Request
    │
    ├─ EX-05 (eval reallocation) ─── Autonomous: log and proceed
    │
    └─ EX-01 through EX-04 ─────── Human approval required (T3)
         │
         ├─ Approved ─── Set timer for auto-expiry
         │                Log approval with conditions
         │                Enable exception with guardrails
         │
         └─ Denied ───── Log denial with reason
                         Continue under normal guardrails
```

### 3.3 Approval SLA

| Exception Type | Approval SLA | Escalation if No Response |
|---------------|-------------|--------------------------|
| EX-01 Budget Override | 4 hours | Operate under normal caps |
| EX-02 Kill-Switch Suspension | 15 minutes | Kill-switch stays active |
| EX-03 Tier Lock | 2 hours | Downgrade proceeds |
| EX-04 Scaled Burst | 4 hours | Use default GPU count |
| EX-05 Reallocation | Instant (autonomous) | N/A |

---

## 4. Exception Limits

| Constraint | Limit |
|-----------|-------|
| Max active exceptions | 2 concurrent (excluding EX-05) |
| Max exceptions per month | 4 (excluding EX-05) |
| Max cumulative overspend per month | $150 (30% of cap) |
| Max consecutive months with exceptions | 2 — third month requires budget revision |
| EX-05 reallocations per month | 2 |

---

## 5. Exception Tracking

All exceptions are tracked in the exception log:

```yaml
exception_log:
  - id: "EXC-2026-02-001"
    type: EX-01
    status: active|expired|revoked
    approved_by: "operator_name"
    approved_at: "ISO-8601"
    expires_at: "ISO-8601"
    actual_additional_spend_usd: 0.00
    outcome: "gate G2 passed during exception window"
    post_mortem_required: true|false
```

---

## 6. Post-Exception Review

Every EX-01, EX-02, EX-03, and EX-04 exception triggers a post-exception review:

1. **Was the exception necessary?** Could downgrade or rescheduling have worked?
2. **Was the budget impact within the approved envelope?**
3. **Did the exception achieve its goal?** (gate progress, checkpoint saved, etc.)
4. **Should guardrails be adjusted?** If the same exception type recurs, the budget
   policy or caps may need amendment.
5. **Root cause:** Why did normal budget prove insufficient?

Reviews are documented in the monthly budget review process
(`01_compute_budget_policy.md` Section 8).

---

## 7. What Exceptions Cannot Do

Exceptions **never** allow:

- Exceeding hard_stop_usd by more than 20% ($600 absolute monthly ceiling)
- Running without experiment attribution (KS-ORPHAN cannot be excepted)
- Bypassing KS-MONTHLY entirely (only EX-01 can raise the cap, not remove it)
- Operating without cost tracking enabled
- Approving exceptions retroactively (must be approved before the overspend)
- Stacking EX-01 + EX-04 simultaneously (compound risk too high)
