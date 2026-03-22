# Runway & Burn Dashboard Specification — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26

---

## 1. Purpose

The Runway & Burn Dashboard provides real-time visibility into compute spend,
projected runway, burn rate, and gate progress. Its goal is to make budget drift
impossible to miss and downgrade decisions data-driven.

## 2. Dashboard Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  THETA-GAMMA v4.1 — RUNWAY & BURN DASHBOARD                       │
├──────────────────────┬─────────────────────────────────────────────┤
│  [A] Budget Gauges   │  [B] Burn Rate Chart                       │
│  Monthly | Daily     │  30-day rolling spend with projection       │
├──────────────────────┼─────────────────────────────────────────────┤
│  [C] Runway Counter  │  [D] Gate Progress vs Cost                 │
│  Days remaining at   │  Accuracy gains plotted against cumulative  │
│  current burn rate   │  spend                                     │
├──────────────────────┼─────────────────────────────────────────────┤
│  [E] Tier Status     │  [F] Kill-Switch Status                    │
│  Current tier + hist │  All 6 kill-switches: armed/tripped        │
├──────────────────────┴─────────────────────────────────────────────┤
│  [G] Alert Feed — live stream of budget events                     │
└────────────────────────────────────────────────────────────────────┘
```

## 3. Panel Specifications

### Panel A: Budget Gauges

**Type:** Dual radial gauge (monthly + daily)

| Element | Specification |
|---------|--------------|
| Monthly gauge | 0–$500 scale, current spend filled, color-coded |
| Daily gauge | 0–$50 scale, current spend filled, color-coded |
| Color zones | Green: 0–60%, Yellow: 60–80%, Orange: 80–95%, Red: 95–100% |
| Numeric overlay | "$X / $500" and "$Y / $50" centered in each gauge |
| Category breakdown | Donut chart inside gauge: training, eval, perf, infra, CI |
| Refresh rate | Every 60 seconds |

### Panel B: Burn Rate Chart

**Type:** Time-series line chart with projection cone

| Element | Specification |
|---------|--------------|
| X-axis | Calendar days (1–30/31 for month) |
| Y-axis | Cumulative spend ($0–$500) |
| Actual line | Solid blue, cumulative spend to date |
| Projected line | Dashed blue, linear extrapolation from 7-day average burn |
| Projection cone | Shaded blue area showing min/max projected spend (based on min/max daily over last 7 days) |
| Threshold lines | Horizontal lines at $400 (80%), $450 (90%), $475 (95%), $500 (100%) |
| Threshold labels | Yellow, orange, red, dark-red respectively |
| Daily burn bars | Semi-transparent bars behind the line showing per-day spend |
| Refresh rate | Every 5 minutes |

### Panel C: Runway Counter

**Type:** Numeric display with trend indicator

| Element | Specification |
|---------|--------------|
| Primary display | "X.X days of runway remaining" (large font) |
| Calculation | (monthly_cap - monthly_spend) / avg_daily_burn_7day |
| Trend arrow | Up/down/flat comparing today's burn to 7-day average |
| Sub-display | "At current rate, budget exhausted by [DATE]" |
| Zero-runway alert | Flashing red when runway < 3 days |
| Tier-adjusted display | Secondary line: "At T2 rate: X.X days | At T3 rate: X.X days" |
| Refresh rate | Every 5 minutes |

### Panel D: Gate Progress vs Cost

**Type:** Dual-axis scatter/line chart

| Element | Specification |
|---------|--------------|
| X-axis | Cumulative spend ($) |
| Y-axis (left) | Cross-modal accuracy (%) |
| Y-axis (right) | Inference latency (ms, inverted) |
| Data points | One per eval run, showing accuracy and cost at that point |
| Gate threshold lines | Horizontal lines at 40% (G1), 60% (G2), 70% (G3) |
| Latency threshold | Horizontal line at 100ms on right axis |
| Efficiency trend | Slope of accuracy-vs-cost (cost-per-point) shown as annotation |
| Color coding | Points colored by tier: T1=blue, T2=yellow, T3=orange |
| Refresh rate | After each eval run |

### Panel E: Tier Status

**Type:** Status card with history timeline

| Element | Specification |
|---------|--------------|
| Current tier | Large badge showing current tier (e.g., "T2-Efficient-ZeRO2") |
| Tier color | T1=green, T2=yellow, T3=orange, T4=red, T5=dark-red |
| Time in tier | "In T2 for 3d 14h" |
| History timeline | Horizontal timeline showing tier changes with timestamps |
| Last downgrade reason | Text showing trigger (e.g., "Monthly spend at 82%") |
| Next downgrade threshold | "Downgrade to T3 at $450 (currently $410)" |
| Refresh rate | On tier change events |

### Panel F: Kill-Switch Status

**Type:** Status grid (6 switches)

| Element | Specification |
|---------|--------------|
| Switches displayed | KS-DAILY, KS-MONTHLY, KS-RUNAWAY, KS-DURATION, KS-REGRESSION, KS-ORPHAN |
| States | Armed (green outline), Tripped (red filled), Cooldown (yellow) |
| Proximity indicator | For each: "X% to threshold" |
| Last trip time | If previously tripped: timestamp of last activation |
| Refresh rate | Every 60 seconds |

### Panel G: Alert Feed

**Type:** Scrolling event log

| Element | Specification |
|---------|--------------|
| Event types | Budget alerts, tier changes, kill-switch events, experiment starts/stops |
| Format | `[TIMESTAMP] [SEVERITY] [EVENT_TYPE] message` |
| Color coding | Info=gray, Warning=yellow, Critical=orange, Kill=red |
| Max visible | Last 50 events, scrollable |
| Filters | Toggleable: budget, tier, kill-switch, experiment |
| Refresh rate | Real-time (push-based) |

## 4. Data Sources

| Panel | Data Source | Query Pattern |
|-------|-----------|---------------|
| A, B, C | Cost event stream (see `01_compute_budget_policy.md` §3.1) | Aggregate by day/category |
| D | Metric store (eval results) + cost events | Join on experiment_id |
| E | Downgrade decision log (see `03_auto_downgrade_rules.md` §7) | Latest entry |
| F | Kill-switch state table | Current state per switch |
| G | Unified event bus | All budget-related events |

## 5. Alert Routing

| Severity | Dashboard | Slack/Chat | Email | PagerDuty |
|----------|-----------|------------|-------|-----------|
| Info | Display only | No | No | No |
| Warning | Display + highlight | Yes | No | No |
| Critical | Display + flash | Yes | Yes | No |
| Kill | Display + full-screen overlay | Yes | Yes | Yes |

## 6. Derived Metrics

The dashboard computes and displays these derived values:

| Metric | Formula | Purpose |
|--------|---------|---------|
| Burn rate (7d avg) | sum(last 7 days spend) / 7 | Runway calculation |
| Burn rate (24h) | sum(last 24h spend) | Daily trend |
| Projected month-end spend | current_spend + (burn_rate_7d * days_remaining) | Forecast |
| Cost-per-point (rolling) | last_experiment_cost / last_accuracy_delta | Efficiency |
| Runway at current tier | (cap - spend) / burn_rate_7d | Days remaining |
| Runway if downgraded | (cap - spend) / estimated_lower_tier_burn | Downgrade benefit |
| Gate ETA | (threshold - current_accuracy) / accuracy_gain_per_day | Days to gate |
| Budget-to-gate fit | runway_days - gate_eta_days | Positive = on track |

## 7. Access & Permissions

| Role | Access Level |
|------|-------------|
| Training pipeline (automated) | Write cost events, read dashboard |
| Team members | Read all panels, acknowledge alerts |
| Budget owner | Read all panels, override kill-switches (T3), amend budget |
| Automated downgrade system | Read panels A/C/F, write tier changes |

## 8. Implementation Notes

- **Backend:** Time-series database (e.g., InfluxDB or TimescaleDB) for cost events
- **Frontend:** Grafana or custom dashboard (React + D3 for custom panels)
- **Alerting:** Grafana alerting or standalone alert manager
- **Refresh:** WebSocket for real-time panels (F, G), polling for others
- **Retention:** 12 months of cost event history, 3 months at full resolution
- **Export:** CSV export of all panels for monthly review process
