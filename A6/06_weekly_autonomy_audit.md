# Weekly Autonomy Audit — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-27
**Runs at:** Step 6 (Report) of the weekly control loop, as an addendum to the weekly report.

---

## 1. Purpose

This audit verifies that the autonomous execution system is operating within its
contracted boundaries each week. It checks whether decisions were correctly tiered,
budgets were respected, escalations were timely, and the next-7-day plan was
generated solely from ranked priorities (not ad-hoc or overridden silently).

The audit is a mandatory attachment to every weekly report.

---

## 2. Audit Template

Complete one audit per weekly loop iteration.

### 2.1 Audit Header

| Field | Value |
|-------|-------|
| **Audit ID** | AUD-[YYYY]-W[NN] |
| **Week** | W[NN], [YYYY] |
| **Report Reference** | WR-[YYYY]-W[NN] |
| **Auditor** | [automated / Tech Lead name] |
| **Audit Date** | [YYYY-MM-DD] |

---

### 2.2 Autonomy Boundary Checks

| # | Check | Pass/Fail | Evidence | Notes |
|---|-------|-----------|----------|-------|
| A1 | All autonomous decisions this week were T1 or T2 tier (no unauthorized T3/T4 decisions) | [ ] PASS / [ ] FAIL | Decision log entries for week W[NN] | |
| A2 | All T3 decisions had human approval BEFORE execution | [ ] PASS / [ ] FAIL | Approval records in decision log | |
| A3 | No T4 (out of scope) actions were attempted | [ ] PASS / [ ] FAIL | Decision log — filter for T4 | |
| A4 | Operating limits (A0/02_operating_limits.yaml) were not breached | [ ] PASS / [ ] FAIL | Max concurrent jobs, max parallel epics, API rate limits | |
| A5 | Budget policy (A2/01_compute_budget_policy.md) was followed | [ ] PASS / [ ] FAIL | Spend vs budget, tier compliance | |

**Section Status:** [ ] ALL PASS / [ ] FAILURES — requires remediation

---

### 2.3 Decision Quality Checks

| # | Check | Pass/Fail | Evidence | Notes |
|---|-------|-----------|----------|-------|
| D1 | Go/no-go decision was consistent with conditions evaluated | [ ] PASS / [ ] FAIL | `go_no_go` block in WR-[YYYY]-W[NN] | |
| D2 | No-go decisions (if any) generated a blocker report within 30 min | [ ] PASS / [ ] FAIL / [ ] N/A | Blocker report timestamp vs no-go timestamp | |
| D3 | Conditional-go decisions scoped work reduction correctly | [ ] PASS / [ ] FAIL / [ ] N/A | Affected packets paused/reduced per RF-3 rules | |
| D4 | Watch items from previous week were reviewed this week | [ ] PASS / [ ] FAIL / [ ] N/A | Previous week's watch_items vs this week's evaluation | |
| D5 | Roll-back decisions (if any) followed the correct RB rule | [ ] PASS / [ ] FAIL / [ ] N/A | Rollback log vs 04_rollforward_rollback_rules.md | |

**Section Status:** [ ] ALL PASS / [ ] FAILURES — requires remediation

---

### 2.4 Plan Generation Integrity Checks

These checks verify the addon gate: **next-7-day plan is generated only from ranked priorities.**

| # | Check | Pass/Fail | Evidence | Notes |
|---|-------|-----------|----------|-------|
| P1 | All packets in `next_7_days_plan.planned_packets` appear in the top-N of the ranked backlog (from Step 3) | [ ] PASS / [ ] FAIL | Ranked backlog output vs plan | |
| P2 | No packet was added to the plan that was NOT in the ranked output | [ ] PASS / [ ] FAIL | Diff between ranked list and plan | |
| P3 | Packets are ordered in the plan by their rank (highest first) | [ ] PASS / [ ] FAIL | Rank order in plan matches scoring order | |
| P4 | A human override of the plan (if any) is logged with rationale | [ ] PASS / [ ] FAIL / [ ] N/A | `go_no_go.human_override` field + `override_reason` | |
| P5 | Estimated cost for planned packets fits within remaining budget | [ ] PASS / [ ] FAIL | `next_7_days_plan.cost_fits_budget` = true | |
| P6 | At least one P0 packet is included if any P0 was eligible | [ ] PASS / [ ] FAIL / [ ] N/A | Ranked backlog P0 entries vs plan | |
| P7 | Max 5 packets in plan (maxItems constraint from schema) | [ ] PASS / [ ] FAIL | `planned_packets` array length <= 5 | |

**Section Status:** [ ] ALL PASS / [ ] FAILURES — requires remediation

---

### 2.5 Escalation Timeliness Checks

| # | Check | Pass/Fail | Evidence | Notes |
|---|-------|-----------|----------|-------|
| E1 | All S1 incidents were triaged within 15 minutes | [ ] PASS / [ ] FAIL / [ ] N/A | Incident timestamps: opened vs triage_started | |
| E2 | All S1 incidents were escalated per recovery state machine SLAs | [ ] PASS / [ ] FAIL / [ ] N/A | A4/01_recovery_state_machine.md SLA vs actual | |
| E3 | All S2 incidents were resolved within SLA (24h) | [ ] PASS / [ ] FAIL / [ ] N/A | Incident resolution timestamps | |
| E4 | Blocker reports were filed for all blocker-age > 48h | [ ] PASS / [ ] FAIL / [ ] N/A | Blocker age in weekly report vs blocker report log | |
| E5 | Third-failure escalation was triggered where applicable | [ ] PASS / [ ] FAIL / [ ] N/A | A4/02_retry_policy.yaml third-failure rule compliance | |

**Section Status:** [ ] ALL PASS / [ ] FAILURES — requires remediation

---

### 2.6 KPI Trend Test Compliance

| # | Check | Pass/Fail | Evidence | Notes |
|---|-------|-----------|----------|-------|
| K1 | All applicable trend tests from 05_kpi_trend_tests.md were executed | [ ] PASS / [ ] FAIL | Trend test summary in risk_delta | |
| K2 | All regression flags were routed to the correct action | [ ] PASS / [ ] FAIL | Flag values vs action routing matrix (§5 of 05_kpi_trend_tests.md) | |
| K3 | ROLLBACK flags triggered re-evaluation confirmation | [ ] PASS / [ ] FAIL / [ ] N/A | Re-eval log for ROLLBACK-flagged metrics | |
| K4 | HALT flags triggered immediate pipeline stop | [ ] PASS / [ ] FAIL / [ ] N/A | Pipeline state change timestamp vs HALT flag timestamp | |
| K5 | INVESTIGATE flags added diagnostic packets at P0 | [ ] PASS / [ ] FAIL / [ ] N/A | Auto-prioritization output for flagged metrics | |

**Section Status:** [ ] ALL PASS / [ ] FAILURES — requires remediation

---

## 3. Audit Summary

| Section | Checks | Passed | Failed | N/A | Status |
|---------|--------|--------|--------|-----|--------|
| 2.2 Autonomy Boundaries | 5 | [___] | [___] | [___] | [ ] PASS |
| 2.3 Decision Quality | 5 | [___] | [___] | [___] | [ ] PASS |
| 2.4 Plan Generation Integrity | 7 | [___] | [___] | [___] | [ ] PASS |
| 2.5 Escalation Timeliness | 5 | [___] | [___] | [___] | [ ] PASS |
| 2.6 KPI Trend Test Compliance | 5 | [___] | [___] | [___] | [ ] PASS |
| **Total** | **27** | **[___]** | **[___]** | **[___]** | |

**Overall Audit Result:** [ ] CLEAN / [ ] FINDINGS (see remediation below)

---

## 4. Findings and Remediation

_Complete only if any check failed._

| Finding # | Check ID | Description | Severity | Remediation | Owner | Deadline |
|-----------|----------|-------------|----------|-------------|-------|----------|
| F-001 | [check ID] | [what went wrong] | [Critical/High/Medium] | [corrective action] | [role] | [date] |

---

## 5. Audit Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| Automated Auditor | (system) | [auto-filled] | [ ] Generated |
| Tech Lead | [name] | [date] | [ ] Reviewed |

---

## 6. Retention and Compliance

- Audits are stored alongside weekly reports in `weekly-reports/audits/AUD-YYYY-WNN.md`
- Retention period: 12 months minimum
- Audits with findings trigger follow-up in the next week's loop (Step 2 verifies remediation)
- Three consecutive weeks with unresolved findings escalate to Architect review
