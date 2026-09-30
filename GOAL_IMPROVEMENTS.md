# GOAL_IMPROVEMENTS — the Goal run's one list

Contract: `GOAL_RUN_PROMPT.md` §5. Newest first. Status is SHIPPED (commit + live proof), BUILT (ready,
not yet live — says why), REVIEW NOW, APPROVED or REJECTED.

## REVIEW NOW

### GI-0008 · 30 Sep · SO-6 sweep: six more "small yeses" carried a cost or broke an earlier rule — **This changes a rule / the cost model**
You asked for this on 30 Sep morning. I read all 192 rulings against PRICING_CANON.md. RUL-167 was not alone.
Each line: what it adds · cost as the files state it · the rule it collides with · what I recommend.
- **RUL-138 (17 Sep) — the maintenance agent never stops on cost.** When no model fits the day's budget "the CHEAPEST
  rung still answers", and `_check_cost_ceiling` "is deliberately not called". Cost: uncapped above
  `daily_user_ceiling_usd` (no figure). Collides with RUL-096(e) "raising [a ceiling] is spending money, reserved" and
  RUL-007 "flat cappable external costs only". **Amend:** keep the step-down, add a hard daily stop.
- **RUL-189 + RUL-191 TESTER-INVITE-1 (27 Sep) — testers run every paid AI feature, for ever; each named tester gets
  200T.** No cap on how many testers. Cost: 200T each (R-value at your T price; the canon values T at about $2, so
  ~$400 face value each) plus the paid feeds they fire. Collides with PRICING_CANON §5: the paid-feed class "was leaking
  ~$3,264/mo … when free/granted Tuppence funded it" — "Free, Starter and Agency are blocked". **Amend:** cap testers
  and grants per month, from a named budget line.
- **RUL-191(3) FAIR-PRICE-LM-1 (27 Sep) — 1T fair-price check on Collectors and Local Market** via Numista / JustTCG /
  BrickLink / (now) web comparables. Feed and per-call cost not stated. Collides with canon §5 (paid-feed class Pro-only,
  "B7 sign-off + ceiling still required"). Tonight it also runs on the OpenAI account that is out of credit (GI-0009).
  **Amend:** state the cost per check and which tier may fire it.
- **RUL-144 (18 Sep) and RUL-178 PHONE-CRED-1 (27 Sep) — a confirmer "verifies a phone number", and a verified phone is
  worth 2 Trust points.** A phone check means an SMS code at our cost. RUL-192(b) banned sign-in codes but did not name
  these two. Collides with RUL-122 and RUL-192(b). **Amend:** e-mail (or wa.me) only; say so in RUL-192.
  RUL-178 also calls BANKRESOLVE-1 "the paid lane David approved" with no per-lookup figure — **disclose it.**
- **RUL-155/156 (19 Sep) — licences shown "VERIFIED through the existing ID-upload verification lane".** Built today by
  the cloud lane as a person-checked queue (LICENCE-GATE-1), which is fine; but the wording collides with RUL-039 "ONLY
  THE PAID ONE MAY SAY 'VERIFIED'". **Amend the word**, not the gate.
- **RUL-192(a) (30 Sep) — our SMS carries cold outreach to phone-only prospects.** Its cost is stated (~R350 prepaid,
  40/day cap). What it does not say: the opt-out register (RUL-054) and the 60-day floor (RUL-106) live inside
  `send_email()` only, so an SMS lane bypasses both; RUL-052 relied on an unsubscribe link SMS does not have; RUL-101(a)
  requires prior opt-in for personal mailboxes, and these are personal phones. POPIA s69 (my reading, not legal
  advice) wants prior consent for electronic direct marketing to a non-customer. **Recommend:** before the first
  outreach SMS, rule that SMS obeys the same suppression list and 60-day floor, carries "reply STOP", and goes only to
  prospects whose consent position a lawyer has cleared. Nothing that sends SMS to prospects exists yet; I have built none.
- Smaller, one line each (no action unless you want it): RUL-130 turned the tester REPORT tab back on without citing
  RUL-040/064 that removed it; RUL-179(e) refuses a new Circle connection when full, against RUL-173(b)/135(h);
  RUL-162/163 translate every advert on the OpenAI key with a per-advert cap but no rand ceiling.
- **What I recommend overall:** amend RUL-138 and RUL-189/191 first — they are the two that can spend without a stop.
  I have changed no ruling and built nothing on any of these.

### GI-0009 · 30 Sep · The OpenAI account ran out of credit at ~19:20 UTC tonight (money — yours)
- **Evidence:** server log: last OpenAI `200` at 19:17 UTC; every OpenAI call since 19:23 is `429 … no credits
  remaining` (62 by 21:10, one every 5 minutes from a background job). `launch_switches.ai_active = openai`.
- **What still works:** photo safety checks, vision drafts and Trust Score guidance fall over to Anthropic (54 calls
  since 19:20) — so a seller can still add photos and publish. **What is down:** every paid AI report (5T Collectables,
  Area Dossier…) and the web fair-price check ("No verified price — not charged"). Nothing is charged for a failed run.
- **Cost note (SO-6):** the failover means tonight's AI traffic is being paid on the Anthropic key instead — a spend
  shift nobody decided. I have not measured its rand figure.
- **Recommend:** top up OpenAI (or switch the active lane on Page 4); the cloud lane has L34 open to re-walk F10 after.

### GI-0006 · 30 Sep · Collectors step 6 greets a one-coin seller with "SEVERE PENALTIES" (agency positioning — yours)
- **Evidence:** walk step 8 (`docs/E2E_2026-09-30.md`). For one R350 coin the last step before the score is an
  auction-house pitch, SAPS dealer registration, CITES permits and a signed agreement; that she is exempt is small
  print at the foot. No funnel number yet (FUNNEL-QA-1 only started separating our walks from people tonight).
- **What I would do:** when she picked "Single item", one line at the top of the card: "Selling one thing of your own?
  The dealer rules don't apply — keep any certificate and describe it honestly." Nothing removed. Reversible.
- **Why it is yours:** step 6 is the agency pitch you designed (LEGAL-STEP-2); softening it is positioning.
- **Recommend:** yes.

### GI-0003 · 29 Sep · A cleaner has no door in Sell that names her (changes a ruling — yours)
- Unchanged from 29 Sep: a full-width "Work for yourself?" card opening Quick, which changes RG-0478 ("small and
  unobtrusive"). **Recommend:** yes.

### GI-0004 · 29 Sep → 30 Sep · Phone-only sellers
- **Overtaken by RUL-192 (30 Sep):** SMS is outreach-only; the app sends no sign-in codes. Phone sign-up (§7) is
  therefore off by your ruling, not waiting on plumbing. The open part is the Gumtree 1,111 outreach — see GI-0008,
  RUL-192(a). I will not raise the SMS price again.

## Rows

| id | date | change | evidence | expected effect / how we'd know | size | status |
|----|------|--------|----------|---------------------------------|------|--------|
| GI-0009 | 30 Sep | OpenAI account out of credit; paid reports + web fair-price down; traffic failing over to Anthropic | server log 19:17 last 200, 429s since | reports deliver again; `GET /ai/jobs` no 429 | small | REVIEW NOW (money) |
| GI-0008 | 30 Sep | SO-6 sweep of RULINGS.md: RUL-138, 189/191, 191(3), 144/178, 155/156 wording, 192(a) | all 192 rulings vs PRICING_CANON | each amended or re-confirmed with its cost stated | several | REVIEW NOW (rulings + cost model) |
| GI-0007 | 30 Sep | **FUNNEL-QA-1** (RG-0644): sell-flow beacons carrying the QA key, tester cookie or a QA address are stored bot=2, out of the stranger funnel | every "human" Quick draft since 1 Sep came from an emulated phone in a scripted burst | `/onboard/funnel` humans fall to people only; first real stranger is visible | small | **SHIPPED** 30 Sep 21:20Z, 39572d8. Live proof: beacon from `dmcontiki2+qa-goalrun25@gmail.com` stored bot=2. Ledger fails on old tree, passes new |
| GI-0006 | 30 Sep | One-line "selling one thing of your own?" note on Collectors step 6 for a single item | walk step 8 | fewer Collectors drafts stopping at `legal` | small | REVIEW NOW (positioning) |
| GI-0005 | 30 Sep | **LM-TILE-LABEL-1** (RG-0643): Home's Local Market tile shows "Local Market · N listings" over its photos | walk step 2: `elementFromPoint` hit the photo layer | the tile says what it is; taps on it | small | **SHIPPED** 30 Sep 21:20Z, 39572d8, ms.js?v=875. Live: label on top, screenshot |
| GI-0004 | 29 Sep | Reach phone-only sellers (SMS account; legal read on the Gumtree 1,111) | see REVIEW NOW | first phone sign-ups; `users.phone_verified_at` count | major | SMS: **APPROVED 30 Sep** by David (BulkSMS, ~R350 prepaid, "no run-away"). Built and live: SMS-DAILY-CAP-1 (RG-0554, bff6cc0) caps the server at 40 SMS/day and fails closed; `add_sms_key.bat` puts the token on the server. Waiting on David to open the account and run the bat. Gumtree consent SMS: not yet decided |
| GI-0003 | 29 Sep | Full-width "Work for yourself?" card in Sell opening Quick | walk step 2 | sell-flow q_door sessions/week up | small | REVIEW NOW (ruling change, RG-0478) |
| GI-0002 | 29 Sep | Archive QA adverts 425, 426, 429, 431 (+438, drafts) | live DB 21:05Z | 0 test adverts in the public grid | small | **DONE by another lane**: all five `paused` at 30 Sep 18:46:19Z (not archived); 0 QA adverts public at 21:10Z. Drafts remain |
| GI-0001 | 29 Sep | **HUB-AGENT-FIT-1** (RG-0552): Seller Hub hides the "Agent Hub — estate, car & tour agents" card when every advert she has is outside Property/Cars/Adventures (shown as before when she has none). Quick line wording in Sell and the Sell sheet: "In a hurry? 5-tap Quick listing" → "Cleaner, gardener, nanny, driver? Quick listing" (size unchanged, inside RG-0478) | walk steps 2 and 8 | a new cleaner's hub opens on her own advert; sell-flow / sell-sheet q_door sessions per week vs Sep | small | **SHIPPED** 30 Sep 00:14Z, commit 06bf885, live ms.js?v=851. Proof on the live page: agentHubFit none→shown, Services only→hidden, +Adventures→shown, Property→shown; both Quick lines read the new words. Ledger RG-0552 LOCKED (fails on the previous tree, passes live) |
