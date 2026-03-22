# Decision Deadline Policy — Theta-Gamma v4.1

**Version:** 1.0.0
**Created:** 2026-02-27

---

## 1. Purpose

Every human decision in the Theta-Gamma pipeline has a hard deadline. This policy
ensures no decision blocks the pipeline indefinitely. When a deadline passes
without a response, the system applies the pre-defined default action and
proceeds autonomously.

**Core principle:** No open-ended questions without a deadline. Every question
has a concrete deadline and a concrete default.

---

## 2. Standard Deadlines

### 2.1 Weekly Decision Packet (routine)

| Event | Time (UTC) | Action |
|-------|------------|--------|
| Packet generated | Monday 09:30 | System compiles top-5 decisions |
| Packet delivered | Monday 09:35 | Sent to reviewer via all channels |
| **Response deadline** | **Tuesday 18:00** | Human must respond by this time |
| Defaults applied | Tuesday 18:01 | Unanswered decisions auto-execute |

**Turnaround:** 32.5 hours from delivery to deadline.

### 2.2 Mid-Week Circuit Breaker Decisions

When a circuit breaker fires (S1 incident, kill-switch, consecutive gate failure),
the pipeline may need urgent decisions outside the weekly packet.

| Severity | Deadline | Default If No Response |
|----------|----------|----------------------|
| S1 (pipeline halted) | 4 hours from notification | Apply safest option: hold pipeline, do not resume |
| S2 (significant issue) | 8 hours from notification | Apply recommended recovery action |
| Budget kill-switch | 4 hours from notification | Apply tier downgrade, hold at safe tier |
| Gate rollback restart | 24 hours from notification | Hold at current state, do not restart |

### 2.3 Gate Transition Decisions

| Gate | Decision | Deadline | Default |
|------|----------|----------|---------|
| G1 pass → G2 start | Approve G2 training plan | Next weekly packet | Proceed with generated plan |
| G2 pass → G3 start | Approve cross-modal training | Next weekly packet | Proceed with generated plan |
| G3 pass → Pilot | Approve pilot launch (T3 required) | 48 hours from notification | **No default — must respond** |
| G4 pass → Production | Approve production deployment (T3) | 48 hours from notification | **No default — must respond** |

**Exception:** G3→Pilot and G4→Production are T3 decisions. They have NO automatic
default and WILL block the pipeline until the human responds. These are the only
two decisions in the entire system that can block indefinitely.

---

## 3. Deadline Calculation Rules

### 3.1 Standard Rules

1. **Business hours only:** Deadlines that fall on weekends shift to Monday 10:00 UTC
2. **Holiday adjustment:** Known holidays shift deadline to next business day 10:00 UTC
3. **Minimum window:** No deadline shorter than 4 hours (even for S1)
4. **Maximum window:** No deadline longer than 48 hours (except T3 gate transitions)

### 3.2 Deadline Extension

The human may request a one-time extension:

| Original Deadline | Maximum Extension | How to Request |
|-------------------|-------------------|----------------|
| Weekly packet (Tue 18:00) | +24 hours (Wed 18:00) | Reply "EXTEND" before deadline |
| Mid-week S1 (4h) | +4 hours (8h total) | Reply "EXTEND" before deadline |
| Mid-week S2 (8h) | +8 hours (16h total) | Reply "EXTEND" before deadline |
| Gate transition (48h) | +48 hours (96h total) | Reply "EXTEND" before deadline |

**Limit:** One extension per decision. No second extensions. After extended
deadline, default applies (or blocks if T3).

---

## 4. Notification Protocol

### 4.1 Initial Notification

Delivered simultaneously via all configured channels:

| Channel | Format | Content |
|---------|--------|---------|
| Dashboard | Banner notification | Packet link + deadline countdown |
| Email | Structured email | Full packet content + response instructions |
| Slack | Message with buttons | Summary + quick-response buttons |

### 4.2 Reminder Schedule

| Time Remaining | Reminder Type | Channel |
|---------------|---------------|---------|
| 8 hours before deadline | Gentle reminder | Email + Slack |
| 2 hours before deadline | Urgent reminder | All channels + Slack DM |
| 30 minutes before deadline | Final warning | All channels, highlighted |
| At deadline | Default applied notice | All channels |

### 4.3 Missed Response Tracking

| Consecutive Misses | Action |
|---------------------|--------|
| 1 | Apply defaults, note in next packet header |
| 2 | Apply defaults, escalate to stakeholder, request delegation |
| 3+ | Apply defaults, flag in weekly report, recommend autonomy tier upgrade |

---

## 5. No Open-Ended Questions Rule

**Hard rule:** The pipeline NEVER presents an open-ended question to the human.

Every decision MUST have:
- Exactly 2–4 concrete options
- One option marked as recommended default (Option A)
- A hard deadline
- Automatic default execution at deadline

**Prohibited formats:**
- "What should we do about X?" ← No options, no default
- "Please advise on the approach for Y" ← Open-ended, no deadline
- "When would you like to schedule Z?" ← Open-ended time question

**Required format:**
- "D3: Gate regression detected. (A) Roll back to G2 checkpoint [recommended]. (B) Continue with reduced scope. Deadline: Tue 18:00. Default: A."

---

## 6. Decision Types and Their Deadlines

| Decision Type | Source | Standard Deadline | Default Category |
|--------------|--------|-------------------|-----------------|
| Pipeline go/no-go | A6 weekly loop | Weekly packet (Tue 18:00) | Proceed with watch items |
| Gate progression | A1 gate evaluator | Weekly packet or 48h for T3 | Proceed (T1/T2) or block (T3) |
| Budget amendment | A2 budget policy | Weekly packet (Tue 18:00) | Hold at current tier |
| Recovery restart | A4 recovery | 24h from notification | Hold pipeline |
| Blocker resolution | A4 blocker report | Weekly packet (Tue 18:00) | Apply recommended resolution |
| Architecture change | Design proposal | Weekly packet (Tue 18:00) | Defer to next week |
| Partner decision | A5 external | Weekly packet (Tue 18:00) | Proceed with recommended path |
| Tier downgrade approval | A2 auto-downgrade | 4h (budget-critical) | Apply downgrade |
