# PKT-INFRA-004: Implement Cost Event Emitter

**Priority:** P0
**Domain:** INFRA
**Estimated Effort:** 8h
**Depends On:** PKT-INFRA-001
**Source Artifacts:** A2/01_compute_budget_policy.md

## Objective
Build the cost event emitter that tracks per-action compute cost and publishes to the budget monitoring pipeline.

## Inputs
- Cloud billing API access
- Cost event schema from A2 budget policy
- Time-series database

## Commands
1. Set up time-series database (InfluxDB or TimescaleDB)
2. Implement cost event emitter module
3. Integrate with cloud billing API for real-time cost data
4. Implement cost attribution by experiment_id
5. Add cumulative daily and monthly spend tracking
6. Test with simulated compute events

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Event emission test | `python cost_emitter_test.py --mode emit` | Emit 10 cost events, query DB, all 10 present = pass |
| Attribution test | `python cost_emitter_test.py --mode attribution` | Events tagged with experiment_id are queryable by ID = pass |
| Cumulative test | `python cost_emitter_test.py --mode cumulative` | Daily sum matches individual events = pass |

## Done Definition
Cost events are emitted for all compute actions, stored in time-series DB, queryable by experiment_id.

## Stop Condition
If billing API access cannot be obtained or time-series DB deployment fails after 2 attempts.

## Notes
The cost event emitter is a critical dependency for the kill-switch controller (PKT-INFRA-005), auto-downgrade controller (PKT-INFRA-006), and the runway dashboard (PKT-INFRA-007).
