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
- `collector/collector.webmanifest`, `seller/seller.webmanifest` — ready, not deployed.

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
