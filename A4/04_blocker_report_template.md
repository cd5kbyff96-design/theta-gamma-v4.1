# Blocker Report Template — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-26

---

## Usage

This template is used when a failure reaches the ESCALATED state (third consecutive
failure) per `02_retry_policy.yaml`. It provides the escalation target with all context
needed to make a decision without additional research.

---

## Blocker Report

```
╔══════════════════════════════════════════════════════════════╗
║  BLOCKER REPORT — ESCALATION REQUIRED                      ║
╚══════════════════════════════════════════════════════════════╝

Report ID:        BLK-YYYY-MMDD-NNN
Generated:        [ISO-8601 timestamp]
Incident ID:      INC-YYYY-MMDD-NNN
Severity:         [S1|S2|S3]
Failure Mode:     [FM-XX-NN] — [name]
Pipeline State:   [HALTED|PAUSED|DEGRADED]

═══ SUMMARY (read this first) ═══════════════════════════════

[2-3 sentence plain-language summary of what failed, what was
tried, and why human decision is needed now.]

═══ FAILURE DETAILS ═════════════════════════════════════════

Failure Mode ID:    [FM-XX-NN]
Failure Mode Name:  [name]
Detection Signal:   [metric ID or description]
Signal Value:       [actual value]
Threshold:          [expected value]
First Detected:     [ISO-8601]
Time in Failure:    [Xh Ym]

Current Pipeline State:
  - Gate:           [G1|G2|G3|G4]
  - Training Tier:  [T1-T5]
  - Training Step:  [N]
  - Checkpoint:     [checkpoint ID]
  - Monthly Spend:  $[X.XX] / $500
  - Daily Spend:    $[X.XX] / $50

═══ RETRY HISTORY ═══════════════════════════════════════════

Attempt 1 (same path):
  - Action:     [what was tried]
  - Started:    [ISO-8601]
  - Duration:   [Xh Ym]
  - Outcome:    FAILED
  - Details:    [why it failed]

Attempt 2 (fallback):
  - Action:     [what was tried]
  - Started:    [ISO-8601]
  - Duration:   [Xh Ym]
  - Outcome:    FAILED
  - Details:    [why it failed]

Both retries exhausted. Third-failure escalation is MANDATORY.

═══ IMPACT ASSESSMENT ═══════════════════════════════════════

Training Time Lost:     [X hours]
Compute Cost Wasted:    $[X.XX]
Gate Progress Lost:     [X.X percentage points]
Data Integrity Impact:  [none|suspected|confirmed]
Blocked Packets:        [list of PKT-XXX-NNN IDs]
Downstream Impact:      [what can't proceed until this resolves]

═══ ROOT CAUSE ANALYSIS ═════════════════════════════════════

Suspected Root Cause:   [description]
Cause Category:         [transient|config|data|code|infra|architecture|unknown]
Confidence:             [high|medium|low]
Evidence:               [what supports this diagnosis]

═══ OPTIONS FOR RESOLUTION ══════════════════════════════════

Option A: [name]
  Description:  [what this involves]
  Estimated Time: [Xh/Xd]
  Estimated Cost: $[X.XX]
  Risk:          [low|medium|high]
  Trade-offs:    [what we give up]
  Recommended:   [YES/NO]

Option B: [name]
  Description:  [what this involves]
  Estimated Time: [Xh/Xd]
  Estimated Cost: $[X.XX]
  Risk:          [low|medium|high]
  Trade-offs:    [what we give up]
  Recommended:   [YES/NO]

Option C: [name — e.g., accept and move on]
  Description:  [what this involves]
  Estimated Time: [Xh/Xd]
  Estimated Cost: $[X.XX]
  Risk:          [low|medium|high]
  Trade-offs:    [what we give up]
  Recommended:   [YES/NO]

═══ RECOMMENDATION ══════════════════════════════════════════

Recommended Option:  [A|B|C]
Rationale:           [1-2 sentences]

═══ DECISION REQUIRED ═══════════════════════════════════════

Escalation Target:   [name/role from recovery state machine]
Decision Needed:     [specific question — e.g., "Approve Option A to
                      revert to G1 checkpoint and restart training with
                      revised architecture?"]
Impact If Delayed:   [what happens if no decision is made within SLA]
SLA Deadline:        [ISO-8601 — when decision is needed by]

═══ SIGNATURES ══════════════════════════════════════════════

Prepared By:         [name/role]
Prepared At:         [ISO-8601]

Decision By:         [name/role]          ← TO BE FILLED
Decision:            [approved option]    ← TO BE FILLED
Decision At:         [ISO-8601]           ← TO BE FILLED
Decision Rationale:  [notes]              ← TO BE FILLED
```

---

## Example: Completed Blocker Report

```
╔══════════════════════════════════════════════════════════════╗
║  BLOCKER REPORT — ESCALATION REQUIRED                      ║
╚══════════════════════════════════════════════════════════════╝

Report ID:        BLK-2026-0315-001
Generated:        2026-03-15T14:30:00Z
Incident ID:      INC-2026-0314-003
Severity:         S2
Failure Mode:     FM-GT-02 — G2 gate failure
Pipeline State:   PAUSED

═══ SUMMARY ═════════════════════════════════════════════════

G2 gate has failed twice consecutively. Cross-modal accuracy
plateaued at 57% despite two retry attempts (continued training
and LR adjustment). Modality gap is at 18pp, exceeding the 15pp
threshold. Human decision needed on whether to revert to G1
checkpoint with revised training plan or adjust G2 thresholds.

═══ FAILURE DETAILS ═════════════════════════════════════════

Failure Mode ID:    FM-GT-02
Failure Mode Name:  G2 gate failure
Detection Signal:   M-CM-001 (cross_modal_accuracy)
Signal Value:       57.2%
Threshold:          60.0%
First Detected:     2026-03-13T09:00:00Z
Time in Failure:    53h 30m

Current Pipeline State:
  - Gate:           G2
  - Training Tier:  T2-Efficient-ZeRO2
  - Training Step:  45000
  - Checkpoint:     ckpt-20260315-1200
  - Monthly Spend:  $340.00 / $500
  - Daily Spend:    $28.00 / $50

═══ RETRY HISTORY ════════════════════════════════════════════

Attempt 1 (same path):
  - Action:     Continued training with adjusted LR schedule
  - Started:    2026-03-13T10:00:00Z
  - Duration:   24h
  - Outcome:    FAILED
  - Details:    Accuracy improved 0.3pp to 57.2%, still below 60%

Attempt 2 (fallback):
  - Action:     Reverted to G1 checkpoint, created revised training
                plan with modality-specific learning rates
  - Started:    2026-03-14T10:00:00Z
  - Duration:   28h
  - Outcome:    FAILED
  - Details:    Accuracy reached 58.1% but modality gap at 18pp (>15pp)

Both retries exhausted. Third-failure escalation is MANDATORY.

═══ OPTIONS FOR RESOLUTION ═══════════════════════════════════

Option A: Extended Training with Data Rebalancing
  Description:  Rebalance training data to equalize modality
                representation, continue training for 5 more epochs
  Estimated Time: 3d
  Estimated Cost: $90
  Risk:          Medium
  Trade-offs:    Uses 68% of remaining monthly budget
  Recommended:   YES

Option B: Relax G2 Modality Gap Threshold
  Description:  Adjust modality_gap_max from 15pp to 20pp for G2
  Estimated Time: 1h (config change)
  Estimated Cost: $0
  Risk:          Low for G2, may defer problem to G3
  Trade-offs:    May hit same issue at G3 with stricter 10pp threshold
  Recommended:   NO

Option C: Architecture Change — Add Modality Balancing Loss
  Description:  Add explicit modality balance loss term, retrain from G1
  Estimated Time: 5d
  Estimated Cost: $150
  Risk:          High — significant rework
  Trade-offs:    Most thorough fix but highest cost and time
  Recommended:   NO

═══ RECOMMENDATION ══════════════════════════════════════════

Recommended Option:  A
Rationale:           Data rebalancing addresses the root cause (modality
                     imbalance) at reasonable cost. Lower risk than
                     architecture change and more sustainable than
                     relaxing thresholds.

═══ DECISION REQUIRED ═══════════════════════════════════════

Escalation Target:   Architect
Decision Needed:     Approve Option A (data rebalancing + 5 epoch
                     extension) at estimated $90 additional cost?
Impact If Delayed:   Each day of delay costs ~$28 in idle infra and
                     pushes pilot timeline by 1 day.
SLA Deadline:        2026-03-16T14:30:00Z (24h from report)

═══ SIGNATURES ══════════════════════════════════════════════

Prepared By:         ML Engineer (automated)
Prepared At:         2026-03-15T14:30:00Z

Decision By:         [Architect name]
Decision:            Option A approved
Decision At:         2026-03-15T16:00:00Z
Decision Rationale:  Budget permits it, root cause analysis is sound
```

---

## Checklist for Blocker Report Authors

Before submitting, verify:

- [ ] Summary is plain-language and understandable by non-technical stakeholders
- [ ] Both retry attempts are documented with specific outcomes
- [ ] Impact assessment includes compute cost and gate progress lost
- [ ] At least 2 resolution options are presented with trade-offs
- [ ] One option is explicitly recommended
- [ ] Decision question is specific and actionable
- [ ] Impact-if-delayed is stated
- [ ] SLA deadline is set
