# Auto-Prioritization Rules — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26

---

## 1. Purpose

These rules deterministically rank the packet backlog each week during Step 3 of
the weekly control loop. The output is a scored, sorted list of packets with the
top 5 selected for execution in the coming week.

## 2. Scoring Formula

Each packet receives a composite score:

```
score = (W_gate × gate_blocking_score)
      + (W_deadline × deadline_pressure_score)
      + (W_dep × dependency_readiness_score)
      + (W_priority × priority_score)
      + (W_cost × cost_efficiency_score)
      + (W_risk × risk_reduction_score)
```

### 2.1 Weights

| Weight | Value | Rationale |
|--------|-------|-----------|
| W_gate | 0.30 | Gate-blocking work is highest priority |
| W_deadline | 0.20 | Time-sensitive work needs attention |
| W_dep | 0.20 | Only executable work should be planned |
| W_priority | 0.15 | Respect original priority assignment |
| W_cost | 0.10 | Prefer cost-efficient work when otherwise tied |
| W_risk | 0.05 | Prefer work that reduces open risk |

### 2.2 Component Scores (each normalized 0–100)

#### Gate Blocking Score

| Condition | Score |
|-----------|-------|
| Packet is on critical path AND blocks the current active gate | 100 |
| Packet is on critical path for the next gate | 75 |
| Packet supports current gate but is not blocking | 50 |
| Packet supports a future gate (not next) | 25 |
| Packet does not affect any gate | 10 |

#### Deadline Pressure Score

| Condition | Score |
|-----------|-------|
| Packet is overdue (past expected completion date) | 100 |
| Packet due within 3 days | 80 |
| Packet due within 7 days | 60 |
| Packet due within 14 days | 40 |
| Packet due within 30 days | 20 |
| No deadline or > 30 days | 5 |

#### Dependency Readiness Score

| Condition | Score |
|-----------|-------|
| All dependencies complete, packet is immediately executable | 100 |
| All dependencies complete except one, which is in-progress and > 80% done | 60 |
| Dependencies partially complete (> 50%) | 30 |
| Dependencies mostly incomplete (< 50%) | 10 |
| Dependencies not started | 0 |

Note: Packets with readiness score 0 are excluded from the top-5 selection since
they cannot be started this week.

#### Priority Score

| Priority | Score |
|----------|-------|
| P0 — Critical path | 100 |
| P1 — High | 70 |
| P2 — Medium | 40 |
| P3 — Low | 10 |

#### Cost Efficiency Score

| Condition | Score |
|-----------|-------|
| Packet estimated cost <= $10 | 100 |
| Packet estimated cost $10–$25 | 75 |
| Packet estimated cost $25–$50 | 50 |
| Packet estimated cost > $50 | 25 |
| Packet is documentation/runbook (zero cost) | 100 |

#### Risk Reduction Score

| Condition | Score |
|-----------|-------|
| Packet directly resolves an open S1 incident | 100 |
| Packet directly resolves an open S2 incident | 75 |
| Packet implements a kill-switch or safety control | 60 |
| Packet adds monitoring or observability | 40 |
| Packet does not reduce active risk | 0 |

## 3. Selection Rules

1. **Score all pending and in-progress packets** using the formula above
2. **Exclude** packets with `dependency_readiness_score = 0`
3. **Sort** by composite score descending
4. **Select top 5** (or fewer if the backlog is smaller)
5. **Constraint check:**
   - Total estimated cost of selected packets must fit within remaining weekly budget
   - No more than `max_parallel_epics` (3) packets in concurrent execution
   - At least 1 P0 packet must be included if any P0 is ready
6. **If constraint violated:** drop lowest-scoring packet and re-check

## 4. Tie-Breaking

If two packets have identical composite scores:
1. Prefer the packet with higher `gate_blocking_score`
2. If still tied, prefer the packet with lower estimated cost
3. If still tied, prefer the packet with the lower sequence number (earlier in backlog)

## 5. Dynamic Re-Prioritization Triggers

These events force an immediate re-prioritization outside the weekly loop:

| Trigger | Action |
|---------|--------|
| S1 incident opens | Re-score all packets, boost risk_reduction_score for related packets |
| Kill-switch trips | Pause all non-essential packets, prioritize budget/infra packets |
| Gate passes | Immediately re-score: new gate's blocking packets get +100 gate_blocking_score |
| Consecutive gate failure | Boost related diagnostic/rollback packets to top of queue |
| Budget tier downgrade | Re-score cost_efficiency; expensive packets may drop out of top 5 |
| New blocker report | Boost resolution packets to top |

## 6. Deferral Rules

Packets are deferred (removed from this week's consideration) if:

| Condition | Action |
|-----------|--------|
| Packet has been blocked > 14 days with no resolution path | Defer to backlog, log as stale |
| Packet's gate target has already passed | Deprioritize to P3 unless still needed |
| Packet cost exceeds remaining monthly budget at any tier | Defer to next budget month |
| All dependencies are > 2 weeks from completion | Defer until dependencies are closer |

## 7. Output Format

The prioritized list is emitted as part of `next_7_days_plan` in the weekly report:

```yaml
prioritized_backlog:
  - rank: 1
    packet_id: PKT-TRAIN-005
    title: Execute Baseline Training Run (G1 Target)
    composite_score: 87.5
    scores:
      gate_blocking: 100
      deadline_pressure: 60
      dependency_readiness: 100
      priority: 100
      cost_efficiency: 50
      risk_reduction: 0
    rationale: "Critical path, blocks G1, all deps met, P0"
    selected: true

  - rank: 2
    ...
```
