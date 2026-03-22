# PKT-INFRA-002: Configure Checkpoint Storage and Versioning

**Priority:** P0
**Domain:** INFRA
**Estimated Effort:** 4h
**Depends On:** PKT-INFRA-001
**Source Artifacts:** A0/03_risk_appetite_profile.md, A1/04_failure_signals.md

## Objective
Set up versioned checkpoint storage with integrity validation and automated retention policy.

## Inputs
- Object storage bucket
- Checkpoint format specification
- Retention policy (30 days)

## Commands
1. Create object storage bucket for checkpoints
2. Configure lifecycle policy for 30-day retention
3. Implement checkpoint save with SHA-256 hash validation
4. Implement checkpoint load with integrity verification
5. Test save/load round-trip with dummy model
6. Configure automated cleanup of expired checkpoints

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Round-trip test | `python checkpoint_test.py --mode roundtrip` | Save checkpoint, load it, verify hash match = pass |
| Retention policy test | `python checkpoint_test.py --mode retention` | Expired test checkpoint is cleaned up = pass |
| Corruption detection | `python checkpoint_test.py --mode corrupt` | Tampered checkpoint raises error = pass |

## Done Definition
Checkpoint storage is operational, save/load with integrity checks works, retention policy is active.

## Stop Condition
If storage bucket creation fails or permissions cannot be configured after 2 attempts.

## Notes
SHA-256 hashes are stored alongside each checkpoint to enable integrity verification on load.
