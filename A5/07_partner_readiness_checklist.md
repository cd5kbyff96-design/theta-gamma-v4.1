# Partner Readiness Checklist — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-27
**Usage:** Complete this checklist before onboarding a pilot partner. All items in a section must pass before proceeding to the next phase with that partner.

---

## How to Use This Checklist

1. Fill one checklist per pilot partner
2. Work through sections sequentially (Pre-Engagement → Technical → Operational → Go-Live)
3. Each item is pass/fail — mark the box when verified
4. Record the verifier and date for audit trail
5. A section is complete only when ALL items in that section are checked
6. Any failed item becomes a blocker — log it in `04_blocker_report_template.md`

---

## Partner Information

| Field | Value |
|-------|-------|
| **Partner Organization** | [PARTNER_ORGANIZATION] |
| **Partner Contact** | [NAME], [TITLE], [EMAIL] |
| **Technical Contact** | [NAME], [TITLE], [EMAIL] |
| **Pilot ID** | PLT-[YYYY]-[NNN] |
| **SOW Reference** | SOW-TG-[YYYY]-[NNN] |
| **Checklist Started** | [YYYY-MM-DD] |
| **Checklist Completed** | [YYYY-MM-DD] |

---

## Section 1: Pre-Engagement Readiness

Verify before sending the SOW or beginning technical discussions.

| # | Item | Pass/Fail | Verifier | Date | Notes |
|---|------|-----------|----------|------|-------|
| 1.1 | Partner use case aligns with Theta-Gamma capabilities (text/image/audio cross-modal) | [ ] PASS / [ ] FAIL | | | |
| 1.2 | Partner has designated a technical point of contact | [ ] PASS / [ ] FAIL | | | |
| 1.3 | Partner has designated a business/decision-maker contact | [ ] PASS / [ ] FAIL | | | |
| 1.4 | NDA or confidentiality agreement executed (if required) | [ ] PASS / [ ] FAIL / [ ] N/A | | | |
| 1.5 | Partner has reviewed Theta-Gamma capability summary | [ ] PASS / [ ] FAIL | | | |
| 1.6 | Pilot scope and timeline discussed and agreed in principle | [ ] PASS / [ ] FAIL | | | |
| 1.7 | No known legal or regulatory blockers to the pilot | [ ] PASS / [ ] FAIL | | | |

**Section 1 Status:** [ ] COMPLETE / [ ] INCOMPLETE (blockers: _______________)

---

## Section 2: Legal and Data Readiness

Verify before exchanging any data or deploying any systems.

| # | Item | Pass/Fail | Verifier | Date | Notes |
|---|------|-----------|----------|------|-------|
| 2.1 | Pilot SOW drafted from `02_pilot_sow_template.md` | [ ] PASS / [ ] FAIL | | | |
| 2.2 | SOW reviewed by legal (both sides) | [ ] PASS / [ ] FAIL | | | |
| 2.3 | SOW signed by both parties | [ ] PASS / [ ] FAIL | | | |
| 2.4 | Data Processing Agreement (DPA) or Data Use Agreement (DUA) signed | [ ] PASS / [ ] FAIL | | | |
| 2.5 | Data handling requirements documented (PII, retention, deletion) | [ ] PASS / [ ] FAIL | | | |
| 2.6 | Regulatory requirements identified (GDPR, HIPAA, etc.) | [ ] PASS / [ ] FAIL / [ ] N/A | | | |
| 2.7 | IP ownership and usage rights for pilot outputs agreed | [ ] PASS / [ ] FAIL | | | |

**Section 2 Status:** [ ] COMPLETE / [ ] INCOMPLETE (blockers: _______________)

---

## Section 3: Technical Readiness — Provider Side

Verify that our systems are ready to support this partner.

| # | Item | Pass/Fail | Verifier | Date | Notes |
|---|------|-----------|----------|------|-------|
| 3.1 | Model checkpoint selected and G3+G4 gates passed | [ ] PASS / [ ] FAIL | | | |
| 3.2 | Model endpoint deployed and responding | [ ] PASS / [ ] FAIL | | | |
| 3.3 | Endpoint meets latency targets (p95 <= 100ms) | [ ] PASS / [ ] FAIL | | | |
| 3.4 | Endpoint meets throughput targets (>= 100 QPS) | [ ] PASS / [ ] FAIL | | | |
| 3.5 | Safety filters active and violation rate <= 0.1% | [ ] PASS / [ ] FAIL | | | |
| 3.6 | Monitoring and alerting configured per A4 recovery state machine | [ ] PASS / [ ] FAIL | | | |
| 3.7 | On-call rotation staffed for pilot duration | [ ] PASS / [ ] FAIL | | | |
| 3.8 | Integration guide (D2) prepared and reviewed | [ ] PASS / [ ] FAIL | | | |
| 3.9 | API authentication configured for partner access | [ ] PASS / [ ] FAIL | | | |
| 3.10 | Weekly report template prepared | [ ] PASS / [ ] FAIL | | | |

**Section 3 Status:** [ ] COMPLETE / [ ] INCOMPLETE (blockers: _______________)

---

## Section 4: Technical Readiness — Partner Side

Verify that the partner's systems are ready for integration.

| # | Item | Pass/Fail | Verifier | Date | Notes |
|---|------|-----------|----------|------|-------|
| 4.1 | Partner has reviewed integration guide (D2) | [ ] PASS / [ ] FAIL | | | |
| 4.2 | Partner's integration environment is provisioned | [ ] PASS / [ ] FAIL | | | |
| 4.3 | Partner can authenticate with API endpoint | [ ] PASS / [ ] FAIL | | | |
| 4.4 | Partner has completed a test query (hello-world) | [ ] PASS / [ ] FAIL | | | |
| 4.5 | Partner's system sends correctly formatted requests | [ ] PASS / [ ] FAIL | | | |
| 4.6 | Partner's system handles error responses gracefully | [ ] PASS / [ ] FAIL | | | |
| 4.7 | Benchmark dataset (D4) received from partner | [ ] PASS / [ ] FAIL | | | |
| 4.8 | Benchmark dataset validated (format, size, modality coverage) | [ ] PASS / [ ] FAIL | | | |
| 4.9 | Partner has query traffic available for monitored operation | [ ] PASS / [ ] FAIL | | | |

**Section 4 Status:** [ ] COMPLETE / [ ] INCOMPLETE (blockers: _______________)

---

## Section 5: Operational Readiness — Go-Live Gate

Final verification before starting the monitored operation phase.

| # | Item | Pass/Fail | Verifier | Date | Notes |
|---|------|-----------|----------|------|-------|
| 5.1 | All Section 1–4 items marked PASS | [ ] PASS / [ ] FAIL | | | |
| 5.2 | Benchmark results (D5) delivered and reviewed with partner | [ ] PASS / [ ] FAIL | | | |
| 5.3 | Incident response plan shared with partner (escalation contacts, SLAs) | [ ] PASS / [ ] FAIL | | | |
| 5.4 | Communication cadence agreed (weekly calls, async channel) | [ ] PASS / [ ] FAIL | | | |
| 5.5 | Go-live date confirmed by both parties | [ ] PASS / [ ] FAIL | | | |
| 5.6 | Pilot scorecard template shared with partner for transparency | [ ] PASS / [ ] FAIL | | | |
| 5.7 | Rollback plan documented (what happens if pilot must abort) | [ ] PASS / [ ] FAIL | | | |

**Section 5 Status:** [ ] COMPLETE / [ ] INCOMPLETE (blockers: _______________)

---

## Section 6: Post-Pilot Readiness

Verify after monitored operation concludes, before finalizing the pilot report.

| # | Item | Pass/Fail | Verifier | Date | Notes |
|---|------|-----------|----------|------|-------|
| 6.1 | All weekly status reports delivered | [ ] PASS / [ ] FAIL | | | |
| 6.2 | Pilot scorecard completed with measured values | [ ] PASS / [ ] FAIL | | | |
| 6.3 | Partner feedback survey completed | [ ] PASS / [ ] FAIL | | | |
| 6.4 | Final pilot report (D7) drafted | [ ] PASS / [ ] FAIL | | | |
| 6.5 | Final pilot report reviewed by partner | [ ] PASS / [ ] FAIL | | | |
| 6.6 | Lessons learned documented | [ ] PASS / [ ] FAIL | | | |
| 6.7 | Data deletion scheduled per SOW/DPA terms | [ ] PASS / [ ] FAIL | | | |
| 6.8 | Go/no-go recommendation for production documented | [ ] PASS / [ ] FAIL | | | |

**Section 6 Status:** [ ] COMPLETE / [ ] INCOMPLETE (blockers: _______________)

---

## Summary

| Section | Items | Passed | Status |
|---------|-------|--------|--------|
| 1. Pre-Engagement | 7 | [___] | [ ] COMPLETE |
| 2. Legal & Data | 7 | [___] | [ ] COMPLETE |
| 3. Provider Technical | 10 | [___] | [ ] COMPLETE |
| 4. Partner Technical | 9 | [___] | [ ] COMPLETE |
| 5. Go-Live Gate | 7 | [___] | [ ] COMPLETE |
| 6. Post-Pilot | 8 | [___] | [ ] COMPLETE |
| **Total** | **48** | **[___]** | |

**Partner Ready for Pilot:** [ ] YES (all sections COMPLETE) / [ ] NO (blockers exist)

---

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Tech Lead | | | |
| Partner Contact | | | |
