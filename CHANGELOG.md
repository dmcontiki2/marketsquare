## Session 41 (continued) — Seller onboarding funnel: magic link landing flow

**Task: Seller onboarding funnel in marketsquare.html**
Built the complete magic link landing flow as `screen-seller-onboard` — a four-phase screen that intercepts the magic link URL (`?magic=1`) and routes the seller through onboarding before any listing goes live.

Phase 1 (Draft preview): calls `GET /listings/mine?email=` to find all draft listings for the seller, renders them as private cards with a "Draft — not yet live" badge. No listing IDs in the URL — seller email from the magic link is the only lookup key (Option B). Phase 2 (Tier picker): Free / Standard / International selection with visual feature comparison, Free pre-selected by default, no card required. Phase 3 (EULA): inline seller terms with two acceptance checkboxes — terms and content standards — both required before Go live is enabled. Phase 4 (Success): calls `POST /users` to register the seller (idempotent), then `PUT /listings/{id}/publish` for each draft, stamps `published_at`, transitions listing to live. Stores email in localStorage for returning seller recognition, refreshes buyer feed, navigates to seller dashboard.

End-to-end verified via API: draft listing (ID 77) created, confirmed invisible to public feed, published via the endpoint, confirmed live in public feed, cleaned up. JS syntax checked with node --check before deploy. Deployed to trustsquare.co.
## Session 41 — Seller onboarding flow: draft-first publish gate

**Task: Draft-first listing flow — admin app + BEA**
Identified that the admin tool was publishing listings live immediately, with no subscription gate, no EULA, and no seller registration. Implemented the first stage of a corrected three-stage onboarding flow:

BEA (`bea_main.py`): `POST /listings` now saves all listings with `listing_status = 'draft'` and `published_at = NULL`. Added new endpoint `PUT /listings/{id}/publish?email=` which transitions a draft listing to `live`, stamps `published_at = now()`, and performs email-auth (seller_email must match or is stamped if NULL). The existing `GET /listings?city=X` filter already excludes non-live listings so no buyer-side changes were needed.

Admin app (`marketsquare_admin.html`): Step 4 renamed from "Review & publish" to "Review & save draft". Button label changed from "Publish all →" to "Save drafts →". All success messaging updated to reflect draft-saved state. Magic link hint text now explains the full seller onboarding journey: tier selection → EULA → registration → listing goes live. No listing is publicly visible until the seller completes onboarding via the magic link. Listing 76 (Tutors, created this session before the change) remains live as a legacy record.

Next session (42): Build the magic link landing flow in `marketsquare.html` — private listing preview, subscription tier picker, EULA screen, and registration completion, culminating in calling `PUT /listings/{id}/publish` to go live.
# MarketSquare · CHANGELOG

---

## Session 38 · 3 May 2026 · Two-Path Sell Flow (SELL_FLOW.md v3.0)

**New sell flow — Path A (new seller, 3 taps to live):** Replaced the old `screen-publish` wizard with a streamlined 3-step Path A: (1) single photo upload with preview, (2) category + headline + price with inline Haiku AI market note, (3) identity fields + EULA on submit → listing goes live immediately with 3 free AI sessions credited. `openSellNav()` now routes no-email users to `goTo('publish')` (Path A) instead of the old onboard screen.

**New sell flow — Path B (returning seller, B1–B8):** Added `screen-sell-b` with a full 8-step AI-guided listing flow. B1: account confirmation. B2: category selection + agent/private gate for Property. B3: structured fields (dynamic per category via `SB_FIELDS` config) + inline Haiku AI market note. B4: AI drafts description via `/advert-agent/coach`. B5: room-by-room photo gallery with dynamic slots per category (`SB_PHOTO_SLOTS`). B6: skippable selfie. B7: Trust Score checklist with full signal tables per category/gate (`SB_SIGNALS`), live score preview, and AI coaching scripts per signal. B8: publish review + async submit. `sellSheetContinue()` now routes returning sellers to `goTo('sell-b')`.

**Routing wired:** `goTo('sell-b')` calls `sbReset()` on navigation. `sell-b` added to DEMO_MODE block list. File integrity restored after truncation — working file rebuilt from new content + git HEAD tail, ending correctly with `</html>` at 11,274 lines.

**Session 38 fixes (testing feedback):** (1) Photo step label on B1 intro is now category-specific — "Room-by-room photos" for Property, "Full vehicle walkthrough" for Cars, "Teaching environment photos" for Tutors, etc. Updated dynamically when B5 renders. (2) Skip buttons on B7 Trust Score now work correctly — skipped signals collapse to a small "+ Add [signal]" restore link; `sbRestoreSignal()` brings them back. (3) Experience tier mutual exclusivity — declaring/uploading a higher tier (10+, 7+, 5+) hides the lower tier card automatically. (4) All sellers start at Trust Score 40 (Established tier) — base score applies to all categories not just LocalMarket. (5) Publish error messages are now descriptive — raw BEA error body is read and shown with actionable guidance. (6) Draft save/resume — `sbSaveDraft()` saves state to IndexedDB (`aaDB`) keyed by email. Auto-saves on every forward step. "Save draft — finish later" button on B7 and B8. Resume banner appears on B1 when a draft exists. Dashboard shows "Continue draft" banner. Draft deleted on successful publish. Drafts expire after 7 days.

## Session 37 · 2 May 2026 · Listing State Machine — BEA Schema + Query Guards

**BEA schema migration — listing state machine columns:** Added `listing_status TEXT NOT NULL DEFAULT 'live'`, `status_changed_at TEXT`, `block_cause TEXT`, and `fade_nudge_sent_at TEXT` to the listings table via an idempotent `run_migrations` block. Added `eula_accepted_at TEXT` to the users table (separate from `lm_eula_accepted_at` which is the Local Market supplemental EULA). Created `idx_listings_status` index on `listing_status` for efficient filtered queries. All existing listings default to `'live'` — no data backfill required. Default is intentionally `'live'` so current production data remains visible without a migration script.

**BEA query guards — `listing_status = 'live'` enforcement:** Five endpoints now enforce the state machine. `GET /listings` (main public browse) — `suspension_filter` extended to include `listing_status IS NULL OR listing_status = 'live'`, covering both branch A (home city) and branch B (extended city reach via UNION). `GET /local-market/listings` — added `listing_status` guard to the WHERE clauses list. `GET /local-market/listings/{listing_id}` — same guard in the single-row fetch. `POST /intros` (standard intro creation) — returns HTTP 409 with detail `"Listing is not available for introductions (status: X)"` if listing is not live. `POST /local-market/intro` — same 409 gate immediately after the existing suspension_reason check. The `IS NULL OR = 'live'` pattern is used deliberately on all read paths so that the `DEFAULT 'live'` rows added before the migration guard runs correctly in production.

**File tail restored:** The working copy of `bea_main.py` was pre-truncated (20 lines missing from the `/opt-out` endpoint function body — same truncation bug as noted in CLAUDE.md). Tail restored from `git show HEAD` before syntax check. File now passes `python -m py_compile` cleanly at 6022 lines.

---

## Session 35 · 1 May 2026 · Multi-city seller reach

**Seller city reach — Free vs Starter/Premium:** Free sellers are visible in their home city only. Starter ($5/month) and Premium ($15/month) sellers can extend any listing to additional cities in the country. Buyers in those cities see the listing as local — they never need to know the seller's home base. The seller makes an explicit confirmation per city ("I can service buyers in [City]") which is recorded with a timestamp.

**BEA: listing_cities table:** `id, listing_id, city_id, seller_confirmed_at, added_at` with UNIQUE(listing_id, city_id). Three new endpoints: `GET /listings/{id}/cities` (public), `POST /listings/{id}/cities` (seller email-auth + tier gate), `DELETE /listings/{id}/cities/{city_id}` (seller email-auth). Free sellers receive HTTP 402 with upgrade message. `PUT /users/{email}/seller-tier` (admin/Paystack webhook) sets `free | starter | premium`.

**BEA: seller_tier column on users:** `seller_tier TEXT DEFAULT 'free'` added via idempotent ALTER TABLE migration. All existing users default to free.

**BEA: listings query includes extended cities:** `GET /listings` now returns a UNION of (a) listings with home city matching the buyer's city and (b) listings extended to the buyer's city via `listing_cities`. Buyer experience is unchanged — they simply see more listings. Suburb filter applies only to the home-city branch.

**BEA: geo/cities search:** `GET /geo/cities` now accepts `q=` parameter for name search (LIKE %q%), capped at 20 results. Used by the city-reach typeahead in admin.

**Admin: Extend City Reach panel:** After publishing, a green "Extend City Reach" panel appears below AI Guidance. Shows currently extended cities with remove button. City search input with 300ms debounce typeahead — select a city, confirm with "I can service buyers in [City]" checkbox, city is added instantly. Free sellers see a locked amber upgrade prompt (no search shown). Panel re-renders after each add/remove.

---

## Session 34 · 1 May 2026 · KYC identity verification + banking + cert name-match

**BEA: KYC identity verification (SA ID / Passport / National ID):** New `POST /users/{email}/verify-identity` endpoint. Accepts `id_number`, `full_name`, `doc_type`, and `doc_url`. For SA IDs: validates 13-digit Luhn checksum + extracts DOB/gender. Hashes the raw ID number with SHA-256 — never stored in plaintext. Calls Sonnet vision (`claude-sonnet-4-6`) to cross-check the uploaded document image against the claimed name and ID number. Awards tiered Trust Score signals: `id_uploaded` (+3, set on doc upload), `id_number_valid` (+4, Luhn pass), `id_ai_verified` (+8, Sonnet confidence ≥ 0.80 + name match ≥ 0.80). SWAP POINT documented: `_sonnet_verify_identity()` is the single function to replace with PaddleOCR for zero-token local verification. `_upsert_credential()` helper prevents downgrading earned signals to pending/rejected.

**BEA: Banking details + name-match:** New `POST /users/{email}/banking` endpoint. Stores account holder name, bank name, account last-4 digits, and branch code. Fuzzy-matches the account holder name against the verified `id_name` (if set) using `_names_match()` — handles initials, surname-first ordering, returns 0.0–1.0 confidence. Scores ≥ 0.70 auto-award `banking_name_match` (+5 pts) signal as earned; below threshold sets it to pending for admin review. `banking` (+3 pts) signal always awarded on submit.

**BEA: Certificate name-match via Sonnet (background task):** Document upload endpoint for `certificate`, `training`, and `membership` doc types now triggers `_run_cert_name_check()` as a FastAPI BackgroundTask after upload. If the seller has a verified ID (`id_verified_at` set), Sonnet reads the certificate and checks whether the name on the cert matches `id_name` (fuzzy match ≥ 0.70 + Sonnet confidence ≥ 0.75). Awards `cert_name_verified` (+3 pts) as earned or pending accordingly. Upload response is instant — check runs in background.

**Admin: ID verification UI in Document Hub:** After uploading an `id_doc` type document, the Document Hub shows an inline "Verify Identity" panel (purple border) with fields for full name, doc type selector (SA ID / Passport / National ID), and ID/passport number. Calls `POST /users/{email}/verify-identity`, displays Sonnet confidence %, name match %, ID format validity, signals awarded, and AI notes. Existing verified status shown as a green banner on panel load; unverified-but-doc-uploaded state shows an amber "Verify Now" prompt. "Skip" button dismisses the panel.

**DB migration:** `user_credentials.updated_at` column added to live DB (idempotent ALTER TABLE added to `init_db` migration block for future redeploys). Ten KYC columns added to `users` table: `id_number_hash`, `id_name`, `id_doc_type`, `id_verified_at`, `id_ai_score`, `banking_holder`, `banking_bank`, `banking_account_last4`, `banking_branch`, `banking_added_at`.

**Trust signal hierarchy (max 25 pts for full identity verification):** uploaded(+3) → number valid(+4) → AI verified(+8) → admin confirmed(+10). Privacy principle: raw ID numbers are never stored.

---

## Session 34 · 1 May 2026 · LM multi-photo upload + Document Hub + 12 LM Trust Score signals

**LM multi-photo upload (admin):** LM create modal now uploads up to 5 photos in sequence via `/listings/photo`, collects all URLs into `photo_urls` JSON array, and sends it with the listing POST. Photo preview thumbnails shown inline as files are selected. `LMListingIn` Pydantic model and `lm_create_listing` INSERT both updated to accept and store `photo_urls`.

**Document Hub (admin):** New Document Hub panel renders below the Trust Score Hub whenever a seller profile is looked up. Seller can upload PDF/image/Word documents, label them, choose doc type (ID, Certificate, Training, Professional Body, Official Role, Product Guide, Recipe, Presentation, Other), and set visibility: **Private** (never shown to buyers) or **Visible after introduction** (shown on seller profile once intro is accepted). Uploading certain doc types auto-sets the matching Trust Score signal to `pending` — e.g. uploading an ID doc triggers `category.lm.id_uploaded`, uploading a certificate triggers `category.lm.formal_cert`. Admin can then mark as earned/rejected from the Trust Score Hub. Document list shows with emoji icon, label, visibility badge, View link, and delete button.

**New seller_documents DB table:** `id, email, doc_type, label, url, visibility, signal_id, uploaded_at` — created via `init_db` on BEA restart. Four new BEA endpoints: `POST /users/{email}/documents`, `GET /users/{email}/documents` (admin), `GET /users/{email}/documents/public` (buyer, returns only post_intro), `DELETE /users/{email}/documents/{id}`.

**12 LM Trust Score signals:** `local_market` category group expanded from 2 to 12 signals (max 40 pts total): phone verified (+5), banking (+5), ID uploaded (+10), 1yr experience (+4), 5yr experience (+4, replaces 1yr), training course (+4), formal cert (+6, replaces training), professional body (+5), official role (+6), product guide/recipe (+3), media feature (+3), social proof (+2).

**Buyer app — seller documents visible:** `openLMSellerProfile()` now async — fetches `/users/{email}/documents/public` and renders shared documents in the credentials section. Seller-chosen `post_intro` docs (guides, recipes, certificates, etc.) appear with emoji icon, label, and View link. Private docs are never exposed.

---

## Session 33 · 30 April 2026 · LM home tile: cycling photos + live count + card photo fix

LM home tile now shows live listing count ("12 listings") via `initLMHomeTile()` which fetches `/local-market/listings` on load and updates `#lm-home-count`. Background image cycles through all 12 LM listing thumbs (random start, 3.5s interval, 0.6s fade transition) while the 🛍️ icon and "Local Market" label stay fixed in the centre overlay. LM card grid photos fixed: added `referrerpolicy="no-referrer"` to all LM `<img>` tags (card thumbs + detail strip slides) so Unsplash serves images without requiring a page referrer header — was causing emoji fallback to show instead of real photos.

---

## Session 33 · 30 April 2026 · LM multi-photo strip + 12 example listings

**LM photo strip:** `lm_get_listing` BEA endpoint updated to SELECT `l.photo_urls` and return it in the response. `lmOpenDetail` frontend updated to parse the `photo_urls` JSON array and render a full `photo-strip-wrap` / `photo-strip` / `photo-strip-slide` structure — identical to standard listing detail: swipe/scroll with snap, dot indicators, left/right arrow buttons, lightbox on tap (using generic `openLightboxById`/`_listingPhotosCache` keyed as `lm-{id}`), dnav back button (→ `local-market`) and wishlist heart. Falls back to `medium_url` or `thumb_url` if no `photo_urls`. **12 new example LM listings** (ids 57–68) inserted into live DB with 5 Unsplash photos each: Bee Lady honey/beauty, MtG rare cards, Samsung S24 Ultra, MacBook Pro M3, Gaming PC RTX 4080, Samsung washing machine, Rare SA stamps, Rare SA coins/Krugerrands, Leica M6 camera, Vintage vinyl records, Antique riempie chair, Hermès Birkin 30. `photo_urls` TEXT column added to `listings` table via ALTER TABLE. All verified live at trustsquare.co.

---

## Session 33 · 30 April 2026 · LM cards: heart icon + View Seller Profile + flow diagram

LM cards now match standard cards: heart/wishlist button added to top-right of image box (uses `lm_N` key to avoid collision with standard listing ids); "View seller profile" badge added to card bottom — taps through to LM seller CV screen via `lmOpenDetailAndProfile()`. LM detail screen now has full Soft Queue flow diagram (🛍️ Soft Queue · Local Market, 5 steps, seller-pays copy). Grid updated to 3 columns. Intro modal copy corrected: Tuppence notice updated to seller-pays, CTA reads "free for buyers". Immediate `addTx` + toast feedback in `lmSubmitIntro` so buyer sees confirmation instantly.

---

## Session 33 · 30 April 2026 · LM grid 3-column + intro modal flow fixed

LM browse grid changed from 2 columns to 3 (`repeat(3,1fr)`, gap 8px, padding 12px) to match standard listing grid. Adventures/Experiences grid stays single-column (flex column) as designed. LM intro modal flow fixed: `openLMModal()` now updates the Tuppence deduction notice to "Seller-pays model — no Tuppence deducted from you" and sets the CTA to "Request Introduction · free for buyers". `lmSubmitIntro()` now calls `addTx()` + `showToast('⏳ Sending…')` immediately for visible feedback before the async API call. `openModal()` (standard) now resets the Tuppence notice text and clears `pendingLMIntroId` so LM state never leaks into standard listing modals.

---

## Session 33 · 30 April 2026 · AI Guidance (Haiku 4.5) + LM detail fixes

**AI Guidance feature:** New `POST /trust-score/guidance` BEA endpoint calls Haiku 4.5 (`claude-haiku-4-5-20251001`) to generate a personalised, category-specific action plan showing sellers exactly what evidence to upload to reach Trust Score 50 (Established tier). Endpoint computes current score from DB, identifies unearned signals, sends a structured prompt to Haiku, and returns `{intro, steps[{action, points, why}], closing, current_score, points_needed}`. Falls back to pure-local logic if API key is absent. Admin app: after `publishAll()` succeeds, `loadAIGuidance()` is automatically called and renders a purple-branded panel inside the publish-result area — shows score bar, numbered action steps with point values, and AI/local badge. `@keyframes spin` added for the loading spinner. Smoke tested live: Haiku returning correct category-specific steps for Services-Technical, Tutors, and local_market.

**LM detail fixes:** View Seller Profile button added → `openLMSellerProfile()` renders into standard `screen-seller-cv`. Sticky-CTA now opens standard `intro-modal` via `openLMModal()`. `submitIntro()` updated with `pendingLMIntroId` branch → `lmSubmitIntro()` calls `/local-market/intro` with full error handling (403/410/402/429) and `showToast()` instead of `alert()`.

---

## Session 33 · 30 April 2026 · LM detail: View Seller Profile + proper intro modal wired

**L1 + L2 (pre-session):** Removed `POST /dev/credit` BEA endpoint and Dev Tools nav tab from admin app — pre-launch security cleanup. **H1 (pre-session):** Local Market cards and detail screen updated to use standard `lcard`/`dsheet` CSS classes for visual parity with standard listings. **H1 fixes:** Three items added to LM detail screen that were missing after H1: (1) "View Seller Profile" button — taps through to seller CV screen using `openLMSellerProfile()`, same layout as standard BEA seller profile; (2) sticky-CTA "Request Introduction" now opens the standard `intro-modal` (nice sheet UI) via `openLMModal()` instead of a raw browser `prompt()`; (3) `submitIntro()` updated to detect `pendingLMIntroId` and route to `lmSubmitIntro()` which calls `/local-market/intro` with all correct error handling (403/410/402/429). `_lmCurrentListing` module variable holds the fetched LM listing so both new functions have access without passing arguments through onclick strings.

---

## Session 32 · 30 April 2026 · Zero listings bug fixed — truncated HTML restored

**Root cause:** `marketsquare.html` was silently truncated mid-line during a previous write, cutting off the last 63 lines including the closing `</script>` tag. The entire `ms-logic` script block was dead — `loadLiveListings` was never defined, so no listings ever loaded. Restored missing tail from git commit ff2f4cd. Added HTML tail-check rule to CLAUDE.md to prevent recurrence. Also added retry logic to `loadLiveListings` (retries once after 4s on BEA failure) and placeholder fallback to `renderCatCounts` so tiles never show "0 listings".

---

## Session 31 · 30 April 2026 · Full Paystack payment flow wired end-to-end

`confirmTopUp()` in the buyer app now passes a `callback_url` (`?ps_return=1`) to `/payment/initialize`, which forwards it to Paystack so buyers are returned to the app after checkout. Added a `ps_return` URL param handler in `DOMContentLoaded` — detects the Paystack redirect, calls `/payment/verify`, credits the local Tuppence balance, shows a success toast, and navigates to the wallet screen. Cancellation (no reference param) shows a "Payment was cancelled" toast. BEA `/payment/initialize` endpoint updated to accept and forward `callback_url`. Smoke tested: real Paystack checkout URLs generated correctly from the live server. Full flow is ready to test end-to-end the moment Paystack live mode is approved.

## Session 31 · 30 April 2026 · payments.py created, Paystack webhook endpoint, live mode ready

`payments.py` written from scratch and added to the local repo. Module reads `PAYSTACK_SECRET_KEY` from the server `.env` — works transparently in both test and live mode with no code changes. Exports `initialize_payment`, `verify_payment`, `get_balance`, and `verify_webhook_signature`. Added `POST /payment/webhook` endpoint to `bea_main.py` — handles Paystack `charge.success` events, validates HMAC-SHA512 signature using `PAYSTACK_WEBHOOK_SECRET`, and credits Tuppence/AI sessions with idempotency guard (skips re-processing the same reference). This is now the authoritative server-side credit path; the existing client-side `/payment/verify` remains as a belt-and-braces backup. Added `.env.example` template documenting all required server environment variables. Added `PAYSTACK_SETUP_GUIDE.md` with step-by-step instructions for completing Paystack business verification (CIPC cert + FNB bank details), configuring the webhook URL, retrieving live keys, and running end-to-end test card verification.

Cost model impact: Paystack live mode will incur 2.9% + R1 per ZAR transaction (capped at R2,000/month at high volume). At R36 per Tuppence, net per T ≈ R33.96. Settlement T+1 to FNB account 63208160117.

## Session 30 · 29 April 2026 · CIPC registration confirmed — banking & payment unblocked

TRUSTSQUARE (PTY) LTD (registration number 2026/340128/07) was formally incorporated on 29 April 2026 under the Companies Act, 2008. Director and sole incorporator: David Maurice Conradie. Financial year end: February. Two official CIPC documents confirmed and saved to the MarketSquare project folder: `CoR15_1_A_9457451003.pdf` (COR 14.3 Registration Certificate + COR15.1A Memorandum of Incorporation) and `9457451884.pdf` (COR9.4 Name Reservation Confirmation — TRUSTSQUARE reserved until 29 October 2026). Registration unblocks Paystack live mode and the FNB Business Account application. Critical follow-up actions logged in STATUS.md: Beneficial Ownership filing with CIPC (legal obligation, due by ~13 May 2026), FNB account (prerequisite for Paystack live mode), and international entity decision for Stripe (required before Wave 1 global launch — NY/LON/BER cannot process payments through a SA entity alone; cost model already budgets $100/month for this). TRUSTSQUARE name challenge window runs until 29 July 2026 — monitor CIPC correspondence. First Annual Return due Feb/Mar 2027.

Cost model impact: None to current model. International entity cost ($100/mo) already included in Operating Costs sheet from Day 1. Paystack live mode activation will shift SA transactions from test to live — blended 2.5% rate assumption in cost model is correct.

---

## Session 29 · 28 April 2026 · LM sell flow, photo compress, home grid, superuser, CRLF fix

- **CSS fix**: Added `--navy` CSS variable to admin app `:root` — Confirm button in LM modal was transparent/invisible.
- **SSH deploy**: Project `.ssh/id_ed25519` key committed — sandbox can now deploy autonomously every session without PowerShell.
- **Superuser system**: `isSuperuser()` helper in both apps; BEA `is_superuser` column seeded for David, Maroushka, Dave, Maurice — bypasses trust score gates and LM publish checks until launch day.
- **CRLF fix (permanent)**: `.gitattributes` enforces `eol=lf` on all text files — eliminates recurring UTF-8 truncation from Windows CRLF conversion.
- **Sell wizard**: Local Market tile added to Step 2 category picker in marketsquare.html.
- **sellSheetContinue()**: Fixed routing — now opens publish wizard instead of going to dashboard.
- **Photo compression**: `handleImg()` silently compresses photos >2MB via canvas (1200px max, 80% JPEG) instead of warning.
- **API_KEY fix**: Added `const API_KEY` to marketsquare.html config block — was undefined, causing "Connection error" on LM publish.
- **Double photo fix**: Step A photo (pubImg) passed to LM modal; photo row hidden if photo already chosen.
- **Home grid**: Full-width Local Market tile added to Categories grid (`grid-column:1/-1`, aspect-ratio 6/1) — ready for future boosted ad scroll strip.
- HEAD: 4e7c97f

## Session 28 · 27 April 2026 · Hotfix — Trust Score is buyer-filter, not server gate (LM-08 / LM-15 design correction)

**Defect found in V1 of Local Market.** As shipped in `0baa67b`, `_lm_check_seller_can_publish` rejected `POST /local-market/listings` with HTTP 403 if the seller's Trust Score was below 30. `lm_create_intro` rejected `POST /local-market/intro` with HTTP 403 if the buyer's score was below 20. `_lm_recompute_seller_state` auto-suspended a seller's listings any time the score recomputed below 30, regardless of cause. All three behaviours faithfully implemented LM-08 / LM-15 / LM-17 as written in the v0.1 spec. All three were wrong: every new seller starts at 0 and every new buyer starts at 0, so the gates blocked the entire bootstrap path. The first user to try to publish on production hit `trust_score_below_30` and could not proceed without a manual DB poke (the conversation thread that surfaced this — the admin's own seller email computed to 10 after the Trust Score Hub recomputation, well below the 30 threshold).

**Root cause — internal contradiction in `LOCAL_MARKET_REQUIREMENTS.md` v0.1.** LM-08 said "Trust Score ≥ 30 to publish." LM-14 said "sellers below 40 are visible but warned." Both clauses cannot be true simultaneously. The build agent in Session 28 implemented LM-08 literally without flagging the contradiction. LM-14 was always the correct intent, consistent with `WISHLIST_REQUIREMENTS.md` PR-08/PR-09 (Trust Score is a buyer-set filter with "Any seller" as the default), the marketplace philosophy of universal visibility + buyer-side trust signalling, and the platform principle that buyers earn the right to filter while sellers earn the right to be seen.

**Fix.** `_lm_check_seller_can_publish` now blocks publish only on permanent LM ban (third-strike, LM-14e) or active 30-day cooling-off period (second suspension within 90 days, LM-14e). Bootstrap-by-low-score is no longer a gate. `lm_create_intro` no longer gates on buyer Trust Score — instead, the buyer's score is exposed in the response and in the n8n notification payload so the seller can see it on the intro request and decide whether to accept. `_lm_recompute_seller_state` only auto-suspends a seller when there are active complaints AND the score is below 30 — a new seller with score 0 and zero complaints stays live. Frontend updated: dead `buyer_trust_below` 403 branch removed from `lmRequestIntro`; admin LM creation modal now shows a soft toast warning when the seller's score is below 40 ("score X/40 limits reach. Build Trust to widen visibility.") instead of erroring out; suspension panel message clarified to attribute suspension to upheld complaints rather than mere score collapse; EULA modal clauses 2 and 4 rewritten to match the corrected design.

**`LOCAL_MARKET_REQUIREMENTS.md` bumped to v0.2.** LM-08, LM-14, LM-14a, LM-15, LM-17, §11.2, §11.4 all rewritten with `(v0.2 — REWRITTEN)` or `(v0.2 — clarified)` markers preserving the audit trail. The bad-actor suspension logic (LM-14a–f, three-strike escalation, permanent ban) is unchanged — those are complaint-driven, not bootstrap-driven, and they're correct as designed.

**Privacy / cost confirmations.** Anonymity unchanged — buyer Trust Score is surfaced to the seller as a number on the intro request, never an identifier. The seller does not see the buyer's email or token at any point before mutual acceptance. Zero new external API calls — the soft-warning lookup uses the existing `GET /users/{email}` endpoint to read the score back after publish. SQLite-only.

**Cost model impact:** none. No new infrastructure, no new pricing.

---

## Session 28 · 27 April 2026 · Section 5 — version bump, deploy verifications, final review (BEA v1.2.0 → v1.3.0)

**BEA bumped to v1.3.0** in both the FastAPI app constructor and the `/health` response. Sessions 27/28 land Local Market and Trust Score Hub end-to-end.

**Deploy script verifications** in `deploy_marketsquare.bat` extended with seven new checks: BEA Local Market endpoints, BEA Trust Score Hub endpoint, buyer Local Market page, admin Local Market form + EULA modal, admin Trust Score Hub UI, and a localhost `/health` curl that asserts v1.3.0 is actually running (catches the case where the SCP succeeded but systemd didn't reload). Each check is independent so a single missing component shows as a `[FAIL]` line without aborting the rest.

**Final review pass.** All Trust Score point values cross-checked against `TRUST_SCORE_CRITERIA.md` v1.0 row by row — the `_TRUST_SIGNALS` and `_CATEGORY_SIGNALS` dicts in `bea_main.py` mirror the spec exactly: PPRA=15, NQF4=6, NQF5=+6, NQF6+=+8, IEASA/SAPOA/NAR=5; SACE=8, NQF5–6 cert=6, NQF7=10 (replaces), NQF8+=14 (replaces); ECSA/PIRB=12, trade cert=8, CoC=5, additional tickets +3 max +6, 3–7yr=4, 7+yr=+4, strong CV=2; NQF qualification=8, 2–4yr=6, 5+yr=+8, ref letter=8, second ref=+5, profile=5; FGASA/PADI=12, First Aid=6, 3–7yr=5, 7+yr=+5, safety cert=4, insurance=5, secondary qual=3; TGCSA 1★=6, 2★=10, 3★=14, 4★=18, 5★=22 (chained replacements), licence=6, H&S=5, fire=4, award=3; specialisation=4, tx 1–4=8, 5–14=+6, 15+=+6, auth cert=8, appraisal=5, association=3. Penalty scale `[-8,-5,-3,-2,-1]` and cap `−22` match §5a exactly.

**Anonymity review.** All Local Market and Trust Score Hub endpoints audited: `lm_list_listings` and `lm_get_listing` SELECT only public fields and pass through `_strip_seller_identity`; `lm_create_intro` returns `tuppence_charged_to_seller` (a count, not an identifier) and never echoes seller_email; `boost_stats` and complaint endpoints return aggregate counts only; the wishlist feed continues to scrub identity through `_strip_seller_identity`. The Trust Score breakdown is delivered to the admin tool only — buyers never see this surface.

**Bad-actor suspension is server-side, not just frontend.** Verified by reading `_lm_check_seller_can_publish` (called from `lm_create_listing` before any DB writes), the `suspension_reason IS NULL` filter on every `GET /local-market/*` endpoint, and the `_lm_recompute_seller_state` hook fired from `GET /trust-score/breakdown` whenever the recomputed score crosses the 30 threshold. Admin tool's frontend rendering is purely informational — bypassing the UI cannot get a suspended seller's listings published or visible.

**Zero external API calls in matching, tip generation, or suspension paths.** Grep-confirmed: `httpx`, `anthropic`, `openai` appear only in pre-existing flows (GeoNames seeding, Advert Agent coach, opt-out webhook, n8n webhooks, Paystack). The new Trust Score Hub uses pure Python list comprehensions and dict lookups; the Haiko tip is a sort-and-pick over the open-items list with a within-5-of-tier preference clause; the matcher (used by both wishlist and Local Market free-text search) reuses the Session 25 `LocalKeywordMatcher`. SQLite-only — no Redis, no Elasticsearch, no vector DB. Cost constraint holds.

Cost model impact: No new infrastructure. New revenue surface — Local Market seller-pays Tuppence (1T per listing's first intro, 2T if boosted) — to be projected into `Cost_Breakdown_GlobalLaunch.xlsx` once the feature has 1 week of live traffic. ⚠️ XLSX WRITE RULE applies — David must `git add Cost_Breakdown_GlobalLaunch.xlsx` after the next manual update.

---

## Session 28 · 27 April 2026 · Section 4 — Wishlist category dropdown removed (LM-22 free-text only)

**Removed the `<select id="wl-explicit-cat">` dropdown** from the wishlist add screen in `marketsquare.html`. Buyer types free-text only. Updated input placeholder to "Describe what you want — e.g. red mountain bike, 21-speed" and added an inline hint reading "Free-text — describe in your own words. We match across every category, including the Local Market." `wlAddExplicit()` now sends `category: null` to the BEA. No backend change required — `LocalKeywordMatcher.score_match` already handled null categories correctly from Session 25 onwards (the category mismatch gate short-circuits when `sig_cat` is falsy, and the +30 category bonus is simply not awarded). Trade-off: max possible score for a no-category signal is 70 instead of 100 — feed threshold of 60 still surfaces strong textual matches; push threshold of 80 becomes harder to reach for fuzzy-intent signals, which is intentional behaviour. Comment markers added in HTML and JS noting LM-22 so a future agent doesn't reintroduce the dropdown.

---

## Session 28 · 27 April 2026 · Section 3 — Trust Score Hub (BEA endpoint + admin UI)

**BEA — `GET /trust-score/breakdown?email=`** returns the full structured breakdown: score, tier name + colour, next-tier delta, three groups (Universal/Track Record/Category) each with `{earned, max, items}`, Haiko tip, and active penalties. Score is recomputed from `user_credentials` on every call and persisted to `users.trust_score` as a side-effect — so wishlist matching's trust gate and Local Market's suspension state see the live value. `_lm_recompute_seller_state` is hooked from this path, closing the loop on Section 2's "no automatic trigger yet" flag: when the Hub recomputes a score below 30, suspension fires; when it recomputes back above 30, restoration fires automatically.

**Schema additions** — new tables `user_credentials(email, signal_id, status, points, evidence_url, notes, submitted_at, verified_at, verified_by)` keyed UNIQUE on (email, signal_id) with status `pending|earned|rejected`, and `seller_complaints(seller_email, buyer_token, listing_id, reason_code, status, filed_at, resolved_at, points_deducted)` for the §5a diminishing-scale penalties. New column `users.primary_category` to drive which Group 3 checklist the seller sees; falls back to inferring from the most recent listing's category and service_class (handles Services-Technical/Casuals + Adventures-Experiences/Accommodation sub-cases).

**Constants** — `TRUST_TIERS` for tier thresholds; `_TRUST_SIGNALS` (10 universal + track signals); `_CATEGORY_SIGNALS` for all 7 category sets plus the Local Market signal subset per `TRUST_SCORE_HUB_REQUIREMENTS §3` last block; `_COMPLAINT_PENALTY_SCALE = [-8,-5,-3,-2,-1]`, `_COMPLAINT_PENALTY_CAP = -22`. Every value mirrors `TRUST_SCORE_CRITERIA.md` v1.0 exactly.

**Helpers** — `_compute_universal_track_status` (system-calculated signals: profile completeness, intro count milestones at 1/5/20, zero-ignored-90d window, tenure ≥ 6 months); `_sum_earned_with_replaces` (honours replacement chains so e.g. NQF7 replaces NQF6, only one TGCSA star level counts); `_seller_active_complaints` (diminishing scale per ordinal, 50% decay at 24 months, capped at −22); `_haiko_tip` (picks highest-impact uncompleted action; if within 5 of next tier, prefers the smallest action that closes the gap; respects `additional_to` prerequisite chains; pure local Python — zero external API).

**Admin endpoints** — `POST /trust-score/credential` flips a credential's state (`pending|earned|rejected`); validates `signal_id` against the known set so typos can't enter unknown rows. `GET /trust-score/credentials/pending` returns the ops review queue.

**Admin UI** — `#tsh-panel` div added inside the Profile view; auto-loads via a `loadSellerProfile` hook so admins look up a seller and immediately see the Hub. CSS for gradient summary panel, four tier badges (grey/blue/green/gold), bar fill animation, Haiko tip card, three collapsible groups with ✓/⏳/✗/○ status icons, and a red penalties section. Each Universal and Category row has inline "Mark earned / Pending / Reject" buttons (Track Record rows are read-only — system-calculated only, matching the spec). Clicking any button POSTs to the credential endpoint, refreshes the Hub, and re-renders the LM suspension panel since score recomputation may have flipped suspension state.

---

## Session 28 · 27 April 2026 · Section 2 — Local Market full implementation (BEA + buyer page + admin form)

**Local Market shipped end-to-end** per `LOCAL_MARKET_REQUIREMENTS.md` v0.1. New open-ended peer-to-peer category with seller-pays Tuppence model, completely separated from the structured-category grid, integrated with the existing wishlist matching engine.

**BEA — `bea_main.py`.** Schema migrations added under `run_migrations()`: `listings.suspension_reason`, `listings.lm_intro_charged` (idempotency flag), `intro_requests.intro_type` (default 'standard', 'local_market' for LM intros), `users.lm_eula_accepted_at`, `users.lm_banned_at`, `users.country` (default 'ZA' for LM-29 geo filtering), new tables `buyer_trust(buyer_token, score, last_changed_at)`, `lm_complaints(id, listing_id, seller_email, buyer_token, intro_id, reason, status, filed_at, resolved_at, credit_issued)`, `lm_suspensions(id, seller_email, suspended_at, restored_at, reason, cooling_off_until, is_permanent)` driving the LM-14e three-strike escalation. Constants exactly match the spec: `LM_INTRO_COST_T=1`, `LM_BOOST_COST_T=2`, `LM_SELLER_MIN_TRUST=30`, `LM_BUYER_MIN_TRUST=20`, `LM_REPEAT_WINDOW_DAYS=90`, `LM_COOLING_OFF_DAYS=30`, `LM_BUYER_NOSHOW_PENALTY=3`. Helpers: `_lm_check_seller_can_publish` (returns None or error string), `_lm_apply_suspension` (counts past suspensions in 90-day window — 1st = simple suspension, 2nd within 90d = 30-day cooling-off, 3rd = permanent ban via `users.lm_banned_at`), `_lm_try_restore` (auto-reactivates listings when score recovers AND cooling-off expired AND not permanently banned), `_lm_recompute_seller_state` (single hook to call when Trust Score changes). Endpoints: `POST /local-market/listings` (API key, gates on suspension/ban/score, persists country, kicks off `run_match_job`); `GET /local-market/listings` (anonymous-stripped, hides suspended, supports city/suburb/min_trust + free-text Haiko search via `MATCHER`); `GET /local-market/listings/{id}` (public detail, suspension-aware); `POST /local-market/intro` (buyer trust ≥ 20 gate, 7-day cooldown after decline/auto-close per LM-F3, seller balance check on first chargeable intro, idempotent first-intro-only deduction via `listings.lm_intro_charged` flag); `POST /local-market/complaint` (seller files no-show, status starts pending); `PUT /local-market/complaint/{id}/uphold` (API key, applies −3 buyer Trust per LM-T4/LM-16, issues 1T `lm_credit` to seller if listing still active per LM-T3); `PUT /local-market/complaint/{id}/dismiss`; `GET /local-market/complaints` (ops queue); `GET /local-market/suspension/check` (recovery-path query for admin tool); `POST /local-market/eula/accept` (records §11 EULA acceptance per LM-14f). `GET /listings` extended to hide suspended listings AND exclude `category='local_market'` from the main grid unless explicitly requested — preserves the LM-02 separation principle.

**Buyer app — `marketsquare.html`.** Stats row removed from home screen permanently per LM-19 (the bottom-half wishlist feed already lives in that real estate). Local Market banner added to Browse page per LM-20 — visually distinct gradient card above the structured chips, navigates to `screen-local-market`. New `screen-local-market` dedicated page with Trust Score guidance message, four-chip Trust filter (Any/40/70/90), debounced free-text search bar (also fires `wlCaptureSearch` so wishlist learns from LM searches), and a 2-column grid of anonymous cards. New `screen-local-market-detail` separate from the standard `openDetail` per LM-05 — hero image, title, price, suburb, Trust Score banner, description, "Request introduction" CTA. `lmRequestIntro()` handles 403 (buyer trust below 20), 402 (seller insufficient Tuppence), 429 (7-day cooldown), with friendly per-state messages. Defensive change to `updateTuppenceUI()` — the removed `tn-home-bal` element no longer throws.

**Admin — `marketsquare_admin.html`.** Local Market filter chip added to My Listings (🛍️ Local Market) — surfaces the "+ Create Local Market listing" action when active. Country selector on Profile per LM-29, populated from `GET /geo/countries`. Suspension status panel auto-rendered on Profile lookup per LM-14c, showing banned / cooling-off / suspended states with recovery messages. EULA modal with all six §11 clauses inline shown once before first publish per LM-14f — "I accept" calls `POST /local-market/eula/accept`. Listing creation modal with no category selector per LM-28: title, description, price, suburb, city, photos (first becomes thumbnail). Handles all error states with status text in the modal.

---

## Session 27 · 27 April 2026 · Geo/city selector bug fix (Section 1 of Local Market build)

**Root cause — listing creation hardcoded city='Pretoria'.** The publish flow in `marketsquare.html` (`doPublish`) sent `city: 'Pretoria', area: 'Pretoria'` to `POST /listings` regardless of which city the seller had selected. This was the dominant geo bug — every seller's listing got stamped Pretoria server-side, which then propagated everywhere else through the live-listings normalizer. The fix reads from `activeCity.name` and `activeCity.id`, attaches `geo_city_id` for the new geo hierarchy, and supplies the required `suburb` field (which was missing entirely — the server-side validator would have rejected publishes silently). A secondary bug in `loadLiveListings` was also corrected: the BEA returns both `area` and `suburb` distinctly, but the normalizer was overwriting both with `l.area`, ignoring `l.suburb`.

**Subtitle staleness across browse and filter sheets.** The browse page subtitle (`#browse-sub`) and six filter-sheet subtitles (Property, Tutors, Services, Adventures, Collectors, Cars) all hardcoded "Pretoria · …" strings. After switching cities the subtitles never updated. Fixed by reading `activeCity.name` in `filterBrowse` and `setFilter`, and by tagging the six static filter-sheet subtitles with `js-city-sub` for centralised refresh. Added a new `_refreshCityLabels()` helper called from `updateBadgeLabel()` so every city change flows through every dependent display string in one pass.

**Magic-link parser fallback.** The campaign magic-link parser fell back to the literal `'Pretoria'` when the `city` query param was absent. Fixed to fall back to `activeCity.name` (and empty string if also unset). Defensive — campaign emails should always include the param, but a malformed link no longer pre-fills the wrong city.

**What was confirmed not a bug.** The initial seed `let activeCity = { id: null, name: 'Pretoria' }` is correct — it's the bootstrap value before `_resolveActiveCity()` runs. The static demo `LISTINGS` and `SELLERS` arrays contain Pretoria strings as content (not state) — out of scope. The single live-listings GET (`/listings?city=...&suburb=...`) was already reading `activeCity.name` correctly.

**Verification.** Standalone commit. Frontend-only — no BEA changes. File structure preserved (1383 `<div>` / `</div>` paired, 8621 lines, 4 `</script>` blocks unchanged). After the fix, only two `'Pretoria'` references remain in app logic: the seed value and an explanatory comment in `_resolveActiveCity`.

---

## Session 26 · 27 April 2026 · Local Market + Trust Score Hub — requirements documents

**Local Market requirements written** as `LOCAL_MARKET_REQUIREMENTS.md` v0.1. Full specification for the new open-ended peer-to-peer trading category: dedicated page separate from all structured categories, unique seller-pays Tuppence model (1T deducted from seller on first introduction request per listing), Commitment introduction flow with 48hr response window and Trust Score incentives (+3 for <24hr response, −1 for ignoring), buyer no-show complaint flow (−3 buyer Trust Score, 1T seller credit on uphold), Trust Score minimum gates (30 to publish, 20 to submit intro), bad actor suspension policy (auto-suspend listings below score 30, Tuppence frozen not forfeited, three-strike escalation to permanent ban), and full EULA clauses covering all of the above. Wishlist Feed integration specified — Local Market listings feed into the "For You" home screen via semantic matching, badged separately. Home page stats row removed permanently to make space for the feed. Browse page gets a dedicated Local Market entry point.

**Trust Score Hub requirements written** as `TRUST_SCORE_HUB_REQUIREMENTS.md` v0.1. Full UI spec for the My Seller Hub Trust Score breakdown screen in the admin tool. Covers: summary panel with progress bar, tier badge, points-to-next-tier gap, and Haiko "best next step" tip card; three collapsible groups (Universal 30pts, Platform Track Record 30pts, Category Credentials 40pts) each showing exact point values, earned/pending/not-done status, and a direct upload action per credential; category-specific credential checklists for all 7 categories (Property, Tutors, Services Technical, Services Casuals, Adventures Experiences, Adventures Accommodation, Collectors, Local Market); penalties section showing active deductions with dispute link. All point values sourced directly from `TRUST_SCORE_CRITERIA.md` v1.0.

**Showcase seed script** `seed_showcase.py` deployed and run — 12 aspirational listings created (IDs 40–51): 1933 Double Eagle gold coin, Rolex Submariner, Penny Black stamp, MTG Alpha Black Lotus PSA 8, 1908 Ford Model T, 50-year Krugerrand set, Rolex Daytona Paul Newman, Inverted Jenny stamp, Pokémon Charizard PSA 10, Patek Philippe Grand Complication, 1994 Mandela inauguration gold coin, MTG Beta Mox Sapphire. All added to `wishlist_showcase` table. Photos pending (no thumb_url set — to be added in next session).

## Session 25 · 27 April 2026 · Wishlist Feed — full implementation (BEA + frontend + Web Push)

**Wishlist Feed v1 shipped end-to-end** per `WISHLIST_REQUIREMENTS.md` v0.2. The platform now hunts on the buyer's behalf: browsing builds a wishlist, the matching engine surfaces hits within 60 seconds in a bottom-half scroll feed on the home screen, and strong matches push to a connected wearable. Zero external API cost — all matching runs locally on the existing Hetzner CPX22.

**BEA — `bea_main.py` v1.1.0 → v1.2.0.** Five new SQLite tables (`wishlist_signals`, `wishlist_matches`, `wearable_devices`, `wishlist_showcase`, `wishlist_subscriptions`), new columns on `users` (`buyer_token`) and `listings` (`published_at`, `boost_until`, `view_count`). New `LocalKeywordMatcher` class with stop-word filter, inline Porter-style stemmer, curated synonym map, and a 0–100 score combining category match (+30, hard zero on mismatch), title-token overlap (up to +35), body-token overlap (up to +20), suburb/city match (+10), and price-range fit (+5). Six standalone matcher tests pass — "red bicycle" ↔ "crimson bike, 21-speed" scores 85 confirming PR-12. Hot-swappable behind `MATCHER = LocalKeywordMatcher()` so a future Haiko 4.5 implementation can drop in without touching call sites. `run_match_job(listing_id)` runs as a `BackgroundTask` from `POST /listings`, `POST /advert-agent/publish`, and `PUT /listings/{id}` — never blocks publish (PR-14). Trust Score gate is absolute (PR-08, PR-43): listings from sellers below the per-signal `min_trust_score` are excluded before scoring. Geographic gate honours subscription tier — free buyers see only same-country listings unless the seller boosted, Global tier sees everything. New endpoints across the wishlist surface: `POST /buyer-token`, full CRUD on `/wishlist/signals`, `GET /wishlist/feed` (with anonymity-stripped cards + free-tier upgrade prompt), `GET /wishlist/showcase`, admin showcase add/reorder/remove, `POST /wishlist/boost` (2T deduction via `transactions` table with `type='boost_deduct'`, 7-day boost window, kicks off re-match at the 45 threshold), `GET /wishlist/boost/stats` (aggregate counts only, never identities — PR-42), `POST /wishlist/subscription/initialize` + `verify` for the $5/month Global tier via Paystack, plus `GET /wishlist/subscription/status`. Wearable Web Push uses free VAPID — auto-generated P-256 keypair persisted to `/etc/marketsquare-vapid.json`, `pywebpush` for delivery direct to FCM/Mozilla/Apple gateways. Push payload contains category + suburb/city + ≤90-char excerpt only — no seller identity, no listing_id, no price (PR-35 strict). Rate-limited to 3 pings/buyer/hour (PR-36). Dead push subscriptions returning 404/410 are auto-removed.

**Frontend — `marketsquare.html`.** Bottom-half wishlist feed container added to `screen-home` with horizontal scroll, FEATURED/Trust badges, and a free-tier upgrade banner that surfaces when matching listings exist in other countries. New `screen-wishlist` settings screen with Trust Score floor (Any/40/70/90) that propagates to every saved signal so wearable pings honour the floor, an explicit-item form, a saved-signals list with per-row delete and "Forget me" wipe, a wearable pings toggle, and the privacy footer "Your wishlist never leaves MarketSquare." Signal capture wired non-invasively by wrapping `goTo`, `openDetail`, `filterBrowse`, and `setFilter` — every category click and listing view becomes a wishlist signal. Showcase scroll runs for visitors with <3 signals (PR-27/28); personalised feed takes over after that. 60s polling refresh while home screen is active (PR-31). Web Push registration flow uses the standard browser API: `navigator.serviceWorker.register`, `pushManager.subscribe`, sends subscription to BEA — handles permission denial and unsupported browsers gracefully.

**Admin — `marketsquare_admin.html`.** New "Showcase ✨" tab between Cities and Dev. Curate the empty-state feed with a search-filter picker over all listings, current-showcase list with up/down/remove controls, and add/reorder/remove all wired to the new admin showcase endpoints.

**New file — `service-worker.js`** at project root. Installs with `skipWaiting` + `clients.claim` for fast updates. `push` event renders a notification tagged by `match-{id}` so re-runs of the match job for the same listing don't double-ping. `notificationclick` focuses an open MarketSquare tab or opens the site root. Deploys via `deploy_marketsquare.bat` (now Step 3 of 6).

**Deploy script — `deploy_marketsquare.bat`.** Bumped from 5 steps to 6: added `service-worker.js` SCP step, added pre-flight existence check for the new file, added three new server-side verifications (BEA wishlist endpoints, admin showcase tab, buyer wishlist UI, service-worker.js presence). David must `pip install pywebpush cryptography` on the Hetzner server before first deploy of v1.2.0 — without these, the BEA falls back gracefully (pings disabled, all other wishlist features still work).

**Privacy architecture confirmations.** Anonymity is absolute throughout: the feed endpoint omits `seller_email`, `name`, `email`, `aa_*`, `photo_url` from every card; boost stats return aggregate counts only; push payloads omit listing_id and price; buyer_token never appears in URLs except dedicated wishlist endpoints; matching queries never expose buyer identity to any external caller; 90-day inactivity expiry on signals (PR-06) lazy-purged on read.

Cost model impact: BEA bumps from 1.1.0 to 1.2.0 with new revenue streams now live in code — Global wishlist subscription at $5/month per buyer (R90 ZAR via Paystack) and Tuppence boost at 2T = $4 per listing per 7 days. Server-side cost increase is zero — matching is pure Python, push uses free VAPID, no new infrastructure. SQLite database adds ~5 small tables; estimated 100 KB per active buyer per quarter. Volumes to be projected into `Cost_Breakdown_GlobalLaunch.xlsx` once the feature has 1 week of live traffic. ⚠️ XLSX WRITE RULE applies — David must `git add Cost_Breakdown_GlobalLaunch.xlsx` after the next manual update.

---

## Session 24 · 26 April 2026 · Wishlist Feed — Requirements & Architecture

**Wishlist Feed requirements document written and saved** as `WISHLIST_REQUIREMENTS.md` v0.2 in the MarketSquare project folder. The document covers the full product vision, 44 product requirements across 8 sections, data model (5 new tables), system flow, agent responsibilities, and privacy architecture. Key design decisions locked: Trust Score filter as a first-class safety gate (≥90 for Highly Trusted sellers), Free/Global subscription tiers ($0 national / $5/month global), Tuppence boost at 2T with expanded match tolerance and global reach, Haiko 4.5 as the semantic matching agent socket with keyword fallback, Apple Watch in scope for V1 via APNs, and the empty-state showcase (gold coins, Rolex watches, rare collectors cards) as the wow-factor first impression for new visitors. Banking details collected at onboarding earn bonus Trust Score points — required later for payments, optional now. Privacy principle formalised: "Your wishlist never leaves MarketSquare." Feature is fully specified and ready for implementation by a build agent in Session 25.

Cost model impact: Two new revenue streams identified — Global wishlist subscription ($5/month per buyer) and Tuppence boost (2T = $4 per listing per 7 days). Volumes to be projected and added to Cost_Breakdown_GlobalLaunch.xlsx before build begins.

## Session 23 · 25 April 2026 · UX feedback round + cost model + whitepaper + launch campaign

**Cost model:** ZAR/USD rate added (Assumptions B62 = R18.50). Three new overhead rows: Accountant R2,000/mo, software R500/mo, SA corporate tax 27% (Year 1 = $0). Revenue vs Cost rows 21–25 number format fixed (was showing $ on unit counts).

**FEA:** Desktop Featured carousel scroll arrows (pointer:fine only). Photo lightbox — tap photo to full-screen, arrows + keyboard + Escape to close. My Requests dashboard tab added. Back buttons on Browse, Saved, Wallet, Recruit screens. Coming soon cards now always sort last in grid. Credentials renderer fixed (string vs object — was showing "undefined"). Trust Score composition note added to seller CV hero. Browse back button added. Deploy pending (run deploy_marketsquare.bat).

**WhitePaper v3:** Full IP hardening — 7 patent claims (Unified Participation Model, Tuppence currency, anonymous intro protocol, Trust Score, geo-tier visibility, founding cohort, combination claim). Added database schema specificity, dual-entity structure (SA + international IP-holding entity), infrastructure redundancy roadmap, security architecture, trademark filing guide (CIPRO Classes 35/36/42 + Madrid Protocol), 5 independent timestamp authorities, provisional patent filing instructions. Saved as `TrustSquare_WhitePaper_v3.docx`.

**Launch campaign:** 5-wave email sequence written for Pretoria property agents, Keller Williams RSA, and global agents. Wave 1 (launch 9 AM) · Wave 2 (+2h, scarcity) · Wave 3 (+4h, objections) · Wave 4 (Day 2, personal founder note) · Wave 5 (Day 5, final close). Full sending guidelines, UTM tracking, suppression logic, and post-wave-5 nurture plan included. Saved as `TrustSquare_LaunchEmails_5Wave.docx`.

## Session 22e · 19 April 2026 · Fix Adventures detail view — CATS lookup crash + rich detail fields

**Root cause** — `openDetail()` called `CATS[l.cat]` with `l.cat = 'adventures_accommodation'` or `'adventures_experiences'`, neither of which exists in the `CATS` object (which only has `'Adventures'`), causing an immediate crash.

**Fix:**
- Added `catCfg(l)` helper that maps Adventures subcategories to `CATS['Adventures']` with a safe fallback
- Replaced all 21 `CATS[l.cat]` usages in `openDetail`, `cardHtml`, `renderFeatured`, and related functions with `catCfg(l)`
- Adventures detail screen now shows correct category display label (🏕 Accommodation / 🌄 Experiences)
- Location meta now includes country flag + code and environment label
- Price shown with correct per-country currency symbol (R / $ / CA$ / £ / € / A$ / NZ$)
- Adventure-specific detail chips: group size, duration, environment type

---

## Session 22d · 19 April 2026 · Fix Adventures browse screen — cards not rendering

**Root cause found and fixed** — `renderAdvGrid()` called `esc()` (an HTML-escape helper) which was never defined anywhere in the codebase. When the function ran, it filtered listings and set the count text successfully, then crashed with `ReferenceError: esc is not defined` before it could set `grid.innerHTML` — leaving the grid visually empty despite the correct listing count appearing above it.

**Fix applied:**
- Added `const esc = s => ...` HTML-escape function directly above the Adventures screen code
- Fixed `demo_adv_1–10` listings: changed `cat:'Adventures'` to proper subcategories (`adventures_experiences` for experiences, `adventures_accommodation` for demo_adv_6 (Waterberg Lodge) and demo_adv_7 (Waterkloof Guesthouse))
- Added `country:'ZA'` to all `demo_adv_*` listings (previously missing, causing all to pass the ZA filter without being country-tagged)
- Replaced `adventureType` field with `environment_type` on all `demo_adv_*` listings (matching the chip filter keys)
- Normalised price strings to numeric format (`'R 2 450'` → `'2450'`) for correct currency display

**Adventures ZA count:** 17 listings (12 experiences + 5 accommodation). All tab and environment chip filters now work correctly. JS syntax verified clean.

---

## Session 22c · 19 April 2026 · Full demo listings for Property, Tutors and Services

**Property demo listings (8)** — Waterkloof Ridge family home, Erasmuskloof Tuscan estate, Menlyn cluster, Brooklyn penthouse, Raslouw smallholding with income, Irene townhouse, Hatfield investment flat, Silver Lakes vacant stand. All with propType, beds, baths, garages, floor_area, erf_size, listingType, full descriptions and 3 Unsplash photos each.

**Tutors demo listings (6)** — Maths & Science matric specialist, English Home Language online tutor, Piano lessons ABRSM Grade 8, Accounting & Business Studies CA(SA), Afrikaans Home Language, Life Sciences & Geography. All with subject, level, mode fields.

**Services demo listings (7)** — Registered electrician, landscape gardener, PIRB plumber, web developer, house cleaner, chartered accountant, painter. All with service_class (Technical / Casuals) and serviceType fields.

**Seller profiles updated** — Property, Tutors and Services seller profiles (sellerIdx 0, 1, 2) upgraded from empty placeholders to full demo profiles with stats, credentials, tags, availability and seller photos.

---

## Session 22b · 19 April 2026 · Adventures multi-country demo listings + expanded country picker

**Adventures demo data** — added 10 Accommodation and 10 Experiences demo listings spanning 7 countries: South Africa (ZA), Canada (CA), United States (US), United Kingdom (GB), Europe/EU, Australia (AU), New Zealand (NZ). Each listing has correct `cat` field (`adventures_accommodation` / `adventures_experiences`), `country` code, `environment_type` for chip filtering, real Unsplash hero and gallery photos, rich operator-grade descriptions, group size, duration, and Trust Score. Adventures browse screen now filters and displays these correctly with the matching flag and currency symbol per country.

**Country picker expanded** — Adventures country sheet now lists: South Africa, Namibia, Mozambique, United States, Canada, United Kingdom, Europe, Australia, New Zealand, All countries. `ADV_COUNTRY_FLAGS` and `ADV_COUNTRY_CURRENCY` maps updated to cover all codes. Price labels now show the correct currency prefix per country (R / $ / CA$ / £ / € / A$ / NZ$).

---

## Session 22 · 19 April 2026 · Adventures screen, full category sell-side, founding seller bar removed

**Adventures browse screen** — Adventures now opens a dedicated `screen-adventures` instead of the standard browse grid. Features: dark green hero header with country switcher pill (ZA / Namibia / Mozambique / All countries), Accommodation / Experiences subcategory toggle buttons, horizontal environment filter chips (Bush & Wildlife, Mountain, Coastal, Winelands, Karoo, Forest, Farm). Listing cards show subcategory badge, country flag, environment label, and price. Empty state shown when no listings match filters. Both the home screen category tile and browse chip route to this screen.

**Sell side — all 6 categories** — Category selector (pub-b step) now shows all 6: Property, Tutors, Services, Adventures, Collectors, Cars. Adventures routes through a sub-step (pub-b2) to choose Accommodation or Experiences. Onboarding dropdown updated with all categories including both Adventures subcategories. Model picker updated to list all queue-model categories.

**AA_CATEGORIES expanded** — Adventures split into Accommodation (price/night, sleeps, amenities, environment) and Experiences (activity type, duration, group size, price/person, difficulty) service classes with separate photo slots. Cars added with full vehicle fields and 5 photo slots.

**normCat() updated** — handles `adventures_accommodation` and `adventures_experiences` from BEA.

**Founding seller progress bar removed** — removed from buyer home screen (CSS, HTML, JS function, 3 call sites). Remains in CityLauncher Ops Dashboard.

---

## Session 21 · 18 April 2026 · Photo carousel right arrow positioning fix

Fixed a visual bug in the detail/listing screen's photo carousel where the right arrow button was misaligned and unreachable. **Buyer app (`marketsquare.html`):** added `z-index:5` to `.dnav` (the top navigation bar with back button and heart/wishlist button) to ensure it sits above the carousel slide arrows; added `pointer-events:none` to `.dnav` and `pointer-events:auto` to `.dib` buttons so the overlay doesn't block arrow clicks; changed `.photo-strip-wrap` overflow from `hidden` to `visible` to allow the absolutely-positioned arrow buttons to render fully outside the container bounds. The carousel now displays both left and right arrows correctly and both are clickable.

---

## Session 20c · 17 April 2026 · Dev-phase tools — AI sessions + Tuppence seeding without payment

Added pre-launch dev tooling so the development team can test the full intro flow, AI Coach, and listing accepts without Paystack being live. **BEA (`bea_main.py`):** added `GET /tuppence/balance?email=` (public) — returns SUM of all transaction amounts for an email, enabling the buyer app to sync BEA balance; added `POST /dev/credit?email=&tuppence=N&ai_sessions=N` (API key protected) — upserts the user record crediting AI sessions and inserts a `dev_topup` transaction for Tuppence without payment; returns new balances and a warning label. **Admin app (`marketsquare_admin.html`):** added 🛠 Dev nav tab and `#view-devtools` panel with: a prominent amber warning banner, a "Seed Dev Account" card (email + T amount + AI sessions + Seed button, calls `POST /dev/credit`), a "Check Balances" card (parallel fetch of `/tuppence/balance` + `/users/{email}` to show live balances), and a purple "Before launch" instruction note listing the two things to remove. `devSeedAccount()` and `devCheckBalance()` JS functions added. **Buyer app (`marketsquare.html`):** added a silent background fetch of `/tuppence/balance` on page load — if the BEA balance is higher than the local `tuppence` variable (default 5), the BEA value is used and the UI is updated; this means seeding an email via Dev Tools is immediately reflected in the buyer app without any extra step. Cost model impact: AI Coach calls in dev phase run against the existing Anthropic billing account — no additional infrastructure cost.

---

## Session 20b · 17 April 2026 · Profile photo persistence + edit-screen fixes

Fixed two bugs found during testing. **Profile photo persistence:** photo was stored only in `localStorage` (`ms_seller_photo`) which iOS Safari clears after 7 days of inactivity. Fixed by adding `photo_url TEXT` column to the `users` table (migration), and a new `POST /users/{email}/photo` endpoint that compresses the photo to a square 400×400 JPEG, uploads to R2 (or local fallback), saves the URL to the user record, and returns the URL. `handleCVPhoto` now uploads to BEA in the background after setting the local copy; `removeCVPhoto` clears both keys. On page load, a background async task checks whether `SELLER_PHOTOS[0]` is empty and if so fetches `GET /users/{email}` to restore `photo_url` — this silently recovers the photo after any browser cache clear without slowing page load. **Edit screen navigation:** fixed `openEditListing` which was failing for two reasons — (1) the Edit button rendered `openEditListing(undefined)` for listings without a BEA id (fixed: button now only renders when `dl.beaListingId` is truthy); (2) `_raw` was null for listings that arrived via the intros path rather than `/listings/mine` (fixed: `openEditListing` is now async and calls `GET /listings/{id}` on demand to populate `_raw` before opening the form). Also fixed the BEA `PUT /listings/{id}` to accept any email for admin-created listings with `seller_email = NULL`, stamping the first editor as the owner.

---

## Session 20 · 17 April 2026 · Seller edit-after-publish + admin edit + version control

Implemented a full edit-after-publish flow across both apps, with version-archived audit trail. **BEA (`bea_main.py`):** added `listing_versions` table (id, listing_id, version_num, changed_by, changed_at, snapshot_json) and `updated_at` column to listings via `run_migrations`; added `ListingUpdate` Pydantic model (all fields optional); added six new endpoints — `GET /listings/mine?email=` (seller's own listings, no auth required), `GET /listings/{id}` (single listing), `PUT /listings/{id}?email=` (seller edits own listing — email must match `seller_email`; archives current state as a version before applying changes; goes live immediately), `GET /listings/{id}/versions` (admin API key — version metadata only), `GET /listings/{id}/versions/{version_num}` (admin API key — full snapshot JSON). Route order maintained: `GET /listings/mine` registered before parameterized `GET /listings/{id}` to prevent int-cast conflict. **Frontend (`marketsquare.html`):** added `#screen-edit-listing` — a clean manual edit form with category-aware fields (reuses `AA_CATEGORIES` definitions), pre-populated from live BEA data, with an optional "Ask AI" button (pay-per-use, costs 1 coaching session, suggestions inline under each field); updated `loadLiveDash()` to call `GET /listings/mine` and populate `dashState.listings._raw` with full listing objects so the edit form has complete data; wired the "Edit" button in `renderDashCard` to `openEditListing(beaId)`; added JS functions `openEditListing`, `renderEditForm`, `_elGetFields`, `_elFieldVal`, `_elCollectFields`, `elApplySuggestion`, `saveEditedListing`, `editAISuggest`. **Admin (`marketsquare_admin.html`):** added slide-up edit modal (full-screen overlay, sticky header/footer) with category-aware field list, AI suggestions button, and Save via `PUT /listings/{id}?email=seller_email`; added version history modal (fetches `GET /listings/{id}/versions` with API key, shows v-number, changed_by, changed_at for each version); replaced the stubbed Pause button in the Listings Manager with live ✏️ Edit and 📋 History buttons.

---

## Session 19 · 17 April 2026 · Slide deck — Trust Score System slide added (Slide 8)

Added a new Slide 8 "Trust Score System" to `MarketSquare_LaunchPlan_Updated.pptx` using direct OOXML editing of the unpacked presentation. The slide uses a dark navy (`1E2761`) LAYOUT_WIDE (13.33"×7.5") background and is divided into four zones: **Zone A** — header strip with title "Trust Score System" in white Calibri Bold 22pt, right-aligned grey subtitle, and a teal (`00C9A7`) rule; **Zone B** — left column with 4 coloured tier cards (Highly Trusted/Gold, Trusted/Teal, Established/Blue, New/Grey) each with coloured left-border accents and 3-line content (tier name, score range, benefit), plus a dark-red Penalties box; **Zone C** — three score columns (Universal Score 50pts/blue, Track Record 30pts/purple, Category Credentials 20pts/teal) with coloured header cards, alternating item rows showing right-aligned point values via tab stops, and progress bars; **Zone D** — dark (`141E40`) footer strip with 5 teal-accented rule pills covering key system rules. The slide was iterated through multiple render-and-inspect cycles using PowerPoint COM export to resolve layout issues including Zone B overflow into the footer strip.

---

## Session 18b · 16 April 2026 · n8n email outreach system — templates, workflow, opt-out

Built the full founding seller email outreach system across three deliverables. **Email templates (7 categories):** Created category-specific HTML email templates for all current and planned categories — Property, Tutors, Services Technical, Services Casuals, Adventures Experiences, Adventures Accommodation, and Collectors. Each template has a distinct colour palette, category-appropriate copy, a personalisable magic link CTA, and a one-click unsubscribe footer. All stored in `n8n/email_templates/`. **n8n workflow (`n8n/n8n_outreach_workflow.json`):** Importable workflow that triggers via webhook POST, queries the CityLauncher SQLite DB for un-emailed, un-opted-out prospects in a given city/category, renders the correct HTML template, sends via SendGrid v3 API at a rate-limited pace (200ms between sends), marks each prospect as emailed in the DB, and sends David a wave completion summary. Supports a `dry_run` flag for safe testing before live sends. **Opt-out endpoint (`bea_main.py` → `GET /opt-out`):** Added a one-click unsubscribe endpoint to the BEA. When a prospect clicks the unsubscribe link in any email, the endpoint calls the CityLauncher API `/prospects/opt-out` to set `opted_out = 1` on the prospect record, returns a clean HTML confirmation page, and gracefully logs-and-continues if CityLauncher is unreachable. **Setup guide (`n8n/N8N_EMAIL_SETUP.md`):** Full deployment guide covering SendGrid Essentials account setup, sender domain authentication, n8n credential config, Docker volume mount for template files, CityLauncher DB schema requirement, wave trigger syntax, and volume planning across all launch waves.

**Cost model impact:** SendGrid Essentials plan required at $19.95/month. This is not currently in the cost model. Recommend adding to Operating Costs sheet under Infrastructure. Volume is well within 50k/month for all planned waves combined.

---

## Session 18 · 15 April 2026 · Slide deck updated — live CityLauncher data

Updated `MarketSquare_LaunchPlan.pptx` slides 2 and 5 to reflect the real current state from the CityLauncher dashboard. **Slide 2 ("Where We Are Now"):** Replaced the single "23/60 Founding Sellers (Pretoria)" stat card with four updated cards — 693 Total Sellers Live, 5 Cities at Threshold, 11 Cities in Pipeline, and BEA v1.2.0 Live. Updated "Still To Do" list: removed the now-obsolete "60 founding sellers (Pretoria)" and "NY/LON/BER pre-scrape" items; added "Sydney, Durban, Bloemfontein nearing threshold" and "Berlin pipeline not started". **Slide 5 ("City Pipeline · Launch Status"):** Complete redesign from a 4-city placeholder view to an 11-city dashboard layout. Top section shows the 5 threshold-met cities (Pretoria 62/60, New York 60/60, London 63/60, Cape Town 65/60, Johannesburg 63/60) as green-bordered cards. Bottom section shows the 6 in-progress cities (Durban 97%, Sydney 87%, Bloemfontein 90%, East London 78%, Port Elizabeth 67%, Polokwane 23%) as horizontal progress bars with count labels. Dark navy background, teal/green accents for threshold cities, blue bars for in-progress. Berlin excluded — not yet in pipeline.

---

## Session 17d · 15 April 2026 · Cost model — tiered AI pack pricing on Assumptions + Operating Costs

Updated `Cost_Breakdown_GlobalLaunch.xlsx` to reflect the tiered AI pack pricing introduced in Session 17b. **Assumptions sheet:** (1) C65 comment updated to "T spent per adopting seller per year across all tiers"; (2) new section "TIERED AI PACK PRICING" (row 68, bold header matching existing style) added with three tier rows (rows 69–71: 5T/40 uses, 10T/100 uses, 25T/320 uses) as blue hardcoded inputs, plus formula rows for sessions-per-T for each tier (rows 72–73) and a blended sessions-per-T formula `=(B72+B73+320/B71)/3` ≈ 10.27 (row 74, cell B74). **Operating Costs sheet:** row 20 Anthropic API formulas (columns B, C, D) updated to replace the hardcoded `*8*` multiplier with `*Assumptions!$B$74*` (the blended sessions-per-T cell); E20 comment updated accordingly. Cost model impact: Anthropic API costs in Operating Costs will now auto-update whenever tier pricing assumptions change, and the blended rate (~10.27 sessions/T vs. the previous 8) slightly reduces projected API cost per T of AI pack revenue.

---

## Session 17c · 15 April 2026 · Wallet UI consistency — unified 3-row buttons, dual balance, transaction history

Three wallet screen improvements. (1) **Consistent 6-button layout** — all six purchase buttons (3 Tuppence + 3 AI Coach) now follow the same 3-row format: `#T` (top, large), `# intros` or `# AI uses` (middle, medium), `$# · R#` (bottom, small — USD as global reference with ZAR local equivalent). A `localPrice(usd)` JS helper computes ZAR at R18/$1; when live forex is added, only this function needs updating. The confirm modal also reflects the same format. (2) **Transaction history** now shows two opening rows: "Welcome bonus · Account created · Introductions → +5T" (green) and "AI coaching trial · 1 free session included → +1 Use" (indigo) — matching the two separate balance types. (3) **Dual balance widget** — the "AI Coach Credits" section is renamed "Balances" and shows two side-by-side cards: Introductions (Tuppence, navy) and AI Coach (uses left, indigo). `updateTuppenceUI()` now syncs both `tn-balance-display` and the new `tn-wallet-intros` element so the intro balance is always current in both places. Deployed.

---

## Session 17b · 15 April 2026 · AI Coach tiered pack pricing

Replaced the single "Buy AI Pack — 8 sessions · 1T" button with three tiered bundle cards matching the Tuppence top-up UI pattern. **Tiers:** 5T = 40 uses (R180), 10T = 100 uses (R360, marked "BEST VALUE"), 25T = 320 uses (R900). Standard rate is 8 uses/T; the 10T pack gives 25% more sessions and the 25T pack gives 60% more. The same tiered cards appear in the inline "no sessions remaining" prompt inside the AA flow. **Payment flow:** `aaBuyAIPack(t, sessions)` reuses the existing topup modal but passes `ai_pack_sessions` in the Paystack metadata. BEA `/payment/initialize` now accepts an optional `ai_pack_sessions` query param; `/payment/verify` reads it from metadata and — if non-zero — upserts the user record and credits the sessions to `aa_sessions_remaining` in the same transaction. `/advert-agent/buy-pack` now accepts a `sessions` parameter (default 8) for admin manual grants. Both files deployed.

---

## Session 17 · 15 April 2026 · Dave round-2 feedback — call-out fee, rate input, email registration, intro flow

Four fixes from Dave's second test round. (1) **Call-out fee field** — added optional `callout_fee` rate field (with `/visit`, `flat fee`, `POA` units and helper text) to both Services Technical and Services Casuals categories. It appears below the main Rate field and is stored in the listing description. (2) **Rate input not reflecting typed value** — two fixes: (a) changed `type="number"` to `type="text" inputmode="decimal"` with `min-width:80px` to prevent mobile rendering clipping; (b) added live `R{amount}{unit}` preview line below the rate field (same pattern as the price formatter) so the formatted result is always visible; (c) changed `.aa-rate-wrap` from `overflow:hidden` to `overflow:visible` with per-child border-radius to eliminate clipping. (3) **Email not recognised in AI Coach** — founding sellers onboarded via admin never got a `users` record. Fixed two ways: (a) `davidconradie1234@gmail.com` added to users table immediately; (b) the `aa_coach` endpoint now auto-registers any unknown email (INSERT into users with aa_free_used=0) instead of returning 404 — so any seller gets their 1 free session without needing prior admin registration. Additionally, `aa_publish` now upserts a users record on listing submission, so AA-onboarded sellers are registered going forward. (4) **Introduction flow wiring** — three BEA changes: (a) `seller_email` column added to listings table and stored by `aa_publish`; (b) accept_intro now inserts a real `intro_deduct` transaction (-1) against the buyer's email so the wallet balance is server-persisted; (c) new `N8N_WEBHOOK_NEW_INTRO` webhook fires on every new intro submission (event: `intro_submitted`) with buyer details, listing title, category, and seller_email — so David receives an immediate email alert when a buyer requests an intro. Both files deployed, BEA restarted.

---

## Session 16c · 15 April 2026 · Advert Agent — four bug fixes ahead of Maroushka + Dave re-test

Four consistency bugs identified and fixed. (1) **Rate format** — `R${amt} ${unit}` had an unwanted space before the unit string (produced "R300 /hr" instead of "R300/hr"). Fixed in both `aaSaveDetailAndNext` and `aaRunCoach` field-reading loops. (2) **`aaApplySuggestion` for compound fields** — function was calling `el.value` on div container elements for `rate` and `multiselect` field types, which silently failed. Now handles each type: multiselect ticks any chips matching the AI suggestion string (comma-split, case-insensitive); rate parses the suggestion as "R{amount}{unit}" and populates the number input and unit dropdown separately; standard inputs unchanged. (3) **`aaSelectServiceClass` suggestions drop** — switching between Technical/Casuals re-rendered the form without passing the 4th `suggestions` param to `aaRenderDetailForm`, so AI pills disappeared after a class switch. Fixed by passing `aaCurrentSuggestions` as the 4th argument. (4) **BEA publish — structured fields missing from listing description** — `/advert-agent/publish` only wrote the `desc` textarea to the database; structured fields (subjects, level, mode, rate, area, radius, service_type, experience, etc.) were discarded. Now builds a structured block prepended to the description using human-readable labels, so buyer-facing listings display meaningful content for all field types. Both `marketsquare.html` and `bea_main.py` deployed and BEA restarted.

---

## Session 16b · 15 April 2026 · Advert Agent — UX polish from Dave + Maroushka test feedback

Six UX improvements based on first real-world test: (1) **Email auto-fill** — seller email now persists to `localStorage` (key: `ms_aa_email`) on first entry and is automatically seeded into every new draft, so returning sellers never need to re-enter it. Magic-link and publish-screen email confirmations also write to localStorage. (2) **Tutors subject multi-select** — the plain text "Subjects" field is replaced with a chip-based multi-select of 21 SA curriculum subjects (Mathematics through Other) — tap to toggle, stored as comma-separated string. (3) **Structured rate field** — the free-text "Rate" field for Tutors and Services is replaced with a compound control: number input + unit dropdown. Tutors: /hr, /session, /month, once-off, POA. Services Technical: /hr, /day, /visit, once-off/fixed, POA. Services Casuals: /hr, /day, /week, /month, once-off, POA. Stored as e.g. "R300 /hr". (4) **Travel radius** — new "Travel radius" select field added to Tutors, Services Technical, and Services Casuals (5 km → City-wide / Online only). (5) **Teaching example photo not required** — changed from `required:true` to `required:false` so photo stage is never a blocker for tutors. (6) **BEA seller profile fix** — "View seller profile" for live (BEA) listings was showing SELLERS[0] (demo Property seller). Now routes to a new `openBEASellerProfile(listing)` function that builds a correct profile from the listing's own category, area, description, and trust score. `service_class` now also carried through `loadLiveListings` mapping so Technical/Casuals badge shows. **Photo upload fix** — `aaDoPublish` was checking `p.blob` (never set); now converts `p.dataUrl` (base64) to Blob before upload. `service_class` now included in FormData sent to BEA. All deployed.

---

## Session 16 · 15 April 2026 · Advert Agent — "One Form, Two Passes" UX redesign

Redesigned the Advert Agent flow from a 4-stage blocking cycle to a clean 3-stage flow (Item Details → Photos → Publish) with AI coaching embedded directly in Stage 1. **BEA changes:** The `/advert-agent/coach` endpoint now instructs Claude Haiku to return ONLY a structured JSON object (`{fields: {field_id: {suggestion, reason}}, trust_score_actions: [{action, points, doc}], anonymity_warning}`), instead of free-form prose. Response is JSON-parsed with a regex fallback for markdown-wrapped output; missing keys are defaulted. Returns `coaching_json` instead of `coaching`. **Frontend changes (marketsquare.html):** (1) Stage pills updated: "Stage 1–2 of 4" → "1–2 of 3"; Stage 4 (Publish) becomes Stage 3 of 3. (2) New `aaRenderAIPanel(draft)` renders email entry, session balance badge, "✨ Get AI Suggestions" button, anonymity warning, and numbered Trust Score Action Plan — all inside Stage 1 below the form fields. (3) `aaFieldsHtml()` now accepts a third `suggestions` param; when suggestions exist, a `💡` pill with an "✓ Apply" button appears under each relevant field. Clicking Apply pastes the AI's ready-to-use text directly into the input. (4) `aaRunCoach()` rewritten: saves current form state first, calls BEA, stores `coachSuggestions` JSON on draft, re-renders Stage 1 in-place with inline pills — never navigates away. (5) `aaSavePhotosAndNext()` now advances to Publish (not Coach). (6) `aaOpenDraft` / `aaOpenDraftAt` simplified to 3 stages; old stage-3/4 coach references removed. (7) Publish screen shows Trust Score action plan from `coachSuggestions` (styled numbered list) instead of raw `coachOutput` textarea. (8) `aaDoPublish` sends a compact text summary of Trust Score actions as `coach_output`. Legacy `screen-aa-coach` HTML kept in place but is unreachable from the main flow. All three files deployed to Hetzner.

---

## Session 15 · 15 April 2026 · Cost model update — AI Coach + Trust Score acceptance uplift

Updated `Cost_Breakdown_GlobalLaunch.xlsx` to reflect the Advert Agent (AI Coach) subscription revenue stream and its associated Anthropic API costs, and to capture the Trust Score-driven improvement in intro acceptance rate. Changes: (1) **Assumptions sheet** — intro acceptance rate raised from 0.60 to 0.65 (Trust Score uplift, +8.3% Tuppence revenue); three new AI Coach assumption rows added: adoption rate = 15% of active sellers, avg packs per seller = 2/yr, Anthropic Haiku 4.5 cost per session = $0.01. (2) **Operating Costs sheet** — new "Anthropic API — AI Coach (Haiku 4.5)" line in the Development section, formula-linked to Wave Growth seller count × adoption × packs × 8 sessions × cost/session; Development subtotal updated to include it. (3) **Revenue vs Cost sheet** — new "AI Coach pack revenue" line added (sellers × adoption × packs × $2 per pack), correctly ordered before TOTAL REVENUE; TOTAL REVENUE and all downstream formulas (Net Income, Operating Margin, Revenue per seller, Avg monthly revenue) updated to reference the new row. Net Y1 impact: +~$14,233 (+6.8%). File recalculates automatically on next Excel open.

Cost model impact: Intro acceptance rate raised to 65% (was 60%) increases Tuppence revenue by ~8.3% across all years. AI Coach pack revenue adds ~$6,268 Y1 / ~$15,670 Y2 / ~$31,340 Y3. Anthropic API costs ~$251 Y1 / ~$628 Y2 / ~$1,256 Y3. Net margin impact is strongly positive: platform earns $2 per pack, spends $0.16 per pack in API costs.

---

## Session 14b · 15 April 2026 · Advert Agent — Trust Score maximisation as primary mission

Restructured the Advert Agent system prompt so that Trust Score maximisation is the explicit primary coaching mission, not a passive appendix. The AI is now instructed to: (1) scan every field the seller fills in for mentions of qualifications, registrations, certifications, experience years, memberships, star ratings, and tickets — each one is a credential they likely hold and can submit; (2) name each spotted credential specifically with the exact points it unlocks and the document needed to claim it; (3) list additional credentials they may hold but haven't mentioned; (4) calculate the approximate maximum score they appear entitled to vs. their current score and show the gap; (5) end every session with a numbered "YOUR TRUST SCORE ACTION PLAN" section, highest-value action first. DB query expanded to also fetch `trust_score` so the AI knows the seller's current tier at the start of every session. User message updated to pass current score and tier, and to explicitly ask for both listing improvements and a personalised Trust Score action plan. `max_tokens` raised from 1024 to 1800 to give the AI room for both sections. Deployed to Hetzner.

---

## Session 14 · 15 April 2026 · Trust Score criteria framework

Designed and documented the full category-specific Trust Score criteria system. Created `TRUST_SCORE_CRITERIA.md` (v1.0) as the authoritative design spec — covers all six categories (Property, Tutors, Services Technical, Services Casuals, Adventures Experiences, Adventures Accommodation, Collectors) with signal weights, verification methods, and a penalty/anti-manipulation framework. Adventures category formally split into two sub-classes: Experiences (guided activities) and Accommodation (B&B/guesthouses/boutique hotels), with TGCSA star grading as the highest-weight Accommodation signal (1-star = 6 pts up to 5-star = 22 pts). Complaint penalties use a diminishing scale (−8/−5/−3/−2/−1) capped at −22 total, with escalation triggers at 3+ complaints in 90 days and immediate review for safety concerns. Anti-manipulation rules lock all credential signals behind manual document review, verify registration numbers against public registers (PPRA, SACE, TGCSA, ECSA, PIRB, etc.), and keep score server-side only. Created `TRUST_SCORE_CODEX_AMENDMENT.md` with ready-to-paste content for Codex v4.5. Created `onboarding/ONBOARDING_CHECKLIST.md` — manual per-category credential checklist with scoring paths and verification steps for each category. Updated `bea_main.py` Advert Agent system prompt to include category-specific Trust Score guidance, so the AI coach actively advises sellers on which credentials to upload and the pts each unlocks. Updated `AGENT_BRIEFING.md` (MarketSquare) with Adventures sub-class definitions and expanded Trust Score summary. Updated `AdvertAgent/AGENT_BRIEFING.md` Category Intelligence table to split Adventures into two rows (Experiences / Accommodation) with appropriate Stage 1 fields and photo checklists.

**David action required:** Upload `Solar_Council_Codex_v4_4.docx` to Claude Chat, apply `TRUST_SCORE_CODEX_AMENDMENT.md` content, increment to v4.5, and replace the local .docx. Then update version references in CLAUDE.md, STATUS.md, both AGENT_BRIEFINGs, and PRINCIPLE_REQUIREMENTS.md.

---

## Session 13 · 15 April 2026 · Gate 0 — platform stabilisation

Fixed a JS syntax error (unescaped apostrophe in AA_FLOWS Collectors entry) that broke the live site immediately after Session 12 deploy. Set ANTHROPIC_API_KEY in /etc/environment on Hetzner and restarted the marketsquare service — AI Coach is now live but pending Anthropic billing activation (support ticket raised). Fixed the magic onboarding link: the `magic-banner-area` div was missing from the onboard screen HTML, and `renderMagicBanner()` was never called from `goTo()` — both fixed, banner now shows and fields pre-fill correctly from URL params. Added `aaClearEmail()` function to the AI Coach screen so sellers can correct a wrong email without restarting. Improved coach error handling: 503 (not configured), 404 (email not registered), and 402 (no sessions) now each show a specific toast instead of the generic "unavailable" message. Admin tool fixes: category selection now auto-advances to Step 3 without a separate Continue click; all listing form placeholders (Title, Price, Area, Headline, Tagline, Summary) update dynamically per category (Property/Tutors/Services); `autocomplete="off"` added to all listing form fields to prevent browser suggesting old values; listing queue and form state reset when category changes; magic link box moved to always visible on Step 4 arrival (generated in `buildReviewScreen`) rather than hidden inside the post-publish result div. All files deployed.

---

## Session 12 · 14 April 2026 · Phase 1 category alignment — canonical register

Locked the canonical category register (Property · Tutors · Services · Adventures · Collectors) across all platform files. Services was split into two sub-classes — Technical (licensed/accredited trades: Electrical, Plumbing, HVAC, Solar, IT, Legal, Financial, Landscaping) and Casuals (domestic/informal: Domestic, Gardening, Dog Walking, Child Minding, Temp, General Labour) — with a single "Services" browse tile and an internal `service_class` filter. Help Wanted absorbed into Casuals. Automotive deferred (no phase). Adventures (formerly Travel & Experiences) and Collectors (merges MTG/Collectibles + Philately) confirmed as Phase 2. The `service_class` TEXT column was added to the `listings` table via idempotent `run_migrations()`. The `Listing` model and both insert paths (POST /listings and /advert-agent/publish) were updated to write `service_class`. The AdvertAgent AA_CATEGORIES object was rebuilt with the 5-category canonical register: Real Estate renamed to Property, Tutors added, Services given a `serviceClasses` sub-structure (Technical/Casuals each with their own field sets and photo checklists), Adventures and Collectors added as Phase 2. A `aaCatConfig(draft)` helper function routes field/photo config through `service_class` for Services drafts. The AA Stage 1 form now shows a class chip selector (Technical/Casuals) before rendering the Services form. The admin tool's Help Wanted category tile was removed; Services now shows a Class dropdown (Technical/Casuals) and a combined service type optgroup list. The buyer app filter sheet for Services gained a "Class" chip section (Any / Technical / Casuals) at the top. The `filterState.services.serviceClass` property was added, wired into `applyFilters`, `clearFilters`, and `renderActiveFilterTags`. Card badges show 🔧 Technical or 🤝 Casuals sub-badge where `service_class` is set. PRINCIPLE_REQUIREMENTS.md D7 updated to the locked 5-category register. AGENT_BRIEFING.md updated in both MarketSquare and AdvertAgent projects. CityLauncher gumtree.py updated to output `service_class` and normalise Casuals→Services category. `migrate_db_v2.py` extended with Part 4 to add `service_class` to `prospects` and `prospects_raw` tables. All three files deployed.

---

## Cross-project update · 12 April 2026 · PRINCIPLE_REQUIREMENTS v1.1

PRINCIPLE_REQUIREMENTS.md v1.1 — Rule B7 added: no consumption-based external API without David's explicit approval and cost ceiling. Triggered by Google Cloud API incident (R3,612 charged without approval). Updated in all 3 project folders: MarketSquare, CityLauncher, AdvertAgent. Dated 12 April 2026.

---

## Cross-project update · 11 April 2026 · Cowork framework + AdvertAgent scaffold

Updated `CLAUDE.md` Codex reference from v4_3 to v4_4. `AGENT_BRIEFING.md` was already at v1.3 (11 April 2026) with correct Codex reference. AdvertAgent project scaffolded at `C:\Users\David\Projects\AdvertAgent\` — governed by PRINCIPLE_REQUIREMENTS.md Part G (G1–G4), with its own AGENT_BRIEFING.md (v0.1 pre-kickoff), STATUS.md, CHANGELOG.md, and CLAUDE.md. PRINCIPLE_REQUIREMENTS.md v1.0 copied to both CityLauncher and AdvertAgent project roots. Architecture, subscription pricing, and UI integration point for AdvertAgent deferred to kickoff session.

---

## Cross-project update · 10 April 2026 (CityLauncher Session 9)

### Photo storage migrated to Cloudflare R2, admin app UX fixes

Photo storage moved from degraded Hetzner Object Storage (NBG1, down since 5 March 2026) to Cloudflare R2 EU jurisdiction. Bucket: `marketsquare-media`. Public URL: `pub-3c51d058a6494b93af4d242d07bdc4da.r2.dev`. Server env vars updated (`HETZNER_S3_*` reused — S3-compatible, no code changes). `_s3_upload()` in `main.py` updated to return R2 public dev URL. Three admin app fixes: (1) property feature checkboxes now clickable — excluded checkboxes from `-webkit-appearance: none`; (2) multiple photo upload race condition fixed — slots reserved synchronously; (3) removed extra click — direct onclick handler + drag-drop + clipboard paste support. Native `<select>` dropdowns restored on mobile with `appearance: menulist`.

Cost model impact: Photo storage $0 (10 GB free, zero egress). Replaces Hetzner Object Storage which was unreliable and charged per-GB egress.

---

## Session 10 · 5 April 2026 · 4-level location hierarchy — buyer app + admin tool

Replaced the flat city/suburb selectors in both frontends with a full Country → Region → City → Suburb drill-down. Buyer app: activeCity is now an object {id, name} (resolved to Pretoria's DB id on startup via _resolveActiveCity()); activeSuburb is {id, name} or null; activeCountry and activeRegion track the full hierarchy. updateBadgeLabel() shows all four levels. The location selector sheet now has four panels (country, region, city, suburb) driven by /geo/* API calls. Tier gating: free opens suburb panel directly; starter opens city panel; premium opens country panel. loadLiveListings() and renderGrid/renderCatCounts updated to use .name properties. Admin tool: static city dropdown replaced with cascading Province → City selects populated from /geo/regions?country=ZA and /geo/cities?region_id=. goNext() step 1 now stores geo_city_id on sellerData. loadSuburbsForForm() switched to /geo/suburbs?city_id= returning {id, name} objects.

---

## Session 10 · 5 April 2026 · Geographic hierarchy — BEA database restructure

Replaced the flat suburbs table with a proper 4-level relational schema: geo_countries, geo_regions, geo_cities, geo_suburbs. South Africa seeded on first startup from the GeoNames ZA data dump (downloaded to /tmp, parsed, deleted). Provinces, cities and suburbs linked relationally via admin1+admin2 codes. New /geo/* endpoints serve the full hierarchy. Old /suburbs and /cities endpoints preserved as compatibility shims. New POST /geo/countries endpoint triggers background GeoNames API seed for any new country. GEONAMES_USERNAME=dmcontiki2 added to /etc/environment. Existing listings migrated to geo_city_id where city name matches exactly.

---

## Session 10 · 5 April 2026 · buyer_name field in buyer app

Added buyer_name input to the intro request form in marketsquare.html. Field appears above the email input, styled consistently. The POST /intros fetch payload now includes buyer_name (null if left blank — field is optional). Intro sheet reset now clears the name field alongside email and message. BEA stores and forwards the value through n8n webhook payloads on accept/decline.

---

## Session 10 · 5 April 2026 · buyer_name fix (BEA)

Added buyer_name field to the intro_requests table and throughout the intro submission flow. run_migrations() now detects and adds the column on startup (idempotent). IntroRequest Pydantic model accepts buyer_name as an optional field. POST /intros stores it. Both n8n webhook payloads (accept and decline) now read buyer_name from the DB row instead of sending null. No frontend changes required — the field is optional so existing intro submissions without it continue to work.

---

## Session 1 · 28 March 2026 · Morning

### What was built
- Claude Code 2.1.84 installed via winget on Windows 11
- Project folder created: C:\Users\David\Projects\MarketSquare
- Master CLAUDE.md created with 5 operating principles
- Three agent folders created: agents/architect/ · agents/frontend/ · agents/admin/
- Each agent folder has its own CLAUDE.md defining its lane
- Git initialised, identity configured, first commit made
- Core files renamed (removed Windows duplicate suffix) and committed:
  - marketsquare_v8_6b.html
  - marketsquare_admin_v1_1.html
  - Solar_Council_Codex_v4_0.docx
- 360 Total Security whitelisted: Claude Code · Git · MarketSquare folder

### Operating principles locked
1. When unsure — make best guess, implement, flag uncertainty at end
2. Change size — one feature or bug fix per task, one file section at a time
3. Git — auto-commit after every completed task with descriptive message
4. Definition of done — working code + one-paragraph entry appended to CHANGELOG.md
5. Conflict arbitration — Architect agent arbitrates via Codex; escalate to David only if Codex cannot resolve

### Agent structure
- Architect agent · agents/architect/CLAUDE.md · owns Codex rules and system design
- Frontend agent · agents/frontend/CLAUDE.md · owns marketsquare_v8_6b.html
- Admin agent · agents/admin/CLAUDE.md · owns marketsquare_admin_v1_1.html

### Decisions made
- BEA and CityAutoRollOut agents deferred — add when those concepts have their own dedicated files
- GitHub setup deferred to Session 2
- Startup script deferred to Session 2

### Open items for Session 2
1. Build master briefing document for the 3 Claude Code agents
2. Set up GitHub for project backup
3. Build and test start_marketsquare.bat desktop startup script
4. Correct Codex — Solis is a ChatGPT/OpenAI persona, not a Grok agent
5. Correct Codex — 1 Tuppence = USD $2 (not $1)
6. Update agent CLAUDE.md files to reflect MarketSquare is a marketplace app, not a game

### Notes
- MarketSquare is a local marketplace app (not a game)
- Three agents are Claude Code agents, not ChatGPT/Grok/Claude mix
- Solis is a David persona used in ChatGPT — external to Claude Code setup
- 1 Tuppence = USD $2
- Pro plan in use — no additional costs beyond subscription

---

## Session 2 · 28 March 2026 · Afternoon

### What was built
- start_marketsquare.bat created — desktop startup script
  - Copies last CHANGELOG entry to clipboard
  - Opens claude.ai/new in browser
  - Opens trustsquare.co and trustsquare.co/admin.html
  - Launches Claude Code in Windows Terminal at project folder
- CHANGELOG.md created (this file)

### Open items continuing
1. Build master briefing document for the 3 Claude Code agents
2. Set up GitHub for project backup
3. Test start_marketsquare.bat end-to-end

---

## Session 2 · 28 March 2026 · Afternoon (continued)

### What was built
- AGENT_BRIEFING.md completed — master briefing document for all three Claude Code agents.
  Single source of truth covering: product overview, core concepts, file map, agent lanes,
  BEA API reference, infrastructure, operating rules, and pending items.
- GitHub repository set up at https://github.com/dmcontiki2/marketsquare
  - Account created: dmcontiki2 (dmcontiki2@gmail.com)
  - Empty repo created: marketsquare
  - All project files pushed to main branch with tracking set up

### All Session 2 open items resolved
1. ✅ Master briefing document — AGENT_BRIEFING.md
2. ✅ GitHub backup — github.com/dmcontiki2/marketsquare
3. 🔜 Test start_marketsquare.bat end-to-end — deferred to Session 3

### Notes
- From Session 3 onward, agents should read AGENT_BRIEFING.md at session start
- Future commits will be backed up to GitHub automatically via Claude Code auto-commit rule
- CLAUDE.md still describes MarketSquare as a game — update is pending (Session 2 open item 8)

---

## Session 3 · 30 March 2026 · Morning

### What was built

**Claude Code settings.json updated** — four settings configured:
- conversationRetentionDays: 365
- CLAUDE_CODE_MAX_OUTPUT_TOKENS: 150000
- CLAUDE_AUTOCOMPACT_PCT_OVERRIDE: 75
- CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS: 1

**Three critical bugs fixed in marketsquare_v8_6b.html:**
1. Category mismatch — BEA listings showing in wrong category. Fixed by adding normCat() function in loadLiveListings() to normalise BEA category strings (e.g. 'property', 'PROPERTY') to exact CATS keys ('Property', 'Tutors', 'Services').
2. Adverts not clickable — openDetail(id) was using LISTINGS[id] as an array index, which fails for BEA string ids like 'bea_3'. Fixed by adding findListing(id) helper that searches by value. Also fixed all onclick handlers that interpolated l.id without quotes, causing browser to treat 'bea_3' as an undefined variable.
3. Magic claim links broken — admin tool generated correct URLs but frontend had no code to read the URL params. Fixed by adding URLSearchParams parser on DOMContentLoaded that reads magic=1, name, email, cat, city params and routes straight to the onboard screen with fields pre-filled.

**Hardcoded demo data removed from marketsquare_v8_6b.html:**
- 6 hardcoded listings replaced with 3 placeholder cards (one per category) — dashed border, faded, non-clickable, labelled 'Awaiting first [category] seller'
- 6 hardcoded seller CVs replaced with 3 minimal placeholder sellers
- Hardcoded dashState listings replaced with empty array — populated by loadLiveDash() from BEA
- renderGrid() updated to show placeholders despite paused:true flag
- renderFeatured() updated with empty state message when no featured listings exist
- Results count excludes placeholders

**Server deployment issues resolved:**
- Identified correct nginx serve path: /var/www/marketsquare/ (not /var/www/html/)
- admin.html was missing from server — uploaded via SCP from local Windows terminal
- nginx config updated to add location = /admin.html block so it doesn't fall through to FastAPI
- Correct SCP commands for future deployments documented below

**360 Total Security false positive resolved:**
- atiuxp64.dll (AMD GPU driver) flagged on every startup — confirmed false positive
- Fix: exclude entire C:\Windows\System32\DriverStore\FileRepository folder in 360 settings

### Deployment commands (save these)
```
# Deploy buyer app
scp C:\Users\David\Projects\MarketSquare\marketsquare_v8_6b.html root@178.104.73.239:/var/www/marketsquare/index.html

# Deploy admin tool
scp C:\Users\David\Projects\MarketSquare\marketsquare_admin_v1_1.html root@178.104.73.239:/var/www/marketsquare/admin.html
```

### Status at end of session
- trustsquare.co — live, Maroushka's property listings loading from BEA, fully clickable ✅
- trustsquare.co/admin.html — live, admin onboarding tool accessible ✅
- Magic claim links — working end-to-end ✅
- Placeholder cards — visible in browse grid, one per category ✅
- Email to Maroushka and David — drafted, ready to send ✅

### Open items for Session 4
1. Send email to Maroushka and David to start adding property listings
2. Maroushka to add real property listings via admin tool
3. n8n email notifications — buyer emailed on intro accept/decline
4. Hetzner Object Storage — migrate photos off local /media
5. Update start_marketsquare.bat with correct SCP deploy commands
6. Correct Codex — Solis is a ChatGPT/OpenAI persona, not Grok
7. Correct Codex — 1 Tuppence = USD $2 (currently blank in table)
8. Update agent CLAUDE.md files to reflect marketplace, not game
9. Paystack live mode — pending CIPC registration

---

## Session 4 · 31 March 2026

### What was built
- `marketsquare_admin.html` upgraded from v1.0 (4-step wizard only) to v2.0 (full dashboard). The existing 4-step onboarding wizard is unchanged and now lives under the **Onboard** tab. Five new sections added via a fixed bottom nav bar: **My Listings** (fetch all BEA listings, filter by category, delete); **Seller Profile** (look up by email via `GET /users/{email}`, delete account); **Analytics** (live pending intro count + live listing count from BEA, with Coming Soon placeholders for BEA v1.2 metrics); **Account & Billing** (placeholder pending Paystack live mode); **Alerts** (load all pending intros from `GET /intros`, show 48hr countdown with colour coding, Accept/Decline buttons wired to BEA).

### Status at end of session
- marketsquare_admin.html (local) — v2.0 dashboard built ✅
- Needs SCP deploy to server to go live at trustsquare.co/admin.html

### Open items carried forward
1. Deploy marketsquare_admin.html to server (SCP command in AGENT_BRIEFING)
2. Maroushka real listings — add via admin tool
3. n8n email notifications — buyer emailed on intro accept/decline
4. Hetzner Object Storage — migrate photos off local /media
5. Update start_marketsquare.bat with correct SCP deploy commands
6–8. Codex corrections and agent CLAUDE.md updates (Architect agent)
9. Paystack live mode — pending CIPC registration

## Session 5 · 31 March 2026

### Completed in this session

**Planning and architecture (claude.ai):**
- Session 4 briefing completed — open items 1, 6, 7 confirmed done
- Admin dashboard spec defined: 5 panels (Profile, Listings, 
  Analytics, Billing, Alerts) with full field and metric breakdown
- Property filter gap analysis completed — buyer app filter sheet 
  missing 9 property types, Listing Type, Furnished, Pet Friendly, 
  Internet, 10 features vs admin tool
- Auto-research session protocol designed — OIM framework documented
  for future sessions
- Token management strategy confirmed — Claude Code preferred over
  claude.ai for all file editing tasks

**Deployment:**
- Both files deployed to server via PowerShell SCP:
  - marketsquare.html → /var/www/marketsquare/index.html
  - marketsquare_admin.html → /var/www/marketsquare/admin.html
- Correct local filenames confirmed: marketsquare.html and 
  marketsquare_admin.html (no version suffix on disk)
- AGENT_BRIEFING, CHANGELOG, CLAUDE, settings files still have 
  Windows duplicate suffixes — rename in Claude Code Session 5

### Open items for Session 6
1. Fix buyer app property filter sheet to match admin tool fields
2. Build seller self-service dashboard in admin tool (5 panels)
3. Maroushka real listings — add via admin tool
4. n8n email notifications — buyer emailed on intro accept/decline
5. Hetzner Object Storage — migrate photos from local /media
6. Update start_marketsquare.bat with correct SCP deploy commands
7. Rename project files — remove Windows duplicate suffixes
8. Paystack live mode — pending CIPC registration

## Session 6 · 1 April 2026

### Completed in this session

**Planning and architecture (claude.ai):**
- Maroushka test review analysed — 4 bugs identified and task
  instructions written for Claude Code
- Security warning on start_marketsquare.bat diagnosed — Windows
  SmartScreen false positive, not 360 antivirus; fix is to unblock
  the file via Properties
- Codex v4.2 produced — new §6 Buyer Subscription Tiers & Cost Model
  added covering tier definitions, fixed infrastructure costs,
  breakeven scenarios, and server capacity notes

**Five Claude Code tasks worded and ready for execution:**

- Task 1 · Currency formatting — standardise all monetary values to
  R1,234,456.00 format throughout both apps using a shared formatZAR()
  helper function
- Task 2 (revised) · Structured description — replace free-text
  description field in admin tool with structured editor (headline,
  tagline, summary, repeatable sections + bullets); serialise as JSON
  into existing BEA description field; buyer app renderer detects JSON
  and renders as formatted HTML, falls back to plain text for legacy
  listings
- Task 3 · Photo carousel — listing detail screen becomes a
  horizontally swipeable carousel with arrow buttons, dot indicators,
  and touch/swipe support; uses medium_url array from BEA listing
- Task 4 · Category listing counts (city-scoped) — counts derived
  dynamically from live listings filtered to active city only;
  excludes ph_ placeholders; re-renders after loadLiveListings()
  completes
- Task 5 · City selector tier-gated — Free tier locked to local city
  (non-interactive); Starter ($5/mo) opens country-scoped city
  dropdown; Premium ($15/mo) opens global city dropdown; stats strip
  updates to match selected city; BEA /cities endpoint flagged as
  pending

**Buyer subscription tier model defined (preliminary):**

| Tier     | Price   | Sessions/day | City scope                  |
|----------|---------|-------------|------------------------------|
| Free     | $0      | 3 (hard)    | Local city only              |
| Starter  | $5/mo   | 20          | All cities in same country   |
| Premium  | $15/mo  | 50          | All cities globally          |

Note: prices and session limits are preliminary pending Paystack
go-live and final product decision.

**Infrastructure cost model established:**
- Fixed costs: ~$10/month (Hetzner CPX22 + domain)
- Breakeven: 2 Starter subscribers covers all infra costs
- CPX22 can comfortably serve ~16,000 free-only users before upgrade
- Next tier: Hetzner CPX32 at ~$17/month
- AI agent app token costs are a separate model — not applicable to
  MarketSquare itself

### Open items for Session 7
1. Execute Task 1 — currency formatting (Claude Code)
2. Execute Task 2 — structured description editor + renderer (Claude Code)
3. Execute Task 3 — photo carousel (Claude Code)
4. Execute Task 4 — category listing counts city-scoped (Claude Code)
5. Execute Task 5 — city selector tier-gated (Claude Code)
6. Deploy all changes to server after testing
7. Maroushka real listings — re-enter via admin tool using new
   structured description editor once Task 2 is done
8. n8n email notifications — buyer emailed on intro accept/decline
9. Hetzner Object Storage — migrate photos from local /media
10. Update start_marketsquare.bat — correct SCP deploy commands
11. Paystack live mode — pending CIPC registration
12. Rename project files — remove Windows duplicate suffixes

---

## Session 7 · 1 April 2026 (continued)

### Completed in this session

Tasks 1–5 confirmed complete via git history. The SESSION_7_START_PROMPT.md process was validated — agent correctly identified outstanding work and confirmed completed tasks instantly. Start prompt format confirmed solid for future sessions.

- **Task 1 · Currency formatting** — formatZAR() helper implemented across both marketsquare.html and marketsquare_admin.html. All monetary values display as R1,234,456.00.
- **Task 2 · Structured description** — admin tool listing form replaced with structured editor (headline, tagline, summary, sections + bullets), serialised as JSON. Buyer app renderer detects JSON and renders as formatted HTML, falls back to plain text for legacy listings.
- **Task 3 · Photo carousel** — listing detail screen updated with swipeable carousel, arrow buttons, dot indicators, and touch/swipe support. Uses medium_url array from BEA listing object.
- **Task 4 · Category listing counts** — counts now derived dynamically from live listings, filtered to active city and suburb scope, excluding ph_ placeholders. Re-renders after loadLiveListings() completes.
- **Task 5 · City selector tier-gated** — Free locked to local city, Starter opens country-scoped selector, Premium opens global selector. Tier state defaults to Free pending Paystack go-live.

### Open items for next session
1. Deploy all Task 6 changes to server (both HTML files + bea_main.py)
2. Maroushka real listings — re-enter via admin tool using structured description editor
3. n8n email notifications — buyer emailed on intro accept/decline
4. Hetzner Object Storage — migrate photos from local /media
5. Update start_marketsquare.bat with correct SCP deploy commands
6. Paystack live mode — pending CIPC registration

---

## Session 7 · 1 April 2026 · Task 6 Part A — BEA suburbs & cities

Added three-level location hierarchy support to the BEA (main.py). Migration runs on startup: creates `suburbs` table (id, name, city, country, active, created_at) with index on city+active, adds `suburb TEXT` column to listings, and defaults existing rows to "Central". Seed function loads suburbs_seed.json (31 Pretoria suburbs) on first start, skipping subsequent runs. `GET /listings` now accepts optional `&suburb=` filter. `POST /listings` now requires `suburb` field (400 if missing), and inserts it. New endpoints: `GET /suburbs?city=` returns sorted active suburb names; `GET /cities?country=` returns city list for that country; `GET /cities` returns all cities grouped by country; `POST /cities` (auth required) creates a city placeholder and triggers a background GeoNames fetch to seed its suburbs (requires GEONAMES_USERNAME in .env). `httpx` added as import for async GeoNames calls.

**Deploy:** `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py` then `scp suburbs_seed.json root@178.104.73.239:/var/www/marketsquare/suburbs_seed.json` then `systemctl restart marketsquare.service`.

## Session 7 · 1 April 2026 · Task 6 Part C — Buyer app three-level location selector

Replaced the single-city badge with a Country → City → Suburb drill-down. Added `activeSuburb` (null = All suburbs) and `availableSuburbs` state variables. Added `updateBadgeLabel()` which sets the badge to `{city} · All suburbs` or `{city} · {suburb}`. The location bottom sheet now has two panels: city panel and suburb panel. `openLocPanel('city'|'suburb')` switches between them. Selecting a city drills directly into the suburb panel. `selectSuburb()` sets `activeSuburb`, updates the badge, and re-calls `loadLiveListings()`. `loadLiveListings()` now appends `&suburb=` to the BEA query when a suburb is active. Tier gating: Free opens suburb panel directly (city locked); Starter opens city panel filtered to ZA; Premium opens city panel globally. `renderCatCounts()` and `renderGrid()` both respect `activeSuburb`. Startup sequence: `loadCities → loadSuburbsForSelector → loadLiveListings`.

## Session 7 · 1 April 2026 · Task 6 Part B — Admin tool suburb dropdown + City Management tab

Added suburb selection to the listing form in Step 3 of the admin onboarding wizard. When the form opens, `loadSuburbsForForm()` fetches `GET /suburbs?city={sellerData.city}` and populates a dropdown. Suburb is required — `saveListingToQueue()` blocks submission if unset. The suburb value is stored in `formData.suburb` and included in the BEA publish payload. The old free-text "Area / Suburb" field is now labelled "Area" (still optional/freeform). Added a City Management tab (nav icon 🌍) with a cities table (city, country, suburb count) loaded from `GET /cities`, and an "Add city" form that POSTs to `POST /cities` and shows a "fetching suburbs in background" status. `goView('cities')` auto-loads the table on tab open.

---

## Session 8 · 2 April 2026 · Task 2 — n8n email notifications (BEA)

Added fire-and-forget webhook calls to `PUT /intros/{id}/accept` and `PUT /intros/{id}/decline`. Two new env vars — `N8N_WEBHOOK_ACCEPT` and `N8N_WEBHOOK_DECLINE` — are read at startup via `os.getenv()`; if either is missing the BEA logs one warning and continues without sending that email. Both endpoints now accept `BackgroundTasks` and schedule an async `_fire_webhook()` call after the DB update completes. The webhook uses `httpx.AsyncClient` with a 5-second timeout; any failure is logged and the API response is unaffected. Webhook payloads include event type, intro/listing IDs, listing title, buyer email, city, and UTC timestamp. `buyer_name` and `seller_display_name` are sent as `null` — these fields are not yet stored in the current schema (noted as a future addition). No frontend changes required. **n8n setup is a one-time manual step — see deploy notes below.**

**n8n server setup (one-time manual steps on Hetzner):**
1. `npm install -g n8n`
2. Create `/etc/systemd/system/n8n.service`:
   ```
   [Unit]
   Description=n8n workflow automation
   After=network.target
   [Service]
   Type=simple
   User=root
   ExecStart=/usr/bin/n8n start
   Restart=on-failure
   Environment=N8N_PORT=5678
   Environment=N8N_PROTOCOL=http
   Environment=N8N_HOST=localhost
   Environment=WEBHOOK_URL=http://localhost:5678
   [Install]
   WantedBy=multi-user.target
   ```
   Then: `systemctl enable n8n && systemctl start n8n`
3. n8n runs on `localhost:5678` only — do NOT expose publicly; do not add nginx proxy.
4. Access via SSH tunnel: `ssh -L 5678:localhost:5678 root@178.104.73.239` then open `http://localhost:5678`
5. Create two workflows in n8n UI: Webhook trigger → Send Email (accepted), Webhook trigger → Send Email (declined). Configure SMTP credentials (Brevo / Mailgun / Resend — free tier sufficient).
6. Add to `/var/www/marketsquare/.env`:
   ```
   N8N_WEBHOOK_ACCEPT=http://localhost:5678/webhook/<your-accept-uuid>
   N8N_WEBHOOK_DECLINE=http://localhost:5678/webhook/<your-decline-uuid>
   ```

**Deploy:** `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py` then `systemctl restart marketsquare.service`

**Session 8 deploy notes (actual):**
- Env vars live in `/etc/environment` (not `.env`) — systemd drop-in points there
- n8n installed via Docker (npm global install failed on isolated-vm native build)
- n8n Docker command: `docker run -d --name n8n --restart unless-stopped -p 127.0.0.1:5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n`
- Access n8n UI via SSH tunnel: `ssh -L 5678:localhost:5678 root@178.104.73.239`
- N8N_WEBHOOK_ACCEPT and N8N_WEBHOOK_DECLINE confirmed live ✅
- HETZNER_S3_ACCESS_KEY and HETZNER_S3_SECRET_KEY still to be added via `nano /etc/environment` ⚠️

---

## Session 8 · 2 April 2026 · Task 3 — Hetzner Object Storage photo migration (BEA)

Added S3-compatible photo storage to the BEA with graceful local-disk fallback. Four new env vars — `HETZNER_S3_ENDPOINT`, `HETZNER_S3_BUCKET`, `HETZNER_S3_ACCESS_KEY`, `HETZNER_S3_SECRET_KEY` — are read at startup. If any are missing the BEA logs one warning and continues using local `/media` (existing behaviour unchanged). When all four are set, `boto3` client is initialised at startup and `POST /listings/photo` uploads the compressed medium JPEG to S3 (key pattern: `media/{uuid}_{filename}`), sets `ACL=public-read`, and returns the S3 public URL as both `thumb_url` and `medium_url` (Hetzner does not auto-generate thumbnails — same URL for now). New admin endpoint `POST /admin/migrate-photos` (API-key auth) scans all listings with local `/media/` paths, uploads each file (thumb + medium separately) to S3, and updates the DB rows in place. Returns `{"migrated": N, "failed": M, "skipped": K}`. Idempotent — skips rows already pointing to an S3 URL. Never deletes local files. `boto3` added to `requirements.txt`.

**Deploy:**
1. Add to `/var/www/marketsquare/.env`:
   ```
   HETZNER_S3_ENDPOINT=https://<your-region>.your-objectstorage.com
   HETZNER_S3_BUCKET=<your-bucket-name>
   HETZNER_S3_ACCESS_KEY=<your-access-key>
   HETZNER_S3_SECRET_KEY=<your-secret-key>
   ```
2. `/var/www/marketsquare/venv/bin/pip install -r requirements.txt` (installs `boto3` — use venv pip, not system pip)
3. `scp requirements.txt root@178.104.73.239:/var/www/marketsquare/requirements.txt`
4. `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py`
5. `systemctl restart marketsquare.service`
6. Once running: `curl -X POST https://trustsquare.co/admin/migrate-photos -H "X-Api-Key: ms_mk_2026_pretoria_admin"` to migrate existing local photos to S3.

---

## Session 8 · 2 April 2026 · Task 5 — GeoNames config guard (BEA)

The `_fetch_geonames_suburbs` background task already checked for `GEONAMES_USERNAME` via `os.getenv()` (added in Session 7 Task 6). Updated the silent return to emit a `WARNING` log: `"GEONAMES_USERNAME not set in .env — suburb auto-seed skipped for city {city_name}"`. No other logic changes. To enable suburb auto-seeding for new cities, register free at geonames.org and add `GEONAMES_USERNAME=<your_username>` to `/var/www/marketsquare/.env`, then `systemctl restart marketsquare.service`.

**Deploy:** `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py` then `systemctl restart marketsquare.service`

---

## Session 9 · 3 April 2026

Hetzner Object Storage fully activated: `HETZNER_S3_ACCESS_KEY` and `HETZNER_S3_SECRET_KEY` added to `/etc/environment`, BEA restarted, and the INFO log confirming S3 initialisation was verified on the server. The `POST /admin/migrate-photos` endpoint was run and returned 0 local photos to migrate — all existing listings had no local `/media/` paths, so new uploads will go directly to S3 from this point forward. `start_marketsquare.bat` was updated to include the correct SCP deploy commands for both `marketsquare.html` and `marketsquare_admin.html` in the end-of-session reminder block, so the deploy commands are visible each time a session is started.

---

STATUS.md + AGENT_BRIEFING.md: replaced stale hardcoded values with live pointers to BEA/admin sources of truth.

---

## Session 10 · 5 April 2026 · Proximity search — lat/lng, distance badges, map view, near-me filter

Full proximity search built across BEA and buyer app. BEA: added lat/lng REAL columns to geo_cities and geo_suburbs; updated seed_geo_za() and _seed_country_from_geonames() to store coordinates from GeoNames data; added _backfill_geo_coords() one-time function that re-downloads ZA.zip and UPDATEs existing rows with lat/lng; added _haversine_km() helper; new GET /geo/nearby endpoint returns suburbs within a configurable radius sorted by distance (bounding-box pre-filter + Haversine); GET /geo/suburbs and /geo/cities now return lat/lng; GET /listings JOINs geo_suburbs for suburb_lat/suburb_lng on each listing. Buyer app: added Leaflet.js 1.9.4 + MarkerCluster CDN; browser Geolocation API detects buyer GPS on startup; distance badges ("2.3 km") shown on listing cards; grid/map view toggle with Leaflet map using OpenStreetMap tiles, clustered listing pins with popups, blue circle for buyer location; "📍 Near me" option in suburb panel calls /geo/nearby (10 km radius), filters listings client-side to matching suburbs; listings sort by distance when GPS is available. Zero-cost tile solution: OpenStreetMap/OpenFreeMap, scalable to self-hosted Protomaps on Hetzner if needed.

---

## Session 11 · 5 April 2026 · Admin city search + duplicate cleanup

Replaced the "Add a new city" form in the admin Cities tab with a search input that filters the cities table by city name or province as you type. Removed POST /geo/cities endpoint from BEA — cities are seeded exclusively from GeoNames, not created manually. The old Add City form had caused a duplicate lowercase "pretoria" (id 101) with 0 suburbs; deactivated on server via UPDATE geo_cities SET active=0 WHERE id=101. Real Pretoria (id 47) has 140 suburbs.

---

## Session 21 · 17 April 2026 · Edit polish, smart sell flow, price fix, demo data, category photos

### Bug fixes (marketsquare.html)

**Edit screen photo wiring** — `elRenderPhotos()` now called inside both `openEditListing()` and `editAISuggest()` so uploaded photos and AI-warning badges appear correctly in the edit sheet.

**Structured fields from DB columns** — `loadLiveListings()` now prefers dedicated DB columns (`l.beds`, `l.baths`, `l.garages`, `l.prop_type`, `l.listing_type`, `l.floor_area`, `l.erf_size`, `l.subject`, `l.level`, `l.mode`, `l.service_type`, `l.availability`) over description-text parsing. Regex updated to `/(\d+)[-\s]*bed/i` to match "3-bedroom" hyphenated forms. Result: structured info pills now survive AI rewrites of the description.

**floor_area / erf_size** — Added to mapped listing object in `loadLiveListings()` and to `saveEditedListing()` payload. Both fields now display in the detail view and persist on save.

**Stale buyer cache after save** — `saveEditedListing()` now calls `Promise.all([loadLiveDash(), loadLiveListings()])` after a successful PUT so the buyer grid refreshes immediately.

**listing_type detection** — Regex expanded to match AI-written prose (`per month`, `monthly rent`, `to let`, `to-let`, `rental`) not just exact "for rent" strings.

**Commitment Model step text** — Removed outdated "Seller pays 1T penalty" copy from the commitment flow. Step now reads "Listing becomes available to other buyers again."

**Price corruption fix** — `saveEditedListing()` and `_elFieldVal()` now strip all non-numeric characters before saving price (`replace(/[^0-9.]/g, '')`). Prevents AI-suggested multi-option price strings (e.g. "R26,990/month (all-inclusive from R28,480)") from concatenating into a corrupt value. DB corrected via `fix_prices.py` (IDs 5–8).

**Profile photo drag and drop** — Added `ondragover`, `ondragleave`, and `ondrop` inline handlers to the CV photo circle. New `handleCVPhotoDrop(e)` function processes dropped image files identically to the click-to-upload path.

**Tutors & Services edit fields** — `_elFieldVal()` now maps `subject`, `level`, `mode`, `service_type`, `availability` from BEA raw data. Detail view shows info pills for all three categories (Property: beds/baths/garages/floor_area/erf_size; Tutors: subject/level/mode; Services: service_class/service_type/availability).

### Smart + Sell routing (marketsquare.html)

`+ Sell` nav button now calls `openSellNav()` instead of going directly to the onboard form. If `ms_aa_email` is present in localStorage an account-picker bottom sheet appears with two options: continue with the existing account, or start a fresh account for a second business. Sellers whose storage was cleared can also recover their session via a new "sign in with existing account" section at the bottom of the onboard form. `submitOnboard()` now stores `ms_aa_name` in localStorage. Fixed a bug where `sellSheetNewAccount()` was prematurely clearing the email key before the onboard form had a chance to write a new one. `.ob-form` padding-bottom increased to `max(calc(env(safe-area-inset-bottom) + 80px), 100px)` to prevent the submit button from hiding under the bottom nav bar on iOS.

### Trust score column (bea_main.py)

Added `("trust_score", "INTEGER")` to the `run_migrations()` migration loop (already present alongside `seller_email` from session prep). `Listing` Pydantic model gains `trust_score: Optional[int]` and `seller_email: Optional[str]`. `create_listing` POST endpoint INSERT updated to save all structured fields: `prop_type`, `beds`, `baths`, `garages`, `subject`, `level`, `mode`, `service_type`, `availability`, `trust_score`, `seller_email`. Previously only 10 base columns were saved; now 21.

`loadLiveListings()` in `marketsquare.html` uses `l.trust_score || 40` instead of the hardcoded value `40`, so trust badges now reflect real DB data.

### Demo seed data

`seed_demo_data.py` creates 20 demo listings under `dmcontiki2@gmail.com` (all editable via the seller edit flow):
- 10 Tutors: Maths/Physics (88), Piano (84), Stats/Data Science (92), Coding/Robotics (79), English/Afrikaans (76), Accounting (72), Life Sciences (61), Primary (67), Zulu/Sesotho (55), Chess (48)
- 10 Services: Plumber (90), Electrician (87), Web Design (85), Bookkeeping/Tax (83), Personal Trainer (78), Photography (74), Graphic Design (69), House Cleaning (63), Garden (58), Car Valeting (52)

Each listing has Unsplash royalty-free photos, full structured fields, and mock certificate text in the description. Trust scores vary 48–92 to demonstrate all four trust tiers.

### Category shopfront photos (marketsquare.html)

Category tiles on the home screen now show representative full-cover Unsplash photos instead of emoji on a gradient:
- **Property** — `photo-1570129477492-45c003edd2be` (warm suburban house at golden hour)
- **Tutors** — `photo-1580582932707-520aed937b7b` (teacher working with student)
- **Services** — `photo-1621905251918-48416bd8575a` (skilled professional at work)

Solid-colour fallback (`#1e3a5f` / `#14532d` / `#7c2d12`) retained for offline/load-error cases. `.cat-overlay` gradient keeps category name and listing count legible over any photo. Category photo URLs also added to `CATS` config as `catPhoto` and used as fallback in `cardHtml()` when a live listing has no uploaded photo.

**Deploy:** `scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html` · `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py` · `ssh root@178.104.73.239 "systemctl restart marketsquare"`

## Session 35 (continued) — Edit Screen: Multi-photo, Document Hub, Trust Score + AI Guidance

### marketsquare.html (buyer app seller self-edit screen)
- **Multi-photo management on edit screen**: `elRenderPhotos()` now reads `photo_urls` JSON array (falls back to `medium_url`/`thumb_url`). Shows all photos with 🔄 Replace + ✕ Remove buttons plus an "+ Add Photo" card (up to 10 photos). `elRemovePhoto(idx)` splices `_elPhotoUrls` and auto-saves. `elAddPhoto(event)` uploads to `/listings/photo`, pushes URL, auto-saves via PUT.
- **Trust Score panel on edit screen**: `elLoadSidebarPanels()` loads score bar, tier label, and Haiku tip into `el-tsh-section` on edit open (GET `/trust-score/breakdown`).
- **AI Guidance panel on edit screen**: POST `/trust-score/guidance` loads personalised action plan into `el-aiguidance-section` so the seller knows exactly what evidence to upload next.
- **Document Hub on edit screen**: `elRenderDocHub()` renders full upload + listing in `el-dochub-section`. `elDocHubUpload()` uploads doc and refreshes Trust Score + Doc Hub in one pass.
- **`_elPhotoUrls` module-level array**: tracks photo state during edit session; `saveEditedListing()` now includes `photo_urls: JSON.stringify(_elPhotoUrls)` in PUT payload.
- **`apiPost` helper**: added for clean JSON POST calls with API key header.
- Deployed to trustsquare.co (index.html). 9740 lines, tail verified.

## Session 36 — Document Hub + Photo fixes (2026-05-01)

### Bugs fixed
- **Document Hub 401 / empty** — Cloudflare strips `X-Api-Key` headers on GET requests before they reach the BEA. Fixed by: (1) adding `require_api_key_header_or_query` dependency to `auth.py` that accepts key as `?api_key=` query param; (2) updating `GET /users/{email}/documents`, `POST /users/{email}/documents`, and `DELETE /users/{email}/documents/{doc_id}` to use it; (3) updating all front-end document fetches to pass `?api_key=API_KEY` in the URL.
- **Photo not persisting after edit-screen save** — `ListingUpdate` Pydantic model was missing `photo_urls`, `thumb_url`, and `medium_url` fields, so the PUT body was silently discarding them. Added all three fields. Also updated the auto-save on photo upload to send `thumb_url` / `medium_url` from the newly uploaded photo so listing card thumbnails update too.
- **`apiGet` ignores options** — the function signature only takes `path`; callers passing `{ headers: { 'X-Api-Key': ... } }` as a second arg were being silently ignored. Fixed by moving auth to query param (see above).
- **Listing 69 `photo_urls` backfilled** — updated DB directly to set `photo_urls` to the existing `medium_url` so the edit screen shows the correct photo strip on next open.

### Files changed
- `auth.py` — added `require_api_key_header_or_query` dependency
- `bea_main.py` — document endpoints use new dependency; `ListingUpdate` gets `photo_urls`, `thumb_url`, `medium_url`
- `marketsquare.html` — document fetches pass `?api_key=`; photo auto-save sends `thumb_url` + `medium_url`

## Session 36b — Trust Score live feedback after document upload (2026-05-01)

### New features
- **Pending points indicator** — Trust Score panel now shows earned score + a yellow bar for points pending admin verification (e.g. "26 pts earned + 8 pts pending review"). Score recomputes correctly on every `/trust-score/breakdown` call; pending signals don't inflate the live score.
- **AI comment after each upload** — new `POST /trust-score/upload-comment` endpoint calls Haiku 4.5 to generate a personalised 2-sentence response: what the uploaded document will contribute once verified, plus a specific next-step suggestion (highest-value unsubmitted signal). Shown inline in the Document Hub in a green confirmation panel.

### Files changed
- `bea_main.py` — `trust_score_breakdown` returns `pending_points` + `pending_signals`; new `UploadCommentRequest` model + `POST /trust-score/upload-comment` endpoint
- `marketsquare.html` — Trust Score panel renders pending bar + badge; `elDocHubUpload` calls upload-comment and renders AI feedback in green panel

## Session 36c — Fully automated Trust Score verification (2026-05-01)

### No humans in the loop — ever

**Design decision**: Removed all "pending → admin review" paths. Verification is now 100% automated:

- **Certificates, training docs, memberships, guides** → auto-earn the signal the moment the document is uploaded (self-attestation model, same as Fiverr/Upwork/LinkedIn). If a verified ID name exists, a background Sonnet task also checks the cert name and can award `cert_name_verified` (+3 pts).
- **ID/Passport** → Sonnet vision auto-earns `id_ai_verified` at confidence ≥ 0.60 (lowered from 0.75). Format-valid check always earns `id_number_valid`. No fallback to admin queue.
- **Future upgrade path**: Swap in Smile Identity or Datanamix SA DHA API call (~R1–R3/check) in `_sonnet_verify_identity` — zero code changes needed in upload flow.

### Files changed
- `bea_main.py` — `upload_seller_document` auto-earns all non-ID signals; uses `BackgroundTasks` for cert name check; ID verify confidence threshold lowered to 0.60; cert_name_check always earns
- `marketsquare.html` — upload status message reflects earned vs pending per doc type

### DB patch
- Retroactively earned `category.lm.formal_cert`, `category.lm.training_course`, `category.lm.product_guide` for dmcontiki2@gmail.com — score: 26 → 34

## Session 36d — Stacking Trust Score signals for Local Market (2026-05-01)

### New features
- **Stacking credentials** — uploading multiple relevant documents now earns points for each one, up to a per-type cap:
  - Certificates/diplomas: 1st = 6 pts, 2nd = 4 pts, 3rd = 3 pts (max 3)
  - Training courses: 1st = 4 pts, 2nd = 3 pts (max 2)
  - Association memberships: 1st = 5 pts, 2nd = 4 pts (max 2)
  - Product guides/recipes: 1st = 3 pts, 2nd = 2 pts, 3rd = 2 pts (max 3)
- **Named role in association** — new `category.lm.assoc_role` signal (+7 pts) for secretary, chair, committee member etc. Upload an appointment letter, meeting minutes, or association confirmation. Higher value than plain membership.
- **Smart signal routing** — `_next_signal_for_doc()` function checks which slots are already filled and routes each new upload to the correct next slot automatically. Sellers don't choose the slot — the system handles it.
- **Doc Hub stacking hints** — selecting a document type in the upload form now shows a blue hint bar explaining how many uploads count and what each is worth (e.g. "Up to 3 counted — 6, 4, then 3 pts each").

### Theoretical max score for a Local Market seller now
Universal (30) + Track Record (30) + Category (40) = 100. Category breakdown:
- Identity signals: up to ~33 pts
- Credentials (3 certs + 2 training): up to 20 pts  
- Memberships (2) + role (1): up to 16 pts
- Guides (3) + media + social: up to 10 pts
- Experience (5yr path): up to 8 pts

### Files changed
- `bea_main.py` — `local_market` signals expanded with stacking slots; `_DOC_TYPE_TO_SIGNAL` replaced by `_DOC_TYPE_SIGNAL_CHAINS` + `_next_signal_for_doc()`
- `marketsquare.html` — `EL_DOC_LABELS` updated; `EL_DOC_STACKING` hints map added; `elUpdateDocHint()` shows hint on type select

## Session 36e — 40-point base score + rebalanced Local Market signals (2026-05-01)

### Design decision: 40-point base for Local Market
Every Local Market seller now starts at 40 — "Established" tier begins at 40 so sellers can trade immediately without waiting. Penalties pull below 40 (bad actors); credentials push above. Other categories (Property, Tutors, Services) unchanged.

### Tier thresholds (unchanged values, new meaning):
- 0–39: New / penalised (LM suspension triggers below 30)
- 40–69: Established ← where every new seller lands on day 1
- 70–89: Trusted ← serious practitioners with credentials
- 90–100: Highly Trusted ← top of field nationally

### Signal rebalancing (anti-gaming principle: hard-to-fake = high value):
| Signal | Old | New | Reasoning |
|--------|-----|-----|-----------|
| Named association role | 7 | **15** | NBA Secretary = top-3 national role, publicly accountable |
| Government/regulatory appointment | 6 | **10** | Independently verifiable |
| 1st membership | 5 | **8** | External org vetted them |
| 2nd membership | 4 | **6** | Convergent external validation |
| 1st formal diploma | 6 | **7** | Accredited, SAQA-traceable |
| 2nd cert | 4 | **5** | Still meaningful |
| Product guides | 3/2/2 | **2/1/1** | Soft signal, easy to pad |
| Social proof | 2 | **1** | Easiest to produce |

### Score benchmarks verified live (dmcontiki2 with 3 docs):
- Current: **74/100 Trusted** (base 40 + 34 earned)
- Add NBA membership: ~82
- Add NBA Secretary role: ~97 (Highly Trusted)
- New seller, no evidence: **40** (Established, can trade)

### UI: Trust Score progress bar now shows grey base (40) + coloured earned segment

## Session 36 — Declaration System + Trust Score Live Updates

### Changes
- **BEA: Declaration endpoint** — `POST /users/{email}/declare` records a free-text declaration, awards `declaration_points` (80%) immediately, sets credential to `declared` status. Idempotent: re-declaring updates text but does not re-award points.
- **BEA: Evidence upgrade** — `upload_seller_document` now detects if target signal is already `declared` and upgrades to `earned` on upload. Response includes `evidence_points_awarded` and `declaration_completed` flags.
- **BEA: Stacking signal chains** — `_DOC_TYPE_SIGNAL_CHAINS` routes each upload of the same doc type to the next unfilled slot (e.g. 3 certificates fill cert_1, cert_2, cert_3 in sequence).
- **BEA: Breakdown includes declaration fields** — `_build_breakdown_items` now returns `declaration_points`, `evidence_points`, `awarded_points`, `evidence_points_remaining`, `has_declaration`, `declaration_prompt` per item.
- **BEA: Declared status counted in score** — `_sum_earned_with_replaces` counts both `earned` (full pts) and `declared` (partial pts via `awarded_points`) credentials.
- **BEA: 40-pt base for local market** — local_market sellers start at 40 pts (Established immediately); earned credentials push above this; penalties can pull below.
- **BEA: Auto-earn AI comment** — `POST /trust-score/upload-comment` returns personalised 2-sentence Haiku 4.5 feedback after each upload.
- **BEA: DB** — `user_declarations` table added (auto-created on restart): stores free-text declaration, signal_id, points_awarded, timestamp.
- **Frontend: Declaration cards** — Doc Hub now shows amber "Declare" cards for each declarable signal not yet earned. Seller writes free text and clicks "Declare — Earn +X pts immediately". Cards turn green after declaration, showing evidence upload nudge.
- **Frontend: Live Trust Score refresh** — After declaration or upload, both the Trust Score panel and Doc Hub reload automatically so the new score is visible immediately.
- **Frontend: Correct pts display** — Declaration button shows `declaration_points` (80%) not total; evidence hint shows remaining `evidence_points` (20%).

### Signal point structure (local market)
| Signal | Total | Declare | Evidence |
|---|---|---|---|
| Named role in association | 15 | 12 | 3 |
| Govt/regulatory appointment | 10 | 8 | 2 |
| Second association membership | 6 | 5 | 1 |
| 5+ years experience | 3 | 2 | 1 |

### Deployment
- `bea_main.py` → `/var/www/marketsquare/main.py` · BEA restarted active
- `marketsquare.html` → `/var/www/marketsquare/index.html`

## Session 38 (cont.) · 2 May 2026 · is_demo flag — real vs seed data separation

**is_demo column on listings** — Added `is_demo INTEGER DEFAULT 0` to the listings table. All seed/showcase data marked `is_demo=1`: 10 Services + 10 Tutors (dmcontiki2@), 12 Collectors + 12 LM (showcase@trustsquare.co). Real data stays `is_demo=0`: bee LM listing (dmcontiki2@) and 4 Property listings (miconradie1@). Both `/listings` and `/local-market/listings` BEA endpoints now accept `?demo=1` — real app (default) filters seed data out, demo mode passes demo=1 to include it. Frontend passes the flag automatically based on DEMO_MODE. Smoke test confirmed: real app returns 4 Property + 1 LM (real only); demo returns 30 + 13 (all). Zero contamination risk going into financials work.

---

## Session 38 · 2 May 2026 · Demo mode

**Demo mode** — `trustsquare.co/demo` now serves the marketplace in a read-only showcase mode. Nginx redirects `/demo` to `/?demo=1`. The frontend detects the flag and: (1) hides Sell, Wallet, and Seller nav buttons; (2) shows a sticky blue demo banner with a "Join as a founding seller →" CTA that routes to the real app; (3) navigates directly to Browse so prospects see the marketplace immediately; (4) blocks navigation to tuppence, dashboard, onboard, publish, and plans screens with a toast. The real app at `trustsquare.co` is completely unaffected — no seller flows or data are changed. Also fixed: category-scoped document list (bee certs no longer show in plumber edit screen), trust score DB write blocked when category override active, listings.trust_score synced on breakdown call so card badge matches edit screen.

---

## Session 37 (cont.) · 2 May 2026 · Category-scoped document list

**Category-scoped Document Hub** — `GET /users/{email}/documents` now accepts an optional `?category=` parameter. When supplied, the BEA returns only documents whose `signal_id` matches that category prefix (e.g. `category.lm.*` for LocalMarket), plus universal and track_record documents, plus any doc with no signal_id. Documents from other categories are hidden. Frontend passes `&category=elCurrentCat` on both the initial load and the post-upload reload, so each listing's edit screen only shows its own relevant evidence — bee certificates no longer bleed into the plumber listing.

---

## Session 37 — LocalMarket category normalisation fix

**Problem:** `normCat()` had no case for `'local_market'` or `'LocalMarket'`, so all Local Market listings fell through to `'Services'`. This caused:
- Seller dashboard showing "SERVICES" label and Services icon/colour for bee listings
- `openEditListing` setting `elCurrentCat = 'Services'`, so the edit form showed Services fields instead of LM fields
- Confusion when a new Property listing attempt opened with mismatched fields

**Fixes applied to marketsquare.html:**
1. `normCat()` — added `'localmarket' | 'local_market' | 'local market'` → `'LocalMarket'`
2. `CATS` — added `LocalMarket: { icon: '🛒', bg: green gradient, model: 'queue' }` so dashboard cards render correctly
3. `AA_CATEGORIES` — added `'LocalMarket'` entry with 4 simple fields: title, price, desc, area — so the edit form renders correct fields for LM listings
4. `renderDashCard` label — `'LocalMarket'` displays as `'Local Market'` (readable label)

**Deployed:** marketsquare.html → /var/www/marketsquare/index.html (9947 lines, file intact)

## Session 37 (continued) — Category-scoped Trust Score credentials

**Problem:** One email = one trust score meant a multi-category seller (bee products + real estate) had their LM credentials bleed into the Property listing's Doc Hub and vice versa. The system assumed a seller lists in only one category.

**Design:** Trust Score credentials are now category-scoped.
- Universal + Track Record signals remain person-scoped (NULL listing_category) — ID, referrals, intros belong to the person not the listing type.
- Category signals store `listing_category` matching the signal prefix (e.g. `category.lm.*` → `local_market`, `category.property.*` → `Property`).
- `trust_score_breakdown` now accepts an optional `?category=` param. The edit screen always passes `elCurrentCat`, so each listing gets the correct signal set.

**BEA changes (bea_main.py):**
1. DB migration: `ALTER TABLE user_credentials ADD COLUMN listing_category TEXT`
2. `_signal_listing_category(signal_id)` helper — derives category from signal_id prefix
3. `_build_breakdown_items` — filters credentials by `listing_category` (NULL = applies everywhere; category-signal row only applies if its listing_category is in the current signal set)
4. `trust_score_breakdown` — accepts `?category=` param, normalises frontend names to `_CATEGORY_SIGNALS` keys
5. `_upsert_credential` — stores `listing_category` on insert/update
6. `trust_score_set_credential` (admin) — stores `listing_category`
7. Live DB backfill: 12/17 existing credential rows assigned correct `listing_category`

**Frontend changes (marketsquare.html):**
8. All 3 breakdown fetch calls now pass `&category=<elCurrentCat>`

**Smoke test:**
- `?category=local_market` → score 100, LM signals ✓
- `?category=Property` → score 25, Property signals only (no LM bleed) ✓

**Deployed:** bea_main.py + marketsquare.html → trustsquare.co

---

## Session 38 — Part 2 (3 May 2026) — Post-Publish Bug Fixes

### Fix: Missing X-Api-Key on POST /listings (sbDoPublish)
`sbDoPublish()` was sending `POST /listings` without the required `X-Api-Key: API_KEY` header. Every Path B publish attempt returned "Invalid or missing API key". Added header to raw fetch call. Verified on live server.

### Fix: Trust score not saved on publish
`sbDoPublish()` POST body did not include `trust_score`. BEA stored 0/default. Now sends `trust_score: sbCalcScore()` so the score built in B7 is persisted correctly.

### Fix: Structured property fields not sent as top-level BEA columns
`beds`, `baths`, `garages`, `floor_area`, `erf_size`, `prop_type`, `listing_type` were only inside `structured_fields` JSON string. BEA already had dedicated columns for all of them. Now sent as top-level fields in POST body — chips and filters work correctly for new listings.

### Fix: Only first photo uploaded; selfie upload missing X-Api-Key
Photo upload loop now iterates all `sbState.photos` (not just index 0), with `is_primary=true` on first. Selfie upload to `/users/{email}/photo` was silently failing — missing `X-Api-Key` header added.

### Fix: Seller CV credentials section dead for BEA listings
`openBEASellerProfile()` showed static placeholder text. Now parses `structured_fields._signals` from the listing and renders each signal the seller claimed or uploaded. Blurred seller photo shown in CV hero if available.


### Fix: 0-listings startup — root cause was BEA crash loop
BEA had restarted 19,594 times in 7 days due to the opt_out duplicate body bug (fixed earlier this session). Every time a user loaded the app during a restart window (~30s cycle), the BEA was unavailable and listings returned nothing. Since the BEA fix: one restart only, server stable. The startup blank screen was not a client-side timing issue — it was the server crashing continuously. Added 3× exponential backoff retry to loadLiveListings() as a safety net for genuine network blips.

### Fix: Inline script tag in template literal broke entire app
The credentials section fix (openBEASellerProfile) injected a `<script>` tag inside a JavaScript template literal. The browser parser sees the closing `</script>` inside the string and terminates the outer script block early, silently breaking all JS on the page. Fixed by rewriting as a pure IIFE expression returning HTML — no script tags involved.

### Fix: JS syntax error — duplicate const cat/f in sbTriggerMarketNote
My fix to show the AI note immediately added `const cat` and `const f` at the top of sbTriggerMarketNote, but those variables were already declared later in the same function scope. This caused a SyntaxError that silently killed all JavaScript on page load — 0 listings, all sections stuck on Loading. Fixed by removing the duplicate declarations. Added mandatory pre-deploy JS syntax check (node --check) to catch this class of error before it reaches the live server.

### Fix: BEA /listings/photo never saved URLs to listing row
The photo upload endpoint accepted listing_id as a form field but ignored it — it uploaded to R2 and returned the URLs in the response body without writing them to the listings table. All photo uploads from sbDoPublish() were silently discarded. Fixed: endpoint now accepts listing_id + is_primary form fields, writes thumb_url/medium_url to the listing row, and appends additional photos to the [photos:url1|url2|...] description prefix for the multi-photo strip.

## Session 39 — AI guidance fixes + photo captions

**AI guidance stale data fixed:** `sbTriggerMarketNote` now uses an `AbortController` to cancel any in-flight request from a previous listing session before issuing a new one. A field-presence guard prevents the AI call firing until at least one key field (`beds` for Property, `subjects` for Tutors, `trade_type` for Services) is populated — eliminating the "3-bedroom" stale response on a fresh 1-bedroom listing. The fallback note always reflects the current `sbState.fields` values immediately.

**AI guidance field triggers expanded:** `sbSaveField` now re-fires `sbTriggerMarketNote` when `beds`, `baths`, `price`, or `rate` are updated (in addition to `suburb`, `subjects`, `trade_type`). The note updates live as the seller fills in details.

**Photo captions implemented end-to-end:** Sellers enter captions in B5. On publish, captions are sent as a `caption` form field alongside each photo upload. The BEA encodes them into the `[photos:]` description prefix as `url::caption` pairs. `loadLiveListings` parses these into a `photoData` array `[{url, caption}]`. `openDetail` renders captions as a gradient overlay at the bottom of each photo strip slide.

**BEA restore:** The Edit tool truncated `bea_main.py` to 6062 lines mid-session. Restored from `git show HEAD:bea_main.py` (6023 lines) and re-applied all changes via Python replace. Root-cause note appended to the tail-truncation rule: the Edit tool must never be used on `bea_main.py` — Python replace-only, same as `marketsquare.html`.

## Session 39 continued — Trust Score display fix + private seller signal set

**Trust score mismatch fixed:** BEA `trust_score_breakdown` was using `base_score=0` for Property sellers while the sell-flow `sbCalcScore()` uses base 40. Changed BEA `base_score` to 40 for all sellers — matching the "all sellers start at Established" model. Dashboard and edit-listing Trust Score panel now show the same value as the home page listing card.

**Private seller PPRA tip fixed:** Added `Property_private` and `Cars_private` signal sets to `_CATEGORY_SIGNALS` — private sellers get experience-based signals only, never PPRA/NQF4 agent credentials. The `_cat_norm` map in `trust_score_breakdown` now routes `Property_private` to the correct signal set. Gate is stored in `structured_fields._gate` at publish time and read back by the edit-listing screen to set a gate-aware `elCurrentCat` (`Property_private` / `Property_agent`) before calling `elLoadSidebarPanels`.

## Session 39 continued — For You card: price + trust badge

**For You card improved:** Added price line below the title (bold, accent colour) — shown when price is not POA/0. Trust badge updated to show ★ star prefix at all tiers (Established / Trusted / Highly Trusted) so it reads as a trust indicator rather than a plain number. Trust score on the card now reflects the corrected base-40 value from the BEA.

---
*Session 39 closed. All changes deployed to trustsquare.co. Next: Session 40 — retest across categories, home page scroll fix, For You score refresh.*

## Session 40 — Card UI polish + cost model review

**Photos lost on PUT /listings fixed:** The `update_listing` endpoint was overwriting the `[photos:...]` description prefix when a seller's AI-generated description was saved. Fixed: if the existing description starts with `[photos:` and the incoming description does not, the endpoint re-prepends the photo prefix before writing. Listing 74's photos were manually restored from `listing_versions` snapshot via direct SQLite UPDATE on the server.

**For You tile tap fixed:** The wishlist feed returns raw numeric listing IDs from the BEA; `openDetail()` expects `'bea_N'` format. Fixed `wfFeedTap()` and `wfShowcaseTap()` to normalise any raw integer ID to `'bea_N'` before calling `openDetail`.

**Photo caption overlay styled:** Caption pill rendered bottom-right of each photo slide — frosted-glass dark background (`rgba(10,10,20,.78)` + `backdrop-filter:blur(6px)`), 11.5px Inter font, rounded corners. Always readable over any photo.

**Category chips added for all missing categories:** `openDetail` now renders profession/detail chips for Local Market (purple), Collectors (amber), and Cars (blue) — matching the existing chip rows for Property, Tutors, Services.

**Featured card layout refactored:** Cards now use flexbox column layout. Photo fixed at 88px top, category label + title (clamped 2 lines at 11.5px) in flex body, location + price + trust badge pinned to fixed bottom footer. Consistent alignment across all cards regardless of title length. Trust badge moved to float top-right over the photo as an absolute overlay.

**For You card aligned to Featured:** Same flexbox column layout, same dimensions (150px wide, 88px photo), same bottom-pinned footer with location + formatted price + trust badge overlay on photo. Price now formatted via `formatZAR()` — renders `R 2 500 000` correctly. Trust badge uses same tier colours as Featured.

**AI cost model review (Session 40):** Confirmed free seller costs ~$0.58/year — consistent with cost model's $0.645/year blended figure. Key finding: `sbTriggerMarketNote` fires for free sellers on every publish/edit (unmodelled). At Year 1 scale (7,312 free sellers × 4 edits) = ~$67/year — trivial but worth a future gate. Haiku 4.5 actual cost is ~$0.0023/session vs $0.01/session in model — model is conservatively priced, which is correct. On-server AI replacement (planned) would reduce this to ~$0/session variable cost. Local Market crossfade not broken — only 1 LM listing with a photo; animation requires 2+.

Cost model impact: AI Coach cost per session ($0.01 modelled) is ~4× higher than actual Haiku 4.5 rate ($0.0023). Conservative buffer is intentional pending on-server AI replacement. No model update required.

---
*Session 40 closed. All changes deployed to trustsquare.co. Next: Session 41 — category testing across Tutors/Services/Collectors/Cars/Local Market.*

## Session 42 — Part 3: Real EULA embedded in onboarding Phase 3

Replaced the 7-point placeholder seller terms in `screen-seller-onboard` Phase 3 with the full content of `MarketSquare_EULA_v1_0_Draft.docx` (v1.0, 18 April 2026, SA governing law). The `.sob-eula-box` scrollable panel now renders all 12 substantive sections: Definitions, Platform Scope & Acceptance, Anonymity & Identity Verification, Listings & Content, Tuppence & Introductions (including all introduction models and the ECT Act §44 cooling-off right), Fees & Subscriptions (with confirmed tier spec: Free 2/30d, Standard 20/60d/$5, International 40/90d/$15), Professional Credentials, User-Uploaded Content & IP (including no-photo-stock commitment and IP indemnity), Privacy & POPIA (consent, data retention, POPIA rights, Information Regulator contact), Disputes & Liability (60-day negotiation, SAAF arbitration, liability cap), Trust Score mechanics and penalties, and Governing Law & Termination. The document header notes it is a draft for legal review. Two checkbox consent fields below the scroll box remain unchanged. JS check passed; deployed to trustsquare.co.

## Session 42 — Part 4: Tutors Trust Score signals + subject-aware AI coach

**BEA (`bea_main.py`):**
Added three missing Tutors credential signals from the TrustScore_Signal_Audit.xlsx spreadsheet: `category.tutors.clearance` (Police clearance / DBS check, 8 pts — highest-value signal for tutors working with minors; SA: SAPS clearance, UK: DBS, AU: WWC, US: state background check), `category.tutors.safeguarding` (Safeguarding / child protection cert, 3 pts — NSPCC, Mandatory Reporter, etc.), and `category.tutors.online_ready` (Online platform proficiency declaration, 1 pt — Zoom, Google Classroom, etc.). Updated `how_to_earn` for `category.tutors.specialisation` to include subject-specific examples by discipline (Maths/Science, Music, Languages, Coding, Accounting, Sport coaching, etc.) rather than generic text. Corrected SACE note to clarify it is mandatory for SA school teachers only — private/independent and tertiary tutors do not need it. Updated the AI coach credential reference for Tutors to be fully subject-aware: coach now reads the `subject` field first, leads with police clearance for minor-facing tutors, tailors subject specialisation examples to the seller's actual subject, and is explicitly prohibited from suggesting unrelated credentials (e.g. "Beekeeping Certificate").

**Admin app (`marketsquare_admin.html`):**
Document Hub upload dropdown is now category-aware for Tutors: when editing a Tutors listing, the "Upload new document" dropdown switches from the generic Local Market list to a Tutors-specific set (Police Clearance / DBS Check, Degree / Diploma / Certificate, Subject Specialisation Certificate, SACE Registration, Safeguarding / Child Protection Cert, CV with Teaching Experience, Professional Body Membership, Other). Label placeholder also switches to `'Label (e.g. 'SACE Registration' or 'BSc Mathematics')'` for Tutors, replacing the generic "Beekeeping Certificate" example. Category is now passed through from the listing to `docHubLoad()` to enable all category-aware rendering.

## Session 42 — Part 5: All-category Trust Score signals + doc type dropdowns

Applied the full TrustScore_Signal_Audit.xlsx recommendations across all categories, not just Tutors.

**BEA — new credential signals added:**
- Property: `ffc` (Fidelity Fund Certificate, 10 pts — annual, separate from PPRA), `mandate` (signed instruction letter, 8 pts), `private_seller` (0 pts transparency label)
- Services-Technical: `insurance` (public liability, 5 pts), `cidb` (CIDB grading for construction, 6 pts)
- Services-Casuals: `clearance` (police clearance/background check, 10 pts — highest priority for in-home workers)
- Adventures-Experiences: `permit` (operator permit/concession licence, 6 pts), `regulator_compliance` (sector regulator cert beyond guide cert, 5 pts)
- Collectors: `provenance` (chain of custody doc, 8 pts — required for high-value items), `dealer_reg` (dealer/reseller registration, 6 pts)
- Cars: `dealer_reg` (MIRA dealer licence, 8 pts), `inspection` (independent inspection report, 5 pts), `service_history` (4 pts), `private_seller` (0 pts transparency label) — these join the existing ownership/rwc/finance_clear signals

**BEA — AI coach credential references updated for all categories:**
- Property: added FFC and mandate coaching; distinguishes agent vs private seller flow
- Services: added insurance and CIDB for technical; leads with police clearance for casuals
- Adventures: added permit and regulator compliance; TGCSA still leads for accommodation
- Collectors: added provenance and dealer_reg; instructs AI to tailor by collecting domain
- All categories now include a COACHING INSTRUCTION block directing the AI to read listing-specific fields before suggesting credentials and to never suggest unrelated documents

**Admin app — Document Hub dropdown now fully category-aware:**
- Property: PPRA, FFC, Mandate, NQF Certificate, Professional Body, Other
- Services (Technical): Body Registration, Trade Certificate, Insurance, CIDB, CoC/Licence, Safety Ticket, CV, Other
- Services (Casuals): Police Clearance, Reference Letter, NQF/Short Course, CV, Other
- Adventures: Guide Cert, Operator Permit, Insurance, First Aid, TGCSA, Municipal Licence, Health & Safety, Safety Cert, Award, Other
- Collectors: Auth Certificate, Provenance, Appraisal, Dealer Registration, Association Membership, Other
- Cars: NATIS Papers, Dealer Registration, Roadworthy Certificate, Inspection Report, Service History, Finance Clearance, Other
- Label placeholder text also updates per category (e.g. "NATIS RC1" for Cars, "FGASA Level 1 2025" for Adventures)

---

## Session 43 · 4 May 2026

### Part 1 — Legal Entity Registration & TrustSquare Rebrand

Trustsquare (Pty) Ltd was formally registered with CIPC on 29/04/2026 (Reg 2026/340128/07, Director: David Maurice Conradie). The platform has been fully rebranded from MarketSquare to TrustSquare across all user-facing strings in marketsquare.html (buyer app), marketsquare_admin.html (admin app), and bea_main.py (BEA). Legal entity name "Trustsquare (Pty) Ltd" and registration number "2026/340128/07" added to the embedded EULA header and waterline. BEA health endpoint now returns "TrustSquare BEA v1.3.0". All test listings and users (51 listings, 5 users, all associated records) wiped from marketsquare.db for a clean production start. Geo data (countries, regions, cities, suburbs) preserved. All three files deployed to Hetzner and BEA restarted successfully.

## Session 43 · Part 2 · 2026-05-05

**Trust Score integrity overhaul.** Demo trust scores were arbitrary (66–93); David flagged this as a legal and trust exposure risk. All scores now calculated from `_TRUST_SIGNALS` and `_CATEGORY_SIGNALS` in bea_main.py. Property private sellers cap at ~44 (Established tier — no PPRA/FFC applicable), Tutors at ~81 (Trusted — Honours + SACE + police clearance + 12yr experience), Services at ~88 (Trusted — Red Seal + ECSA + insurance + 14yr experience), Adventures ~76, Collectors ~54, Cars ~49. The seller CV now displays `s.trustScore` (the seller-level verified score) instead of the per-listing `l.trust` field, making it traceable and defensible.

**Availability rendering fixed.** The seller CV showed "undefined · undefined" because `avail` entries were plain strings but the renderer expected `{day, time}` objects. All 7 SELLERS entries now use `{day, time}` object format matching the template.

**Property seller credentials corrected.** Demo property seller now shows "Private seller declaration" (transparent to buyers, 0 pts — regulatory honesty) plus compliance docs, matching actual signal structure. Removed misleading "Title deed confirmed" credential (that belongs to the agent, not the private seller).

**All 70 demo listings complete.** Added 40 new listings: Adventures (10), Collectors (10), Cars (10), Local Market (10). Adventures: Big 5 walk, hot air balloon, abseil gorge, horse trail, quad biking, escape room, wine tasting, cooking class, photography walk, waterfall hike. Collectors: Rolleiflex TLR, SA stamps, Krugerrands, antique Transvaal map, Pierneef lithograph, Wilbur Smith first edition, Voortrekker medals, SA railway prints, Leica M3, Boer War campaign group. Cars: Porsche 911 Carrera S, BMW M4, AMG C63 S, Ford Mustang Mach 1, Tesla Model 3, Land Cruiser 79, plus two farm properties (Bela-Bela smallholding and Limpopo game farm), Lamborghini Huracán, vintage Mercedes W108. Local Market: MTG Black Lotus, Pokémon Charizard PSA 8, Rolex Submariner, 1900 Hornby train set, SA jazz vinyl collection, signed Springbok 2019 RWC jersey, ZAR Pond NGC MS63, KWV 30-year brandy, Boer War Mauser (deactivated), Hermanus Steyn oil painting. Local Market seller (idx 6) added to SELLERS array with trustScore 62.

## Session 43 · Part 3 · 2026-05-05

**Local Market home tile fix.** The `initLMHomeTile` function fetches counts and photos exclusively from the BEA `/local-market/listings` endpoint. When BEA returns empty (no live listings yet), the tile showed "0 listings" even though 10 demo listings existed. Added a demo fallback: when BEA returns empty, `initLMHomeTile` now counts and pulls photos from the local LISTINGS array filtered by `normCat === 'LocalMarket'`. Tile now shows "10 listings" with photo slideshow during the demo phase.

**Local Market browse grid fix (lmLoadGrid).** Same BEA-only issue in the browse function — added identical demo fallback so the Local Market screen renders the 10 `demo_lm_` listings when BEA is empty.

**Category chip fix.** The "🛒 Local Market" filter chip was missing from the category bar — only 6 chips were rendered (All through Cars). Added the LocalMarket chip. Also fixed `renderGrid` to use `normCat(l.cat)` for category comparison so `local_market` listings correctly match the `LocalMarket` filter.

**Cost model impact:** None. xlsx unchanged since Session 24.
