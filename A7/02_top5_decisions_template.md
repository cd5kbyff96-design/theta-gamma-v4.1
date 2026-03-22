# Top-5 Decisions Template — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-27
**Usage:** Auto-generated every Monday at 09:30 UTC. Exactly 5 decisions, ranked by impact × urgency. Human responds by deadline or defaults fire.

---

## Packet Header

| Field | Value |
|-------|-------|
| **Packet ID** | DP-[YYYY]-W[NN] |
| **Week** | W[NN], [YYYY] |
| **Generated** | [YYYY-MM-DD HH:MM] UTC |
| **Weekly Report** | WR-[YYYY]-W[NN] |
| **Response Deadline** | [TUESDAY_DATE] 18:00 UTC |
| **Respond To** | [CHANNEL: dashboard / email / Slack] |

---

## Executive Summary

_One paragraph. What happened this week, why these 5 decisions need your input._

[EXECUTIVE_SUMMARY — auto-generated from weekly report: milestone trajectory, risk level, budget health, any incidents or gate changes. Max 100 words.]

---

## Decision 1 of 5

| Field | Value |
|-------|-------|
| **Decision ID** | D1 |
| **Title** | [DECISION_TITLE] |
| **Impact** | [1–5] — [Critical / High / Medium / Low / Minimal] |
| **Urgency** | [1–5] — [Immediate / This week / Soon / Upcoming / Low] |
| **Score** | [IMPACT × URGENCY] |
| **Source** | [go_no_go / gate_evaluator / budget / recovery / blocker / external / architecture] |
| **Deadline** | [TUESDAY_DATE] 18:00 UTC |
| **Default fires if no response** | Yes |

**Context:**
[2–4 sentences. What happened, why this requires a human decision. Reference specific metrics, incidents, or packet IDs.]

**Options:**

| Option | Description | Risk | Cost Impact |
|--------|-------------|------|-------------|
| **A (Recommended)** | [DEFAULT_ACTION — what the system will do if you don't respond] | [Low / Medium / High] | [$ estimate or "none"] |
| B | [ALTERNATIVE_1] | [Low / Medium / High] | [$ estimate or "none"] |
| C | [ALTERNATIVE_2 — optional, include only if meaningfully different] | [Low / Medium / High] | [$ estimate or "none"] |

**Your choice:** [ A / B / C ]

---

## Decision 2 of 5

| Field | Value |
|-------|-------|
| **Decision ID** | D2 |
| **Title** | [DECISION_TITLE] |
| **Impact** | [1–5] — [Level] |
| **Urgency** | [1–5] — [Level] |
| **Score** | [IMPACT × URGENCY] |
| **Source** | [source] |
| **Deadline** | [TUESDAY_DATE] 18:00 UTC |
| **Default fires if no response** | Yes |

**Context:**
[2–4 sentences.]

**Options:**

| Option | Description | Risk | Cost Impact |
|--------|-------------|------|-------------|
| **A (Recommended)** | [DEFAULT_ACTION] | [level] | [estimate] |
| B | [ALTERNATIVE_1] | [level] | [estimate] |

**Your choice:** [ A / B ]

---

## Decision 3 of 5

| Field | Value |
|-------|-------|
| **Decision ID** | D3 |
| **Title** | [DECISION_TITLE] |
| **Impact** | [1–5] — [Level] |
| **Urgency** | [1–5] — [Level] |
| **Score** | [IMPACT × URGENCY] |
| **Source** | [source] |
| **Deadline** | [TUESDAY_DATE] 18:00 UTC |
| **Default fires if no response** | Yes |

**Context:**
[2–4 sentences.]

**Options:**

| Option | Description | Risk | Cost Impact |
|--------|-------------|------|-------------|
| **A (Recommended)** | [DEFAULT_ACTION] | [level] | [estimate] |
| B | [ALTERNATIVE_1] | [level] | [estimate] |

**Your choice:** [ A / B ]

---

## Decision 4 of 5

| Field | Value |
|-------|-------|
| **Decision ID** | D4 |
| **Title** | [DECISION_TITLE] |
| **Impact** | [1–5] — [Level] |
| **Urgency** | [1–5] — [Level] |
| **Score** | [IMPACT × URGENCY] |
| **Source** | [source] |
| **Deadline** | [TUESDAY_DATE] 18:00 UTC |
| **Default fires if no response** | Yes |

**Context:**
[2–4 sentences.]

**Options:**

| Option | Description | Risk | Cost Impact |
|--------|-------------|------|-------------|
| **A (Recommended)** | [DEFAULT_ACTION] | [level] | [estimate] |
| B | [ALTERNATIVE_1] | [level] | [estimate] |

**Your choice:** [ A / B ]

---

## Decision 5 of 5

| Field | Value |
|-------|-------|
| **Decision ID** | D5 |
| **Title** | [DECISION_TITLE] |
| **Impact** | [1–5] — [Level] |
| **Urgency** | [1–5] — [Level] |
| **Score** | [IMPACT × URGENCY] |
| **Source** | [source] |
| **Deadline** | [TUESDAY_DATE] 18:00 UTC |
| **Default fires if no response** | Yes |

**Context:**
[2–4 sentences.]

**Options:**

| Option | Description | Risk | Cost Impact |
|--------|-------------|------|-------------|
| **A (Recommended)** | [DEFAULT_ACTION] | [level] | [estimate] |
| B | [ALTERNATIVE_1] | [level] | [estimate] |

**Your choice:** [ A / B ]

---

## Deferred Decisions (auto-defaulting)

_Decisions ranked 6+ that will execute their default automatically._

| # | Title | Score | Default Action | Status |
|---|-------|-------|----------------|--------|
| D6 | [TITLE] | [score] | [default] | Auto-defaulting at deadline |
| D7 | [TITLE] | [score] | [default] | Auto-defaulting at deadline |

_(Table empty if ≤ 5 decisions pending this week.)_

---

## How to Respond

1. **Reply with your choices** using the format below (email, Slack, or dashboard):

```
D1: A
D2: B
D3: A
D4: A
D5: C
```

2. **To accept all defaults:** Reply `ALL DEFAULTS`

3. **Deadline:** [TUESDAY_DATE] 18:00 UTC. After this time, unanswered decisions execute Option A (recommended default).

4. **Estimated review time:** < 15 minutes.

---

## Validation Checklist (system use)

- [ ] Exactly 5 decisions (or fewer if < 5 pending)
- [ ] All decisions ranked by impact × urgency (D1 has highest score)
- [ ] Every decision has Option A as recommended default
- [ ] Every decision has a deadline
- [ ] No open-ended questions (all options are concrete actions)
- [ ] Context references specific data (metrics, packet IDs, incident IDs)
- [ ] Deferred decisions listed with their auto-defaults
