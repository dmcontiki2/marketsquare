# GOAL_IMPROVEMENTS — the Goal run's one list

Contract: `GOAL_RUN_PROMPT.md` §5. Newest first. Status is SHIPPED (commit + live proof), BUILT (ready,
not yet live — says why), REVIEW NOW, APPROVED or REJECTED.

## REVIEW NOW

*Open actions only — updated 4 Oct 2026 (run 29). One decision, unchanged since run 28.*

### GI-0020 · The 1T fair-price check — the cost breakdown you asked for (RUL-199(3))
Measured on the live spend log, 27 Sep – 2 Oct (18 web look-ups, 16 with the provider's real cost):

| | per check | note |
|---|---|---|
| Web comparables (OpenAI web search, `/listings/price-check#web-comps`) | **$0.052 average, $0.098 worst** (≈ R0.95, R1.75) | the whole cost; spent even when it finds fewer than 3 named sources |
| Reasoning step (`/listings/ai-price-check`) | $0.002–$0.004 | negligible |
| Catalogue feeds (Numista coins, JustTCG cards, BrickLink Lego) | $0 | free tiers, used first when they answer |
| **Price to the person** | **1T = $2 (≈ R36)** | charged only when a verified range is delivered (deliver-then-charge); a miss costs us ≈R1 and her nothing |

Ceilings already in force: $0.50 per person per day and $10 for the whole platform per day (ai_spend_config) — the platform
stop (RUL-199(1)) also stops this check. Today any signed-in person with 1T can fire it, buyer or seller, on Collectors and
Local Market (Property's paid tiers are off).

Options: **(a)** keep it as it is — 1T, any plan, inside the two ceilings (worst day: $10); **(b)** as (a), plus the seller's
*first* check on each new listing free — costs ≈R1 per new listing (R20 a month at the 20-seller target) and lets a
collector shop see the product work before she has bought a Tuppence; **(c)** Pro-only — takes it away from the free plan,
where every new seller starts. **Recommend (a) now and (b) as soon as a stranger reaches the Collectors score card** — say (b) and it
is built in a day.

### Closed since the last list
- **GI-0008 SO-6 sweep:** answered by you on 3 Oct (RUL-199) and shipped the same evening (db67a6e, RG-0811). Only item 3
  stayed open — it is GI-0020 above.
- **GI-0006 Collectors step 6:** shipped with RUL-199(7) — seen live on today's walk ("Selling one thing of your own? The
  dealer rules below don't apply to you…", permit rows "ONLY FOR PROTECTED ITEMS").
- **GI-0003 Quick card in Sell:** shipped 3 Oct (QUICK-CARD-1, RG-0810, 60acafd) — seen live on today's walk.
- **GI-0017 twin Townhouse adverts:** #469 paused 3 Oct 06:00Z; #468 stays live.
- **GI-0009 OpenAI credit:** answering (fair-price look-ups and vision reads ran through 2–4 Oct).

## Rows

| id | date | change | evidence | expected effect / how we'd know | size | status |
|----|------|--------|----------|---------------------------------|------|--------|
| GI-0021 | 4 Oct | **AI-DESC-SHOWN-1 + AI-PRICE-HINT-1** (RG-0876): the photo read's description now fills her first story box ("✎ I drafted this from your photo — buyers will read it as written"), cleaned of notes-to-self (what is not visible, props, styling); clearing it means no AI text. The vision prompt says description_draft is buyer-facing. A price guess under 0.5 confidence is a placeholder ("Photo guess R80 — your price"), not her price | walk (`docs/E2E_2026-10-04_run29.md`): a marmalade seller's advert would have gone live with an AI paragraph she never saw — honey, bread loaves, a jug and flowers "as market styling", ending "…and pricing are not visible." R80 at confidence 0.28 sat in her price box. Same price behaviour run 28 saw on Collectors (R200) | no AI notes-to-self in new adverts' descriptions (grep live descriptions for "not visible"); prices on new photo-read listings differ from `suggested_price` | small | **SHIPPED** 4 Oct 21:11Z, 046b996, ms.js?v=935 — live: fresh profile, jars photo → price box empty, placeholder "Photo guess R80 — your price" (conf 0.42); story box held the read's text with the note, its "…expiry dates are not shown." sentence dropped; the new prompt no longer described the bread or props. Ledger 2 !!!! (RG-0840, RG-0871, both on base too; base 3). RG-0876 LOCKED |
| GI-0020 | 4 Oct | The 1T fair-price check: cost breakdown and options (RUL-199(3), OPEN) | ai_spend_log: 18 web look-ups $0.052 avg / $0.098 max; 1T = $2; deliver-then-charge; $0.50 user / $10 platform daily ceilings | David picks (a), (b) or (c) | small | **REVIEW NOW** |
| GI-0019 | 4 Oct | **MAGIC-HELLO-1** (RG-0813): an invited seller is greeted by name on step 1 of the sell flow ("This is the TrustSquare invitation we e-mailed you — … Start with one listing … free plan"); the Home long-press tip no longer fires over her form | walk B (`docs/E2E_2026-10-04.md`): the Collector Shops letter's link opened on "Step 1 of 6 · Photos" with no word of who or why, a Home tip floating over it; the old "Welcome, <name>" banner was left behind by SELL-FLOW-REDO-2 (15 Jul) — every invitee since then has landed this way | invited arrivals that pick a photo or press Item Details (funnel `photo_pick` / `q_step` after `landed` with magic) rise above today's 0 | small | **SHIPPED** 4 Oct 07:55Z, bb5d7d5, ms.js?v=920 — live: the Collector Shops link shape opens with "Welcome, QA Goal28 Collectables. This is the TrustSquare invitation we e-mailed you…" above the meter; no Home tip over it; a cold Collectors walk shows no greeting. RG-0813 LOCKED |
| GI-0018 | 4 Oct | **COL-DRAFT-1** (RG-0812): on Collectors the photo read fills Category, Year / era and Maker blanks from what it already knows (the vision prompt now asks for `collectible_type`, a legible year and maker) | walk A step 5: the read titled the coin "1947 Vintage Coin" and left Category "—" and Year empty | fewer blank Category values on Collectors drafts; Browse's Collectible Type filter finds new items | small | **SHIPPED** 4 Oct 07:55Z, bb5d7d5 — live: a cold Collectors walk, one coin photo → the read returned `collectible_type: Coins`, `year: 1947`, `maker: null`; Item Details opened with Category **Coins**, Year **1947**, Maker blank. RG-0812 LOCKED |
| GI-0016 | 2 Oct | **QUICK-DUP-1** (RG-0793): a signed-in member whose Quick publish matches an advert she already has live from the last 24 h (title, category, price, city, suburb) gets that advert back; no second copy | #468 / #469 identical Townhouse adverts, same seller, 12 min apart, both public | no identical twins in the grid; log line `QUICK-DUP-1:` when it fires | small | **SHIPPED** 2 Oct 21:14Z, 26db01f, ms.js?v=905 — live proof in GOAL_STATE run 27. Proven on the live DB read-only: #469's fields → finds 469; changed price → none |
| GI-0015 | 2 Oct | **LANG-PILL-SOB-1 + LETTER-WORD-1** (RG-0792): language pill hidden on the terms step; way-back letter says "saved", not "composed" | walk steps 11, 14 | Back button tappable; letter uses Quick's word | small | **SHIPPED** 2 Oct 21:14Z, 26db01f, ms.js?v=905 — live proof in GOAL_STATE run 27 |
| GI-0014 | 2 Oct | **TERMS-NOTE-1** (RG-0791): terms-step note "Read the Terms of Use below and accept them — your listing goes live straight after" (was "You have an existing account but haven't yet accepted…") | walk step 13: said to a seller two minutes old | fewer Quick drafts stopping at the terms step | small | **SHIPPED** 2 Oct 21:14Z, 26db01f, ms.js?v=905 — live proof in GOAL_STATE run 27 |
| GI-0013 | 2 Oct | **QUICK-ONE-TAB-1** (RG-0790): Quick's key step hides the tab bar when Email is its only tab | walk step 9: a full-width orange "Email" button that did nothing | fewer q_draft sessions with no q_id_email | small | **SHIPPED** 2 Oct 21:14Z, 26db01f, ms.js?v=905 — live proof in GOAL_STATE run 27 |
| GI-0012 | 1 Oct | **FUNNEL-WEBDRIVER-1** (RG-0654): ms.js / quick.html / quick_next.html beacons carry `wd` (navigator.webdriver); the server stores such steps bot=2 | 45 of 55 "human" sessions on 1 Oct were scripted (cloud check 35, this walk 10) | `/onboard/funnel` humans = people; first stranger visible | small | **SHIPPED** 1 Oct 21:28Z, 33f3052. Live: this run's Playwright sessions stored bot=0 before (10, 20:59–21:09Z) and bot=2 after (obmuq1ra…, obmuq1ry…, 21:29Z) |
| GI-0011 | 1 Oct | **LM-COACH-TRUTH-1** (RG-0653): Local Market step 2 coach "Name it the way a buyer would search — … Added a photo? The AI has drafted a title" | walk step 5: photo skipped, coach still said "The AI drafts a title from your photo" | no promise the app has not kept | small | **SHIPPED** 1 Oct 21:28Z, 33f3052. Live: step 2 text read back from a fresh profile |
| GI-0010 | 1 Oct | **LM-UNIT-1** (RG-0652): the Local Market "Sold" choice travels with the price ("R85 per box" / "R85 each"); Food & Produce gains "Per pack" and "Each" | walk step 10: `sfListingFields().price` was "85" with "Per box" chosen | cards show what the price buys; fewer "how much is a jar?" questions | small | **SHIPPED** 1 Oct 21:28Z, 33f3052. Live: fresh profile, Each, R85 → price "R85 each"; node test: services /hour, /day unchanged, POA unchanged |
| GI-0009 | 30 Sep | OpenAI account out of credit; paid reports + web fair-price down; traffic failing over to Anthropic | server log 19:17 last 200, 429s since | reports deliver again; `GET /ai/jobs` no 429 | small | **CLOSED** 2 Oct: OpenAI answering since 1 Oct 04:15Z (last 429 03:50Z) |
| GI-0008 | 30 Sep | SO-6 sweep of RULINGS.md: RUL-138, 189/191, 191(3), 144/178, 155/156 wording, 192(a) | all 192 rulings vs PRICING_CANON | each amended or re-confirmed with its cost stated | several | REVIEW NOW (rulings + cost model) |
| GI-0007 | 30 Sep | **FUNNEL-QA-1** (RG-0644): sell-flow beacons carrying the QA key, tester cookie or a QA address are stored bot=2, out of the stranger funnel | every "human" Quick draft since 1 Sep came from an emulated phone in a scripted burst | `/onboard/funnel` humans fall to people only; first real stranger is visible | small | **SHIPPED** 30 Sep 21:20Z, 39572d8. Live proof: beacon from `dmcontiki2+qa-goalrun25@gmail.com` stored bot=2. Ledger fails on old tree, passes new |
| GI-0006 | 30 Sep | One-line "selling one thing of your own?" note on Collectors step 6 for a single item | walk step 8 | fewer Collectors drafts stopping at `legal` | small | REVIEW NOW (positioning) |
| GI-0005 | 30 Sep | **LM-TILE-LABEL-1** (RG-0643): Home's Local Market tile shows "Local Market · N listings" over its photos | walk step 2: `elementFromPoint` hit the photo layer | the tile says what it is; taps on it | small | **SHIPPED** 30 Sep 21:20Z, 39572d8, ms.js?v=875. Live: label on top, screenshot |
| GI-0004 | 29 Sep | Reach phone-only sellers (SMS account; legal read on the Gumtree 1,111) | see REVIEW NOW | first phone sign-ups; `users.phone_verified_at` count | major | **CLOSED** 2 Oct: overtaken by RUL-192 (SMS outreach-only); outreach SMS is GI-0008 item 6 |
| GI-0003 | 29 Sep | Full-width "Work for yourself?" card in Sell opening Quick | walk step 2 | sell-flow q_door sessions/week up | small | REVIEW NOW (ruling change, RG-0478) |
| GI-0002 | 29 Sep | Archive QA adverts 425, 426, 429, 431 (+438, drafts) | live DB 21:05Z | 0 test adverts in the public grid | small | **DONE by another lane**: all five `paused` at 30 Sep 18:46:19Z (not archived); 0 QA adverts public at 21:10Z. Drafts remain |
| GI-0001 | 29 Sep | **HUB-AGENT-FIT-1** (RG-0552): Seller Hub hides the "Agent Hub — estate, car & tour agents" card when every advert she has is outside Property/Cars/Adventures (shown as before when she has none). Quick line wording in Sell and the Sell sheet: "In a hurry? 5-tap Quick listing" → "Cleaner, gardener, nanny, driver? Quick listing" (size unchanged, inside RG-0478) | walk steps 2 and 8 | a new cleaner's hub opens on her own advert; sell-flow / sell-sheet q_door sessions per week vs Sep | small | **SHIPPED** 30 Sep 00:14Z, commit 06bf885, live ms.js?v=851. Proof on the live page: agentHubFit none→shown, Services only→hidden, +Adventures→shown, Property→shown; both Quick lines read the new words. Ledger RG-0552 LOCKED (fails on the previous tree, passes live) |
