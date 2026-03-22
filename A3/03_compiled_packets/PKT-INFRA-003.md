# PKT-INFRA-003: Set Up Experiment Tracking and Logging

**Priority:** P1
**Domain:** INFRA
**Estimated Effort:** 4h
**Depends On:** PKT-INFRA-001
**Source Artifacts:** A0/00_autonomy_contract.md, A1/01_metric_dictionary.yaml

## Objective
Deploy experiment tracking system (MLflow or W&B) to log all training metrics, hyperparameters, and artifacts.

## Inputs
- Tracking server infrastructure
- Metric dictionary from A1
- Experiment ID schema

## Commands
1. Deploy experiment tracking server
2. Configure metric logging for all 27 metrics in metric dictionary
3. Set up experiment ID auto-generation
4. Configure hyperparameter logging
5. Set up artifact logging for checkpoints and eval results
6. Test end-to-end logging with dummy training run

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Metric logging test | `python tracking_test.py --mode metrics` | Log 5 metrics and retrieve them via API = pass |
| Experiment ID test | `python tracking_test.py --mode experiment_id` | Two runs get unique IDs = pass |
| Artifact test | `python tracking_test.py --mode artifacts` | Upload and download artifact matches = pass |

## Done Definition
Tracking server is running, metrics log correctly, experiments get unique IDs, artifacts are retrievable.

## Stop Condition
If tracking server cannot be deployed after 2 attempts or licensing blocks usage.

## Notes
All 27 metrics from the A1 metric dictionary must be registered in the tracking system before training begins.
