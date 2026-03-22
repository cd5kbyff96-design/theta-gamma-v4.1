# Packet Quality Rubric — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-27
**References:** `02_task_packet_schema.yaml`, `05_packet_verification_matrix.csv`

---

## 1. Purpose

This rubric defines how to assess the quality of compiled task packets. Every packet
is scored against these criteria during compilation and before execution. Packets
that fail any mandatory criterion must be revised before entering the execution queue.

---

## 2. Scoring Dimensions

### 2.1 Completeness (Mandatory — all must pass)

| Criterion | Pass | Fail |
|-----------|------|------|
| **Objective present** | Single clear sentence stating what the packet achieves | Missing, vague, or multi-objective |
| **Inputs listed** | All prerequisites, data, and artifacts enumerated | Missing inputs or implicit dependencies |
| **Commands specified** | Ordered list of concrete, executable actions | Abstract instructions like "set up the thing" |
| **Tests defined** | At least 1 test with command and expected outcome | No tests, or tests without expected outcomes |
| **Done definition present** | Unambiguous statement verifiable by a third party | Missing or subjective ("works well") |
| **Stop condition present** | Explicit condition to abort without completing | Missing or always-continue ("keep trying") |
| **Verify command exists** | Entry in `05_packet_verification_matrix.csv` | No verification matrix entry |
| **Rollback command exists** | Entry in `05_packet_verification_matrix.csv` | No rollback command |

**Rule:** Any packet missing a mandatory criterion is rejected and returned for revision.

### 2.2 Specificity (Scored 1–3)

| Score | Description |
|-------|-------------|
| 3 — Executable | Commands can be run as-is with parameter substitution only. Tests have concrete thresholds. |
| 2 — Translatable | Commands need minor interpretation (e.g., choosing a specific config value). Tests have measurable criteria but may need parameter tuning. |
| 1 — Abstract | Commands require significant design decisions before execution. Tests are qualitative. |

**Minimum:** Score 2 for P0 packets, Score 1 for P1+.

### 2.3 Isolation (Scored 1–3)

| Score | Description |
|-------|-------------|
| 3 — Fully isolated | Packet can be executed independently given its declared inputs. No hidden state dependencies. |
| 2 — Loosely coupled | Packet has 1–2 implicit assumptions about system state beyond declared inputs. |
| 1 — Tightly coupled | Packet relies on undeclared system state or runtime conditions. |

**Minimum:** Score 2 for all packets.

### 2.4 Reversibility (Scored 1–3)

| Score | Description |
|-------|-------------|
| 3 — Fully reversible | Rollback command restores system to pre-execution state completely. |
| 2 — Mostly reversible | Rollback restores primary artifacts; some side effects (logs, metrics) persist. |
| 1 — Partially reversible | Rollback mitigates damage but cannot fully restore prior state. |

**Minimum:** Score 2 for P0/P1 packets, Score 1 for P2+.

### 2.5 Testability (Scored 1–3)

| Score | Description |
|-------|-------------|
| 3 — Automated | All tests can run unattended and return pass/fail programmatically. |
| 2 — Semi-automated | Tests run programmatically but may need human interpretation of results. |
| 1 — Manual | Tests require human judgment to determine pass/fail. |

**Minimum:** Score 2 for P0 packets, Score 1 for P1+.

---

## 3. Quality Tiers

| Tier | Criteria | Action |
|------|----------|--------|
| **Gold** | All mandatory pass + all dimensions score 3 | Ready for autonomous execution |
| **Silver** | All mandatory pass + all dimensions score >= 2 | Ready for supervised execution |
| **Bronze** | All mandatory pass + no dimension below 1 | Requires review before execution |
| **Reject** | Any mandatory criterion fails OR any dimension scores 0 | Must be revised before queueing |

---

## 4. Domain-Specific Quality Rules

### 4.1 INFRA Packets

- Must include infrastructure-as-code references or specific cloud commands
- Rollback must include resource deprovisioning (prevent cost leaks)
- Tests must verify both provisioning and connectivity

### 4.2 DATA Packets

- Must specify dataset hashes for any eval data referenced
- Must include contamination check if creating eval datasets
- Rollback must not delete source data — only derived artifacts

### 4.3 TRAIN Packets

- Must reference the specific training tier from `A2/02_training_tier_matrix.csv`
- Must include cost budget for the training run
- Stop condition must reference kill-switch thresholds
- Tests must include both metric thresholds and cost checks

### 4.4 EVAL Packets

- Must reference metric IDs from `A1/01_metric_dictionary.yaml`
- Must specify seed for reproducibility
- Tests must include both pass and fail scenarios

### 4.5 BUDGET Packets

- Must reference thresholds from `A2/05_budget_guardrails.yaml`
- Must include mock/simulation testing
- Rollback must not affect cost tracking data integrity

### 4.6 SAFETY Packets

- Must include both positive (detect real issue) and negative (no false positive) test cases
- Rollback must not leave security gaps
- Must reference relevant failure signals from `A1/04_failure_signals.md`

### 4.7 OPS Packets

- Documentation packets must specify minimum content length
- CI/CD packets must include workflow validation
- Runbooks must be testable via dry-run

---

## 5. Review Process

### 5.1 Pre-Execution Review

Before any packet enters the execution queue:

1. **Schema validation:** Automated check against `02_task_packet_schema.yaml`
2. **Rubric scoring:** Score all 4 non-mandatory dimensions
3. **Tier assignment:** Assign Gold/Silver/Bronze based on scores
4. **Verification check:** Confirm entry exists in `05_packet_verification_matrix.csv`
5. **Dependency check:** Confirm all `depends_on` packets exist and are not circular

### 5.2 Post-Execution Review

After packet execution:

1. **Run verify_command** from `05_packet_verification_matrix.csv`
2. **Compare against expected_signal**
3. **If FAIL:** Run rollback_command, log failure, return packet for re-execution or revision
4. **If PASS:** Mark packet as complete in `04_packet_index.csv`

---

## 6. Rubric Application Summary

| Priority | Completeness | Min Specificity | Min Isolation | Min Reversibility | Min Testability |
|----------|-------------|----------------|---------------|-------------------|----------------|
| P0 | All mandatory | 2 | 2 | 2 | 2 |
| P1 | All mandatory | 1 | 2 | 2 | 1 |
| P2 | All mandatory | 1 | 2 | 1 | 1 |
| P3 | All mandatory | 1 | 2 | 1 | 1 |
