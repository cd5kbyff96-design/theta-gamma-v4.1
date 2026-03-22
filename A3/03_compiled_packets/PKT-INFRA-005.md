# PKT-INFRA-005: Implement Kill-Switch Controller

**Priority:** P0
**Domain:** INFRA
**Estimated Effort:** 1d
**Depends On:** PKT-INFRA-004
**Source Artifacts:** A2/01_compute_budget_policy.md, A2/03_auto_downgrade_rules.md

## Objective
Build the kill-switch controller that monitors spend thresholds and terminates jobs when limits are breached.

## Inputs
- Cost event stream from PKT-INFRA-004
- Kill-switch thresholds from A2 budget policy
- Job management API

## Commands
1. Implement KS-DAILY monitor ($50/day threshold)
2. Implement KS-MONTHLY monitor ($500/month threshold)
3. Implement KS-RUNAWAY monitor ($50/experiment threshold)
4. Implement KS-DURATION monitor (24h runtime threshold)
5. Implement KS-REGRESSION monitor (3x avg cost-per-point)
6. Implement KS-ORPHAN monitor ($20 orphan compute/day)
7. Wire each switch to job termination API
8. Add switch state logging and notification hooks
9. Test each switch in isolation with simulated spend

## Tests
| Test | Command | Expected |
|------|---------|----------|
| KS-DAILY test | `python killswitch_test.py --switch daily` | Simulate $51 daily spend, verify jobs terminated = pass |
| KS-RUNAWAY test | `python killswitch_test.py --switch runaway` | Simulate $55 single experiment, verify that experiment terminated = pass |
| State persistence test | `python killswitch_test.py --mode persistence` | Trip switch, restart controller, switch remains tripped = pass |
| Notification test | `python killswitch_test.py --mode notify` | Tripped switch sends notification = pass |

## Done Definition
All 6 kill-switches are operational, tested, and connected to job termination. Switch states persist across restarts.

## Stop Condition
If job management API is unavailable or kill-switch cannot reliably terminate jobs after testing.

## Notes
Kill-switches KS-DAILY, KS-MONTHLY, KS-RUNAWAY, KS-DURATION, KS-REGRESSION, and KS-ORPHAN each have independent thresholds and operate concurrently.
