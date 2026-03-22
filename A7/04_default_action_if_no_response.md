# Default Action If No Response — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-27

---

## 1. Purpose

Every decision in the pipeline has a pre-defined default action that fires
automatically when the response deadline passes without a human reply. This
document catalogs all default actions by decision type, their risk profiles,
and the conditions under which they apply.

**Governing principle:** Defaults are always the SAFEST action that keeps the
pipeline moving. "Safe" means: no irreversible changes, no budget increases,
no scope expansions, no safety compromises.

---

## 2. Default Action Design Principles

1. **Conservative bias** — When in doubt, the default holds current state rather than advancing
2. **Reversible only** — Defaults never trigger irreversible actions (no data deletion, no production deployment, no contract execution)
3. **Budget-safe** — Defaults never increase spend; they may reduce or hold
4. **Safety-first** — Defaults never override safety controls or lower safety thresholds
5. **Logged always** — Every default execution is recorded in the decision log with `decided_by: automated_default`

---

## 3. Default Actions by Decision Type

### 3.1 Pipeline Go/No-Go

| Scenario | Default Action | Risk Level | Rationale |
|----------|---------------|------------|-----------|
| GO (all conditions met) | Proceed with plan | Low | All conditions healthy, safe to continue |
| GO_WITH_WATCH | Proceed with watch items active | Low | Minor issues, defaults to monitoring |
| CONDITIONAL_GO | Proceed with reduced scope only | Medium | Avoids full execution on unhealthy area |
| NO_GO (S1 open) | Hold pipeline, do NOT resume | Low | Safety-first: wait for human |
| NO_GO (budget) | Hold pipeline at safe tier | Low | Budget protection: no spend |
| NO_GO (gate failure) | Hold pipeline, await human plan | Low | Conservative: don't retry without guidance |

### 3.2 Gate Transitions

| Transition | Default Action | Risk Level | Rationale |
|-----------|---------------|------------|-----------|
| G1 pass → start G2 | Proceed to G2 with generated plan | Low | T1 decision, reversible |
| G2 pass → start G3 | Proceed to G3 with generated plan | Low | T2 decision, notify and proceed |
| G3 pass → start pilot | **NO DEFAULT — blocks until response** | N/A | T3 decision, irreversible external commitment |
| G4 pass → production | **NO DEFAULT — blocks until response** | N/A | T3 decision, irreversible deployment |
| Gate regression detected | Roll back to previous known-good checkpoint | Medium | Conservative: protect progress |

### 3.3 Budget Decisions

| Scenario | Default Action | Risk Level | Rationale |
|----------|---------------|------------|-----------|
| Budget warning (60–80%) | Continue at current tier, add budget watch | Low | No change, monitoring |
| Budget critical (80–95%) | Downgrade one tier per A2 rules | Medium | Protect runway |
| Budget exhausted (>95%) | Apply emergency tier (T4 eval-only) | Medium | Prevent overspend |
| Budget amendment request | Deny amendment, hold at current budget | Low | Conservative: no spend increase |
| Kill-switch tripped | Apply auto-downgrade per A2 | Medium | Automatic safety mechanism |

### 3.4 Recovery and Incident Decisions

| Scenario | Default Action | Risk Level | Rationale |
|----------|---------------|------------|-----------|
| S1 escalation (3rd failure) | Hold in ESCALATED state, do not retry | Low | Wait for human root cause decision |
| S2 escalation | Apply recommended recovery from retry policy | Medium | Follow pre-defined fallback |
| Roll-back restart approval | Hold at rolled-back state, do not restart | Low | Conservative: don't restart without human |
| Blocker > 14 days | Defer blocked packets, continue unblocked work | Low | Partial progress over full halt |
| Post-mortem approval | Accept post-mortem findings, apply corrective actions | Medium | Follow standard process |

### 3.5 External and Architecture Decisions

| Scenario | Default Action | Risk Level | Rationale |
|----------|---------------|------------|-----------|
| Partner data access response needed | Send follow-up per template, extend wait 7 days | Low | No commitment without human |
| SOW approval | Hold, do not send SOW | Low | No external commitment |
| Architecture change proposal | Defer proposal to next week | Low | No change without approval |
| New dependency introduction | Reject, continue with existing approach | Low | Conservative: no new risk |

---

## 4. Blocking Decisions (No Default)

These decisions NEVER have a default action. They will block the pipeline
indefinitely until a human responds.

| Decision | Reason | Escalation If Blocked > 48h |
|----------|--------|---------------------------|
| G3 pass → approve pilot | Irreversible external commitment | Escalate to Architect + Stakeholder |
| G4 pass → approve production | Irreversible deployment | Escalate to Architect + Stakeholder |

**These are the only two blocking decisions in the entire system.**

All other decisions have safe defaults and will never block the pipeline
for more than the standard deadline window.

---

## 5. Default Execution Protocol

When a deadline passes without response:

```
1. Log: decision_id, deadline, default_action, decided_by: "automated_default"
2. Apply: execute the default action
3. Notify: send "Default applied" notice to all channels
4. Continue: pipeline resumes autonomous operation
5. Record: include in next weekly report under "Defaulted Decisions" section
```

---

## 6. Default Override Window

After a default fires, the human has a **4-hour override window** to reverse
the default action, ONLY if the default was reversible.

| Default Category | Override Possible | Override Window |
|-----------------|-------------------|-----------------|
| Hold/pause decisions | Yes | 4 hours |
| Tier downgrade | Yes (can upgrade back) | 4 hours |
| Proceed with plan | Yes (can pause) | 4 hours |
| Roll-back executed | No (checkpoint already reverted) | N/A |
| Budget denial | Yes (can approve) | 4 hours |

After the override window closes, the default is final until the next weekly packet.

---

## 7. Cross-Reference

- Default actions are cataloged in `06_default_action_risk_table.csv` with risk levels and owners
- Deadlines follow `03_decision_deadline_policy.md`
- Decision latency targets are in `05_decision_latency_slo.md`
- Decision packet format is in `02_top5_decisions_template.md`
- Recovery defaults align with A4 recovery state machine and A4 retry policy
- Budget defaults align with A2 auto-downgrade rules
- Gate transition defaults align with A0 autonomy contract tier definitions
