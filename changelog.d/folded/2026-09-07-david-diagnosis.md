## 7 Sep 2026 — David's diagnosis of the outreach numbers, tested against the data (DIAG-1)

David: *"i don't see the bad statistics we have regarding emails of 814 sent, 252 opened, 48 clicked as
a valid reflection of the app, i see three causes 1. Physical app blocks preventing people to list,
2. Complexity of the listing flow/process and 3. Semi blind group of a population. If we can provide a
chatting genie to list for people, and if the app works end to end, then we will have much better
statistics."*

**He is right, and the machinery already proves it — but two of his numbers need correcting, and the
correction makes his case STRONGER.**

**1 · The real email numbers** (PROBED, `CityLauncher/data/prospects.db`, read-only, 7 Sep):
1,232 people emailed · 297 opened (**24.1%**) · 64 raw clicks (5.2%) · **0 published**.
But `click_register` grades every click: **56 machine · 48 human_open · 11 uncertain · 2 human_click.**
So the "48 clicked" is **48 human OPENS**; the real human click count is **TWO**. A 24% open rate on
cold outreach is normal-to-good — **the email is not the broken part.**

**2 · The app IS the wall, and it is measured** (PROBED live `/onboard/funnel?days=30&bots=1`, 7 Sep):
**landed 65 → dwell 1 → subpick 1 → photos 17 → ZERO past photos.** Not one arrival in 30 days has
reached any step beyond the photo screen. Already carried as ledger **RG-0326 (OPEN)**, raised this
morning by EMAIL-FORENSIC-1 at 62/15; tonight's re-probe refreshes it to 65/17 and the answer is
unchanged.

**3 · The wall is exactly one gate.** `ms.js sfPhotosS()`: the forward button is rendered **disabled**
until `sfState.photos.main===2` — a main photo uploaded AND passed by the AI check — and the "Skip the
rest of the photos" link only appears AFTER that photo is accepted. **There is no way past screen 1
without a photograph the machine approves.** WRONG-TYPE-1 can also hard-reject exactly what a club
would reach for (a logo, a team shot) on a Tutors-shaped flow. **481 of the 1,232 emailed are Sports
Clubs.**

**4 · The detail that settles it, found the same night in the BOT work:** `_import_quality_score()`
publishes a listing at **60/100 with ZERO photos** (facts 50 + price 6 + suburb 4). **The scorer does
not require a photograph. The flow demands one before a seller may take a single step.** Those two
facts contradict each other and the flow is winning.

**HIS THREE CAUSES, GRADED:**
- **(1) Physical app blocks — CONFIRMED, and now specific.** The historic blocks are fixed and LOCKED
  (RG-0249 self-serve rate listings, RG-0250 invited seller gets the AI draft, RG-0253 first-time
  seller can publish). RG-0326 is the one still open, and it is the binding one.
- **(2) Complexity — CONFIRMED, and it is the SAME defect.** RG-0326's own class line: *a quality gate
  placed before the seller has invested anything, on a flow reached from cold outreach.*
- **(3) Semi-blind population — PARTLY, and unproven either way.** 481/1,232 are sports clubs (an
  organisation is not a person with a thing to sell) and 657 are US against 396 ZA. But the audience
  cannot yet be blamed: they never got the chance to fail, because they were stopped at screen 1.

**5 · The measurement gap behind all of it:** `onboard_events` in prospects.db is **completely empty**
(0 rows) — the click→app join has never been fed. `/onboard/funnel` (RG-0293, LOCKED 5 Sep) is the
working instrument and is what every number above comes from.

**CLAUDE'S RECOMMENDATION, and why it is NOT "build the genie first":** let a seller past screen 1
without a photo — offer it, do not require it — and keep the Listing Rating visible so the photo is
sold as a gain rather than demanded as a toll. That is days of work, not weeks, and it TESTS David's
hypothesis: if arrivals start reaching step 2 next week, the diagnosis is proven and the genie is worth
building on top of it. If they still stop, the genie would not have saved it either. Do not spend the
big build to fix something a small change can measure first.

**RESERVED TO DAVID:** whether a listing may exist without a photograph is a product decision about
what a TrustSquare listing *is* — it touches listing quality, which is the marketplace's proposition —
and it changes the publish flow during launch month. Not touched. Nothing changed this session.
