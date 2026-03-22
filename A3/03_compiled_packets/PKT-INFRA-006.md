# PKT-INFRA-006: Implement Auto-Downgrade Controller

**Priority:** P1
**Domain:** INFRA
**Estimated Effort:** 1d
**Depends On:** PKT-INFRA-004, PKT-INFRA-005
**Source Artifacts:** A2/03_auto_downgrade_rules.md

## Objective
Build the automated tier downgrade/upgrade controller that transitions training between T1-T5 based on budget pressure.

## Inputs
- Cost event stream
- Kill-switch state
- Current tier state
- Downgrade rules D1-D4 and upgrade rules U1-U3

## Commands
1. Implement tier state machine (T1 through T5)
2. Implement D1 rule: T1->T2 at 80% monthly cap
3. Implement D2 rule: T2->T3 at 90% cap
4. Implement D3 rule: T3->T4 at 95% cap
5. Implement D4 rule: T4->T5 at 100% cap
6. Implement U1 rule: T2->T1 when spend < 50%
7. Implement U2 rule: T3->T2 when spend < 60%
8. Implement rollback guards (accuracy drop detection)
9. Add downgrade decision logging
10. Test full cascade with simulated spend ramp

## Tests
| Test | Command | Expected |
|------|---------|----------|
| D1 trigger test | `python downgrade_test.py --rule D1` | Simulate 80% cap, verify tier changes T1->T2 = pass |
| Full cascade test | `python downgrade_test.py --mode cascade` | Ramp spend 0->100%, verify T1->T2->T3->T4->T5 transitions = pass |
| Rollback guard test | `python downgrade_test.py --mode rollback` | Simulate 6pp accuracy drop after downgrade, verify revert = pass |
| Upgrade test | `python downgrade_test.py --rule U1` | Simulate spend drop to 45%, verify T2->T1 = pass |

## Done Definition
Downgrade controller handles all D1-D4 and U1-U3 transitions, rollback guards work, all transitions logged.

## Stop Condition
If tier transitions cannot be validated due to missing training infrastructure or state machine has unreachable states.

## Notes
Rollback guards prevent downgrades that cause accuracy drops exceeding 6 percentage points relative to the pre-downgrade baseline.
