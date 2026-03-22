# Incident Templates — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26

---

## 1. Incident Record Template

Use this template for every failure that enters the DETECTED state.

```yaml
# ═══════════════════════════════════════════════
# INCIDENT RECORD
# ═══════════════════════════════════════════════

incident_id: "INC-YYYY-MMDD-NNN"          # auto-generated
created_at: "ISO-8601"
severity: S1|S2|S3
failure_mode_id: "FM-XX-NN"               # from 01_recovery_state_machine.md
failure_mode_name: ""
owner: ""                                  # from recovery state machine
escalation_target: ""                      # from recovery state machine
sla_class: "immediate|4h|24h"

# ── Detection ──────────────────────────────────
detected_at: "ISO-8601"
detected_by: "automated|manual"
detection_signal: ""                       # metric ID or description
signal_value: ""                           # actual value that triggered
threshold_value: ""                        # expected threshold
detection_source: ""                       # monitor, eval harness, CI, human

# ── Context ────────────────────────────────────
pipeline_state_at_detection:
  current_gate: "G1|G2|G3|G4"
  training_tier: "T1|T2|T3|T4|T5"
  training_step: 0
  last_checkpoint: ""
  monthly_spend_usd: 0.00
  daily_spend_usd: 0.00
  experiment_id: ""

# ── Recovery Timeline ─────────────────────────
state_transitions:
  - state: DETECTED
    entered_at: "ISO-8601"
    exited_at: "ISO-8601"
    duration_minutes: 0

  - state: RETRY-1
    entered_at: "ISO-8601"
    action_taken: ""                       # from retry_same_path_once
    outcome: "success|failure"
    exited_at: "ISO-8601"
    duration_minutes: 0

  - state: RETRY-2                         # only if RETRY-1 failed
    entered_at: "ISO-8601"
    action_taken: ""                       # from retry_fallback_once
    outcome: "success|failure"
    exited_at: "ISO-8601"
    duration_minutes: 0

  - state: ESCALATED                       # only if RETRY-2 failed
    entered_at: "ISO-8601"
    escalated_to: ""
    human_decision: ""
    resolved_at: "ISO-8601"
    duration_minutes: 0

  - state: RECOVERED
    entered_at: "ISO-8601"
    cooldown_complete_at: "ISO-8601"

# ── Resolution ─────────────────────────────────
resolved_at: "ISO-8601"
total_resolution_minutes: 0
sla_met: true|false
resolution_method: "retry_same_path|retry_fallback|human_intervention"
root_cause: ""
root_cause_category: "transient|config|data|code|infra|architecture|unknown"
prevention_action: ""
prevention_ticket_id: ""

# ── Impact ─────────────────────────────────────
impact:
  training_time_lost_hours: 0
  compute_cost_wasted_usd: 0.00
  gate_progress_lost_pp: 0.0
  data_lost: false
  pipeline_downtime_hours: 0

# ── Post-Mortem ────────────────────────────────
post_mortem_required: true|false           # true if S1 or SLA missed
post_mortem_scheduled_at: "ISO-8601"
post_mortem_completed: false
lessons_learned: ""
state_machine_updated: false
```

---

## 2. S1 Critical Incident Template

Extended template for S1 (Critical) incidents with additional fields.

```yaml
# ═══════════════════════════════════════════════
# S1 CRITICAL INCIDENT — EXTENDED RECORD
# ═══════════════════════════════════════════════

# Include all fields from §1, plus:

critical_extension:
  pipeline_halted_at: "ISO-8601"
  pipeline_resumed_at: "ISO-8601"
  total_halt_duration_minutes: 0

  immediate_actions_taken:
    - action: ""
      taken_at: "ISO-8601"
      taken_by: ""
      outcome: ""

  stakeholders_notified:
    - name: ""
      role: ""
      notified_at: "ISO-8601"
      channel: "slack|email|pagerduty|phone"
      acknowledged_at: "ISO-8601"

  blast_radius:
    affected_packets: []                   # PKT-XXX-NNN IDs
    affected_gates: []                     # G1, G2, G3, G4
    downstream_blocked: []                 # packet IDs blocked by this failure
    data_integrity_impact: "none|suspected|confirmed"
    security_impact: "none|suspected|confirmed"

  escalation_chain:
    - level: 1
      target: ""
      notified_at: "ISO-8601"
      response_at: "ISO-8601"
    - level: 2                             # if level 1 didn't respond in time
      target: ""
      notified_at: "ISO-8601"
      response_at: "ISO-8601"
```

---

## 3. Gate Failure Incident Template

Specialized template for gate (G1–G4) failures.

```yaml
# ═══════════════════════════════════════════════
# GATE FAILURE INCIDENT
# ═══════════════════════════════════════════════

# Include all fields from §1, plus:

gate_extension:
  gate_id: "G1|G2|G3|G4"
  gate_name: ""
  consecutive_failure_count: 1             # 1, 2, or 3+
  rollback_triggered: false

  criteria_results:
    - metric_id: ""
      metric_name: ""
      threshold: 0.0
      actual_value: 0.0
      window_values: []                    # values in the rolling window
      passed: true|false
      gap_to_threshold: 0.0               # how far from passing

  best_known_checkpoint:
    checkpoint_id: ""
    gate_status: ""                        # which gate it last passed
    cross_modal_accuracy: 0.0
    created_at: "ISO-8601"

  training_trajectory:
    accuracy_trend_slope: 0.0              # pp per epoch
    cost_per_point_current: 0.0
    cost_per_point_historical_avg: 0.0
    estimated_epochs_to_gate: 0
    estimated_cost_to_gate_usd: 0.0

  rollback_plan:                           # if consecutive_failure_count >= 2
    rollback_to_checkpoint: ""
    rollback_to_gate: ""
    actions: []
```

---

## 4. Delivery Stall Incident Template

Specialized template for stalled progress.

```yaml
# ═══════════════════════════════════════════════
# DELIVERY STALL INCIDENT
# ═══════════════════════════════════════════════

# Include all fields from §1, plus:

stall_extension:
  stall_type: "no_gate_progress|packet_blocked|budget_exhausted|critical_path_fail"
  stall_started_at: "ISO-8601"
  stall_duration_days: 0

  blocked_packets:
    - packet_id: ""
      blocked_since: "ISO-8601"
      blocking_reason: ""
      blocking_dependency: ""              # packet or resource blocking this

  gate_progress_history:
    - date: "YYYY-MM-DD"
      gate: ""
      cross_modal_accuracy: 0.0
      delta_from_previous: 0.0

  budget_status:
    monthly_spent_usd: 0.0
    monthly_remaining_usd: 0.0
    current_tier: ""
    days_remaining_in_month: 0
    runway_days_at_current_rate: 0.0

  options_considered:
    - option: ""
      pros: ""
      cons: ""
      estimated_cost_usd: 0.0
      estimated_time_days: 0
      recommended: true|false
```

---

## 5. Post-Mortem Template

Required after every S1 incident and any incident where SLA was missed.

```yaml
# ═══════════════════════════════════════════════
# POST-MORTEM
# ═══════════════════════════════════════════════

post_mortem_id: "PM-YYYY-MMDD-NNN"
incident_id: "INC-YYYY-MMDD-NNN"
conducted_at: "ISO-8601"
participants: []

# ── Timeline ───────────────────────────────────
timeline:
  - time: "ISO-8601"
    event: ""
    actor: "system|person_name"

# ── Analysis ───────────────────────────────────
what_happened: ""
root_cause: ""
contributing_factors: []
what_went_well: []
what_went_poorly: []

# ── Prevention ─────────────────────────────────
action_items:
  - action: ""
    owner: ""
    due_date: "YYYY-MM-DD"
    ticket_id: ""
    status: "open|in_progress|done"

# ── Metrics Impact ─────────────────────────────
impact_summary:
  total_downtime_hours: 0
  compute_wasted_usd: 0.0
  gate_delay_days: 0
  sla_met: true|false
```
