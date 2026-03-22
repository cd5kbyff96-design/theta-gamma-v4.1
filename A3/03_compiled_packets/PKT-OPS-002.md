# PKT-OPS-002: Create Budget Review Runbook

**Priority:** P2
**Domain:** OPS
**Estimated Effort:** 4h
**Depends On:** PKT-INFRA-007, PKT-BUDGET-001
**Source Artifacts:** A2/01_compute_budget_policy.md

## Objective
Write the operational runbook for monthly budget reviews, kill-switch override procedures, and budget amendment requests.

## Inputs
- Budget policy
- Dashboard spec
- Kill-switch definitions

## Commands
1. Document monthly budget review process (5-report checklist)
2. Document kill-switch override procedure (requires T3 approval)
3. Document budget amendment request process
4. Document cost-per-point review and optimization triggers
5. Document emergency budget procedures
6. Create review checklist template

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Completeness test | Audit runbook against kill-switch definitions | All 6 kill-switches have override procedures = pass |
| Template test | Validate review checklist template | Review checklist template has all 5 required reports = pass |
| Approval test | Review override procedures for approval requirements | Every override explicitly requires T3 human approval = pass |

## Done Definition
Budget review runbook is complete with monthly process, kill-switch overrides, amendment requests, and review templates.

## Stop Condition
If budget policy is still being amended and procedures would be immediately outdated.

## Notes
Kill-switch overrides are the most sensitive procedures in this runbook. Every override must have a documented justification and T3 sign-off before execution.
