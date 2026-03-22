# PKT-SAFETY-002: Implement Training Stability Monitors

**Priority:** P1
**Domain:** SAFETY
**Estimated Effort:** 8h
**Depends On:** PKT-TRAIN-001
**Source Artifacts:** A1/04_failure_signals.md

## Objective
Implement real-time training stability monitors for loss divergence, gradient explosion/vanishing, NaN detection, and overfitting as defined in the failure signals document.

## Inputs
- Training loop from PKT-TRAIN-001
- Failure signal definitions from A1

## Commands
1. Implement loss divergence detector (> 50% increase over 100 steps = S1)
2. Implement gradient explosion detector (norm > 100x EMA = S1)
3. Implement gradient vanishing detector (norm < 1e-7 for 500 steps = S2)
4. Implement NaN/Inf loss detector (S1 immediate)
5. Implement overfitting gap monitor (gap > 0.5 nats and increasing = S2)
6. Implement validation loss plateau detector (no improvement for 10 epochs = S2)
7. Wire all detectors into training loop callbacks
8. Test each detector with synthetic failure scenarios

## Tests
| Test | Command | Expected |
|------|---------|----------|
| NaN test | Inject NaN loss into training loop | S1 alert fires and training halts = pass |
| Gradient explosion test | Inject 1000x gradient into training loop | Detection triggers = pass |
| Plateau test | Simulate flat validation loss for 10 epochs | Alert triggers = pass |
| Normal training test | Run healthy training for 1000 steps | No false alarms produced = pass |

## Done Definition
All 6 failure signal detectors are active during training. Each fires at correct severity. False alarm rate is zero on healthy training.

## Stop Condition
If detectors produce > 1% false positive rate on healthy training runs that cannot be tuned away.

## Notes
S1 signals require immediate training halt. S2 signals are warnings that escalate to S1 if not addressed. NaN/Inf detection must have zero tolerance with no debounce.
