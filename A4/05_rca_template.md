# Root Cause Analysis (RCA) Template — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-27
**References:** `01_recovery_state_machine.md`, `03_incident_templates.md`

---

## Usage

This template is used for every post-mortem following an S1 incident, any incident
where SLA was missed, or any incident that reached the ESCALATED state. It provides
a structured 5-Whys analysis with corrective actions, ownership, and deadlines.

Fill this out within 48 hours of incident resolution.

---

## RCA Record

```yaml
# ═══════════════════════════════════════════════
# ROOT CAUSE ANALYSIS
# ═══════════════════════════════════════════════

rca_id: "RCA-YYYY-MMDD-NNN"
incident_id: "INC-YYYY-MMDD-NNN"
post_mortem_id: "PM-YYYY-MMDD-NNN"
failure_mode_id: "FM-XX-NN"
severity: S1|S2|S3
date_conducted: "ISO-8601"
facilitator: ""
participants: []

# ── Incident Summary ─────────────────────────
summary:
  what_failed: ""
  when_detected: "ISO-8601"
  time_to_resolve_hours: 0
  sla_met: true|false
  resolution_method: "retry_same_path|retry_fallback|human_intervention"
  total_cost_impact_usd: 0.00

# ── 5-Whys Analysis ─────────────────────────
five_whys:
  - level: 1
    question: "Why did [failure] occur?"
    answer: ""
    evidence: ""                              # log line, metric, config file
    evidence_source: ""                       # path or system

  - level: 2
    question: "Why did [answer to why-1] happen?"
    answer: ""
    evidence: ""
    evidence_source: ""

  - level: 3
    question: "Why did [answer to why-2] happen?"
    answer: ""
    evidence: ""
    evidence_source: ""

  - level: 4
    question: "Why did [answer to why-3] happen?"
    answer: ""
    evidence: ""
    evidence_source: ""

  - level: 5
    question: "Why did [answer to why-4] happen?"
    answer: ""
    evidence: ""
    evidence_source: ""

# ── Root Cause Classification ────────────────
root_cause:
  description: ""
  category: "transient|config|data|code|infra|architecture|process|unknown"
  subcategory: ""                             # e.g., "missing validation", "stale cache"
  preventable: true|false
  recurrence_risk: "high|medium|low"
  similar_past_incidents: []                  # list of INC-YYYY-MMDD-NNN

# ── Contributing Factors ─────────────────────
contributing_factors:
  - factor: ""
    category: "process|tooling|monitoring|communication|design"
    severity: "primary|secondary|minor"

# ── Detection Assessment ─────────────────────
detection:
  how_detected: "automated_alert|manual_inspection|user_report|gate_eval"
  detection_delay_minutes: 0
  could_have_been_detected_earlier: true|false
  earlier_detection_method: ""
  monitoring_gaps_identified: []

# ── Recovery Assessment ──────────────────────
recovery:
  retry_1_effective: true|false|na
  retry_1_failure_reason: ""
  retry_2_effective: true|false|na
  retry_2_failure_reason: ""
  escalation_required: true|false
  recovery_bottlenecks: []                    # what slowed recovery

# ── Corrective Actions ──────────────────────
corrective_actions:
  immediate:                                  # already done during incident
    - action: ""
      owner: ""
      completed_at: "ISO-8601"

  short_term:                                 # within 1 week
    - action: ""
      owner: ""
      due_date: "YYYY-MM-DD"
      ticket_id: ""
      status: "open|in_progress|done"

  long_term:                                  # within 1 month
    - action: ""
      owner: ""
      due_date: "YYYY-MM-DD"
      ticket_id: ""
      status: "open|in_progress|done"

# ── State Machine Updates ────────────────────
state_machine_updates:
  new_failure_mode_needed: true|false
  new_failure_mode_id: ""                     # if adding to 01_recovery_state_machine.md
  retry_policy_update_needed: true|false
  retry_policy_changes: ""
  monitoring_update_needed: true|false
  monitoring_changes: ""

# ── Sign-Off ─────────────────────────────────
sign_off:
  prepared_by: ""
  reviewed_by: ""
  approved_by: ""
  approved_at: "ISO-8601"
```

---

## RCA Quality Checklist

Before closing the RCA, verify:

- [ ] All 5 Whys are completed with evidence for each level
- [ ] Root cause category is assigned and matches the evidence chain
- [ ] At least one corrective action exists for each timeframe (immediate, short-term, long-term)
- [ ] Every corrective action has an owner and due date
- [ ] Detection assessment identifies any monitoring gaps
- [ ] Recovery assessment documents what slowed or blocked recovery
- [ ] State machine update decision is documented (even if "no update needed")
- [ ] RCA is linked to the original incident and post-mortem records
- [ ] Similar past incidents are cross-referenced
- [ ] Sign-off from reviewer and approver is obtained

---

## Example: Completed RCA

```yaml
rca_id: "RCA-2026-0315-001"
incident_id: "INC-2026-0314-003"
post_mortem_id: "PM-2026-0316-001"
failure_mode_id: "FM-GT-02"
severity: S2
date_conducted: "2026-03-16T10:00:00Z"
facilitator: "Tech Lead"
participants: ["ML Engineer", "Data Engineer", "Architect"]

summary:
  what_failed: "G2 gate failed twice — cross-modal accuracy at 57.2%, below 60% threshold"
  when_detected: "2026-03-13T09:00:00Z"
  time_to_resolve_hours: 53.5
  sla_met: false
  resolution_method: "human_intervention"
  total_cost_impact_usd: 118.00

five_whys:
  - level: 1
    question: "Why did the G2 gate fail?"
    answer: "Cross-modal accuracy at 57.2%, below the 60% threshold"
    evidence: "Gate eval log 2026-03-13"
    evidence_source: "eval_harness/results/g2_eval_20260313.json"

  - level: 2
    question: "Why was cross-modal accuracy only 57.2%?"
    answer: "18pp modality gap — text-to-image accuracy 22pp higher than image-to-text"
    evidence: "Modality breakdown in eval"
    evidence_source: "eval_harness/results/modality_breakdown_20260313.csv"

  - level: 3
    question: "Why was there an 18pp modality gap?"
    answer: "Training data was 70% text-image pairs, only 30% image-text pairs"
    evidence: "Data pipeline sampling stats"
    evidence_source: "data_pipeline/logs/sampling_ratios_20260310.log"

  - level: 4
    question: "Why was the training data imbalanced?"
    answer: "Image-to-text data source had a silent failure, reducing output by 60%"
    evidence: "Data source health check"
    evidence_source: "data_pipeline/health/source_img2txt_20260301.json"

  - level: 5
    question: "Why was the data source failure not detected?"
    answer: "No per-modality volume monitoring — only total volume was tracked"
    evidence: "Monitoring configuration"
    evidence_source: "monitoring/config/data_pipeline_alerts.yaml"

root_cause:
  description: "Missing per-modality data volume monitoring allowed silent imbalance"
  category: "process"
  subcategory: "monitoring gap"
  preventable: true
  recurrence_risk: "high"
  similar_past_incidents: []

contributing_factors:
  - factor: "No per-modality data volume alerts"
    category: "monitoring"
    severity: "primary"
  - factor: "Modality balance not checked before gate eval"
    category: "process"
    severity: "secondary"

corrective_actions:
  immediate:
    - action: "Rebalanced training data and resumed training"
      owner: "Data Engineer"
      completed_at: "2026-03-15T18:00:00Z"

  short_term:
    - action: "Add per-modality volume alerts to data pipeline monitoring"
      owner: "Data Engineer"
      due_date: "2026-03-22"
      ticket_id: "TASK-0847"
      status: "open"

  long_term:
    - action: "Add pre-gate data balance check to eval harness"
      owner: "ML Engineer"
      due_date: "2026-04-15"
      ticket_id: "TASK-0848"
      status: "open"

state_machine_updates:
  new_failure_mode_needed: false
  retry_policy_update_needed: false
  monitoring_update_needed: true
  monitoring_changes: "Add FM-DP-04 alert for per-modality volume drop"

sign_off:
  prepared_by: "ML Engineer"
  reviewed_by: "Tech Lead"
  approved_by: "Architect"
  approved_at: "2026-03-16T15:00:00Z"
```
