# BOTs — Bolted On Terminals

David's idea, 7 Sep 2026: *"an on-phone remote-console stand-alone micro app, with a singular
modified function."* Its own icon, its own colour, one job, and a genie you talk to.

**Status: DESIGN ONLY. Nothing deployed. No line in `deploy_manifest.txt`. Not launch scope.**

## What a BOT actually is

Not a new app. TrustSquare is ALREADY an installable app — PROBED live 7 Sep 2026:
`/static/brand/site.webmanifest` returns 200 as `application/manifest+json`, and all three icons
(192, 512, maskable) return 200 as PNGs. So the home-screen icon already works.

A BOT is therefore **one more manifest file** pointing at the same app with a different
`name`, `theme_color` and `start_url`. Same code, same server, same login, same Trust Score.

To make one real, three things:
1. a `.webmanifest` (in this folder, ready)
2. three icons in the BOT's colour under `/static/brand/bots/<bot>/`
3. the app reading `?bot=` at boot and opening in that persona — `location.search` is already
   parsed in two places, so this is a branch, not an engine

## Two gaps found on the live site, both worth fixing regardless of BOTs

| Gap | Effect | Size |
|---|---|---|
| No `apple-mobile-web-app-capable` / `-status-bar-style` meta | On iPhone the home-screen icon opens **inside Safari with the browser bars**, so it does not feel like an app. This kills the whole illusion. | 2 lines in `marketsquare.html` |
| No service worker registered (`serviceWorker.register` absent from the live page) | Android Chrome will not **offer** to install; the user must find "Add to Home screen" in the menu. | ~half a day; `APP_PREVIEW.html` already has working SW + push code to lift from |

Neither is a BOT feature — both make the existing app better on a phone today.

## Voice is free, and that is the surprise

`webkitSpeechRecognition` (listening) and `speechSynthesis` (speaking) are built into the phone.
No licence, no per-minute bill. Android Chrome and iOS Safari 14.5+.
UNVERIFIED and worth testing on a real device before promising it: whether the microphone works
in **standalone (installed) mode on iOS**, which has historically been flakier than in Safari
itself. Test on David's phone before this is designed around.

So a spoken conversation costs only the thinking: 3–4 short AI calls, about **3 cents per whole
conversation** at the pessimistic price in `Genie Cost & Profit Impact — nice.docx`. That paper's
figures stand — a BOT conversation is a handful of wishes, not a new class of spend.

## Files

- `collector/BOT_COLLECTOR.html` — BOT #1, running. Real microphone, real slot-filling, David's
  exact Serra Angel conversation on a button.
- `seller/BOT_SELLER.html` — BOT #2, running. The real Listing Rating out of `bea_main.py`,
  coached one question at a time.
- `homehelp/BOT_HOMEHELP.html` — BOT #3, running. Housekeeping registration: the green circle,
  the spoken sign-up, the weekly openings, her area, and the employer link. See the section below.
- `collector/collector.webmanifest`, `seller/seller.webmanifest`, `homehelp/homehelp.webmanifest`
  — ready, not deployed.

## The build order I would argue for

**Collector proves it, Seller banks it.** The Collector BOT is the demo and it is what David asked
for. But the number that is zero is *people publishing a listing*. A green "Sell it" icon that
turns ninety seconds of talking into a live advert is the one that moves the business.

---

## PRICING — RULED (RUL-108, David, 7 Sep 2026)

**Settled. BOTs are a Pro-tier inclusion, not a new price.** David: *"i dont want to charge $20 for
the function, i want to add it to the $20 tier as a free function there."*

- BOTs carry **no price of their own**. When built they are included in **Pro, $20/mo, 30 slots** —
  the tier exactly as it already stands. No new tier, no add-on, nothing in `PRICING_CANON.md` changes.
- **The selling BOT is free to every tier, Free included.** Not merely "not charged extra" —
  deliberately un-gated. The zero number is people publishing.
- **A watch is not a priced feature.** It already earns 1T when it fires and the buyer asks for the
  introduction.
- **What Pro buys:** the work with no introduction at the end — portfolio valuation, bulk listing,
  cross-market price intelligence. `ai_service_tiers.PAID_FEED_FUNCTIONS` already gates that class
  to Pro, so the paywall exists and is in the right place. BOTs make it worth buying.
- **Nothing ships on this.** No BOT exists; no seller-facing surface may advertise one until it does
  (RG-0267).

The arithmetic that supports it is below, kept because it is the reason this is the commercially
right answer and not merely the generous one.

## The workings (recorded 7 Sep 2026)

**David's question, not yet ruled.** Pricing is commercial positioning and is reserved to him
(RUL-037 / RUL-096(f)). This records the recommendation and the arithmetic behind it so the next
session does not re-derive it.

### Claude's recommendation: split it, and do NOT add a new $20 line

**1 · Never charge to LIST.** The Seller BOT must stay free to everyone. The number that is currently
zero is *people publishing a listing*; 65% of sellers are on Free. Charging admission to an empty shop
is the one move that cannot work. `TrustSquare_Revenue_Bridge.docx` is explicit that subscription is
the smallest slice (14% in the new model) and supply is the variable everything else rides on — a
paywall in front of supply discounts the big slice to grow the small one, backwards.

**2 · Do not charge for the watch either.** "Tell me when an Alpha Serra Angel is listed" already
monetises itself: when it fires and the collector wants the seller's identity, that IS an introduction
and already costs 1T. Charging $20 for the watch AND 1T for the introduction is double-dipping the same
event, and it is off-model — MarketSquare's till only takes Tuppence (core constraint, 1 Aug 2026).
At 5% of buyers keeping a watch that is ~1,266 introductions = **$2,532/mo**, earned with no new price.

**3 · There is already a $20 tier — Pro.** A second $20 charge sitting beside it is confusing and
invites exactly the pricing drift `PRICING_CANON.md` exists to prevent. **Make BOTs the reason to be
Pro, not a new line item.**

**4 · What genuinely deserves paying for:** the things with no introduction at the end —
"value my whole collection", bulk-list 40 cards in one conversation, cross-market price intelligence,
a standing portfolio watch. Those are the paid-AI class, which `ai_service_tiers.PAID_FEED_FUNCTIONS`
ALREADY gates to Pro. The paywall exists and is in the right place; BOTs just make it worth buying.

### The prize, measured (Year-1-end scale, Cost_Breakdown_GlobalLaunch.xlsx)

| Pro adoption | Extra Pro sellers | Extra revenue/mo | On subscriptions |
|---|---|---|---|
| 8% (today's plan) | — | — | $22,202 base |
| 11% | +234 | +$4,674 | +21% |
| **15%** | **+545** | **+$10,906** | **+49%** |
| 20% | +935 | +$18,696 | +84% |

Cost to serve BOT conversations to 1,169 Pro sellers (20 conversations each, 4 AI calls each, at the
pessimistic $0.01/call): **$935/mo**. So roughly **12:1** at the 15% case.

### Answered

David ruled it into Pro the same night (RUL-108, above). The separate-subscription option is dead and
should not be re-proposed: buyer subscriptions top out at $5 today, so a second $20 product would have
been a new axis rather than an increment, needing `PRICING_CANON.md` §2 and `_buyer_tier` in
`bea_main.py` amended together.

**Still open, and genuinely David's when the time comes:** whether Pro's price or slot count should
move once BOTs are actually built and their pull on Pro adoption is measured. Not before — that is a
decision that needs data, and there is none yet.

---

## THE PA TIER — David's direction, 7 Sep 2026 (recorded, not built)

David: *"For the $20 tier we will have super feature BOT's, to perform PA type functions like...
i want to buy a home as an investment... i will be in London the 23rd, what sites can i visit that
weekend... i need to sell my BMW on short notice... i need to get a plumber urgently (free), but he
must first give me a quote and have a TS of better than 85."*

This is a different animal from a wish. A wish is one question. **An errand is a piece of work with
judgment in it.** The direction is right; three things about it need to be got right or it fails
expensively.

### 1 · His four examples are NOT equal — two need no supply at all

PROBED live, Pretoria, 7 Sep 2026 (`/listings?city=Pretoria&category=…`):

| Example | Stock behind it today | Verdict |
|---|---|---|
| **"Sell my BMW on short notice"** | none needed — it is a *plan*: price to move, what to fix first, which agents to be introduced to | **Works today** |
| **"London on the 23rd"** | none needed — the output is a trip brief handed to a partnered agency, which IS the introduction (travel positioning, 1 Aug 2026) | **Works today** |
| **"Buy a home as an investment"** | 19 property listings, **median trust 45**, only 1 above 85 | Thin |
| **"Plumber urgently, TS > 85"** | **2 services listings in Pretoria. ZERO above 85.** | **Returns nothing** |

Marketplace-wide in Pretoria: 65 listings, median trust 85 — but 36 of them are Adventures (the
seeded journey content). Services has two. **The PA tier should launch on the two errands that need
no stock**, exactly as RUL-097 parked the category ring until the shelves justify it. An assistant
that answers "I found nobody" twice is uninstalled.

### 2 · The cost shape changes completely, and the existing ceilings break

An errand is 30-300x a wish (`AI_BASELINE.json` worst cases):

| Errand | AI calls | Cost | Share of the $0.50/day per-user cap |
|---|---|---|---|
| A wish (last night's number) | 1 | $0.001 | 0% |
| "Plumber urgently" — a shortlist | 4 | $0.012 | 2% |
| "Sell my BMW" — a plan | 7 | $0.046 | 9% |
| "Buy a home as an investment" | 10 | $0.081 | 16% |
| "London on the 23rd" — a dossier | 14 | **$0.295** | **59%** |

**Two collisions, both real:**
- **Per-user:** the $0.50/day cap allows **1.7 dossier errands a day**. A paying Pro customer gets
  cut off on their second. That is the worst experience the product could deliver.
- **Platform:** 1,169 Pro users (Pro at 15%) doing 12 dossier errands a month = **$4,136/mo = 138%
  of the $100/day platform cap**.

**And the cap cannot simply be raised.** A $20/mo customer is worth $0.667/day. At a $1.50/day
ceiling the worst case is $45/mo of AI against $20 of revenue — **negative margin**. Raising a daily
dollar ceiling to fit errands turns a 96% margin business into a loss-making one for its best
customers.

### 3 · The fix is an ERRAND ALLOWANCE — *not* Tuppence

**SUPERSEDED SAME NIGHT.** The paragraph below originally recommended metering errands in Tuppence.
Running the numbers killed it: Pro's 10T allowance is worth **$20 — the entire subscription price** —
so an errand costing 1T consumes **$2.00 of introduction currency to deliver 1-30 cents of compute**
(7x to 169x its cost), and every errand a Pro user runs is **an introduction they do not make**.
Introductions are 33% of revenue and the engine the model rides on. At Pro 15% there are 11,680T/mo in
play; if half went on errands that is **$11,680/mo of introduction volume displaced** to save a few
hundred dollars of compute. The cure costs seventeen times the disease.

**The recommendation is now: count errands, not money and not Tuppence — "10 assistant errands a
month, included in Pro".** Worst case (every errand a full dossier, every month) **$2.95 per customer
= 85.3% gross margin**; realistic blend ~$1.00. It cannot overspend, it needs no new price, and it
leaves the introduction currency alone. Full workings: `BOT Financial Model — nice.docx`.

The superseded reasoning, kept because the machinery argument was still right:

**~~Meter errands in Tuppence, not in dollars per day.~~** Pro already includes **10T a month**
(`launch_redemption.py TIER_TUPPENCE_MONTHLY`, PRICING_CANON §1). Make a PA errand cost Tuppence and
Pro's existing allowance IS the PA allowance:

- It honours RUL-108 exactly — the errands are **included in the $20**, not charged extra.
- It is **fixed, not ad-valorem** — the 1 Aug pricing rule.
- It is **self-limiting**: 1,169 Pro users x 10 errands = ~$3,390/mo of AI against $23,380/mo of
  revenue, **14.5%**, and it cannot run away because the allowance is the fence.
- It uses machinery that already exists — no new meter, no new ceiling logic, no new price.
- A heavy user who wants more buys Tuppence, which is the till the whole business runs on.

**RESERVED TO DAVID (RUL-105 precedent — raising an AI ceiling is spending money):** the platform
daily cap almost certainly has to move from $100 before a PA tier ships, and the per-user daily cap
should become tier-aware rather than one number for Free and Pro alike. Both are money decisions.
Nothing here changes either.

### 4 · The genuinely new product idea buried in his fourth example

*"He must first give me a quote"* is not a filter — it is **a quote before the introduction**.
Sellers are anonymous until an introduction is accepted, so an anonymous quote is both possible and
better than what exists: the buyer knows the price before deciding to meet, and the introduction is
worth more because it is qualified. That is new machinery (a quote request, a quote reply, a
comparison), not a BOT feature, and it would serve the whole marketplace rather than just the PA
tier. Worth a spec of its own if David wants it.


---

## BOT #3 — HOME HELP · housekeeping registration (David's direction, 9 Sep 2026, BUILT as a prototype)

David: *"a Click - register a service - list Listing for the South African huge house cleaning
market. Again a single Service icon with a similar Round (maybe Green) circle with a hotel room
being cleaned AI photo (also randomly changed)... she can also on a weekly schedule give her
openings for other people needing houskeeping, and her area should be clearly visisble."*

Built the same night as a working picture: `homehelp/BOT_HOMEHELP.html`.
Design only — nothing wired, no flag, no line in `deploy_manifest.txt`, not launch scope.

### The probe that decides whether this works

**PROBED live 9 Sep 2026**, before building anything: `GET /listings?category=services` returns
**two** listings for the whole country — a certified electrician and a garden service, both in
Pretoria, both seeded examples, both trust 85. **There is not one cleaner, housekeeper, laundry or
ironing listing on TrustSquare.**

| Measured | Number | Source |
|---|---|---|
| Domestic workers employed in South Africa | **831,000** | Stats SA, QLFS Q2 2026 |
| Before the pandemic (Q4 2019) | ~1,000,000 | ~150,000 posts never came back |
| Listed on TrustSquare | **0** | Probed 9 Sep 2026 |

### Why this beats both earlier BOTs, and it supersedes my own 7 Sep recommendation

I argued "Collector proves it, Seller banks it" on 7 Sep. Housekeeping beats both, for one reason
neither of them has: **the supply already exists, already has a phone, and already has somebody
who will vouch for her.** A person selling a bakkie arrives with no evidence. A housekeeper arrives
with an employer of three years who can confirm her in one tap.

### The employer link is the mechanism, not the convenience

David framed it as a convenience — she gives her employer a link so they can book her. It does
three jobs:

1. **It solves the cold start.** The Trust Score has to be built out of something. Here the
   evidence walks in with the worker: a real person outside the platform standing behind her
   claim. That is the Verified Evidence Ladder working as designed.
2. **It recruits the demand side free.** Her employer taps the link and lands on a marketplace
   where they could also find a gardener, a tutor, an electrician. Every worker who registers
   brings one to three middle-class households in, warm, at no acquisition cost.
3. **It fits the money model with nothing new to build.** Listing is free (RUL-108 un-gated the
   listing BOT for every tier). Her existing employer books her **free** — there is nothing to
   introduce, they already know each other. A **stranger** asking for her open Wednesday is a real
   introduction and costs **1 Tuppence**, fixed, not a percentage. Nothing but Tuppence goes
   through the till, and wages are settled between them exactly as they are today. The moment a
   platform touches a domestic worker's wages it becomes an employment agency; an introduction
   service does not.

### What the app already gives her, measured

`_import_quality_score()` on the services branch: the trade is worth **25**, a description of
15+ words another **25**, a real price **6**, a suburb **4**, first photo **10** then +8 each.
So **she is listed at 60/100 after four spoken answers and no photograph at all** — and the
fifteen-word description, the single thing most likely to make somebody abandon a listing and
worth a quarter of the score, is written FOR her out of what she said. Scorer in the prototype is
a faithful copy; if it ships the BOT asks the server. One scorer, never two.

### Two gaps this BOT found — flagged, not changed

| David asked for | Today |
|---|---|
| **Her openings on a weekly schedule** | Nothing there. Listings have no concept of a recurring free day; the two seeded service listings say "weekday availability" in their *description text*, which no filter can read. For a housekeeper the free day **is** the product. |
| **Her area clearly visible** | One suburb, worth 4 points. She has two geographies that both matter: where she *lives* and the five suburbs her taxi route *reaches*. A buyer in Faerie Glen cannot find her by searching Mamelodi. |

The fix is small and it is the difference between beautiful listings and findable ones: two fields
on a service listing — `open_days` (seven booleans) and `serves_suburbs` (a list) — and one search
filter, *"housekeeping, Menlyn, Wednesday"*, which is the only search anybody looking for a cleaner
ever runs. Touches the listing schema and the search filter, so not in launch month.

### The one thing I would gate, and would argue hard for

Letting a stranger into your empty house is the highest-trust transaction this marketplace will
ever carry. **A housekeeper is listed immediately, but until one employer confirmation or an ID
check lands, only people she has sent her own link to can contact her.** She loses nothing — her
existing employers are exactly who she wants on day one. It also protects her, which matters more
and is easier to forget: publishing a woman's open days and her suburb to anybody at all, with no
accountability on the other side, is not a service to her. Built into the prototype.

### The wage floor, checked out loud

From **1 March 2026** the national minimum wage is **R30.23 per ordinary hour** and it applies to
domestic workers on the same footing as everyone else; the BCEA four-hour rule makes the practical
floor for a short day **R120.92**. The BOT does the arithmetic in front of her — "R350 for eight
hours is R43.75 an hour, that is above the minimum" — and **refuses to publish a rate below it**,
offering the legal number instead. Verified in the rendered prototype: R150/day is refused with
"shall we put it at R242?". This is not a compliance chore; it is the clearest possible signal
about what kind of marketplace this is, and it costs one comparison.

### Cost

| Job | AI calls | Cost |
|---|---|---|
| One wish (measured 7 Sep) | 1 | $0.001 |
| **Register a housekeeper** | 4 | **$0.04** |
| A travel dossier errand | 14 | $0.295 |

A thousand housekeepers registered costs about **forty dollars** at the pessimistic penny-a-call
price, inside the existing daily ceiling without touching it. The cheapest supply the platform can buy.

### Decisions taken rather than handed back (RUL-037)

- **Colour.** David asked for green; green was already spoken for by Sell It (`#2F8D5C`). Home Help
  takes a brighter jade `#16A97C` — reads as clean rather than as money. **Sell It moves to
  TrustSquare gold when it gets built**; it has no icons yet, so that costs nothing.
- **Where the circle lives.** Both places, same circle: the BOT's own home-screen icon, and one
  green circle inside the app's Services category.
- **Language.** en-ZA / af-ZA / zu-ZA selectable, because the phone does recognition free.
  UNVERIFIED and worth twenty minutes on a real handset: Sepedi, Xitsonga and isiXhosa are not
  reliably offered, and the microphone in installed (standalone) mode on iPhone has always been
  the flaky one.

### Art — SUPERSEDED, see the second pass below

*(First pass used four drawn placeholder scenes. David rejected them the same night. Replaced with
our own AI photographs — see "SECOND PASS" at the end of this file.)*

### Verified

Rendered in a real browser and driven end to end on 9 Sep 2026, not merely written: the scripted
conversation reaches 60/100 and publishes; Mon/Tue read as taken and Wed/Fri as open out of one
sentence carrying both; the employer confirmation lifts trust 38 → 85; the wage floor refuses
R150/day. Console clean.

### Reserved to David

Whether housekeeping goes **ahead of** the Collector and Sell It BOTs in the build order. My answer
is yes, and the reason is the probe at the top of this section.


---

## BOT #3 — SECOND PASS, same night (9 Sep 2026). Two faults David found, both fixed.

David, on the first prototype: *"The idea is good, the photos can again be the AI generated photos
we have for the current services, no none photos please. And the AI did not understand Moreleta
Park, written or spoken."*

### Fault 1 — the drawn art, and the answer that was already on disk

The first pass drew four flat SVG scenes. Wrong: we own a real AI photo library and the whole
project's look comes from it.

First correction reached for `static/super/` — the electrician and garden photos behind the two
live service listings. Right library, **wrong trade**: a distribution board under a heading that
says "Housekeeping" is worse than a drawing of a bed.

The right answer was one folder further on, in **`assets/super/`**, and it reframes the product:

> **A housekeeper does not sell the cleaning. She sells the room afterwards.**

So the circle now carries five of our own photographs of South African rooms — a lodge room made up
at sunset, a bedroom, a bathroom, a lounge with jacarandas through the window, a kitchen. Every one
is a room *after it has been done*. Embedded as data URIs, so the file needs no network and nothing
is ever blank. Random on open, a new one every five seconds.

**Nothing needs generating and nothing needs paying for.** The Higgsfield prompts stay written down
for the day somebody wants a person in frame, but they are no longer on the path.

### Fault 2 — "the AI did not understand Moreleta Park, written or spoken"

Reproduced in a browser. Worse than it looked — three defects, not one:

| Defect | What David saw |
|---|---|
| It never said the name back | The suburb WAS stored, but the BOT went straight to the next question. Indistinguishable from being ignored. |
| A hard list of 15 suburbs | Moreleta Park was on it; Mabopane, Midrand, Olievenhoutbosch were not, and failed silently. A list can never be long enough. |
| Exact matching vs speech | The phone hears "Morelia Park" and an exact match fails — the spoken version of the same bug. |

**Fixed at class level, not instance level.** The list is now only a *spelling aid*, never the gate:

- Anything after **stay in / live in / work in / from / near** is accepted as a place, known or not.
- A near-miss is **snapped to the closest known name** (Levenshtein, tolerance by length) — so
  "Morelia Park" resolves to Moreleta Park.
- The **verb decides the meaning**: *stay* → her home, *work* → a suburb she travels to, both in one
  sentence if she says both.
- The bare name on its own works: typing just "Moreleta Park" is understood.
- A place must sit behind a preposition — without that rule "I work **for** Mrs van Wyk" turned a
  person into a suburb, which it did on the first run and now does not.
- It **says the name back**: *"Moreleta Park. Got it — that is your area on the listing."*

Nine cases pass, written and spoken-style, in a rendered browser.

### And a finding worth more than the bug: the suburb seed has no townships

The spelling aid is now the app's own **`assets/suburbs_seed.json`** — 119 suburbs across twelve
cities. Reading it exposed something that matters well beyond this BOT:

**It contains almost no townships.** Arcadia, Brooklyn, Waterkloof, Centurion — but not Mamelodi,
Soshanguve, Mabopane, Tembisa, Khayelitsha, Umlazi, Chatsworth, Mdantsane.

The seed lists **where the work is, not where she lives**. Every housekeeper on the platform would
have hit it. The prototype carries the townships in its own list; **the real fix is the seed file
itself**, and it reaches search, CityLauncher, and anything else that reads it. Flagged, not
changed — it is a data file that other lanes consume, and this is launch month.

### RUL-114 — "no none photos" is now a ruling

David's four words closed a hole Claude had flagged on the Sell It BOT on 7 Sep and left with him:
`_import_quality_score()` lets a listing with **zero photographs** clear the 50-point publish bar at
60/100, because the facts alone are worth 60.

**One photo is now a floor under publishing**, not merely worth ten points. Built into this BOT: at
60/100 with no picture the button reads *"One photo first — then you are listed"* and stays
disabled. It binds hardest here — nobody lets a stranger into an empty house off a listing with no
picture — but it is a **class ruling**: every category, every BOT, and the publish gate itself.
Drawn or placeholder artwork does not satisfy it.

The live publish gate is NOT moved in launch month. Written to RULINGS.md so the next session builds
to it instead of re-deciding it.

### Verified, second pass

Rendered browser, end to end: nine place cases pass; the BOT says the suburb back by name; the
scripted conversation reaches 70/100 with one photo attached and publishes; at 60/100 with no photo
the publish button is disabled and says so; employer confirmation lifts trust 38 → 85; the wage
floor still refuses R150/day and offers R242. Console clean.


---

## BOT #3 — THIRD PASS, same night (9 Sep 2026). The vouching gate, built.

David, on the safety rule Claude had put in as a single sentence: *"This is a great idea... This
also protects her, which matters more and is easier to forget. A listing that puts a woman's open
days and her suburb in front of anybody at all, with no accountability on the other side, is not a
service to her."*

So it stopped being a sentence. There is now a fifth screen — **A stranger** — which is the
marketplace seen from the other side, before and after somebody vouches.

### Absent, not greyed out

**Before any vouching:** a buyer searching *"housekeeping, Menlyn, Wednesday"* does not see her.
Not a locked card, not a blurred profile — **not there**. A visible-but-useless listing still leaks
her free days and her area to anybody who looks, which is the exact harm the gate exists to stop.

**After one employer confirms her:** she appears, at 85, with an introduction worth 1 Tuppence.

### Building it turned two tiers into three

Asking *which* facts should ever be public produced an answer that is not "all of them, once vouched".

| Tier | What | Why |
|---|---|---|
| **Public** once vouched | The trade, **the suburbs she travels to**, her rate, her free days, her rating, her photos | Everything a buyer needs to decide. Nothing that locates her. |
| **On acceptance** of an introduction | Her full name, her phone number, **the area she lives in** | This release IS what the Tuppence buys — and she can refuse it. |
| **Never published** | Her ID document, and **the identity of the employer who vouched** | Load-bearing. See below. |

**1 · Publish where she works, not where she lives.** A buyer in Menlyn needs to know she can *get
to* Menlyn on a Wednesday. They do not need to know she lives in Mamelodi — and the first version
published exactly that as her main area. Home suburb is now used for matching, shown to her, and
released only on acceptance.

**2 · The employer who vouches is never named.** The listing reads *"confirmed by an employer of 3
years"*, not *"confirmed by Mrs van Wyk"*. If vouching cost the employer their own privacy, far
fewer would do it — and the cold start dies with it. The confirmation is the evidence; the
voucher's identity is not part of what a buyer needs.

**3 · Taken days show as unavailable, never as whose house.** Which household employs her on a
Monday is not something the marketplace publishes.

### What it costs her: nothing

Day one the people she wants are her own employers, and they are precisely who her link goes to.
The gate holds back only strangers, and one tap from somebody who already knows her opens it.

### Ruled

**RUL-115.** Written as a class ruling, not a Home Help feature: any category where a seller admits
a stranger into their home, or is themselves exposed by their own listing, inherits it.

### Verified, third pass

Rendered browser: before vouching the stranger view shows the locked state and the DOM contains
neither her home suburb nor the voucher's name; after vouching she appears with her travel-to
suburbs, her free days and the introduction button, and the DOM still contains neither her home
suburb nor the voucher's name. Everything from passes one and two still passes — nine place cases,
70/100 with one photo, the photo floor at 60/100, the wage floor refusing R150. Console clean.

---

## FOURTH PASS (9 Sep 2026) — the colour system, for all seven categories

David: *"i also love the green full phone screen, this can also be done with the other categories,
but different colors for each?"*

Board: **`BOT_FAMILY.html`** — all seven as full colour-washed phone screens, each with a real
photograph from `assets/super/`, plus the measurement behind the palette and a toggle on the eighth.

### The colours were already decided — and they fail as icons

`BRAND_ASSETS.md` carries seven app tile colours from the `CATS` config. Reused, not re-invented.
But those tiles sit *behind a photograph inside the app*, so they are deliberately dark and
recessive. As icons on a home screen, measured with **CIEDE2000**:

| Pair | ΔE | Reads as |
|---|---|---|
| Tutors / LocalMarket | **6.1** | the same colour |
| Tutors / Adventures | 6.7 | the same colour |
| Adventures / LocalMarket | 11.1 | too close |
| Property / Cars | 11.3 | too close |

**6 of 21 pairs collide.** Three of the seven are green; two are near-black navy; lightness runs
L* 9–37, so on a dark home screen they are seven dark squares.

### The sibling palette — 0 of 21 collide, closest pair ΔE 22.8

Each BOT keeps the hue its category already owns (hue assignments taken from the explainer video's
pastel set — David's own pick, which had already separated blue/green/peach/teal/sand/periwinkle/
pink), pulled to icon strength.

| BOT | Icon colour |
|---|---|
| Property | #2E86E0 |
| Cars | #5B4BD6 |
| Tutors | #4FA83F |
| Services | #B4441F |
| Collectors | #C98A2E *(as set 7 Sep)* |
| Adventures | #12A5A5 |
| LocalMarket | #D8447E |

The app tiles do not change. This is a second palette, for icons and BOT screens only.

### The rule — so no BOT colour is argued about again

- **Hue** comes from the category. Canon, never taste.
- **Shade** belongs to the BOT. A trade inside a category takes a lighter or deeper shade of its
  family — never a hue of its own. A plumbing BOT is a deeper rust; a maths-tutor BOT a deeper
  green. Neither needs a decision.
- **Ring**: a sub-trade BOT wears its family hue as a thin ring, so it reads as its category at a glance.

Recorded in `BRAND_ASSETS.md`, which is the file that says fix it here and everything follows.

### Reserved to David — the one colour I did not change

Home Help is a Services BOT, so the system puts it at clay **#C96B4A**: ΔE 12.0 from its Services
parent (family resemblance, intended) and 18.8 from its nearest outsider. His jade **#16A97C**
measures ΔE 13.4 from Tutors and 15.0 from Adventures — two *other categories*, so beside them it
is a third green.

He said he loves the green the same night, so the prototype and its manifest **stay jade** until he
rules. The board toggles between the two with the numbers on screen. One line changes it either way.

### Files added

`BOT_FAMILY.html`, and one manifest each for property, cars, tutors, services, collectors,
adventures, localmarket. Still to make if any of this is built: three PNG icons per BOT in its
colour under `/static/brand/bots/<bot>/` — a drawing job, not a decision.
