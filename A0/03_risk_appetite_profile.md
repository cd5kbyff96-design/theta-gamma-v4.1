# Risk Appetite Profile — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26

---

## 1. Overall Risk Posture

**Moderate-Conservative.** The project favors velocity on reversible, low-cost actions while maintaining strict guardrails on anything irreversible, external-facing, or cost-significant. The guiding heuristic: *move fast on things you can undo; pause on things you cannot.*

## 2. Risk Dimensions

### 2.1 Financial Risk

| Attribute | Value |
|-----------|-------|
| Appetite | Low |
| Monthly cap | $500 |
| Single-action cap | $50 without escalation |
| Escalation threshold | $200 cumulative or $50 single |
| Tolerance for waste | Up to 10% of monthly cap on failed experiments |

**Rationale:** Compute costs can compound quickly with parallel workloads. Conservative caps prevent runaway spending while allowing meaningful experimentation.

### 2.2 Data Integrity Risk

| Attribute | Value |
|-----------|-------|
| Appetite | Very Low |
| Dev data | Freely mutable, treat as disposable |
| Staging data | Mutable with logging, destructive ops need approval |
| Production data | Immutable without explicit human approval |
| Backup policy | Automated daily, 30-day retention |

**Rationale:** Data loss is the hardest class of error to recover from. Dev environments are explicitly sacrificial to enable speed, but staging and production carry increasing protection.

### 2.3 Security Risk

| Attribute | Value |
|-----------|-------|
| Appetite | Zero tolerance for known vulnerabilities |
| Patching SLA (critical) | Within 24 hours |
| Patching SLA (high) | Within 7 days |
| Secret management | Automated rotation in dev; manual in prod |
| Access control changes | Always require human approval |

**Rationale:** Security incidents have outsized blast radius. The cost of being cautious is low; the cost of a breach is high.

### 2.4 Availability / Operational Risk

| Attribute | Value |
|-----------|-------|
| Appetite | Moderate in dev, Low in staging, Very Low in production |
| Dev downtime tolerance | Unlimited — ephemeral envs are disposable |
| Staging downtime tolerance | Up to 2 hours per incident |
| Production downtime tolerance | Zero planned, < 5 min unplanned |
| Rollback requirement | All deployments must have automated rollback |

**Rationale:** Dev should never block on availability concerns. Production availability is sacrosanct.

### 2.5 Velocity / Delivery Risk

| Attribute | Value |
|-----------|-------|
| Appetite | High — prefer shipping over perfection |
| Acceptable test coverage | 80% line coverage for new code |
| Draft PR policy | Open freely, no approval needed |
| Merge policy | Requires passing CI + human review |
| Feature flag usage | Required for all user-facing changes |

**Rationale:** The autonomy contract exists to maximize delivery speed. Slowing down to chase 100% coverage or perfect code costs more than shipping and iterating.

### 2.6 Technical Debt Risk

| Attribute | Value |
|-----------|-------|
| Appetite | Moderate — accept tactical debt, prevent structural debt |
| Auto-fix policy | Apply safe linting/formatting fixes freely |
| Refactoring threshold | Refactor when touching a file, not as standalone work |
| Dependency staleness | Patch/minor updates automated; major updates planned |

**Rationale:** Some technical debt is the natural cost of velocity. The contract mitigates this by automating routine maintenance (formatting, patching, lockfile updates) while escalating structural changes.

### 2.7 Compliance / Legal Risk

| Attribute | Value |
|-----------|-------|
| Appetite | Zero tolerance |
| License auditing | Automated on every dependency change |
| Copyleft dependencies | Escalate immediately |
| Data handling changes | Always require human review |
| Agreement acceptance | Prohibited without human approval |

**Rationale:** Compliance violations can have existential consequences. No amount of velocity justifies compliance risk.

## 3. Irreversible Decision Inventory

The following decisions are explicitly classified as **irreversible** and always require T3 (human approval) or T4 (prohibited):

| Decision | Tier | Why Irreversible |
|----------|------|------------------|
| Production deployment | T3 | User-facing state change; rollback is not instant |
| Production data deletion | T4 | Data cannot be reconstructed |
| Production schema migration | T3 | May cause data loss or downtime |
| Main branch force-push | T4 | Rewrites shared history |
| External API integration | T3 | Creates third-party dependency |
| License change | T3 | Legal implications |
| Access control modification | T4 | Security boundary change |
| External notification/communication | T4 | Cannot be unsent |
| Production secret rotation | T3 | May break live services |
| Backup deletion | T4 | Eliminates recovery option |
| Container push to production registry | T3 | Consumed by live infrastructure |
| Infrastructure scaling in production | T3 | Cost and availability implications |
| Feature flag toggle in production | T3 | User-facing behavior change |
| Security configuration change | T3 | Attack surface modification |

## 4. Risk Mitigation Strategies

1. **Ephemeral environments** — All dev work happens in disposable environments to contain blast radius
2. **Automated rollback** — Every deployment must have a one-click rollback mechanism
3. **Progressive delivery** — Feature flags gate all user-facing changes
4. **Cost circuit-breakers** — Automated alerts at 80% of caps; hard stops at 100%
5. **Audit logging** — Every autonomous decision is logged for post-hoc review
6. **Daily summaries** — Automated digest of all T1/T2 decisions for human awareness

## 5. Review and Amendment

This profile is reviewed:
- **Per-phase** — Before each new phase begins
- **On-incident** — After any T3/T4 escalation or unexpected outcome
- **Monthly** — As part of operating limits review

Amendments follow the process in `00_autonomy_contract.md` Section 11.
