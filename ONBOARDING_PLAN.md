# THE ONBOARDING PLAN — how 0 becomes 20 by 31 October 2026

*Rewritten 5 Sep 2026 after David asked the five questions this file had no honest answer to.
GOAL_STATE.md is the running state; ONBOARDING_GOAL.md is the contract. This is the route.*

---

## 0. WHAT CHANGED, AND WHY THE OLD PLAN WAS WRONG

The plan written 4 Sep said the constraint was **supply** — too few prospects — and set a
measure-only week before spending "our one pass through the list". Both halves were wrong.

**The constraint was never supply. It was REACH.** Measured 5 Sep:

| what was actually broken | people it stranded |
|---|---|
| `Services` missing from `agency_categories` — the planner could not see the lane | 482 |
| 7 US cities armed in the policy with no line in the wave script | 33 |
| 19 cities across AU, NZ, GB, AR, ZA that the policy had never heard of | 40 |
| `Sports Clubs` had a letter, a collector and 577 contacts — and no category, no lane, no importer | 577 |
| 3 more letters (individual collectors, individual property, casual work) drawable by nothing | 0 today |

None of these was a shortage. Every one was a list that did not match another list, failing
**silently** — the wave simply never mentioned those people, and an absent line reads like an
absent problem. Nothing on the board went red, because nothing was asserting it.

**The one-pass fear was also wrong.** The reachable pool is far larger than the old plan
believed, and it grows when reach is fixed rather than when more scraping is done.

## 1. THE ARITHMETIC — measured 5 Sep 2026, not assumed

**Every live row, sorted by what actually stops it:**

| | rows | |
|---|---|---|
| **reachable now** — guard-clean, law-cleared, in a wave city | **864** | the working pool |
| club contacts, import queued | **577** | Pretoria 366, Cape Town 211 |
| schools and other blocked categories | 1,366 | correctly shut — they are not tutors |
| already contacted or rejected | 930 | spent |
| held by a guard (office desks, government, junk) | 259 | correctly held |
| **France + Portugal** | **179** | **waiting on David — see §4** |

So the honest reachable universe is **1,441 people today**, 1,620 if the EU opens.

**What 20 publishers requires:**

| if click → publish is | publish rate at 10% click | publishers from 1,441 | verdict |
|---|---|---|---|
| 25% | 2.5% | 36 | comfortable |
| 15% | 1.5% | 21 | **just enough — this is the line** |
| 10% | 1.0% | 14 | short; needs the EU or new scraping |
| 5% | 0.5% | 7 | not reachable without much more supply |

**The whole goal turns on one unmeasured number: click → publish.** It has never been observed,
because until 3 Sep the link was broken and until 22 Jul the listing form was. Everything else
is arithmetic around it.

**Capacity is not the constraint.** 43 armed cities at 6 per city is ~130 sends a night, so the
1,441 are spent in roughly 11 nights. There are 56 days left. Supply becomes the constraint
again in mid-September — which is when scraping earns its place, and not before.

## 2. THE RULE THAT REPLACES THE CALENDAR

David, 5 Sep: *"You don't need to stop based on a previous time schedule as if it is a rule. If
we are stopped due to google rules or to-be-released email stops then it is understood... but if
we can target other countries or cities then we should do it."*

**So: gates, not calendars.** A send waits for a REAL gate — bounce stop-loss, the per-city
day gap, provider limits, a legal clearance we do not hold — and for nothing else. A
self-imposed measuring week is not a gate. The old "do not open the tap during Phase 1" line is
retired; the batch cap (6 per city) is the restraint now, and it is a dial, not a date.

## 3. THE ROUTE

**Now → 8 Sep. SEND, AND WATCH ONE NUMBER.**
The 129-person wave across 38 cities is the first ever aimed at individuals rather than office
desks and schools. Every morning: run `scripts/onboarding_number.py`, then read opens, clicks
and *distinct human clickers* for the previous night. The single question is click → publish.
Import the clubs, then let Pretoria and Cape Town draw from them.

**8 → 15 Sep. FIX WHERE THEY STOP.**
By now the funnel has a real denominator. Fix the one step that loses the most people, as a
class and not an instance. If click → publish is above 15%, the arithmetic works and the job is
volume. If it is below 10%, no amount of sending reaches 20 and the answer is the product, not
the list.

**15 Sep → 24 Oct. SPEND, THEN REFILL.**
The 1,441 are gone in about 11 sending nights. From mid-September the binding constraint is
genuinely supply for the first time, and `run_local_scraper.bat` and the club/federation lanes
earn their place. Aim scraping at whatever vertical the measured rate says converts.

**24 → 31 Oct. STOP ADDING, START CLOSING.**
No new lanes. Follow up the people who clicked and did not publish.

## 4. EUROPE — DECIDED, AND CLOSED FOR NOW (RUL-101, 5 Sep 2026)

David, shown the measurement: *"I agree lets not email those two countries."*

France and Portugal are **out of outreach**. No EU representative is bought. The code keeps
refusing to build those messages, which is the mechanism rather than merely the intention.

**Why, in numbers.** 179 FR/PT rows sit behind the fence. 100 are clean on every other count.
Those 100 split on the one thing French and Portuguese law cares about:

| | | |
|---|---|---|
| **35** | business addresses | lawful to cold-email, opt-out basis, message must concern their job |
| **65** | personal mailboxes (gmail, orange.fr, sapo.pt) | need **prior opt-in** — never lawful to cold-email, representative or not |

A representative costs €490–€1,000 a year and would unlock **35 people**. About €20 a head
before anyone converts.

**This defers a market, it does not close one.** European law bites on *offering a service* to
people in the EU, so a representative is needed to have French sellers **at all**, not merely to
email them. The question is therefore "do we want Europe as a market", and it is revisited once
click→publish is known — never again as an emailing cost.

**Ruled out, so nobody re-proposes them:** the "occasional processing" exemption (we hold a
standing database and send repeated waves — the opposite of occasional); and routing through an
EU mail provider or domain, which changes nothing because the law follows the person, not the
server.

**Still open, and free:** the federation route — a European association emails its own members
about us, under its own relationship with them, and we never touch their data. It is the only
route that reaches those 65 personal mailboxes.

**Nothing else waits on David.**

## 5. HOW THIS PLAN STAYS HONEST

The old plan was written once and never revisited, so it went on asserting a supply shortage for
a day after the shortage was disproved. Standing rule now: **when a session's measurement
contradicts this file, this file is edited in that session** — same rule as the ledger and the
rulings register. A plan nobody updates is just an old opinion with a filename.
