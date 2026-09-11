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

**Corrected 6 Sep 2026 (measured):** the registers changed the arithmetic within a day. The
RRCA national running-club register imported **903 US clubs** on 5 Sep 21:30 ('Sports Clubs' is
now 1,568 rows, 1,301 distinct clubs), and USATF New England adds 268 more (import queued 6 Sep).
The reachable universe is therefore roughly **2,600 people**, of which about 1,170 are US club
contacts under 51 state buckets — and the first US club wave (6 Sep 00:10) sent NONE of them,
because the club letter crashed on a rand price for every non-ZA reader (fixed the same night,
wave re-queued). The 250-a-day domain cap (DAILY-CAP-1) is now the binding rate, not supply.

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
By now the funnel has a real denominator — and since 5 Sep evening it has an INSTRUMENT: every
step of the guided sell flow (landing, sub-choice, the required main photo accepted or rejected,
each section, draft, publish) is counted live at `GET https://trustsquare.co/onboard/funnel`
(counts only, no addresses). Read it every morning next to the number. Known before the
instrument existed: about ten real people clicked a working link between 3 and 5 Sep and none
registered. **The first reading (6 Sep) contradicted the assumption:** a Tutors invite lands on
Step 1 of 6 (the required photo of yourself at work), but a CLUB invite did not — the app's
invite map had never heard of 'Sports Clubs', so all four real club landings went to the generic
"what are you selling?" tiles and stopped there (9 sessions landed, 0 reached the photo step).
Fixed and shipped 6 Sep (INVITE-CAT-2); from now on a club arrives at the Tutors photo step and
whether people stop THERE is the reading to take. Fix the one step that loses the most people, as a
class and not an instance.

**Corrected 7 Sep 2026 (measured): the 6 Sep readings were not people.** Every session the funnel
showed at the photo step (9 across Kansas and California) was created 20–40 seconds after its wave's
send time, four at a time within eight seconds, and the web server log showed the poster was
Google-Safety — a link scanner that renders the page and runs our code. So the honest reading on the
evening of 6 Sep was: **humans at the photo step 0; humans landed from the club letters — unknown, the
instrument could not tell.** Fixed the same night: the funnel now flags scanner sessions and hides
them by default, and counts a person only after 12 seconds on the page plus a real touch, key or
scroll. **The click → publish measurement therefore starts on 7 Sep, not 6 Sep.** Anything read off
the funnel before 7 Sep 01:30 SAST is ungraded and must not be used as a rate. If click → publish is above 15%, the arithmetic works and the job is
volume. If it is below 10%, no amount of sending reaches 20 and the answer is the product, not
the list.

**15 Sep → 24 Oct. SPEND, THEN REFILL.**
The 1,441 are gone in about 11 sending nights at a flat 12 — about 5 at the ramp's own pace
(measured 5 Sep evening). From around 10 September the binding constraint is genuinely supply
for the first time. **Refill comes from REGISTERS, not from search scraping — measured, not
assumed (5 Sep, 19:24):** the first-ever US run of `run_us_scraper.bat` searched 11 cities × 7
categories for 33 minutes and found **one** address, and that one was a South African shop
mis-filed under Austin. General search scraping is structurally dead for the US; it stays a
ZA-only top-up until its US fix round measures otherwise (ledger RG-0297 is that task). The
club/federation/association lanes (the register reader and the club importer) are the supply
engine — and since 5 Sep 20:30 they cover **all 50 US states in one adapter** (the RRCA
running-club register, one policy bucket per state, harvested and imported host-side by
`run_us_registers.bat`). Total daily volume is now gated at 250 across the domain
(DAILY-CAP-1), raised on clean days. Aim the next registers at whatever vertical the measured
rate says converts.

**Supply reading, 7 Sep 2026:** the US club pool has 815 uncontacted addresses left (Massachusetts
213, Texas 57, California 55, Northern California 52, New York 44 …) — about three to four sending
nights at 250 a day. **The US club lane runs dry around 10–11 Sep; the next register must be imported
before then, not after.** One is banked: 199 Montana licensed outfitters (Montana Outfitters & Guides
Association directory), category adventures, bucket Montana — collected but not yet drawn, because the
adventures letter does not yet say where we got the address (the club letter does, and that line is a
condition of sending without David's review). Bringing that letter into the approved shape unlocks the
lane; the ledger prints the moment both halves are true. Register pages probed and found empty of
addresses on 7 Sep (do not re-check): Orienteering USA, National Ski Council Federation, American Canoe
Association, American Hiking Society, Idaho IOGA, USATF Minnesota / Oregon / Georgia / New Jersey /
Indiana, Adventure Cycling.

**Corrected 8 Sep 2026 (measured): the ramp never worked, and one register is dead.** Two things this
file assumed were false. (1) "About 5 nights at the ramp's own pace" assumed 12 → 24 → 48 → 96. The wave
counter in the database was stuck at 1 from the first send (a column default nobody noticed), so the ramp
could never see a second clean wave and no city ever exceeded 24 — the accelerator was disconnected in a
second way, one RG-0290 could not see. Fixed 8 Sep (RG-0339); the first real doubling to 48 is tomorrow's
wave, in Massachusetts, Florida, Michigan and Illinois. (2) The USATF New England register is not supply:
25 sent, 7 bounced (28%), personal mailboxes on live domains, so no cleaning rescues it; the source gate
holds all 241 remaining rows including Massachusetts' 213. So the US club lane is rrca 292 + Pacific 40 ≈
330 and runs dry **9–10 Sep**, a day earlier than the 7 Sep reading. The replacement is outfitters:
Montana's 199 are drawn from tonight (their letter is now in the approved shape) and Wyoming's ~95 are
being harvested. Next registers must be the same kind — state outfitter and guide associations that
publish members with mailboxes — not athletics lists, which are the oldest data on the internet.

**Corrected 12 Sep 2026 (measured): the state outfitter-association lane is nearly exhausted, and the next register must be a different KIND.** Harvested and drawn: Montana, Wyoming, Colorado, Alaska and Maine (register bounce rate stays the best we have — 0% on Montana over 48 sends). Probed and NOT harvestable, do not re-check: Idaho (contact form), New Mexico (Airtable widget), Utah (Wix site, directory is a Guidefitter app), New York NYSOGA (mailboxes hidden by Cloudflare anti-bot obfuscation — we do not decode that), Oregon (same), Washington (no public directory), Colorado state licence lookup (search form, no list). The 12 Sep 00:10 wave found sendable people in only four states (Alaska 12, Colorado 24, Maine 12, Montana 24 = 72 sent). The volume that is left sits in OFFICIAL STATE LICENCE FILES, not associations: Texas publishes its whole real-estate licensee register as free bulk downloads (150,000+ rows, by statute) — an estate-agent lane, drawn by the agency letter once RG-0346 gives that letter its console CTA. The sandbox cannot reach trec.texas.gov; the file must be fetched host-side and its columns checked for a mailbox before anything is built on it.

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
