# PKT-DATA-003: Create Adversarial and OOD Evaluation Sets

**Priority:** P1
**Domain:** DATA
**Estimated Effort:** 1d
**Depends On:** PKT-DATA-002
**Source Artifacts:** A1/03_eval_harness_plan.md, A1/04_failure_signals.md

## Objective
Generate adversarial perturbation datasets and out-of-distribution samples for robustness and safety evaluation.

## Inputs
- Eval datasets from PKT-DATA-002
- Adversarial attack specifications (PGD epsilon=8/255, character perturbation)

## Commands
1. Generate PGD adversarial images (epsilon=8/255) from image eval set (2,000 samples)
2. Generate character-level text perturbations from text eval set (2,000 samples)
3. Curate OOD sample set from external sources (3,000 samples)
4. Combine in-distribution eval samples (3,000) with OOD for AUROC evaluation
5. Create safety eval set (5,000 adversarial + benign prompts)
6. Version and freeze all adversarial/OOD datasets

## Tests
| Test | Command | Expected |
|------|---------|----------|
| Adversarial image test | Verify all perturbations are within epsilon bound | Perturbations are within epsilon=8/255 bound |
| Text perturbation test | Compare perturbed text against originals for semantic difference | Perturbed text is semantically different from original |
| OOD test | Measure distribution distance between OOD samples and training data | OOD samples are from clearly different distribution than training |
| Size test | Count samples in adversarial, OOD, and safety sets | Adversarial=2K, OOD=3K+3K, safety=5K |

## Done Definition
Adversarial, OOD, and safety evaluation datasets are created, verified, versioned, and frozen.

## Stop Condition
If adversarial generation fails to produce valid perturbations or OOD sources are unavailable.

## Notes
PGD epsilon=8/255 is the standard robustness benchmark bound for image perturbations. Character-level perturbations include swap, insert, delete, and homoglyph substitution.
