# Decision Latency SLO — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-27

---

## 1. Purpose

This document defines Service Level Objectives (SLOs) for decision latency —
the time between when a decision is surfaced and when it is resolved (by human
response or by default action). The SLOs ensure the pipeline is never blocked
longer than the allowed window for any decision type.

---

## 2. SLO Definitions

### 2.1 End-to-End Decision Latency

| SLO ID | Decision Type | Target Latency | Max Latency | Measurement |
|--------|--------------|----------------|-------------|-------------|
| SLO-D-001 | Weekly packet (routine) | ≤ 24 hours | 32.5 hours (hard deadline) | Packet delivery → response received |
| SLO-D-002 | S1 circuit breaker | ≤ 2 hours | 4 hours (hard deadline) | Notification → response received |
| SLO-D-003 | S2 circuit breaker | ≤ 4 hours | 8 hours (hard deadline) | Notification → response received |
| SLO-D-004 | Budget kill-switch | ≤ 2 hours | 4 hours (hard deadline) | Notification → response received |
| SLO-D-005 | Gate transition (T1/T2) | ≤ 24 hours | 32.5 hours (via weekly packet) | Included in weekly packet cycle |
| SLO-D-006 | Gate transition (T3) | ≤ 24 hours | 48 hours (hard deadline) | Notification → response received |
| SLO-D-007 | Default action execution | ≤ 1 minute | 5 minutes | Deadline passed → default applied |

### 2.2 System-Side Latency (generation and delivery)

| SLO ID | Component | Target | Max | Measurement |
|--------|-----------|--------|-----|-------------|
| SLO-S-001 | Decision collection | ≤ 5 minutes | 15 minutes | Weekly loop end → decisions compiled |
| SLO-S-002 | Impact × urgency scoring | ≤ 2 minutes | 5 minutes | Collection end → scoring complete |
| SLO-S-003 | Packet generation | ≤ 3 minutes | 10 minutes | Scoring end → packet rendered |
| SLO-S-004 | Packet delivery | ≤ 5 minutes | 10 minutes | Rendered → delivered to all channels |
| SLO-S-005 | Response parsing | ≤ 1 minute | 5 minutes | Response received → parsed and validated |
| SLO-S-006 | Decision application | ≤ 5 minutes | 15 minutes | Parsed → pipeline config updated |

### 2.3 Total System Decision Latency Budget

```
Total latency = generation + delivery + human_response + parsing + application

Target:  10 min  +  5 min  +  24 hours  +  1 min  +  5 min  = ~24 hours 21 min
Maximum: 30 min  + 10 min  +  32.5 hours + 5 min  + 15 min  = ~33 hours 0 min
```

---

## 3. SLO Compliance Targets

| Window | Target Compliance | Measurement |
|--------|-------------------|-------------|
| Rolling 4 weeks | ≥ 95% of decisions resolved within target latency | Count of on-time / total decisions |
| Rolling 4 weeks | 100% of decisions resolved within max latency | No decision exceeds hard deadline |
| Rolling 12 weeks | ≥ 90% of weekly packets responded to by human (not defaulted) | Response rate |
| Per incident | 100% of S1 decisions resolved within 4h max | Per-incident tracking |

---

## 4. Latency Measurement Points

```
T0: Decision identified (pending decision created)
T1: Decision scored (impact × urgency computed)
T2: Packet generated (decision included in packet or mid-week alert)
T3: Packet delivered (all channels notified)
T4: Human response received (or deadline reached)
T5: Response parsed and validated
T6: Decision applied to pipeline

Latencies measured:
  System latency:  T0 → T3  (SLO-S-001 through SLO-S-004)
  Human latency:   T3 → T4  (SLO-D-001 through SLO-D-006)
  Execution:       T4 → T6  (SLO-S-005 + SLO-S-006)
  End-to-end:      T0 → T6  (total)
```

---

## 5. Alert Rules

| Alert | Condition | Action |
|-------|-----------|--------|
| Human response approaching deadline | 2 hours remaining, no response | Send urgent reminder (all channels) |
| Human response at deadline | 0 hours remaining, no response | Apply default, send notice |
| System generation slow | SLO-S-001 through SLO-S-004 > max | Page on-call engineer, investigate automation |
| Response parsing failure | SLO-S-005 > 5 minutes or parse error | Page on-call, manual intervention |
| Decision application failure | SLO-S-006 > 15 minutes | Page on-call, hold pipeline |
| Compliance dropping | 4-week compliance < 95% | Review in next weekly report, flag in audit |
| Consecutive defaults | 3+ consecutive packets fully defaulted | Escalate to stakeholder, consider autonomy tier upgrade |

---

## 6. Reporting

Decision latency metrics are included in:

1. **Weekly report** — `go_no_go.decided_at` timestamp vs packet delivery time
2. **Weekly autonomy audit** (A6/06) — §2.5 Escalation Timeliness Checks
3. **Monthly summary** — 4-week compliance rates for all SLOs
4. **Decision packet** — Previous week's response latency noted in header

---

## 7. SLO Exceptions

| Exception | Condition | Modified SLO |
|-----------|-----------|-------------|
| T3 gate transitions (G3→Pilot, G4→Prod) | Blocking decisions, no default | No max latency — blocks until response. Escalation at 48h. |
| Holiday periods | Known holiday calendar | Deadlines shift to next business day per §3.1 of deadline policy |
| Declared emergency | Stakeholder declares emergency | All non-S1 deadlines extend +24h; S1 deadlines unchanged |
