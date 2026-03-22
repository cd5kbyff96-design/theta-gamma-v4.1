# PKT-OPS-001: Create Training Runbook

**Priority:** P1
**Domain:** OPS
**Estimated Effort:** 4h
**Depends On:** PKT-TRAIN-001, PKT-TRAIN-002, PKT-EVAL-005
**Source Artifacts:** A0/00_autonomy_contract.md, A1/04_failure_signals.md, A2/03_auto_downgrade_rules.md

## Objective
Write an operational runbook covering standard training procedures, failure response, tier transitions, and gate evaluation workflows.

## Inputs
- Training loop documentation
- Failure signals
- Downgrade rules
- Gate definitions

## Commands
1. Document standard training start procedure
2. Document checkpoint and resume procedure
3. Document failure response for each S1/S2 signal
4. Document manual tier upgrade/downgrade procedure
5. Document gate evaluation and sign-off workflow
6. Document rollback procedure for consecutive gate failures
7. Review runbook with checklist validation

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Completeness test | Audit runbook against failure signals | Runbook covers all 8 S1 failure signals = pass |
| Procedure test | Review each procedure for clarity | Each procedure has numbered steps that can be followed without ambiguity = pass |
| Gate coverage test | Audit runbook against gate definitions | All 4 gates G1-G4 have documented evaluation procedure = pass |

## Done Definition
Runbook is complete, covers all failure responses, tier transitions, and gate workflows. Each procedure has clear numbered steps.

## Stop Condition
If dependencies (training loops, eval harness) are not yet documented enough to write meaningful procedures.

## Notes
The runbook should be written for an operator who is familiar with the project but may not have been involved in the design. Procedures should be executable without additional context.
