# PKT-DATA-002: Create Held-Out Evaluation Datasets

**Priority:** P0
**Domain:** DATA
**Estimated Effort:** 1d
**Depends On:** PKT-DATA-001
**Source Artifacts:** A1/03_eval_harness_plan.md

## Objective
Create versioned, immutable evaluation datasets for all eval suites (cross-modal, per-modality, safety, adversarial) with verified isolation from training data.

## Inputs
- Full dataset from PKT-DATA-001
- Eval harness dataset size requirements (10K cross-modal, 5K per-modality, 5K safety)

## Commands
1. Split full dataset: 90% training, 10% evaluation
2. Create cross-modal eval set (10,000 samples)
3. Create per-modality eval sets (5,000 each for text, image, audio)
4. Create cross-modal consistency paired set (5,000 pairs)
5. Create retrieval eval query set (5,000 queries)
6. Version each dataset with content hash
7. Run dedup check against training split
8. Freeze eval datasets (make immutable)

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Size test | Count samples in cross-modal eval set | Cross-modal eval = 10K samples |
| Isolation test | Run dedup checker between eval and training sets | Zero overlap between eval and training sets |
| Immutability test | Attempt to modify frozen dataset | Modification attempt raises error |
| Balance test | Compute modality distribution across eval set | Modality distribution within 5% of uniform |

## Done Definition
All evaluation datasets are created, versioned, verified isolated from training data, and frozen.

## Stop Condition
If dedup check reveals more than 1% contamination that cannot be resolved by re-splitting.

## Notes
Eval dataset immutability is critical for reproducible benchmarking across Theta-Gamma v4.1 experiment iterations.
