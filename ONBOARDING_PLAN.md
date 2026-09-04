# THE ONBOARDING PLAN — how 0 becomes 20 by 31 October 2026

*Written 4 Sep 2026, run 1, after the first honest measurement of the funnel.
This is the plan every session works to. GOAL_STATE.md is the running state;
ONBOARDING_GOAL.md is the contract. This file is the route between them.*

---

## 1. THE ARITHMETIC — read this before proposing anything

Everything we know, measured on the live server 4 Sep 2026:

| stage | number | rate |
|-------|--------|------|
| prospects on the list | 3,805 | — |
| emailed so far | 461 | — |
| opened | 155 | **34% of emailed** |
| clicked | 48 | **10% of emailed** (31% of openers) |
| published | **0** | unknown — every click so far hit a locked door |
| never emailed yet | 2,860 (≈2,737 organisations after one-per-org) | — |

The decisive unknown is **click → publish**. We have never observed it, because
until 3 Sep the link was broken and until 22 Jul the listing form was broken.
Zero out of 48 tells us nothing.

**What each possible rate would demand, to reach 20 publishers:**

| if click → publish is | clicks needed | emails needed (at 10% click) | verdict |
|----------------------|---------------|------------------------------|---------|
| 20% | 100 | ~1,000 | comfortable — one third of the list |
| 10% | 200 | ~2,000 | achievable — two thirds of the list |
| 5% | 400 | ~3,800 | tight — the whole list, one pass, no waste |
| 2% | 1,000 | ~9,600 | **not reachable** — 3× more supply than exists |

**So: we have roughly ONE PASS through our list.** Sending capacity is not the
constraint (14 armed cities × ~12 per wave × daily ≈ 4,000 sends before the
deadline). Supply and conversion are. That is why the order below is measure
first, spend second — a wasted pass cannot be bought back.

## 2. THE PLAN

### Phase 1 — MEASURE (4–11 Sep). Get the first real conversion number.

The 130 people sent the apology on 4 Sep are the experiment: a warm audience,
a working link, a repaired listing flow. The webhook resolves opens and clicks
by recipient, so their behaviour is captured even though the apology lane does
not write a 'sent' row — the denominator is 130, from emailer/sent_log.json.

Every session, in order: run `scripts/onboarding_number.py`, then read opens and
clicks for those 130, then record both in GOAL_STATE.md. Nothing else matters
this week. **Do not open the tap during Phase 1** beyond the already-scheduled
daily wave — a bigger send before we know the rate spends the pass blind.

### Phase 2 — FIX THE BIGGEST DROP-OFF (11–18 Sep).

Phase 1 says where people stop. Fix that one thing, prove it, then move on.
Likely candidates, in the order they appear in the journey: the sign-in step,
the photo/AI-draft step, the plan picker, the publish button. The three gates
that were breaking publish are already fixed and locked; whatever Phase 1 finds
will be a fourth, and it should be treated as a class, not an instance.

### Phase 3 — SPEND THE LIST (18 Sep–24 Oct).

Only once the measured rate says 20 is reachable. Top up the empty category
pools, run the wave daily across every armed lane, hold the ramp discipline.
Roughly 2,860 organisations, ~5 weeks, well inside sending capacity.

### Reserve (24–31 Oct). No new sending. Convert whoever is mid-flow.

## 3. THE DECISION GATE — say it early, not on 31 October

At the end of Phase 1, compute the implied emails-needed from the measured rate:

- **implies under 2,000 emails** → proceed to Phase 3 as planned.
- **implies 2,000–3,800** → proceed, but flag to David that it needs the whole
  list with no waste, and that a second supply source should be lined up now.
- **implies over 3,800** → **STOP AND SAY SO.** 20 is not reachable with this
  list. Report the true number, the measured rate, and the one thing that would
  change it (more supply, a warmer channel, or a different vertical). A truthful
  4 is worth more than a manufactured 20 — ONBOARDING_GOAL.md §3.

Never let this arrive as a surprise in the last week.

## 4. WHAT IS IN THE WAY

1. **Supply top-up is locked out.** The tool that refills empty category pools
   cannot reach our own API because the key was never provisioned. Until then
   supply comes from the scraper lane. Tracked as an open ledger entry.
2. **Category pools, not total supply.** The 4 Sep wave reported "no sendable
   prospects" for nine lanes, but that was the AGENCY category being dry — the
   list holds 1,509 teachers/trainers and 159 tutors untouched. Rotate the
   category, do not conclude the list is empty.
3. **Only ~2 real human clicks in the whole campaign to date.** Most recorded
   clicks are corporate link-scanners. Any rate computed from raw click counts
   will flatter us; use the scored human tiers.

## 5. WHAT IS NOT THE PLAN

- More outreach before the rate is known. That spends the one pass blind.
- Mailing the ~310 who received the broken email and never opened it. That is a
  wider send than David authorised, and a cold re-send to non-openers is the
  weakest lever we have. Revisit only if Phase 1 shows a strong rate.
- Anything that makes the number look better without a real person publishing.
