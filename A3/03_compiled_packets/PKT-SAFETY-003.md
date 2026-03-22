# PKT-SAFETY-003: Implement Secret Rotation for Dev Environments

**Priority:** P2
**Domain:** SAFETY
**Estimated Effort:** 4h
**Depends On:** PKT-INFRA-001
**Source Artifacts:** A0/01_decision_matrix.csv (DC-037), A0/03_risk_appetite_profile.md

## Objective
Implement automated rotation of non-production secrets and tokens used in dev/test training environments.

## Inputs
- Secret management system
- List of dev secrets (API keys, DB credentials, storage tokens)

## Commands
1. Inventory all dev/test secrets
2. Implement rotation script for each secret type
3. Configure rotation schedule (every 30 days)
4. Ensure rotated secrets propagate to all dependent services
5. Test rotation end-to-end with a non-critical secret
6. Add monitoring for rotation failures

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Rotation test | Rotate a dev API key | New key works = pass |
| Propagation test | Check dependent services after rotation | Rotated secret available in all dependent services within 5 min = pass |
| Old key test | Attempt to use old key after rotation | Old key is invalidated = pass |
| Schedule test | Verify rotation schedule configuration | Rotation fires on configured schedule = pass |

## Done Definition
Dev/test secrets rotate automatically every 30 days. Old keys are invalidated. Rotation failures trigger alerts.

## Stop Condition
If secret management system does not support programmatic rotation.

## Notes
This covers non-production secrets only. Production secret rotation requires a separate packet with stricter change management procedures.
