# Autonomy Contract — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26
**Scope:** Governs all autonomous decisions made during execution of the Theta-Gamma v4.1 project pipeline.

---

## 1. Purpose

This contract defines the boundaries within which automated agents and pipeline stages may operate without requiring human review. It minimizes unnecessary blocking while ensuring irreversible, high-cost, or ambiguous decisions are escalated.

## 2. Core Principles

1. **Bias toward action** — If a decision is reversible and low-cost, proceed with the default choice and log it.
2. **Explicit escalation** — Irreversible or high-cost decisions must be escalated before execution.
3. **Transparency** — Every autonomous decision is recorded in `decision_log.md` with timestamp, class, choice made, and rationale.
4. **Bounded risk** — No single autonomous action may exceed the cost or blast-radius limits defined in `02_operating_limits.yaml`.
5. **Auditability** — All artifacts produced autonomously must be traceable to a decision class in `01_decision_matrix.csv`.

## 3. Decision Authority Tiers

| Tier | Authority | Scope |
|------|-----------|-------|
| T0 — Full Auto | Agent proceeds without asking | Reversible, cost < $5, no external side effects |
| T1 — Log & Proceed | Agent proceeds and logs rationale | Reversible, cost $5–$50, internal side effects only |
| T2 — Notify & Proceed | Agent proceeds, sends async notification | Reversible, cost $50–$200, limited external side effects |
| T3 — Approval Required | Agent pauses, requests human approval | Irreversible OR cost > $200 OR external-facing |
| T4 — Prohibited | Agent must never execute | Security-sensitive, compliance-gated, or destructive |

## 4. Reversibility Classification

A decision is **reversible** if:
- The prior state can be fully restored within 1 hour
- No data has been permanently deleted or transmitted externally
- No third-party system has been irreversibly modified

A decision is **irreversible** if any of the above conditions are not met.

## 5. Autonomous Scope — Permitted Actions (T0–T2)

The following action categories may proceed autonomously under the limits in `02_operating_limits.yaml`:

- File creation, modification, and deletion within the project workspace
- Dependency installation from approved registries (npm, PyPI, crates.io)
- Running test suites and linters
- Creating git branches, commits, and opening draft PRs
- Spinning up ephemeral dev/test compute (within monthly cap)
- Schema migrations on dev/test databases
- Regenerating derived artifacts (docs, diagrams, caches)
- Retrying failed CI jobs (max 2 retries)
- Selecting between equivalent library versions (patch/minor)
- Formatting, linting auto-fix, and import sorting
- Creating or updating configuration files within project scope
- Running benchmarks and performance tests on dev infrastructure
- Archiving stale branches older than 30 days
- Updating lock files after dependency resolution
- Writing and updating documentation from code changes
- Provisioning ephemeral test environments
- Rotating non-production secrets/tokens
- Adding or updating .gitignore entries
- Creating GitHub issue labels and milestones
- Auto-merging dependabot PRs for patch-level updates
- Generating changelogs from commit history

## 6. Escalation-Required Actions (T3)

The following always require human approval:

- **Production deployments** — Any release to production infrastructure
- **Database migrations on production** — Schema changes affecting live data
- **Major dependency upgrades** — Semver major version bumps
- **External API integrations** — Connecting to new third-party services
- **Security configuration changes** — Auth, encryption, access control
- **Cost commitments** — Any action exceeding $200 or creating recurring cost
- **Public-facing content** — Publishing docs, blog posts, announcements
- **Data deletion in staging/production** — Any destructive data operation outside dev
- **Architectural changes** — Fundamental shifts in system design
- **License changes** — Modifying project or dependency licensing
- **User-facing feature flags** — Enabling features for end users
- **Cross-team dependencies** — Actions requiring coordination with other teams
- **Compliance-related changes** — GDPR, SOC2, HIPAA-adjacent modifications

## 7. Prohibited Actions (T4)

The following must never be executed autonomously under any circumstance:

- Force-pushing to main/production branches
- Deleting production data or backups
- Modifying production access controls or IAM policies
- Exposing secrets, tokens, or credentials
- Sending communications to external users/customers
- Accepting or modifying legal agreements
- Disabling security controls, monitoring, or alerting
- Bypassing code review requirements
- Accessing or modifying other teams' resources without authorization

## 8. Logging Requirements

Every autonomous decision must produce a log entry with:

```
timestamp: ISO-8601
decision_class: <from 01_decision_matrix.csv>
tier: T0|T1|T2
choice_made: <default|fallback>
rationale: <one-line explanation>
reversible: yes|no
artifacts_affected: <list of files/resources>
```

## 9. Override Mechanism

A human operator may at any time:
- Elevate any decision class to a higher tier
- Revoke autonomy for a specific decision class
- Pause all autonomous execution
- Roll back any autonomous decision within the reversibility window

Overrides are recorded in `decision_log.md` with `override: true`.

## 10. Review Cadence

- **Daily:** Automated summary of all T1/T2 decisions
- **Weekly:** Human review of decision patterns and anomalies
- **Per-phase:** Full audit of autonomous actions before phase sign-off

## 11. Contract Amendments

This contract may be amended by:
1. Adding an entry to `decision_log.md` with `amendment: true`
2. Updating this file with the change
3. Incrementing the version number
4. Obtaining human sign-off before the next phase begins

---

*Governed by: `01_decision_matrix.csv`, `02_operating_limits.yaml`, `03_risk_appetite_profile.md`*
