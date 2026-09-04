# THE ONBOARDING PLAN — how 0 becomes 20 by 31 October 2026

*Written 4 Sep 2026, run 1, after the first honest measurement of the funnel.
This is the plan every session works to. GOAL_STATE.md is the running state;
ONBOARDING_GOAL.md is the contract. This file is the route between them.*

---

## 0. HONEST SCORECARD — 4 Sep, first working day

David's challenge, and it is fair: *"i dont know how this brainstorming helps you get to the
20 listings."*

| | |
|---|---|
| the number, start of day | 0 |
| the number, end of day | **0** |
| emails that actually went to a stranger | **130** (the apology to people who engaged) |
| wave emails | 0 — the cooling-off rule blocked every city |
| artefacts built | 7 association pages, a club letter, a club reader, an importer |
| artefacts SENT to anyone | **0** |

What the day genuinely bought: the listing floor is fixed and proven, the scoring instrument
is honest, supply roughly doubled (295 club contacts proven from two pages of one sport), and
one wasted wave was prevented (the 1,509 "teachers" are schools, not teachers).

What it did NOT buy: a single listing. **All of the association work is PHASE 3 supply. It
does not produce a publisher this week, and the agent let that thread run for hours without
saying so.** The discipline this file exists to enforce is: measure first, fix the drop-off,
THEN spend the list. Building supply is not a substitute for either of the first two.

**Standing correction for future sessions:** when a good idea arrives mid-Phase-1, capture it
as a spec and say plainly that it is Phase 3 work. Do not follow it to completion while the
measurement it depends on is still running.

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

## 5. THE SPORTS CLUBS LANE — the supply answer, with one catch

David's clubs idea (SPORTS_CLUBS_LANE + the provincial-secretary letter, 4 Sep) is
assessed here because it attacks §1's binding constraint directly, and nothing else on
the table does.

**Why it matters to this goal — now MEASURED, not estimated (4 Sep).** §1 says we hold
~2,860 unemailed organisations — one pass — so 20 publishers needs click→publish of about
5%. Two provincial athletics pages were read live with `CityLauncher/club_reader.py` and
run through the real send guards:

| province | addresses on the page | sendable after every guard |
|----------|----------------------|-----------------------------|
| Western Province | 211 | **98** |
| Athletics Gauteng North | 366 | **197** |

**295 sendable clubs from two provinces of one sport. Athletics South Africa has 17** —
about 2,500 from athletics alone, before cycling, judo, karate, boxing, swimming, the 227
parkruns or the non-profit register. That roughly DOUBLES the list and drops the required
rate from ~5% to ~2.5% — the difference between "tight" and "comfortable" on §1's table.
For contrast, the existing search-and-maps scraper had found 40 sport entries in the whole
3,805-row database. The word list was never the problem; the place we looked was. It also fixes the SHAPE of the gap: the
4 Sep wave found nine lanes dry in the AGENCY category, and clubs feed Tutors, Services
and Adventures, which still have room, across every province. Cost is zero — public
registers, the scraper we already run, the send machinery we already own.

**The catch, and it decides whether the idea scores at all.** The goal counts people
**we contacted cold**. The letter's current ask is that the secretary forwards a
paragraph to their clubs *in their own words*. Anyone who arrives that way was never in
our list and was never emailed by us: `emailed_at` is NULL, so `onboarding_number.py`
excludes them — correctly, under ONBOARDING_GOAL.md §3. **As written, the federation
route builds the business and scores ZERO on this goal.**

One sentence fixes it. Change the ask from *"I send you one short paragraph you can pass
on to your clubs"* to *"may we email your affiliated clubs directly, with your blessing?"*
Then the clubs enter our list, we contact them, they count — and the same answer supplies
the POPIA permission the lane needs anyway. That wording is commercial and legal
positioning, so it is DAVID'S to change, not a session's.

**Timing: the scrape is the fast lane, the letter is the long game.** Volunteers reply
slowly. Letter → reply (1–3 weeks) → permission → readers → send → convert lands late
October at best. The athletics scrape could be sending inside a week (one provincial page
already shows ~110 clubs with addresses in plain text). So: build readers during Phase 1
as parallel work — it is free and it sends nothing — and treat clubs as Phase 3 supply.

**No counsel gate — RUL-052 / RUL-020.** An earlier version of this section made a lawyer
a precondition. That was wrong and David corrected it: counsel items ride alongside, they
never block a wave, and the same applies here. What follows is therefore the operating
position, not a hold.

**The legal difference the feasibility notes did not name.** Our current ZA sending rests
on a specific basis: OUTREACH_LAW_WORKING_NOTES_2026-08-20.md records that role-based
addresses (info@, sales@) directed at the legal entity fall outside POPIA s69's strictest
consent requirement. Club secretaries are the opposite — **named individuals with
personal addresses**, the case s69 protects most strongly. So this lane is not "the same
as what we already do"; it steps outside the basis we currently rely on. Sharpening the
irony: PERSON-ONLY-2 already HOLDS office desks on the Tutors and teachers lanes because
a person lists as a tutor and an office does not — so our own deliverability guard pushes
us toward exactly the addresses the law protects hardest. So the mitigation that carries this
lane is not a legal opinion, it is the machinery already in place and already binding:
the suppression register checked at two gates fail-safe (RUL-054, "one rule we can not
contravene"), an unsubscribe link in every template, the junk / government /
privacy-officer / competitor filters, one mailbox per organisation, the 12-per-wave ramp,
the 5%-bounce stop-loss and the no-follow-up-on-silence rule. Those did real work on the
real data on 4 Sep: one-per-org held 237 sibling mailboxes and the government filter held
45 officers' .gov.za addresses across the two provinces read. A wrong or dead address is
not a wasted email on this lane, it is a burnt contact — which is exactly why the accuracy
of the list, not its size, is the thing to protect.

## 5b. THE ONE THING THAT STOPS THE AGENT RUNNING THIS ALONE

Everything in this plan is inside the agent's authority except one recurring act: **a letter
going out over David's name to strangers.** Code, deploys, commits, scraping, importing,
measuring, fixing and the gated wave all run unattended today and were proven to on 4 Sep.

But every NEW audience needs a NEW letter, and every letter is commercial positioning —
reserved under RUL-096(f). That is correct as a principle and wrong as a mechanism: it is a
per-letter gate, so it stops the agent every single time, which is exactly the "David clicks"
pattern RUL-095 set out to kill.

**The fix, and it is David's to give or refuse: approve the PATTERN once, not each letter.**
A standing authority of the shape — an outreach letter may send without individual review if
it (a) follows the approved structure of the club letter, (b) names only credentials that are
LIVE in the product (RG-0267), (c) carries the unsubscribe link and the line saying where we
got the address, (d) passes journey_check before the first send, and (e) is filed to
`visuals/letters/` at the moment it sends so David can read anything already gone. Anything
outside that shape still comes to him.

Until that exists, the honest position is: the agent can run the whole route EXCEPT the
moment of first contact with a new audience, and will stall there every time.

## 6. WHAT IS NOT THE PLAN

- More outreach before the rate is known. That spends the one pass blind.
- Mailing the ~310 who received the broken email and never opened it. That is a
  wider send than David authorised, and a cold re-send to non-openers is the
  weakest lever we have. Revisit only if Phase 1 shows a strong rate.
- Anything that makes the number look better without a real person publishing.
