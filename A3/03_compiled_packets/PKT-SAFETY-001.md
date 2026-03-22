# PKT-SAFETY-001: Deploy Safety Classifier

**Priority:** P1
**Domain:** SAFETY
**Estimated Effort:** 1d
**Depends On:** PKT-INFRA-001
**Source Artifacts:** A1/01_metric_dictionary.yaml (M-SAF-001), A1/02_gate_definitions.yaml (G3)

## Objective
Deploy the safety classifier used to measure M-SAF-001 (safety violation rate) and flag policy-violating model outputs.

## Inputs
- Safety classifier model (pre-trained)
- Inference infrastructure
- Safety policy definition

## Commands
1. Deploy safety classifier model on inference endpoint
2. Define safety policy categories (harm, bias, toxicity, PII)
3. Implement classification API (input text -> violation flag + category)
4. Benchmark classifier accuracy on labeled safety dataset
5. Configure threshold for violation flagging
6. Test with known-safe and known-violating inputs

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Known-safe test | Submit 100 benign inputs | 0 violations produced = pass |
| Known-violating test | Submit 100 known-harmful inputs | Flagged at > 95% recall = pass |
| Latency test | Measure classification time per input | Classification < 50ms per input = pass |
| API test | Send request to classification endpoint | Endpoint responds with correct JSON schema = pass |

## Done Definition
Safety classifier is deployed, API is functional, achieves > 95% recall on known-violating inputs, latency < 50ms.

## Stop Condition
If pre-trained safety classifier is unavailable or recall on known-violating inputs < 80%.

## Notes
The safety classifier is a critical dependency for Gate G3 evaluation. The 95% recall target is a minimum; higher recall is preferred even at the cost of some precision.
