# Roll-Forward / Roll-Back Rules — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26

---

## 1. Purpose

These rules define when the weekly control loop advances the pipeline forward
(roll-forward) versus when it reverts to a prior known-good state (roll-back).
They integrate with the go/no-go decision from Step 4 of the weekly loop and
the recovery state machine from A4.

## 2. Decision Framework

```
Weekly Loop Step 4: Go/No-Go
│
├─ GO or GO_WITH_WATCH ──────► ROLL-FORWARD
│   Advance to next planned work.
│
├─ CONDITIONAL_GO ───────────► PARTIAL ROLL-FORWARD
│   Advance on healthy packets only.
│   Pause or roll back affected area.
│
└─ NO_GO ────────────────────► ROLL-BACK (scope depends on trigger)
    Revert to last known-good state.
```

## 3. Roll-Forward Rules

### RF-1: Standard Roll-Forward (GO)

**Trigger:** Go/no-go decision is `go` (all 6 conditions met)

**Actions:**
1. Mark previous week's completed packets as `done`
2. Advance to next planned packets from `next_7_days_plan`
3. Update `current_gate` if a gate passed this week
4. Archive previous week's checkpoint as `known_good_weekly`
5. Continue at current training tier

**Constraint:** Roll-forward is the default. No human approval needed.

### RF-2: Cautious Roll-Forward (GO_WITH_WATCH)

**Trigger:** Go/no-go decision is `go_with_watch`

**Actions:**
1. All RF-1 actions
2. Add watch items to the `next_7_days_plan.watch_items`
3. Set mid-week check-in (Wednesday) to evaluate watch items
4. If any watch item breaches threshold at mid-week: trigger mini-loop (Steps 2–4)

### RF-3: Partial Roll-Forward (CONDITIONAL_GO)

**Trigger:** Go/no-go decision is `conditional_go`

**Actions:**
1. Identify which area is affected (training, eval, infra, budget)
2. Roll forward on unaffected areas
3. For affected area: choose one of:
   - **Pause:** Hold affected packets, continue others
   - **Scope reduce:** Run affected packets at reduced scope (e.g., quick eval instead of full)
   - **Substitute:** Replace affected packet with a lower-risk alternative
4. Set daily check on affected area until resolved
5. Log partial roll-forward decision in decision log

### RF-4: Gate Roll-Forward

**Trigger:** A gate passes during the week

**Actions:**
1. Record gate pass with timestamp, metrics, and checkpoint ID
2. Immediately re-prioritize backlog (next gate's packets rise to top)
3. Archive gate-passing checkpoint as `known_good_gate_<G1|G2|G3|G4>`
4. Update `milestone_delta.current_gate` in next report
5. If G3: request human sign-off (T3) before roll-forward to pilot

## 4. Roll-Back Rules

### RB-1: Metric Roll-Back

**Trigger:** Primary metric for current gate regresses > 5pp from previous week AND
regression confirmed on re-evaluation (not a measurement fluke)

**Actions:**
1. Identify regression cause (data, code, config, infra)
2. Revert to `known_good_weekly` checkpoint from last week
3. Discard all training progress since that checkpoint
4. Log rollback in decision log with root cause
5. Re-run eval on reverted checkpoint to confirm restoration
6. Adjust next week's plan to address regression cause

**Autonomy:** T2 (notify and proceed) — reversible, logs decision.

### RB-2: Gate Roll-Back (Consecutive Failure)

**Trigger:** Current gate fails twice consecutively (per A1 gate definitions)

**Actions:**
1. Revert to `known_good_gate_<previous_gate>` checkpoint
2. Halt current gate's training
3. Generate blocker report (A4/04_blocker_report_template.md)
4. Execute gate-specific rollback actions from A1/02_gate_definitions.yaml:
   - G1: Hyperparameter review
   - G2: Modality balance diagnostic
   - G3: Full diagnostic suite + architecture review
   - G4: Profiling + optimization sprint
5. No-go for next week until human approves recovery plan

**Autonomy:** T3 (approval required) — significant regression.

### RB-3: Budget Roll-Back

**Trigger:** Kill-switch tripped (KS-DAILY, KS-MONTHLY) or budget > 95%

**Actions:**
1. Apply tier downgrade per A2/03_auto_downgrade_rules.md
2. If at T4 (eval-only) or T5 (full stop): roll back scope to eval-only packets
3. Remove all training packets from next week's plan
4. Recalculate weekly cost estimate with new tier
5. If budget exhausted (T5): no-go until next budget period or amendment

**Autonomy:** T1/T2 (automatic/notify) for tier downgrade. T3 for budget amendment.

### RB-4: Safety Roll-Back

**Trigger:** Safety violation rate (M-SAF-001) > 1.0% (10x threshold)

**Actions:**
1. **IMMEDIATE HALT** — stop all training and deployment activity
2. Quarantine current checkpoint — do not serve or deploy
3. Revert to last checkpoint where M-SAF-001 <= 0.1%
4. Re-run safety eval on reverted checkpoint to confirm safety
5. Generate S1 incident report
6. No-go until safety review completed by Safety Lead

**Autonomy:** Automatic halt, T3 for restart.

### RB-5: Infrastructure Roll-Back

**Trigger:** Checkpoint corruption, infra failure, or S1 infra incident

**Actions:**
1. Revert to last valid checkpoint
2. If checkpoint storage is compromised: failover to backup storage
3. Validate all infrastructure health before resuming
4. Re-run last eval to confirm model integrity
5. Resume at same training tier

**Autonomy:** T1 (log and proceed) for checkpoint revert. T3 if storage is compromised.

### RB-6: Full Pipeline Roll-Back

**Trigger:** 3+ S1 incidents active simultaneously OR catastrophic infrastructure failure

**Actions:**
1. Halt entire pipeline
2. Revert ALL components to last `known_good_weekly` state
3. Generate blocker report for each active S1
4. Notify all stakeholders
5. No-go until ALL S1 incidents resolved and post-mortem completed
6. Restart requires Architect + Stakeholder approval

**Autonomy:** Automatic halt. T3 for restart.

## 5. Known-Good Checkpoint Registry

The system maintains these checkpoint categories:

| Checkpoint Type | Updated When | Retention | Used By |
|----------------|-------------|-----------|---------|
| `known_good_weekly` | Every Monday if GO decision | Last 4 weeks | RB-1, RB-6 |
| `known_good_gate_G1` | When G1 passes | Indefinite | RB-2 (from G2) |
| `known_good_gate_G2` | When G2 passes | Indefinite | RB-2 (from G3) |
| `known_good_gate_G3` | When G3 passes | Indefinite | Pilot baseline |
| `known_good_safety` | Every eval where M-SAF-001 <= 0.1% | Last 5 | RB-4 |
| `known_good_latency` | Every build where p95 <= 100ms | Last 5 | RB-1 (latency) |

**Storage:** All known-good checkpoints stored in versioned, checksummed storage
(per PKT-INFRA-002). Integrity verified weekly.

## 6. Roll-Forward / Roll-Back Decision Table

Quick reference combining go/no-go with roll-forward/roll-back:

| Weekly Outcome | Roll Direction | Scope | Human Needed | Checkpoint Action |
|----------------|---------------|-------|-------------|-------------------|
| All nominal, gate progress | RF-1 + RF-4 | Full | No | Save as known_good_weekly + known_good_gate |
| All nominal, no gate progress | RF-1 | Full | No | Save as known_good_weekly |
| Watch items active | RF-2 | Full + monitoring | No | Save as known_good_weekly |
| Localized issue | RF-3 | Partial | No | Save unaffected as known_good_weekly |
| Metric regression confirmed | RB-1 | Targeted | No | Revert to previous known_good_weekly |
| Consecutive gate failure | RB-2 | Training | Yes | Revert to known_good_gate |
| Budget pressure | RB-3 | Budget-scoped | Tier-dependent | Keep checkpoint, change tier |
| Safety violation | RB-4 | Full halt | Yes | Quarantine + revert to known_good_safety |
| Infra failure | RB-5 | Infrastructure | Severity-dependent | Revert to last valid checkpoint |
| Catastrophic failure | RB-6 | Full pipeline | Yes | Full revert to known_good_weekly |

## 7. Post-Roll-Back Recovery

After any roll-back, the following week's loop MUST include:

1. **Root cause** documented in weekly report's `risk_delta.risk_items`
2. **Prevention action** added as a new packet or appended to existing packet
3. **Regression test** covering the specific failure mode
4. **Checkpoint integrity check** on the reverted-to checkpoint
5. **Re-evaluation** of all metrics from the reverted checkpoint

The roll-back is not considered complete until the pipeline returns to HEALTHY
state in the recovery state machine (A4).
