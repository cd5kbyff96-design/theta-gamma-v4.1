# Autonomy Failure Modes — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-27

---

## 1. Purpose

This document enumerates failure modes that can arise when autonomous agents operate under the autonomy contract. Each mode includes detection signals, potential impact, and prescribed mitigation.

---

## 2. Failure Mode Catalog

### FM-01: Runaway Compute Spend

**Description:** Agent spawns parallel workloads or long-running processes that exceed cost guardrails before alerts fire.

| Attribute | Value |
|-----------|-------|
| Likelihood | Medium |
| Impact | High — monthly budget exhausted prematurely |
| Detection | Cost alert at 80% threshold; daily spend exceeds `daily_compute_cap_usd` |
| Mitigation | Hard circuit-breaker at 100% monthly cap; daily cap enforced in `02_operating_limits.yaml` |
| Recovery | Terminate ephemeral resources; review spending log |

### FM-02: Silent Decision Drift

**Description:** Agent makes many individually-acceptable T0/T1 decisions that cumulatively shift the project in an unintended direction without any single decision triggering escalation.

| Attribute | Value |
|-----------|-------|
| Likelihood | Medium |
| Impact | Medium — technical debt accumulation or architectural drift |
| Detection | Weekly human review of decision log; anomaly detection on decision frequency |
| Mitigation | Daily automated digest of T1/T2 decisions; weekly pattern review |
| Recovery | Revert affected changes via git history; recalibrate decision classes |

### FM-03: Cascading Retry Loops

**Description:** Transient failures trigger retries, which fail in the same way, consuming resources and delaying pipeline progress.

| Attribute | Value |
|-----------|-------|
| Likelihood | Medium |
| Impact | Low-Medium — wasted CI time and compute |
| Detection | `max_ci_retries_per_job` exceeded; DC-062 escalation trigger |
| Mitigation | Exponential backoff with max 3 retries; permanent error detection halts retries |
| Recovery | Log failure; halt affected pipeline stage; notify operator |

### FM-04: Stale Lock / Orphaned Resource

**Description:** Agent provisions ephemeral environments or acquires locks that are not properly released due to crash or timeout.

| Attribute | Value |
|-----------|-------|
| Likelihood | Medium |
| Impact | Medium — blocked pipelines or resource waste |
| Detection | Ephemeral env lifetime exceeds `ephemeral_env_max_lifetime_hours`; lock age monitoring |
| Mitigation | Hard lifetime cap on ephemeral envs (8h); automatic teardown of idle environments (4h) |
| Recovery | Force-release orphaned locks; teardown stale environments |

### FM-05: Incorrect Reversibility Assessment

**Description:** Agent classifies a decision as reversible when it is actually irreversible, bypassing required escalation.

| Attribute | Value |
|-----------|-------|
| Likelihood | Low |
| Impact | High — irreversible action taken without approval |
| Detection | Post-hoc audit reveals decision was not actually reversible |
| Mitigation | Conservative reversibility definition in contract §4; explicit irreversible registry (`06_irreversible_decision_registry.csv`) |
| Recovery | Incident response; update decision matrix to reclassify; contract amendment |

### FM-06: Escalation Fatigue

**Description:** Too many T3 escalations cause human operator to rubber-stamp approvals, defeating the purpose of the escalation gate.

| Attribute | Value |
|-----------|-------|
| Likelihood | Medium |
| Impact | High — approvals without genuine review |
| Detection | Approval response time drops below 30 seconds consistently; approval rate exceeds 98% |
| Mitigation | Batch non-urgent escalations; reduce unnecessary T3 classifications over time; provide clear context in escalation requests |
| Recovery | Review and downgrade safe T3 decisions to T2; improve escalation request quality |

### FM-07: Dependency Supply Chain Compromise

**Description:** Agent auto-installs a compromised patch/minor dependency update that passes automated security scans.

| Attribute | Value |
|-----------|-------|
| Likelihood | Low |
| Impact | Critical — malicious code in project |
| Detection | Daily security scans; anomalous behavior in tests; unexpected network calls |
| Mitigation | Only install from approved registries; lockfile pinning; license audit on every change; dependabot auto-merge limited to patch-level |
| Recovery | Revert dependency; rotate any exposed secrets; audit for data exfiltration |

### FM-08: Test Suite False Confidence

**Description:** Agent adds tests that pass but do not meaningfully validate behavior, inflating coverage metrics without catching regressions.

| Attribute | Value |
|-----------|-------|
| Likelihood | Medium |
| Impact | Medium — regressions reach staging/production |
| Detection | Mutation testing scores diverge from line coverage; regressions found post-merge |
| Mitigation | Human review of test changes for security-critical paths (DC-021); mutation testing as supplementary gate |
| Recovery | Add targeted regression tests; tighten test review policy for critical paths |

### FM-09: Partial Pipeline Failure with Implicit Continue

**Description:** A non-critical pipeline stage fails but the agent continues execution, producing artifacts that depend on the failed stage's output.

| Attribute | Value |
|-----------|-------|
| Likelihood | Medium |
| Impact | Medium-High — downstream artifacts are invalid |
| Detection | DC-063 triggers when error is in critical path; artifact validation checks |
| Mitigation | Explicit dependency graph between pipeline stages; critical path errors halt pipeline |
| Recovery | Invalidate and regenerate dependent artifacts; re-run from failed stage |

### FM-10: Notification Storm

**Description:** Rapid autonomous decisions generate excessive internal notifications, overwhelming operators and burying important alerts.

| Attribute | Value |
|-----------|-------|
| Likelihood | Low |
| Impact | Medium — operator misses critical alert amid noise |
| Detection | Notification rate exceeds `max_internal_notifications_per_hour` |
| Mitigation | Rate limiting (20/hour); batched daily digest for T0/T1; priority channel for T3+ |
| Recovery | Silence non-critical notifications; review notification thresholds |

### FM-11: Secret Exposure in Logs or Artifacts

**Description:** Agent inadvertently logs, commits, or includes secrets in generated artifacts, docs, or error messages.

| Attribute | Value |
|-----------|-------|
| Likelihood | Low |
| Impact | Critical — credential compromise |
| Detection | Secret scanning in CI; pre-commit hooks; audit of generated artifacts |
| Mitigation | Secret exposure is T4 prohibited; automated secret scanning; .gitignore enforcement |
| Recovery | Rotate exposed secrets immediately; scrub git history; incident response |

### FM-12: Contract Interpretation Ambiguity

**Description:** Agent encounters a decision that does not clearly map to any existing decision class, and either misclassifies it or invents an ad-hoc classification.

| Attribute | Value |
|-----------|-------|
| Likelihood | Medium |
| Impact | Medium — action taken outside contract bounds |
| Detection | Decision log entry references unknown or improvised class |
| Mitigation | Default to highest applicable tier when ambiguous; log ambiguity for review; 70 decision classes provide broad coverage |
| Recovery | Classify and add the new decision class to the matrix; contract amendment if needed |

---

## 3. Failure Mode Severity Matrix

| ID | Failure Mode | Likelihood | Impact | Risk Level |
|----|-------------|------------|--------|------------|
| FM-01 | Runaway Compute Spend | Medium | High | High |
| FM-02 | Silent Decision Drift | Medium | Medium | Medium |
| FM-03 | Cascading Retry Loops | Medium | Low-Medium | Medium |
| FM-04 | Stale Lock / Orphaned Resource | Medium | Medium | Medium |
| FM-05 | Incorrect Reversibility Assessment | Low | High | Medium |
| FM-06 | Escalation Fatigue | Medium | High | High |
| FM-07 | Dependency Supply Chain Compromise | Low | Critical | High |
| FM-08 | Test Suite False Confidence | Medium | Medium | Medium |
| FM-09 | Partial Pipeline Failure | Medium | Medium-High | Medium-High |
| FM-10 | Notification Storm | Low | Medium | Low-Medium |
| FM-11 | Secret Exposure | Low | Critical | High |
| FM-12 | Contract Interpretation Ambiguity | Medium | Medium | Medium |

---

## 4. Monitoring and Review

- **Real-time:** Cost circuit-breakers, notification rate limits, retry counters
- **Daily:** Decision frequency analysis, cost tracking, security scan results
- **Weekly:** Decision drift review, escalation quality assessment, orphaned resource scan
- **Per-phase:** Full failure mode review and update of this document

---

## 5. Unresolved / Watch Items

None currently. All failure modes have defined detection and mitigation strategies.
