# PKT-BUDGET-002: Implement Pre-Launch Cost Estimator

**Priority:** P1
**Domain:** BUDGET
**Estimated Effort:** 4h
**Depends On:** PKT-INFRA-004
**Source Artifacts:** A2/01_compute_budget_policy.md

## Objective
Build the pre-launch cost estimator that calculates expected cost before any training run starts and blocks launch if budget is insufficient.

## Inputs
- GPU pricing rates
- Experiment configuration (GPU type, count, estimated hours)
- Current budget state

## Commands
1. Implement cost estimator (gpu_type_rate * gpu_count * estimated_hours)
2. Check estimated cost against remaining daily and monthly budget
3. Check estimated cost against single-action cap ($50)
4. Block launch if any budget check fails
5. Log estimate and budget check result
6. Test with various configurations and budget states

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Estimate test | Configure 4xA100 for 8h at known rate | Correct cost estimate is produced = pass |
| Budget block test | Submit estimate exceeding remaining budget | Launch is blocked = pass |
| Cap test | Submit estimate > $50 | Launch is blocked without human approval = pass |
| Pass test | Submit estimate within all limits | Launch is allowed = pass |

## Done Definition
Every training run must pass pre-launch cost estimate before starting. Budget-exceeding launches are blocked.

## Stop Condition
If GPU pricing data is unavailable or stale (> 7 days old).

## Notes
Single-action cap of $50 is a hard limit requiring human override. Daily and monthly budgets are soft limits that can be adjusted through the budget amendment process.
