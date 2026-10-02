# GOAL_IMPROVEMENTS — the Goal run's one list

Contract: `GOAL_RUN_PROMPT.md` §5. Newest first. Status is SHIPPED (commit + live proof), BUILT (ready,
not yet live — says why), REVIEW NOW, APPROVED or REJECTED.

## REVIEW NOW

*Open actions only — updated 2 Oct 2026 on David's request. Three decisions, nothing else waits on you.*

### GI-0008 · SO-6 rulings sweep — six rulings that spend without a stated cost or contradict an earlier ruling
You asked for this on 30 Sep: find every "small yes" that, like RUL-167 with SMS, quietly adds a running cost or breaks
an earlier ruling. Six did. Each needs keep or amend; nothing has been changed or built on any of them.

| # | Ruling | What it does today | What it clashes with | Recommendation |
|---|--------|--------------------|----------------------|----------------|
| 1 | RUL-138 (17 Sep) | The maintenance agent never stops on cost — it steps down to the cheapest model and keeps answering | RUL-007 / RUL-096(e): only flat, cappable costs; raising a ceiling is yours | Keep the step-down and add a daily rand stop you name — this reverses your own "a hard cap is wrong", so it is your call |
| 2 | RUL-189 + RUL-191(4) (27 Sep) | Testers run every paid AI feature for ever, and each named tester gets 200T (~$400 face value); 3 invites so far, no limit on how many | Pricing canon §5: paid-feed AI is Pro-only because granted Tuppence funding it leaked ~$3,264/month | Cap testers per month and pay grants from a named budget line |
| 3 | RUL-191(3) (27 Sep) | A 1T fair-price check on Collectors and Local Market, run on OpenAI web lookups | Canon §5: a paid-feed function needs a stated cost and a ceiling | State the cost per check and which plans may fire it |
| 4 | RUL-144 + RUL-178 | A "verified phone" earns 2 Trust points, and a phone check is an SMS code at our cost | RUL-192(b): the app sends no SMS at our cost | Verify by e-mail or the draft link only; also state BANKRESOLVE-1's price per lookup |
| 5 | RUL-155 / RUL-156 (19 Sep) | A licence shows "VERIFIED" once a person has checked the upload | RUL-039: only the paid check may say "VERIFIED" | Change the word (e.g. "Licence checked"); keep the gate |
| 6 | RUL-192(a) (30 Sep) | Our SMS account may carry cold outreach to phone-only prospects (the Gumtree 1,111) | The opt-out list (RUL-054) and 60-day gap (RUL-106) live only in the e-mail sender, so SMS would skip both; RUL-101(a) requires opt-in for personal addresses and does not say whether phones count | Same opt-out list, same 60-day gap and "reply STOP" in every text before the first one goes; say whether RUL-101(a) covers phones |

Do 1 and 2 first — they are the only two that can spend without a stop.
FYI, no action needed: RUL-130 turned the tester REPORT tab back on without citing RUL-040/064; RUL-179(e) refuses a
new Circle connection when full, against RUL-173(b)/135(h); RUL-162/163 cap translation per advert but have no rand ceiling.

### GI-0006 · Collectors step 6 greets a one-coin seller with "SEVERE PENALTIES"
For one R350 coin the last step is an auction-house pitch, dealer registration and CITES; that she is exempt is small
print at the foot. Recommend yes to one line at the top when she picked "Single item": "Selling one thing of your own?
The dealer rules don't apply — keep any certificate and describe it honestly."

### GI-0003 · A cleaner has no door in Sell that names her
A full-width "Work for yourself?" card opening Quick; it changes RG-0478 ("small and unobtrusive"). Recommend yes.

### GI-0017 · Two identical live Townhouse adverts (#468, #469) in the public grid
Same family seller (davidconradie1234@), published from Quick 12 minutes apart; #458 is a third, draft copy. QUICK-DUP-1 stops it
happening again; the two already live are real data. Recommend: pause #469 (keep #468). Your call or his.

### Closed since the last list
- **GI-0009 OpenAI credit:** answering again since 04:15Z on 1 Oct (last 429 at 03:50Z; 42 good calls since). Run 26
  listed it as open without re-checking — that was wrong.
- **GI-0004 phone-only sellers:** overtaken by RUL-192; the SMS account exists, and outreach SMS is item 6 above.
- **eBay keys for Local Market fair price:** not needed — the check runs on named-source web comparables
  (FAIR-PRICE-WEB-1, 27 Sep); eBay is an optional extra source.

## Rows

| id | date | change | evidence | expected effect / how we'd know | size | status |
|----|------|--------|----------|---------------------------------|------|--------|
| GI-0016 | 2 Oct | **QUICK-DUP-1** (RG-0793): a signed-in member whose Quick publish matches an advert she already has live from the last 24 h (title, category, price, city, suburb) gets that advert back; no second copy | #468 / #469 identical Townhouse adverts, same seller, 12 min apart, both public | no identical twins in the grid; log line `QUICK-DUP-1:` when it fires | small | **SHIPPED** 2 Oct (see GOAL_STATE run 27). Proven on the live DB read-only: #469's fields → finds 469; changed price → none |
| GI-0015 | 2 Oct | **LANG-PILL-SOB-1 + LETTER-WORD-1** (RG-0792): language pill hidden on the terms step; way-back letter says "saved", not "composed" | walk steps 11, 14 | Back button tappable; letter uses Quick's word | small | **SHIPPED** 2 Oct (see GOAL_STATE run 27) |
| GI-0014 | 2 Oct | **TERMS-NOTE-1** (RG-0791): terms-step note "Read the Terms of Use below and accept them — your listing goes live straight after" (was "You have an existing account but haven't yet accepted…") | walk step 13: said to a seller two minutes old | fewer Quick drafts stopping at the terms step | small | **SHIPPED** 2 Oct (see GOAL_STATE run 27) |
| GI-0013 | 2 Oct | **QUICK-ONE-TAB-1** (RG-0790): Quick's key step hides the tab bar when Email is its only tab | walk step 9: a full-width orange "Email" button that did nothing | fewer q_draft sessions with no q_id_email | small | **SHIPPED** 2 Oct (see GOAL_STATE run 27) |
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
