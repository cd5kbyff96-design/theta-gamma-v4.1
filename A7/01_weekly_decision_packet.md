# Weekly Decision Packet — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-27

---

## 1. Purpose

The weekly decision packet is a single, self-contained document delivered to
the human reviewer every Monday alongside the weekly report (A6). It batches
ALL decisions that require human input into exactly 5 ranked items. The human
makes one pass, marks decisions, and returns the packet. The pipeline then
resumes with zero further human interaction until the next Monday.

**Design principle:** The human spends < 15 minutes per week on decisions.
Everything else runs autonomously under the autonomy contract (A0).

## 2. Packet Lifecycle

```
Monday 09:00 UTC — Weekly loop completes (A6 Steps 1–6)
│
├─ 09:30 UTC — Decision packet generated
│  System compiles all pending decisions from the week.
│  Ranks by impact × urgency. Selects top 5.
│  Attaches recommended default for each.
│
├─ 09:35 UTC — Packet delivered
│  Sent via: dashboard notification + email digest + Slack message.
│  Contains: 5 decisions, context, defaults, deadlines.
│
├─ DEADLINE: Tuesday 18:00 UTC (next business day)
│  Human reviews and responds.
│  Any decision without response → default action fires.
│
└─ Tuesday 18:01 UTC — Defaults applied
   Unanswered decisions execute their recommended default.
   Pipeline proceeds autonomously.
```

## 3. Packet Generation Rules

### 3.1 Decision Collection

During the week, the pipeline accumulates pending decisions from:

| Source | Decision Type | Example |
|--------|--------------|---------|
| Go/no-go (A6 Step 4) | Pipeline continuation | NO-GO requires human sign-off |
| Gate evaluator (A1) | Gate progression | G3 pass → approve pilot transition |
| Budget policy (A2) | Budget amendments | Request budget increase for G2 push |
| Recovery state machine (A4) | Escalated failures | Third-failure escalation |
| Blocker reports (A4) | Unresolved blockers | Blocker > 14 days, needs direction |
| Roll-back rules (A6) | Recovery approval | RB-2 gate rollback restart approval |
| External dependencies (A5) | Partner decisions | Data access response needed |
| Architecture decisions | Design choices | Model architecture change proposal |

### 3.2 Ranking Formula

Each pending decision is scored:

```
decision_score = impact_score × urgency_score
```

#### Impact Score (1–5)

| Score | Impact Level | Definition |
|-------|-------------|------------|
| 5 | Critical | Blocks entire pipeline or affects safety |
| 4 | High | Blocks current gate or major milestone |
| 3 | Medium | Affects weekly plan or budget trajectory |
| 2 | Low | Affects single packet or minor process |
| 1 | Minimal | Process improvement, no delivery impact |

#### Urgency Score (1–5)

| Score | Urgency Level | Definition |
|-------|--------------|------------|
| 5 | Immediate | Pipeline halted until decided |
| 4 | This week | Must decide before next Monday or default fires |
| 3 | Soon | Affects next 2 weeks of planning |
| 2 | Upcoming | Affects next gate or milestone |
| 1 | Low | Can wait 30+ days without consequence |

#### Selection

1. Score all pending decisions
2. Sort by `decision_score` descending
3. Select top 5 (or fewer if < 5 pending)
4. If > 5 pending: remaining decisions use their defaults automatically
5. Tie-breaking: prefer the decision with higher impact score; if still tied, prefer older decision

### 3.3 Overflow Handling

When more than 5 decisions are pending:

| Overflow Decision Score | Action |
|------------------------|--------|
| >= 15 (impact × urgency) | Include in packet, bump lowest-scored item |
| 10–14 | Apply default, mention in "deferred decisions" section |
| < 10 | Apply default silently, log in decision log |

**Hard rule:** Decisions with `impact_score = 5` (critical) are ALWAYS included
in the top 5, displacing lower-impact items regardless of urgency.

## 4. Packet Structure

Each weekly decision packet follows the template in `02_top5_decisions_template.md`
and contains:

1. **Header** — Report ID, week, generation timestamp, response deadline
2. **Executive Summary** — One paragraph: what happened, what needs deciding
3. **Decision 1–5** — Ranked items, each with:
   - Decision ID and title
   - Impact × urgency score
   - Context (what happened, why this needs a decision)
   - Options (2–4 choices, never open-ended)
   - Recommended default (what happens if no response)
   - Deadline (when default fires)
4. **Deferred Decisions** — Items ranked 6+ that will auto-default
5. **Response Instructions** — How to respond (reply with decision numbers)

## 5. Response Format

The human responds with a minimal format:

```
D1: A        ← Accept recommended default
D2: B        ← Choose option B
D3: A        ← Accept recommended default
D4: C        ← Choose option C
D5: A        ← Accept recommended default
```

Or simply:

```
ALL DEFAULTS
```

**No prose required.** The system parses single-letter responses.

## 6. Integration with Weekly Loop

The decision packet plugs into the A6 weekly loop as follows:

```
A6 Step 6: Report published (Monday 09:00–09:30)
│
├─ Decision packet generated (09:30)
│  Uses data from Steps 1–5 of weekly loop.
│
├─ Packet delivered to human (09:35)
│
├─ Human responds (by Tuesday 18:00 UTC)
│
├─ Responses applied to pipeline config (Tuesday 18:01)
│  - Go/no-go overrides applied
│  - Budget amendments activated
│  - Recovery plans approved/modified
│  - Gate transitions confirmed
│
└─ Pipeline resumes full autonomous operation
   Next decision point: following Monday
```

## 7. Decision Packet Metrics

Track the health of the decision process:

| Metric | Target | Action if Missed |
|--------|--------|--------------------|
| Packet delivered by | Monday 09:35 UTC | Escalate automation failure |
| Human response time | < 24 hours | Apply defaults at deadline |
| Response rate | 100% of packets | After 2 missed: escalate to stakeholder |
| Default acceptance rate | Track only | If > 80%: consider raising autonomy tier |
| Decision reversal rate | < 10% | Review decision quality if high |

## 8. Escalation for Missed Responses

| Missed Packets (consecutive) | Action |
|-----------------------------|--------|
| 1 | Apply defaults, send reminder for next week |
| 2 | Apply defaults, escalate to stakeholder with notice |
| 3+ | Apply defaults, flag in weekly report, request delegation |

If the human designates a delegate, decision packets route to the delegate
until the primary reviewer resumes.
