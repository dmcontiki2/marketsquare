# BUILD REPORT — CARS-SPEC-1 (Tasks 1–5)
**Scheduled Cowork session · Sat 4 July 2026 ~08:08 SAST · $0 session — no AI calls, no deploy, no commit. STAGED ONLY.**
Plan executed: `docs/CARS_SPEC_1_ARCHITECT_PLAN.md` v1.0 · Scope authority: `docs/CARS_LISTING_AND_VERIFICATION_BRIEF.md` Parts A/B/C (Part D/F Lightstone/TransUnion EXCLUDED — held until live profitability, your call 3 Jul).

## Pre-flight
- STATUS.md + CHANGELOG.md heads read — no conflicting change since the 3 Jul batches. All anchors located by content (plan line numbers were stale as expected).
- Mount health: all 3 files copied to /tmp with byte-size parity vs stat (no torn reads); all writes via anchor-asserted python drivers (`assert count==1` before every replace); Edit/Write tools never used.
- **Backups (restore = `cp <bak> <file>`):** `bea_main.py.bak-carsspec1-20260704-080807` (598,771 B) · `ms.js.bak-carsspec1-20260704-080807` (782,247 B) · `marketsquare.html.bak-carsspec1-20260704-080807` (365,554 B).

## Task 1 — VSPEC-SCHEMA · DONE (staged)
`bea_main.py`: +14 idempotent columns after `grade_tier` (10 discrete: make/model/variant/vehicle_year/mileage_km/transmission/fuel_type/body_type/drivetrain/colour + vehicle_specs JSON + spec_confirmed section map + attested_at/attested_email); `VEHICLE_SECTION_FIELDS` constant + `_validate_vehicle_fields` (400 on malformed JSON, mirrors rental pattern) + `_scrub_vehicle_specs` (D1 public scrub) + `_reset_vehicle_confirmations` (edit hook) beside `_rental_availability`; scrub applied in `get_listings` + `get_listing` (NOT `/mine`); `Listing`+`ListingUpdate` +12 fields each (listing_status and attested_* deliberately excluded — verified by AST); create INSERT extended.
**Verified:** py_compile · INSERT arity by AST = 41 cols / 40 ? + 1 NULL / 40 params · 14/14 standalone unit tests on the three helpers (confirmed+attested survives, unattested hidden, partial sections, demo exempt, non-cars deep-unchanged, legacy cars unchanged, reset semantics ×6, validation ×1).
**Hardened during Task 2:** scrub rebuilt as default-deny — public vehicle_specs is reconstructed from confirmed sections' KNOWN keys only; unknown keys can never leak (re-tested 5/5 incl. rogue-key case).

## Task 2 — VSPEC-VISION · DONE (staged) — AI call site 1/15, only one touched
`bea_main.py`: cars vision instruction now returns top-level `variant` + drafts `vehicle_specs` (fixed key list, omit-when-uncertain, never guess); JSON contract += `"variant": null` + `"vehicle_specs": null` (doc-comment block kept true); `max_tokens` 900→1200 (single call site — the every-category 422-truncation risk the plan flagged); sanitiser force-nulls vehicle_specs/variant on non-cars and drops null keys on cars.
**Verified:** py_compile · `_build_vision_prompt` exec'd standalone for all 7 categories (contract keys present ×7, cars-only instruction confinement, no f-string brace errors) · max_tokens audit (1200 ×1, 900 gone, 700/350/300 call sites untouched) · sanitiser order asserted by AST.
**UNVERIFIED (deliberately):** no real vision call was made — $0 rule. Your one post-deploy Haiku car draft (~$0.01) is the milestone QA and also validates the Haiku-first switch from 3 Jul.

## Task 3 — VSPEC-CAPTURE · DONE (staged)
`ms.js`: `variant` field added to SB_FIELDS.Cars (AA sub-type templates already had it, 3 Jul); new pure `sbVehicleBody(f)` maps quick-list fields → columns + `_prov: seller_entered` blob (engine text → engine_capacity_cc ONLY for explicit 600–9000 cc numbers — litre strings like "2.0 TSI" are never converted, no guessing), spread into the sb publish body (Cars only); guided flow stashes AI draft (make/model/variant/year→vehicle_year/mileage→mileage_km/vehicle_specs, `_prov: ai_guess`) onto `goState.vehicle` in `goApplyVisionToStep2`, carried by `goHandoff` POST and PUT when category is Cars.
**Verified:** node --check · sbVehicleBody 4/4 unit tests (full map, no-litre-guess, empty, junk ints).

## Task 4 — VSPEC-ATTEST · DONE (staged) — all three files
- `bea_main.py` `PUT /listings/{id}/publish`: optional `attested:int=0`; **409 ONLY when cars AND real spec data present AND not attested AND not superuser** (prov-only blobs don't count as spec data — tested); 409 detail exactly per plan; attested=1 stamps attested_at/attested_email post-UPDATE (publish-only write path). Legacy spec-less cars drafts publish exactly as before — GUIDED-PUBLISH-1 regression-safe by construction (gate requires spec data that pre-Task-3 drafts cannot have).
- `aa_publish`: `attested:int=Form(0)`; **stamp-if-present, never blocks**; judgment call implemented: the +21 vehicle field ids from 3 Jul now also persist into the structured columns (fold into description retained — no display regression), populated sections auto-confirm ONLY when attested=1 (seller typed every value themselves). INSERT arity verified by AST (28 cols / 27 ? + datetime('now') / 27 params).
- `marketsquare.html`: hidden `#sob-attest-wrap` before `#sob-p3-err` — **C4 liability wording verbatim from the brief** + section-cards host + single checkbox.
- `ms.js`: `VEHICLE_SECTIONS_JS` mirror + `sobVehicleData/sobRenderAttest/sobConfirmSection/sobAttestSatisfied`; 4 section-confirm cards with provenance chips ("AI draft" amber / "You entered" green), ONE Confirm per section (locked decision — never per-field ticks), only populated sections rendered/required; `sobCheckEula` gates Go-live on EULA + content + attest; phase-3 entry renders the cards (try/catch — can never break the flow); `sobGoLive` PUTs the `spec_confirmed` map (explicit → authoritative over the reset hook), appends `&attested=1`, and surfaces the 409 detail verbatim in `#sob-p3-err`. Dashboard publish: decided **409-guided** — `dashPublish` already surfaces `d.detail` in its toast, zero code change (hub attest affordance logged as follow-on).
**Verified:** py_compile + node --check · publish-gate structure by AST (gate before slot guard, stamp between UPDATE and commit) · has_spec logic 4/4 · attest module 5/5 DOM-stub scenario tests (non-cars null, /mine-sourced cards+chips+rows, gate progression partial→full→checkbox, guided-stash source, legacy cars no-gate).

## Task 5 — VSPEC-DISPLAY · DONE (staged)
`ms.js`: canonical `galThumbClick`/`syncGalThumbs` + one-line `adv*` delegating aliases (inline onclick/onscroll strings in rendered DOM keep working; DOM ids/CSS classes unchanged); thumbnail-strip gate `isAdv → (isAdv||isCars)`; cars chip block replaced by `vehQuickSpec(l)` — **spec-less listings return the legacy chip row byte-identically (proven by string-equality test), spec-bearing listings get the 6-tile strip** (Mileage · Drivetrain · Transmission · Fuel · Consumption · Engine cc, present-values only); `vehSpecPanel(l)` 2×2 Details/Performance/Condition/Features card grid below the description (empty rows/cards/panel hidden; ✅ "Seller-confirmed … attested <date>" note from attested_at; values HTML-escaped); `loadLiveListings` mapper maps all new columns incl. `year` alias — the existing cars Make/Year/Transmission filters now work on live data (the Part B filter deliverable).
**Verified:** node --check · 8/8 display tests incl. pixel-identical legacy fallback, present-values-only, section hiding, attest note, XSS escape. Demo listings carry no vehicle columns → untouched. Adventures gallery unchanged (aliases).

## Task 6 — VSPEC-FILTERS · NOT DONE (deferred by design)
Plan marks it optional/deferrable; unattended session stopped at the mandated 1–5. Variant/Fuel/Body/Drivetrain chips logged on BACKLOG.

## Global verification (final mount state)
py_compile bea_main.py OK · node --check ms.js OK · tails intact ×3 (12,739 / 13,477 / 4,065 lines) · md5 parity /tmp↔mount after every landing · **guardrails:** models carry no listing_status/attested_* (AST), `_SELLER_SUB_TIERS` byte-identical, Tuppence/pricing/payment token counts unchanged, sonnet refs + `_log_ai_spend` + `_check_cost_ceiling` call sites unchanged, single max_tokens change, demo filters unchanged, ms.js DEMO_MODE/topUpBundles/tuppence surfaces unchanged.

## Honest limits (unverified in this session)
- No live HTTP tests — FastAPI was not exercised (sandbox has no server stack); endpoint behaviour is verified at helper/AST level only. The real POST→scrub→publish matrix (plan's verify list a–e) needs the deployed BEA.
- Migration loop not executed against a real DB here (same idempotent pattern as the 20 existing columns; runs at BEA startup on deploy).
- FEA screens not eyeballed in a browser; section cards/strip/panel are DOM-stub- and string-tested only.
- One discrepancy found and resolved: CHANGELOG said ms.js was v214, but marketsquare.html on disk already referenced **v215**; bumped to **v216** per the +1 rule against disk truth.

## Your two actions when ready (nothing is live until you act)
1. **Deploy:** run `deploy_marketsquare.bat` — one deploy ships the 3-Jul batches + this session (bea_main.py, ms.js v216, marketsquare.html). BEA migration adds the 14 columns on restart.
2. **Milestone QA (~$0.01):** one real car vision-draft on Haiku 4.5 — checks the extended contract AND the Haiku-first quality question in one call. Then: **the FEA integrity baseline will flag ms.js/html — refresh `fea_baseline.json` after deploy.**

Rollback: `cp <file>.bak-carsspec1-20260704-080807 <file>` (all three), or redeploy the server copies.
