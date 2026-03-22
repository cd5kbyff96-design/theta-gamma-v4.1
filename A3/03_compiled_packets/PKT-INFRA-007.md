# PKT-INFRA-007: Deploy Runway and Burn Dashboard

**Priority:** P1
**Domain:** INFRA
**Estimated Effort:** 1d
**Depends On:** PKT-INFRA-004, PKT-INFRA-005, PKT-INFRA-006
**Source Artifacts:** A2/04_runway_burn_dashboard_spec.md

## Objective
Deploy the 7-panel Runway & Burn Dashboard with real-time budget gauges, burn rate charts, and kill-switch status.

## Inputs
- Dashboard spec from A2
- Time-series DB from PKT-INFRA-004
- Kill-switch state from PKT-INFRA-005
- Tier state from PKT-INFRA-006

## Commands
1. Deploy Grafana instance or custom dashboard frontend
2. Build Panel A: Budget gauges (monthly + daily)
3. Build Panel B: Burn rate chart with projection cone
4. Build Panel C: Runway counter with tier-adjusted estimates
5. Build Panel D: Gate progress vs cost scatter plot
6. Build Panel E: Tier status card with history
7. Build Panel F: Kill-switch status grid
8. Build Panel G: Alert feed
9. Configure alert routing (Slack, email)
10. Load test dashboard with 30 days simulated data

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Panel render test | `python dashboard_test.py --mode render` | All 7 panels render without error = pass |
| Data freshness test | `python dashboard_test.py --mode freshness` | Panels update within 60s of new cost event = pass |
| Alert routing test | `python dashboard_test.py --mode alerts` | Critical alert appears in Slack within 30s = pass |
| Load test | `python dashboard_test.py --mode load` | Dashboard handles 30 days of data without lag = pass |

## Done Definition
Dashboard is deployed, all 7 panels render correctly, alerts route to configured channels, performs well with realistic data volume.

## Stop Condition
If dashboard framework cannot connect to time-series DB or more than 2 panels fail to render after debugging.

## Notes
The 7 panels are: (A) Budget gauges, (B) Burn rate chart, (C) Runway counter, (D) Gate progress vs cost, (E) Tier status card, (F) Kill-switch status grid, (G) Alert feed.
