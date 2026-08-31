# SQUIRE — the Pro subscriber's personal agent
**Status: RULED BY DAVID 30 Aug 2026 (RUL-077) · NOT YET BUILT · Ledger RG-0224 (OPEN)**
**Tier: the existing $20 Pro subscription. No new tier is created.**

> David, 30 Aug: *"Lets implement this PA (Squire) as a new feature for the $20 subscription tier.
> And i do agree on a cap per month, but to not inhibit a person with a lock, there should be an
> option to maybe buy a token?"*

---

## 1 · Why Squire exists (the hole it fills is one anonymity creates)

TrustSquare is anonymous by design: sellers are hidden until an introduction. That is correct and
load-bearing — but it removes the legwork an ordinary buyer would do. In a normal marketplace you
message six sellers and feel your way. Here you cannot.

**Squire is the missing half of the model, not a bolt-on feature.** It is the thing that acts on
your behalf in a square where you cannot be seen.

### The tier axis this establishes
| | Buys | Nature |
|---|---|---|
| **Free** | Local city | where you may look |
| **Global $5** (buyer axis) | National + global | **reach** — a bigger room |
| **Pro $20** | 30 slots, 10T/mo, **+ Squire** | **representation** — someone in the room for you |

Reach and representation are **different axes**. Nobody who buys Squire feels they overpaid for
reach, and **no $5 subscriber loses anything** — David's binding condition ("without detracting
from the $5"). Reach is never moved up into $20.

### What this fixes commercially
Pro today is priced for **sellers only** — 30 slots matter only to a prolific lister, which is why
the contagion model reads **9 632 free / 61 Starter / 1 Pro** at week 52 (RUL-067). Squire makes
Pro valuable to *anyone who buys*, not only to heavy sellers. That widens the addressable base for
the $20 tier from "prolific sellers" to "anyone with a standing need". Squire lands far sooner
than Auctions (RUL-067, ~31 Aug 2027) and, unlike auctions, **works in a thin market** — it needs
one good match, not a crowd. Squire becomes the first Pro lure; Auctions the second.

---

## 2 · What Squire does — four things a Watch cannot

A Zoom saved path (a **Watch**) is passive and belongs to **every tier** — if Watches ever become
paid, Zoom's fifth rule collapses. Squire is what happens when something *acts*.

1. **Specifies.** You say it once in your own words — *"maths tutor for my 14-year-old, failing
   trig, patient, Afrikaans or English, Menlo Park, weekday afternoons."* Squire turns it into a
   Zoom funnel path **and** a written brief, and asks the two questions you forgot (IEB or CAPS?
   police clearance required?).
2. **Watches.** Continuously, across the reach you hold.
3. **Shortlists with reasons.** Not "3 new matches" but *"this one — the only NQF-verified maths
   tutor with Thursday slots; this one is cheaper but has no clearance on file."*
4. **Prepares the approach.** The brief is drafted so the introduction *starts* with the seller
   understanding the situation.

Point 4 is the one sellers feel: a real brief is a far better lead than "hi is this available",
which lifts accept rates. **Squire is worth something to both sides of a market still thickening.**

### Also in scope
- **Parallel brief** — one brief to the top N matches, replies collated side by side. An RFP for
  ordinary people. Note it *consumes* Tuppence rather than replacing it.
- **Pre-introduction Q&A** — Squire asks your questions through the anonymous channel *before* you
  spend an introduction.
- **Want-list** — a collector loads their list once; Squire watches and flags appearances with
  grade and a fair-value read (ties to the AI Fair Price work).
- **Timing intelligence** — *"tutors book out in January — start now."*
- **Accumulated understanding** — Squire remembers the child's grade, the budget, the gaps in the
  collection. This is the retention mechanism, and it is the honest kind: cancelling loses
  something you built, not something we withheld.

---

## 3 · Hard boundaries (these are what keep Squire legal, anonymous and on-model)

1. **Squire never touches money and never negotiates price.** It briefs, asks, shortlists, and
   hands you an introduction. Introduction-only is the whole model — nothing through the till but
   Tuppence.
2. **Introductions still cost 1T at every tier.** Subscriptions buy slots and reach — never
   introductions (PRICING_CANON §3). Squire may *prepare* an introduction; it may never *grant*
   one. A Squire that hands out free introductions breaks the pricing canon.
3. **Anonymity is absolute and Squire is inside it, not outside it.** Squire never learns or
   reveals seller identity. **A brief describes the NEED, never the person.**
4. **Watches and "For You" stay free to all tiers.** Squire is additive.
5. **Squire never acts without approval on anything that costs Tuppence or contacts a seller.**
6. **Minors (POPIA).** A brief about a child ("my 14-year-old") is personal data about a minor.
   Briefs are held under the **parent as account holder** (RUL-072 principle), minimised to what
   the seller needs, and **never transmitted in identifying form** — "a Grade 9 learner struggling
   with trigonometry", never a name, school or address. This is a build requirement, not a note.

---

## 4 · The cap and the token — DAVID'S QUESTION, ANSWERED

> *"a cap per month, but to not inhibit a person with a lock, there should be an option to maybe
> buy a token?"*

**The instinct is right and the currency already exists: the top-up is TUPPENCE. No second
currency is created.** (CTO call, RUL-037.) A separate "Squire token" would fragment the money
model, duplicate accounting, and break the one-currency simplicity that makes Tuppence legible.
1T = USD $2, fixed.

This is exactly the **ceiling doctrine, RUL-066 rung 1**: where a path to more exists, the
rejection and the offer arrive **together**, priced flat in Tuppence.

### What meters, and what does not
The metering line is **observe vs act**:

| Unit | Cost profile | Treatment |
|---|---|---|
| **Standing briefs held** | near-zero (indexed matching) | generous count included |
| **Watching + shortlist reports** | cheap (batch, small-model) | included, not metered per event |
| **Approach** — a drafted brief sent to a seller, plus its pre-introduction Q&A thread | the expensive unit | **this is what the monthly cap counts** |
| **Introduction** | unchanged | **1T, every tier, always** — not a Squire unit |

So: **watching flows freely; acting is what meters.** That is both the honest cost boundary and
the simplest thing to explain on a pricing page.

### The three ceiling properties (RUL-066), all required
1. **Rung 1 — the offer arrives with the limit.** At the cap: *"You've used your 20 approaches
   this month. Another 5 for 1T?"* Never a bare lock. **No charge on a rejected attempt.**
2. **Rung 2 — warn before effort is spent, and never lose work already done.** If a brief is being
   composed and the cap is near, Squire says so **before** the user writes it, and a drafted brief
   is never destroyed by hitting a ceiling.
3. **Rung 3 — every ceiling-hit logs an event** (limit, tier, category). Demand telemetry that
   prices the next batch.

**No refunds, ever** (canon) — a burned Tuppence is a service rendered.

### Numbers to be set at build (flat and cappable by design — no percentage-of-value costs)
Included allowance, top-up bundle size and price are set with the real inference envelope in
front of us. Constraint from PRICING_CANON: the cost side must be **flat and cappable**, never
ad-valorem. Indicative shape only, to be confirmed against measured cost: a generous double-digit
monthly approach allowance, topped up in small flat Tuppence bundles. Pro already grants 10T/mo,
which absorbs ordinary overflow without a card ever coming out.

---

## 5 · Reach bundling — RESOLVED 30 Aug 2026 (RUL-078)

**Pro ($20) includes Global buyer reach ($5), automatically.** David, same session:
*"I see [the] $20 subscription as having the [$5] reach, automatically."* The CTO recommendation
was accepted — reach is a query filter, not a cost, and a Squire confined to one city loses its
best cases.

**Code consequence, now a build requirement:** `_buyer_tier()` reads `wishlist_subscriptions`
alone and returns `free` | `global`. It must **also** return `global` when the account holds a
live **Pro** seller subscription. Until that lands a Pro subscriber is silently treated as local
— Squire would quietly under-serve the people paying most. Asserted by RG-0224 and recorded in
PRICING_CANON §2c.

**Pricing-page hazard logged (David's call, not a blocker):** there are now two distinct $5
products — *Starter* ($5, 10 seller slots) and *Global* ($5, buyer reach) — and **Starter does
not include Global reach.** Someone paying "$5" could reasonably assume they get both. The two
axes must be visually separate on the pricing page.

---

## 6 · Build shape — APPROVED BY DAVID 30 Aug 2026

- **Squire is a layer over Zoom, not a parallel system.** A brief *is* a Zoom path plus prose.
  Build order therefore: **Zoom first (ZOOM-HMI-1), Squire second.** Squire without the funnel
  would mean writing the matching engine twice.
- Server-side and scheduled, not laptop-resident — Squire watches while the user sleeps
  (RUL-070: anything operational ships server-side from birth).
- Cheap model for matching (batch, nightly); the Sonnet-class call is reserved for brief drafting
  and Q&A, which is exactly what the cap counts. AI lane selection per AI_LANE_GUIDANCE;
  vendor/model choice is RUL-009 class (David's).
- Flag-dark on arrival, same discipline as Zoom (RUL-076): David sees it on the real app before
  the field does; arming is his act.

---

## 7 · Acceptance criteria — APPROVED BY DAVID 30 Aug 2026
*(what RG-0224 asserts when built · David: "I approve - Acceptance criteria". These are settled;
a build session implements them, it does not re-open them.)*

1. Squire is gated to Pro; no Squire capability leaks to Free, Starter or Agency.
2. Watches and "For You" remain available on every tier — Squire never annexes them.
3. No introduction is ever granted by Squire; every introduction still burns 1T at every tier.
4. Seller identity never reaches Squire's context, and no brief transmits an identifying detail
   about a minor.
5. At the cap the offer is presented with the limit; no charge on a rejected attempt; a drafted
   brief survives a ceiling hit.
6. The user is warned before composing effort that will exceed the cap.
7. Every ceiling-hit writes a telemetry event with limit, tier and category.
8. Top-ups are denominated in Tuppence — no second currency exists anywhere in the code.
9. A live **Pro** subscription resolves to `global` reach (RUL-078): `_buyer_tier()` consults the
   seller subscription, not `wishlist_subscriptions` alone. A Pro subscriber is never silently
   treated as local.

---

*Written 30 Aug 2026. Named by David ("I love the new word SQUIRE") — a squire attends you, carries
your brief, and speaks for you in a square where you cannot be seen.*
