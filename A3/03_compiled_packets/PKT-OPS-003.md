# PKT-OPS-003: Configure CI Integration for Eval Harness

**Priority:** P1
**Domain:** OPS
**Estimated Effort:** 8h
**Depends On:** PKT-EVAL-006
**Source Artifacts:** A1/03_eval_harness_plan.md

## Objective
Integrate the eval orchestrator into the CI/CD pipeline with triggers for training completion, PR creation, nightly regression, and pre-deployment.

## Inputs
- Eval orchestrator from PKT-EVAL-006
- CI system (GitHub Actions or similar)
- Training pipeline hooks

## Commands
1. Create CI job for full eval (triggered on training run completion)
2. Create CI job for quick eval (triggered on PR creation/update)
3. Create CI job for perf-only eval (triggered on model export)
4. Create CI job for nightly regression eval
5. Create CI job for pre-deploy full eval
6. Configure eval result artifacts and reporting
7. Test each CI trigger independently

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Full eval trigger test | Complete a training run | Full eval job is triggered = pass |
| Quick eval trigger test | Create a PR | Quick eval job is triggered = pass |
| Nightly test | Verify nightly schedule configuration | Nightly schedule triggers regression eval = pass |
| Artifact test | Run eval job and check artifacts | Eval results are stored as CI artifacts = pass |

## Done Definition
All 5 CI evaluation triggers are configured and functional. Eval results are stored as artifacts and reported.

## Stop Condition
If CI system cannot trigger jobs based on training pipeline events.

## Notes
Quick eval on PR should complete within 15 minutes to avoid blocking developer workflow. Full eval may take longer but should not exceed 2 hours.
