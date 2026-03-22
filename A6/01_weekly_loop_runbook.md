# Weekly Control Loop Runbook — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26
**Cadence:** Every Monday 09:00 UTC (adjustable via amendment)

---

## 1. Purpose

The weekly control loop is the heartbeat of autonomous execution. Each Monday it
collects metrics, evaluates progress, re-prioritizes work, decides go/no-go for
the next week, and publishes a machine-parseable report. Between loops the pipeline
operates under the autonomy contract (A0); the loop is where the human gets a
structured window into what happened and what will happen next.

## 2. Loop Sequence

```
Monday 09:00 UTC
│
├─ STEP 1: Collect ──────────────────────── (automated, 15 min)
│  Gather all metrics from the past 7 days.
│
├─ STEP 2: Evaluate ─────────────────────── (automated, 15 min)
│  Compute deltas, run gate evaluator, assess risk.
│
├─ STEP 3: Prioritize ──────────────────── (automated, 15 min)
│  Re-rank packet backlog using auto-prioritization rules.
│
├─ STEP 4: Decide ──────────────────────── (automated + human, 30 min)
│  Apply go/no-go logic. Escalate if no-go.
│
├─ STEP 5: Plan ────────────────────────── (automated, 15 min)
│  Generate next-7-days execution plan.
│
├─ STEP 6: Report ──────────────────────── (automated, 10 min)
│  Publish weekly report per 02_weekly_report_schema.yaml.
│
└─ STEP 7: Execute ─────────────────────── (rest of week)
   Pipeline operates per plan until next Monday.
```

**Total loop time:** ~100 minutes (60 automated + 30 human review + 10 publish)

## 3. Step Details

### Step 1: Collect (automated)

Gather from all data sources:

| Data Source | Metrics Collected | System |
|-------------|------------------|--------|
| Eval harness | M-CM-001 through M-CM-004, M-MOD-001 through M-MOD-004 | Experiment tracker |
| Latency bench | M-LAT-001 through M-LAT-003, M-THR-001, M-RES-001 | Perf harness |
| Safety eval | M-ROB-001 through M-ROB-003, M-SAF-001 | Safety eval suite |
| Training logs | M-MQ-001 through M-MQ-004 | Training logger |
| Cost tracker | Daily spend, monthly spend, cost-per-point | Budget dashboard |
| Incident log | All incidents opened/closed this week | Incident system |
| Packet tracker | Packets completed, in-progress, blocked | Task tracker |
| Decision log | All autonomous decisions this week | Decision log |
| Gate evaluator | Gate status (G1–G4) pass/fail history | Gate evaluator |

**Output:** Raw data bundle stored as `weekly-data-YYYY-WNN.json`

### Step 2: Evaluate (automated)

Compute deltas and assessments:

| Evaluation | Computation | Stored As |
|-----------|-------------|-----------|
| Milestone delta | Current gate status vs last week | `milestone_delta` |
| Risk delta | Change in risk profile (new incidents, budget pressure) | `risk_delta` |
| Burn delta | Spend this week vs last week, runway projection | `burn_delta` |
| Blocker analysis | Packets blocked > 48h, dependencies unresolved | `blockers` |
| Trend analysis | 4-week rolling trend for primary metrics | trend charts |
| Anomaly detection | Any metric moving > 2σ from 4-week average | anomaly flags |

**Gate evaluation:** Run gate evaluator on latest metrics. Record pass/fail for all eligible gates.

### Step 3: Prioritize (automated)

Apply `03_auto_prioritization_rules.md` to re-rank the packet backlog:

1. Score each pending/in-progress packet
2. Sort by composite score (gate-blocking weight + deadline pressure + dependency readiness)
3. Identify top-5 packets for next week
4. Flag any packets that should be deprioritized or deferred
5. Check for packets blocked > 48h and escalate if needed

**Output:** Ranked packet list with scores and rationale

### Step 4: Decide — Go/No-Go (automated + human)

Apply go/no-go logic to determine whether the next week proceeds as planned
or requires intervention.

#### Go/No-Go Decision Matrix

| Condition | Result | Action |
|-----------|--------|--------|
| All metrics nominal, budget on track, no S1/S2 incidents open | **GO** | Proceed with auto-generated plan |
| Minor issues: budget warning, S3 incident, one metric slightly off-trend | **GO with watch** | Proceed, add specific metrics to watch list |
| Significant issue: S2 incident unresolved, budget > 80%, gate regression | **CONDITIONAL GO** | Proceed with reduced scope, escalate issue |
| Critical issue: S1 open, budget exhausted, consecutive gate failure | **NO-GO** | Pause pipeline, escalate to human, generate blocker report |

#### Detailed Go/No-Go Rules

```yaml
go_conditions:            # ALL must be true for unconditional GO
  - no_open_s1_incidents: true
  - no_open_s2_incidents_older_than_sla: true
  - monthly_budget_below_pct: 80
  - daily_budget_below_pct: 90
  - no_kill_switches_tripped: true
  - no_consecutive_gate_failures: true
  - at_least_one_packet_ready: true

watch_triggers:           # Any true → GO with watch items
  - budget_between_60_and_80_pct: true
  - s3_incident_open: true
  - metric_off_trend_but_above_threshold: true
  - cost_per_point_elevated: true

conditional_go_triggers:  # Any true → reduced scope
  - s2_incident_unresolved_within_sla: true
  - budget_between_80_and_95_pct: true
  - gate_metric_regressed_but_not_consecutive: true
  - blocked_critical_path_packet: true

no_go_triggers:           # Any true → STOP
  - open_s1_incident: true
  - budget_above_95_pct: true
  - two_consecutive_gate_failures: true
  - all_kill_switches_any_tripped: true
  - zero_packets_executable: true
```

**If NO-GO:** Generate blocker report (A4/04_blocker_report_template.md), notify stakeholders, await human decision before proceeding.

### Step 5: Plan (automated)

Generate the next-7-days execution plan:

1. Take the top-5 prioritized packets from Step 3
2. Check dependency readiness (all `depends_on` packets complete)
3. Assign to execution slots (max `max_parallel_epics` from A0)
4. Estimate compute cost for the week
5. Verify cost fits within remaining monthly budget
6. If cost exceeds budget: apply downgrade rules (A2) or reduce packet count
7. Set specific success criteria for each packet this week
8. Set watch items from Step 4

**Output:** `next_7_days_plan` block in weekly report

### Step 6: Report (automated)

Generate weekly report conforming to `02_weekly_report_schema.yaml`:

1. Validate report against schema
2. Publish to designated channels (dashboard, team channel, email digest)
3. Archive in `weekly-reports/YYYY-WNN.yaml`
4. If NO-GO: attach blocker report

### Step 7: Execute (rest of week)

Between loops the pipeline operates autonomously under:
- Autonomy contract (A0/00_autonomy_contract.md)
- Budget policy (A2/01_compute_budget_policy.md)
- Recovery state machine (A4/01_recovery_state_machine.md)

**Mid-week circuit breakers** (trigger immediate mini-loop):
- S1 incident detected
- Kill-switch tripped
- Budget exhausted
- Consecutive gate failure

If any circuit breaker fires, run Steps 2–4 immediately (don't wait for Monday).

## 4. Roles and Responsibilities

| Role | Weekly Loop Responsibility |
|------|--------------------------|
| Automated system | Steps 1, 2, 3, 5, 6 (fully automated) |
| Tech Lead | Review Step 4 go/no-go decision (5 min unless NO-GO) |
| Budget Owner | Review burn delta if budget warning active (5 min) |
| Architect | Review only if NO-GO or architecture-related blocker |
| Stakeholders | Review only if NO-GO escalation |

## 5. Loop Health Metrics

Track the health of the loop itself:

| Metric | Target | Action if Missed |
|--------|--------|-----------------|
| Loop completion time | < 120 min | Investigate automation bottleneck |
| Report published by | Monday 11:00 UTC | Escalate automation failure |
| Go/no-go decided by | Monday 10:00 UTC | Escalate to Tech Lead |
| Data collection success | 100% sources | Retry failed sources, partial report if needed |
| Report schema validation | 100% valid | Fix schema violation before publishing |

## 6. Amendment Process

Changes to the loop cadence, go/no-go rules, or step sequence follow the
amendment process in A0/00_autonomy_contract.md Section 11.
