# MarketSquare · CHANGELOG

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
