# Task Packet Compiler Specification — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26

---

## 1. Purpose

The compiler transforms planning artifacts (autonomy contracts, gate definitions,
budget policies, downgrade rules) into discrete, executable task packets. Each packet
is a self-contained unit of work with clear inputs, commands, acceptance tests, and
stop conditions — enabling autonomous or human execution without ambiguity.

## 2. Input Sources

| Source | Phase | Artifacts Used |
|--------|-------|---------------|
| Autonomy contract | A0 | `00_autonomy_contract.md`, `01_decision_matrix.csv` |
| Operating limits | A0 | `02_operating_limits.yaml` |
| Risk appetite | A0 | `03_risk_appetite_profile.md` |
| Metric dictionary | A1 | `01_metric_dictionary.yaml` |
| Gate definitions | A1 | `02_gate_definitions.yaml` |
| Eval harness plan | A1 | `03_eval_harness_plan.md` |
| Failure signals | A1 | `04_failure_signals.md` |
| Budget policy | A2 | `01_compute_budget_policy.md` |
| Training tiers | A2 | `02_training_tier_matrix.csv` |
| Downgrade rules | A2 | `03_auto_downgrade_rules.md` |
| Dashboard spec | A2 | `04_runway_burn_dashboard_spec.md` |

## 3. Compilation Rules

### 3.1 Decomposition Principles

1. **One objective per packet** — each packet achieves exactly one measurable outcome
2. **Dependency-explicit** — every packet lists its prerequisite packets by ID
3. **Self-contained context** — a packet contains everything needed to execute without reading other packets
4. **Testable completion** — every packet has at least one acceptance test that can be evaluated programmatically or by inspection
5. **Bounded scope** — no packet should take more than 2 days of effort at the expected tier

### 3.2 Packet ID Convention

```
PKT-{domain}-{sequence:3d}
```

Domains:
- `INFRA` — Infrastructure, environment, and tooling setup
- `DATA` — Data pipeline, datasets, and data quality
- `TRAIN` — Training configuration, execution, and optimization
- `EVAL` — Evaluation harness, metrics, and gate evaluation
- `BUDGET` — Budget tracking, alerts, dashboards, and cost governance
- `SAFETY` — Safety, robustness, and security evaluations
- `OPS` — Operational procedures, runbooks, and automation

### 3.3 Priority Assignment

| Priority | Criteria |
|----------|----------|
| P0 — Critical path | Blocks gate progression; no workaround |
| P1 — High | Required for gate but has partial workaround |
| P2 — Medium | Improves efficiency or observability |
| P3 — Low | Nice-to-have; can be deferred |

### 3.4 Dependency Resolution

- Packets form a DAG (directed acyclic graph)
- Circular dependencies are compilation errors
- A packet cannot start until all `depends_on` packets are in `done` state
- Packets with no dependencies can execute in parallel

## 4. Output Format

Each packet is a standalone Markdown file following `02_task_packet_schema.yaml`.
All packets are indexed in `04_packet_index.csv`.

## 5. Compilation Process

```
1. Parse all input artifacts into structured data
2. Identify discrete work units from each artifact
3. Assign packet IDs following domain convention
4. Resolve dependencies between packets
5. Assign priorities based on gate-blocking analysis
6. Generate packet Markdown files
7. Build packet index CSV
8. Validate: all packets have tests, stop conditions, no missing deps
```

## 6. Validation Rules

- Every packet MUST have a non-empty `done_definition`
- Every packet MUST have at least one entry in `tests`
- Every packet MUST have a non-empty `stop_condition`
- Every `depends_on` reference MUST point to an existing packet ID
- No two packets may have the same ID
- Every gate (G1–G4) must be covered by at least one packet
- Every kill-switch must be implemented by at least one packet
