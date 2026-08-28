## 2026-08-27 — CONTAGION-V02-1 (Email Wave Plan v3.2 as a modelled variable, old vs new)

**CONTAGION-V02-1 — the launch simulation now knows about the wave plan.** David asked for the
world simulation to be updated with Email Wave Plan v3.2 and for a button that shows the
difference against the previous version. New file `docs/TrustSquare_Contagion_Model_v0.2.html`;
`v0.1` is left untouched and is now the "old" arm of the comparison rather than a superseded file.

**What v0.1 assumed.** A flat drip: `batch = 28` emails a week, forever, spread proportionally
across every city carrying a scraped pool, wave 2 (US/GB/AU) at week 8, wave 3 at week 20. No
category structure, no per-city cap, no gates, no agency hold. That single lever was the whole of
the injection mechanism.

**What v3.2 actually is, and how it is encoded.** Source of truth read from the canonical board
`MarketSquare/WAVE_PLAN_LAUNCH_2026.html` (not the `Visuals/` index copy — WRONG-FILE-1). Day 0 =
Tue 1 Sep 2026 = model week 0; the four Phase-1 days that fall before launch (28–31 Aug) fold into
week 0. Three groups, each with its own day-offset ladder:

- **Proving cities** (Pretoria, Johannesburg, RUL-057) — offsets −4…+1, the identical six-category
  ladder, strongest first per RUL-058: Tutors → Services casual → Services technical → Experiences
  → Collectors → Stays.
- **Nine SA cities** (CPT·DBN·PE·BFN·EL·PLK·NLP·KIM·PMB) — offsets 0…5, Tutors on 1 Sep then daily.
- **Global three** (New York, London, Sydney) — offsets 0, 3, 4, 5, 6, 7: Tutors on 1 Sep, the
  deliberate hold, then rolling from 4 Sep.

Per-day send = `min(30/cat/city/day (RUL-053), list depth)`. With `measured = 1` the two proving
cities use the 26 Aug counts taken after the STAYS-GEO-1 repair (Tutors 72/82, Services casual
19/32, Services technical 8/17, Experiences 36/3, Collectors 9/6, Stays 6/1) — only Tutors clears
30 in both. Property is out of every singles ladder (RUL-056) and cars gets no cold wave, carried
as a new sampled parameter `catShare` (share of a city's scraped pool that is actually sendable,
prior 0.55 / 0.75 / 0.92). The holistic gates are real: if hard-bounce breaches 5% or the complaint
rate breaches 1.2%, every send at offset ≥ 0 is withheld — the ladder halts where it stands, which
the v0.1 drip could never do. Phase 3 is a hold, not a level: `agGateW` (default week 8) zeroes
agency conversions entirely until traction opens it. `rollW` (default week 26) is the
"from traction →" column — the pool outside the fourteen named cities is only worked after it.

**Schedule validated against the plan's own arithmetic.** Summing the modelled ladder at the cap
with every list full reproduces the volume row on the board exactly:
`60 60 60 60 · 420 330 270 · 360 360 360 · 90 90`. If either the board or the model is edited and
they stop agreeing, that sum is the assertion to re-run.

**Old vs new.** Both plans are simulated on the same seed and the same scenario dials on every
rebuild, so the wave plan is the only difference between the two curves. New `v0.1 drip / v3.2 plan`
toggle in the top bar drives the map, the stats and the diagnostics; a comparison strip under the
top bar shows eight numbers side by side at whatever week is on screen (sellers, ever caught, wave
signups, buyers, cities, countries, MRR, unmailed pool) plus takeoff %; the sellers chart draws the
selected plan solid and the other dashed. Two ensembles now run (110 each, was one at 140).

**What it says — median of 40 seeds, parameters pinned to mid:**

| | wk 26 | wk 52 | wk 104 |
|---|---|---|---|
| v0.1 flat drip | 62 | 112 | 140 |
| v3.2 as written | 21 | 99 | 141 |
| v3.2 + roll from week 4 | 77 | 130 | 140 |
| v3.2 + agencies week 0 + roll week 4 | 86 | 122 | 156 |

v3.2 is roughly three times behind at six months and level by two years. The cause is not the
ladder — it is what the ladder leaves behind. v3.2 fires ~640 mailable prospects into fourteen
cities inside a fortnight and then stops; the v0.1 drip kept injecting for a year and that
injection was holding the number up. The single largest recoverable difference is `rollW`: bringing
the remaining scraped pool forward from week 26 to week 4 puts v3.2 ahead of the drip at six months
(77 vs 62). The agency hold costs less than expected across seeds (21 → 24), because with less
early spread there are fewer cities where an agency has heard of you at all. Ensemble takeoff
91% (v3.2) against 95% (v0.1), with a fatter fizzle tail — the gates can halt the ladder, and there
is no year-long top-up behind them.

**Caveat, unchanged from v0.1:** this is a mechanism model, not a forecast. Nothing is fitted to
observed spread because none has happened yet. The numbers above are a statement about the shape
of the two policies, not a prediction of either.

**Also fixed en route.** The map hover card read the trace snapshot at stride 6 while the snapshot
is written at stride 8, so every hover tooltip in v0.1 showed the wrong city's tier counts. Corrected
in v0.2.

**Verified:** `node --check` clean on the full inline script; the plan schedule reproduces the
board's volume row exactly; headless DOM harness runs the real page script end to end — both
simulations, both ensembles, the toggle in both directions, the comparison strip, and all four
panel tabs — with no exception. Decomposition run over 40 seeds per arm.

**CONTAGION-SPREAD-1 (same session, David's question) — the model cannot report levels, and now says so.**
David asked why the simulation ended a period at `2 / 1 / 0 / 44`. That is the Tier mix readout at week
156 under the **Spam-flag catastrophe** preset with v3.2 selected: 47 sellers, 44 of them agency agents.
Traced and confirmed, three compounding causes: complaint at 4%/seller/week decays deliverability 6% a
week (x0.45 by week 13, x0.20 by week 26, x0.0016 by week 104), cuts word of mouth 56% permanently, and
lifts free-seller churn in a dead city from 10.9%/wk to 18.5%/wk — a 5.4-week seller life. Under v3.2 it
also trips the gate (threshold 1.2%), releasing only **8 of 84 ladder-days** — the four pre-Gate-1 days.
The surviving population is agency agents, which arrive in lumps of ~14 and churn at 0.80x: 44/3 is a
churn-inflow equilibrium, not a decline. Across 40 seeds the catastrophe costs v3.2 more than the drip
(42 vs 49 at wk156) precisely because the gate strands the pool until `rollW`.

The larger finding is a caveat, not a result. Deterministic mid-parameter run at wk104 = **136** sellers;
the ensemble median of the same scenario = **414,708** (p10 2,090, p90 764,453). Three to four orders of
magnitude apart, because transmission is a product of eight uncertain terms and the model straddles R=1 —
so the "mid" run is in neither mode. Fixed where it is read rather than left as folklore: the comparison
strip now shows **Sellers, mid run** and **Sellers, ensemble median** as separate lines, and the binding-
constraint strip raises **"Mid run is not the median"** whenever the two diverge by more than 10x. Backup
`TrustSquare_Contagion_Model_v0.2.html.bak-spread-*`; `node --check` clean and the headless page harness
re-run green (11 strip cells, toggle both ways, all four panels).

**CONTAGION-V03-1 (David's ruling, same session) — no development-stage number throttles the world after launch.**
David: *"do not place our development levels as throttles anywhere, after launch the live data should be
unencumbered, and the spread should be based on how users react to similar apps."* He was right and v0.2 was
wrong in four places. Fixed:

- **`LAUNCH_WINDOW_END`** is now computed from the schedule (week 1). The scraped-list ceiling, the 30/cat/city/day
  cap and the measured PTA/JHB inventory apply inside it and nowhere else.
- **`rollW` default 26 -> 157 (off).** v0.2 worked the leftover pool at `batch = 28/week` — the waves_policy
  pre-launch sending discipline — for three years. After the window there is now no cold email at all; growth is
  organic against the true addressable market. `rollW` survives only as "what would an extra push add".
- **`agGateW` no longer zeroes agencies.** It held ALL agency conversion to zero until week 8; a Phase-3 outreach
  decision was suppressing agencies that would have found us on their own. It now caps the outreach multiplier at
  1.0 before the gate instead of at 0.
- **`catShare`** is scoped explicitly to the cold-email pool — property and cars are out of the singles ladder,
  never out of the market.

**Behaviour re-priored from comparable apps, with sources.** New `bench` provenance tag alongside data/lit/guess.
`churn` .004/.013/.035 -> .007/.011/.025 weekly (a16z: best-in-class marketplaces keep 50-70% of a supplier cohort
at 12 months; Airbnb host revenue retention 90-95% yr2; Etsy new-seller GMS retention 90-107% yr2).
`b2s` .0005/.003/.02 -> .002/.0075/.011 (Poshmark S-1: 41% of first-time buyers also became sellers in year one,
52% by year five; Airbnb S-1: 23% of new hosts started as guests). `buyNeed` 3/12/35 -> 1.4/3.5/16 (disclosed
counts: Poshmark 1.4, Depop 2.2, Reverb 3.6, Airbnb ~13, Etsy 16). `pUp5` .004/.018/.055 -> .0008/.0016/.0035 and
`pUp20` scaled likewise (Lenny's x OpenView x Pendo freemium survey: 3-5%/6mo good, 6-8% great — v0.1 assumed
eleven times the published rate). Two published facts are wired as VALIDITY CHECKS rather than parameters: the
68-91% organic-acquisition band (Nextdoor 68%, Etsy ~79%, Airbnb 79-91%) now raises a diagnostic when the model
falls below it, and Airbnb's "50 markets was too thin, we cut back to ten" raises one against v3.2 opening
fourteen at once. Deliberately NOT invented, because no credible published figure exists: seller activation rate,
time to first listing, lapse rate, marketplace k-factor, views per listing, marketplace seller-subscription take-up.

**CONTAGION-MONEY-1 — "why do we not make any profits?" The MRR line was not the business.**
It summed Starter and Pro subscriptions only. At the 138-seller reading David screenshotted, 98 were agency agents
(FREE by PRICING_CANON 1) and 39 were Free, so exactly one seller was paying — $5/mo, arithmetically right and
commercially meaningless. The till is now modelled from canon: introductions at 1T = $2 paid by the buyer (canon 3),
seller Starter $5 / Pro $20, Agency $0 with a `agSeat` share taking their own $5 seat under RUL-048, and buyer
Global reach $5 (canon 2) — a line entirely absent before, though buyers outrun sellers ten to one. At scale the
split is roughly **introductions 57% · buyer subs 38% · seller subs 5%**: the seller tier ladder is close to
irrelevant to revenue.

Costs added, strictly as FINANCE_CANON states them and no further: Paystack 2.9% + R1 in ZA, merchant-of-record
5% + $0.50 international, and R2,500/mo fixed from month one (accountant + software, RUL-023(a)). Hetzner and AI
spend are **not** modelled — neither has a per-user figure in canon and inventing one would put a guess where a
decision belongs — so the strip reads "Net, canon costs only", never profit. On seed 7 v3.2, net clears zero at
**week 118, ~55 sellers, ~$150/mo**.

**One finding that is David's to rule on.** An introduction is $2 and a merchant-of-record charge is 5% + $0.50,
so **selling Tuppence one at a time burns 23% of revenue at the door**; 2T = 16%, 5T = 12%, 10T = 10%, 25T = 9%.
The Tuppence bundle size is not in PRICING_CANON and it decides whether the introduction business carries its own
fees. Exposed as parameter `bundleT` (1/5/25) with the note saying plainly that this is a pricing call, not a
modelling one, and a diagnostic that fires when fee drag passes 15%.

**What the de-throttled model now says (40 seeds, mid parameters, sellers at 3 years):** v0.1 drip p10/p50/p90 =
576k / 648k / 758k; v3.2 = **290 / 348,636 / 777,867**. The model has gone bimodal — it either never escapes the
cold start or it saturates, with almost nothing between. That reverses v0.2's reading: with dev throttles gone and
behaviour at comparable-app rates, **sustained injection is what reliably carries it over the escape threshold, and
v3.2's single fortnight leaves the outcome to chance.** Still not a forecast, and the spread is the message.

**Verified:** `node --check` clean; headless page harness green end to end after every step; anchor-asserted patches
with backups `*.bak-prev03-*` and `*.bak-precost-*`.

**CONTAGION-V04-1 — the Planner Lane is a loop, not a cost line.** David: *"I don't see the effect of the
Features, how do you simulate the study plans, holidays, weekends etc, those should not just add cost but also
flow over in terms of the listings seen doing them and then using those stays listed there."* Correct — features
appeared nowhere in v0.3 except as unmodelled AI spend. Built from `PLANNER_LANE_DESIGN_2026-08-16_rev2.docx`
and `ai_service_tiers.py`, real numbers on both sides:

| Planner | Tuppence | AI cost | Who | Margin |
|---|---|---|---|---|
| Heritage | FREE | ~$0.01 everyday tier | everyone | -$0.01, the deliberate conversion hook |
| Weekend | 2T = $4 | ~$0.01 everyday tier | any tier | +$3.99 |
| Expedition (Dossier) | 5T = $10 | ~$0.06 heavy tier | $20 Pro only (S3 gate) | +$9.94 |

Five coupled effects, all new: **(1) plan runs** earn fixed Tuppence and cost a compose; **(2) listing slots woven
in** — the design's own words are "sights, food, one stay, listings from the city woven in" — are listings shown to
someone who was not browsing; **(3) a filled slot converts to an introduction**, and the Dossier's designed
"Hand this to a travel agency" button fires one directly, which is the seam the whole travel canon was built for;
**(4) a slot the city CANNOT fill becomes recorded demand** (`wishlist_signals` with result_count = 0, already
stored with category and city) which accumulates per city, decays if unanswered, and **adds to the force of
infection on supply in that city** — a plan that wanted a stay in a town with no stays is an argument aimed at the
person who owns the guest house; **(5) shared plans and printed Dossiers** feed the showcase-reach term. Fill rate
is coupled to the previous week's liquidity, so a thin city writes demand instead of selling supply — which is
exactly the recruiting mechanism, and the diagnostic says so. New lever `featW` (default week 8) because
planners.heritage/.weekend/.expedition ship DARK today.

Effect at week 104, seed 7: with the demand-pull term off, 104,556 sellers; with it on, 574,640. **The flywheel is
worth roughly 5.5x the lane's direct revenue.** New money-strip cells for planner Tuppence, AI compose, and — the
sanity check that matters — **revenue per active user per month**, because a total in the millions only tracks a
runaway population while an ARPU is a number you can argue with. The lane runs at ~$0.73/user/month, which is
arithmetic on `featRun` 0.12 runs/user/week and `featPaid` 0.35; both are guesses and both are flagged as such.

**CONTAGION-RAIL-1 — the rail was ZA-only and it has not been ZA-only since 15 August.** David: *"Why was the
paystack week set to 24? It is already active?"* He is right, and it was a real defect. The model carried
`RAIL_NOW = ["ZA"]` with the rest of the world unlocking when Stripe went live at week 26 — so every seller and
buyer outside South Africa was **unable to pay for the first half-year of every run**, which is a large part of why
the revenue line looked the way it did. **RUL-019 (15 Aug 2026) says otherwise:** "Payments verified
worldwide-capable (Paystack intl enabled + Apple Pay, verified in dashboard): the launch proceeds with WORLDWIDE
reach, not ZA-only; last BACKLOG launch blocker (B1) cleared same session." Nothing was ever set to week 24 —
what David saw at 26 was `stripeW`, and Stripe was shelved on 16 Jul pending ~$500/mo MRR; `africaW` sat at
never. Both are now RETIRED (kept only so old presets do not break) and replaced by a single `liveKeysW`,
default week 0, representing the one gate that genuinely remains and is **David's, not technical**: RUL-019's A10
env pastes, sk_live and the webhook secret. Isolated effect at week 104, planners off: 42 sellers and $0/mo on the
old ZA-only rail against 392 sellers and ~$1k/mo with the worldwide rail — a 9x correction from deleting a
constraint that had already been lifted.

**Verified:** `node --check` clean after every step; headless page harness green end to end; anchor-asserted
patches with backups `*.bak-prev04-*` and `*.bak-prerail-*`. Standing caveat unchanged and now more important:
with throttles gone the model runs above R=1 and reports levels in the millions — read the ARPU and the relative
effects, never the totals.

**CONTAGION-V06-1 — dormancy is not death. The model had a one-way door and David caught it.**
David: *"Why does the kept numbers decline at all? A user once would always be a good prospect to use one of the
features or buy a second time, or decide to sell, take a vacation?"* He is right, and the offending line was a
guess dressed as a fact. v0.1 carried `immune` at **0.78** with the note *"a seller who tried it and left will not
try again"* — so 78% of everyone who ever stopped listing was deleted from the world permanently, and a
registration that never listed went to the same place. Nothing in the published cohort data supports that:

- **Etsy new-seller GMS retention is 90-107% in year two and 59-132% in year four.** A cohort cannot exceed 100%
  if leaving is permanent — those are people coming back and spending more.
- **Airbnb host revenue retention runs 90-95% in year two.**
- **Poshmark buyers were still crossing over into selling in year FIVE** (41% year one, 52% by year five) — long-tail
  conversion of people who arrived long before.

Restructured. `immune` is re-priored to **0.03 / 0.10 / 0.25** and relabelled "of those who stop, the share TRULY
lost" — moved, died, or a bad enough experience to refuse. Everyone else goes to a new **dormant** compartment,
and lapsed registrations go to a new **warm** compartment instead of the grave. Three new parameters: `react`
(dormant back to listing, .004/.012/.040 weekly — mid is about half a dormant cohort returning within a year,
which is what Etsy's above-100% year-two cohorts require), `reactWarm` (registered-never-listed, colder), and
`reactFeat` (the planner lift on coming back). Dormant and warm people **count as planner users** — they open the
app for a holiday with no intention of selling, and that is the way back in. Returning dormant sellers do NOT
increment "ever caught"; a warm registration listing for the first time does.

**What the one-way door was costing** (v3.2, seed 7, sellers listing):

| | wk 26 | wk 52 | wk 104 | wk 156 |
|---|---|---|---|---|
| v0.5 — 78% of leavers gone forever | 519 | 253,122 | 511,767 | **289,967** |
| only the `immune` prior fixed | 1,324 | 389,701 | 498,595 | 286,777 |
| + dormant people come back (v0.6) | 909 | 348,585 | 738,343 | **710,104** |

The decline David was pointing at was the artefact. With the door open the curve **plateaus instead of falling** —
43% off the peak by year three becomes roughly flat. Fixing the prior alone does almost nothing; it is the return
trip that holds the population, because a leaver going back to "susceptible" still has to be re-caught from
scratch, while a dormant person just needs a reason.

New **Dormant** cell in the top bar, dormant and truly-lost rows in the comparison strip, and the "Caught vs kept"
diagnostic rewritten to report the number that actually matters: at week 156 you still **hold 91% of everyone who
ever listed**, where the active-only reading says 62%. It also surfaces the warm pool by name — registered, never
listed, the warmest list in the app, and nothing in the product currently speaks to it.

**Telemetry consequence worth acting on:** none of this is measurable today. There is no `cancelled_at`, no
`returned_at`, and no dormancy concept anywhere in the schema — the app cannot currently tell a churned seller
from a quiet one. That is now the highest-value missing instrument in the Telemetry tab, because the whole shape
of the curve above turns on it.

**Verified:** `node --check` clean; headless page harness green; backup `*.bak-predormant-*`. Levels remain in the
runaway regime and remain unreadable as forecasts — the finding here is the SHAPE (decline becomes plateau), not
the number.

**CONTAGION-V07-1 — David asked whether the model is tilted optimistic. It was, and the mechanism was findable.**
A full one-at-a-time sensitivity sweep (63 parameters, low to high, 16 seeds each) plus a joint-scenario sweep.
Two structural causes found and fixed, and the answer is not "one bad number".

**Cause 1 - the sampler drifted above our own assumptions.** The uncertainty sampler was triangular, mean
(lo+mid+hi)/3. Our mids sit at a mean position of **0.336** within their own ranges, so every draw came out above
the central assumption printed in the panel - and the model multiplies eight such terms. That is the entire
explanation for the previously baffling "mid run 136 vs ensemble median 414,708". Replaced with **PERT**, mean
(lo+4*mid+hi)/6, via a Marsaglia-Tsang gamma -> beta sampler. Verified numerically on lo=.001/mid=.003/hi=.02:
triangular mean 0.0080, PERT mean 0.0055, theory 0.0055. Drift cut from 2.7x the stated mid to 1.8x.

**Cause 2 - there was no incumbent.** The model had a hypothetical clone arriving at week 12 and nobody already
sitting in the categories. **SA Competition Commission OIPMI final report (July 2023)**, subpoena-backed and about
exactly this market: Property24 >50% of property listings, AutoTrader + Cars.co.za >80% of vehicles, top percentile
of platforms taking 70-80% of BOTH paid and organic SA search. Gumtree SA did NOT shut down - Adevinta sold it to
Impresa Capital in July 2022 and it is the surviving generalist incumbent. Two parameters added: `incumbent`
(.30/.60/.85, data) removes the held share from the addressable market, and `entrantPen` (.20/.45/.70, lit) applies
the second-network penalty from **Brown & Morgan's** field experiment - identical goods listed on eBay and Yahoo
simultaneously, eBay revenues 20-70% higher, and changing the product changed nothing. Counterweight recorded in
the note: **Ellison & Fudenberg (QJE 2003)** - these markets do not simply tip, they have a broad plateau where two
survive, and tip only below a critical size.

**Re-priors from documents that were verified this session:** `churn` .007/.011/.025 -> **.013/.016/.025** from
**Angi's** disclosed monthly pro churn of 5.8-7.2% over four quarterly years - the only listed local-services
marketplace that publishes it, and it replaces an a16z venture-portfolio survivor band. `buyGlobal` .01/.04/.09 ->
**.008/.018/.05** from the **Care.com FY2018 10-K**, the one real disclosure of a demand-side-pays marketplace at
scale: 1.8% of registered families paid, $39/mo, 11.3-month tenure, 43% of revenue back out as marketing (and an
FTC order in 2024 for not being upfront about how contact works - the cautionary half of the same comparable).

**What the sweep says now.** No single parameter can make the model fail, because the central case sits ~100,000x
above the takeoff threshold - but joint scenarios fail readily: everything at low = 1 seller; the four biggest
drivers at low = 70; incumbent .85 + entrant penalty .70 + Angi high churn + public exposure low + planner lane
dark = 13. The central case of 277,396 sellers at two years is not a credible forecast and the document says so.
**Six of the top ten drivers remain pure guesses** - `smeDen` (#1), `featRun` (#2), `featPull` (#4), `impr`/`pubBeta`
- and the research established that no company anywhere publishes views-per-listing or organic reach per seller,
so those must come from our own instrumentation.

**A strategic finding recorded as a model diagnostic, not an opinion.** Of ~20 marketplaces in the only real
practitioner sample, every one but Thumbtack constrained categories at launch (Etsy 3, TaskRabbit 3, Eventbrite 2);
we launch with 7. Thumbtack's founder says breadth was a FREQUENCY fix - "from once every couple of years to 8-12
times a year" - and that they went unfunded for years because of it. The diagnostic now states the answerable test:
does the seven-category bundle put one household at ~10 transactions a year, and do the seven share a buyer?

**Six premises corrected before they reached the model** (from the comparables research): Airtasker publishes no
cohort retention curves; the FTC redacted every HomeAdvisor conversion rate; Schibsted Marketplaces is now Vend
Marketplaces ASA; Adevinta's post-2024 accounts are at UK Companies House with no segment note; Trade Me has no
FY2019 report but Apax's holdco files audited accounts; Gumtree SA was never in the Permira/Blackstone deal. A
list of laundered numbers now circulating (the "90% SA smartphone penetration", the Statista SA e-commerce values,
Version One's "30-60% liquidity", CB Insights' "no market need 35%") is recorded in the research file as
do-not-use.

**Deliverable:** `MarketSquare/Simulation Accuracy Review - nice.docx` (Professional Navy house style) carrying the
sensitivity findings, the ranked remaining optimism, the five calibration sources with what each actually
discloses, and a five-item ordered next-step list led by instrumentation. Also: David's hesitancy about mentioning
the RUL-048 agency $5 seat was misplaced - it has been modelled as `agSeat` since v0.3 and does not appear in the
top sixteen drivers.

**Housekeeping:** a research agent left `C:\Users\David\Downloads\_cbi_chart.png` (92KB); the FUSE mount blocks
deletion, so it needs removing host-side.

**Verified:** `node --check` clean; headless page harness green; PERT mean checked numerically against theory;
backup `*.bak-prev07-*`.
