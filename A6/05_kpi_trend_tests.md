# KPI Trend Tests — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-27
**Runs at:** Step 2 (Evaluate) of the weekly control loop, immediately after delta computation.

---

## 1. Purpose

These tests detect metric regressions, stalls, and anomalies automatically. Each test
produces a typed result (`PASS`, `WARN`, `FAIL`) and a **regression flag** that routes
to a specific action. The weekly report schema's `risk_delta` and `go_no_go` sections
consume these flags directly to enforce automated action routing.

---

## 2. Regression Flags

Every test emits a flag using this enum. The flag determines action routing in Step 4.

| Flag | Meaning | Routes To |
|------|---------|-----------|
| `NONE` | Test passed, no action needed | No action |
| `WATCH` | Minor concern, monitor next week | `go_no_go.watch_triggers_active` |
| `INVESTIGATE` | Needs root cause analysis | Mid-week check-in (RF-2) |
| `ROLLBACK` | Regression confirmed, roll back | Roll-back rules (RB-1 through RB-6) |
| `HALT` | Critical safety or infra issue | Immediate NO-GO + S1 incident |

---

## 3. Test Definitions

### 3.1 Week-over-Week Regression Test

**Applies to:** All primary gate metrics (M-CM-001, M-CM-002, M-CM-003, M-CM-004, M-LAT-001, M-LAT-002, M-LAT-003, M-THR-001, M-SAF-001, M-ROB-001, M-ROB-002, M-ROB-003)

**Logic:**

```
delta = metric_current - metric_previous

For higher-is-better metrics (M-CM-*, M-ROB-001, M-ROB-002, M-THR-001):
  IF delta < -5pp                       → FAIL, flag = ROLLBACK
  IF delta < -2pp                       → WARN, flag = INVESTIGATE
  IF delta < 0                          → WARN, flag = WATCH
  IF delta >= 0                         → PASS, flag = NONE

For lower-is-better metrics (M-LAT-*, M-SAF-001, M-ROB-003):
  IF delta > +5pp (or +50ms for latency) → FAIL, flag = ROLLBACK
  IF delta > +2pp (or +20ms for latency) → WARN, flag = INVESTIGATE
  IF delta > 0                            → WARN, flag = WATCH
  IF delta <= 0                           → PASS, flag = NONE
```

**Regression confirmation:** When flag = `ROLLBACK`, re-run evaluation once. If regression
persists on re-evaluation, confirm the flag. If not reproduced, downgrade to `INVESTIGATE`.

---

### 3.2 Four-Week Rolling Trend Test

**Applies to:** All primary gate metrics with >= 4 weeks of history.

**Logic:**

```
trend = linear regression slope over last 4 data points (weeks)

For higher-is-better metrics:
  IF slope < -1.0pp per week (sustained decline)  → WARN, flag = INVESTIGATE
  IF slope < -0.5pp per week                       → WARN, flag = WATCH
  IF slope >= -0.5pp per week                      → PASS, flag = NONE

For lower-is-better metrics:
  IF slope > +1.0pp per week (sustained increase)  → WARN, flag = INVESTIGATE
  IF slope > +0.5pp per week                       → WARN, flag = WATCH
  IF slope <= +0.5pp per week                      → PASS, flag = NONE
```

**Exemption:** Test skipped if < 4 weeks of data available. Logged as `SKIP` with
note "insufficient history."

---

### 3.3 Stall Detection Test

**Applies to:** All primary gate metrics that have not yet passed their gate threshold.

**Logic:**

```
gap_to_threshold = current_value - threshold (for higher-is-better)
                 = threshold - current_value (for lower-is-better)
weeks_at_level = consecutive weeks where |delta| < 1pp

IF weeks_at_level >= 3 AND gap_to_threshold > 5pp  → FAIL, flag = INVESTIGATE
IF weeks_at_level >= 3 AND gap_to_threshold <= 5pp  → WARN, flag = WATCH
IF weeks_at_level >= 2                              → WARN, flag = WATCH
IF weeks_at_level < 2                               → PASS, flag = NONE
```

**Action routing for INVESTIGATE:** Trigger diagnostic sprint. Add diagnostic packet
to next week's plan at P0 priority via auto-prioritization (risk_reduction_score = 100).

---

### 3.4 Safety Violation Escalation Test

**Applies to:** M-SAF-001 only.

**Logic:**

```
IF M-SAF-001 > 1.0% (10x threshold)     → FAIL, flag = HALT
IF M-SAF-001 > 0.5% (5x threshold)      → FAIL, flag = ROLLBACK
IF M-SAF-001 > 0.1% (above threshold)   → WARN, flag = INVESTIGATE
IF M-SAF-001 <= 0.1%                     → PASS, flag = NONE
```

**Action routing for HALT:** Immediately trigger RB-4 (Safety Roll-Back), S1 incident,
pipeline halt. No automated restart.

---

### 3.5 Budget Anomaly Test

**Applies to:** `burn_delta.daily_avg_burn_usd` and `burn_delta.weekly_spend_usd`.

**Logic:**

```
avg_4wk = 4-week average of daily_avg_burn_usd
stddev_4wk = 4-week standard deviation of daily_avg_burn_usd

IF daily_avg_burn_usd > avg_4wk + 3 * stddev_4wk   → FAIL, flag = INVESTIGATE
IF daily_avg_burn_usd > avg_4wk + 2 * stddev_4wk   → WARN, flag = WATCH
IF weekly_spend_usd > 1.5 * weekly_spend_previous   → WARN, flag = WATCH
ELSE                                                 → PASS, flag = NONE
```

**Kill-switch proximity check:** If any kill-switch `proximity_pct > 80`, override
flag to `INVESTIGATE` regardless of statistical test result.

---

### 3.6 Gate Progress Velocity Test

**Applies to:** Current active gate's primary metric.

**Logic:**

```
gap = gap_to_threshold (from milestone_delta)
velocity = average improvement per week over last 4 weeks
estimated_weeks = gap / velocity (if velocity > 0)

IF velocity <= 0 AND gap > 0             → FAIL, flag = INVESTIGATE
IF estimated_weeks > 8                    → WARN, flag = INVESTIGATE
IF estimated_weeks > 4                    → WARN, flag = WATCH
IF estimated_weeks <= 4 OR gate passed    → PASS, flag = NONE
```

**Action routing for INVESTIGATE:** Trigger architecture review. If consecutive gate
failure, apply RB-2 (Gate Roll-Back).

---

### 3.7 Latency Spike Detection Test

**Applies to:** M-LAT-001 (p50), M-LAT-002 (p95), M-LAT-003 (p99).

**Logic:**

```
IF p99 > 500ms                            → FAIL, flag = ROLLBACK
IF p95 > 200ms (2x threshold)             → FAIL, flag = INVESTIGATE
IF p95 > 120ms (1.2x threshold)           → WARN, flag = WATCH
IF p50 > 75ms (1.5x threshold)            → WARN, flag = WATCH
ELSE                                      → PASS, flag = NONE
```

**Action routing for ROLLBACK:** Revert to `known_good_latency` checkpoint.

---

### 3.8 Incident Accumulation Test

**Applies to:** `risk_delta.incidents_open`, `risk_delta.s1_open`, `risk_delta.s2_open`.

**Logic:**

```
IF s1_open > 0                            → FAIL, flag = HALT
IF s2_open > 2                            → FAIL, flag = INVESTIGATE
IF incidents_open > 5                     → WARN, flag = INVESTIGATE
IF incidents_open > 3                     → WARN, flag = WATCH
ELSE                                      → PASS, flag = NONE
```

---

## 4. Test Execution Summary Format

Each weekly report MUST include a trend test summary in the `risk_delta` section:

```yaml
trend_tests:
  - test_id: WOW-001
    test_name: "Week-over-week regression"
    metric: M-CM-001
    result: PASS
    flag: NONE
    value_current: 72.3
    value_previous: 71.8
    delta: +0.5
    note: "Improving"

  - test_id: STALL-001
    test_name: "Stall detection"
    metric: M-CM-002
    result: WARN
    flag: WATCH
    weeks_at_level: 2
    gap_to_threshold: 3.2
    note: "Approaching stall, monitoring"
```

---

## 5. Action Routing Matrix

Summary of how flags route to pipeline actions:

| Flag | Go/No-Go Impact | Roll Direction | Auto-Prioritization Effect | Human Needed |
|------|-----------------|----------------|---------------------------|-------------|
| `NONE` | No impact | RF-1 (standard) | No change | No |
| `WATCH` | Added to `watch_triggers_active` | RF-2 (cautious) | No change | No |
| `INVESTIGATE` | Added to `conditional_go_triggers` | RF-3 (partial) or mid-week check | Diagnostic packet boosted to P0 | No (auto) |
| `ROLLBACK` | Added to `no_go_triggers` | RB-1 or RB-5 | Related recovery packets to top | Review required |
| `HALT` | Forced NO-GO | RB-4 or RB-6 | All non-essential packets paused | Yes — safety review |

---

## 6. Test Dependencies

| Test | Requires | Minimum Data |
|------|----------|-------------|
| 3.1 Week-over-week | Current + previous week values | 2 weeks |
| 3.2 Four-week trend | 4 consecutive weeks | 4 weeks |
| 3.3 Stall detection | 2+ consecutive weeks + threshold | 2 weeks |
| 3.4 Safety escalation | Current M-SAF-001 value | 1 week |
| 3.5 Budget anomaly | 4-week burn history | 4 weeks (stat), 1 week (KS check) |
| 3.6 Gate velocity | 4-week metric history + threshold | 4 weeks |
| 3.7 Latency spike | Current latency values | 1 week |
| 3.8 Incident accumulation | Current incident counts | 1 week |
