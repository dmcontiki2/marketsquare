# CARS-SPEC-1 — Architect Implementation Plan (Brief Parts A, B, C only)
**v1.0 · 3 July 2026 · Plan-agent pass, architect sign-off deliverable for CARS_LISTING_AND_VERIFICATION_BRIEF.md**
*Scope = Parts A (display reuse), B (structured spec model), C (confirm + attest). Part D/F (Lightstone/TransUnion) excluded — gated on David's provider decision. Free own-listing comps shipped separately 3 Jul (CARS-VERIFY-1 free half).*

---

## Exploration findings the plan is built on (verified in code)

1. **Read endpoints need no per-field work.** `GET /listings` (bea_main.py:1422), `GET /listings/mine` (:2050), `GET /listings/{id}` (:2070) all `SELECT *` and return `dict(row)` — new columns flow automatically. The work is the *scrub* (hide unconfirmed values on public endpoints), not the return.
2. **Cars structured fields are currently lost on every write path.** The sb-path publish (ms.js ~:7146) sends `structured_fields` + `listing_status:'live'` — both silently dropped by Pydantic. `/advert-agent/publish` folds only `field_labels`-mapped fields into description (vehicle ids ADDED 3 Jul — interim persistence until columns land). The guided-onboard PUT sends no vehicle fields.
3. **The vision prompt asks for variant in prose but the JSON contract has no `"variant"` key** — contract addition, not a new call.
4. **`_build_vision_prompt` is used by exactly one AI call site** (`vision_draft`, `max_tokens: 900`). Only that call site is touched (prompt text + one max_tokens literal). Other 14 call sites zero-touch.
5. **Two ways listings go live:** `PUT /listings/{id}/publish` and `/advert-agent/publish` (inserts live-equivalent). A publish gate on one endpoint alone does not cover both — handled by the visibility invariant.
6. **`listing_versions` audit is free:** `update_listing` snapshots `dict(existing)` — includes new columns automatically.
7. **Prototype confirms target UX:** VEHICLES_LISTING_PROTOTYPE.html — qspec 6-tile grid, four spec-card sections, renderAttest (3 section-confirm cards + 1 liability checkbox + gated publish).

## Core design decisions

**D1 — Visibility invariant (server-side).** A spec value appears on public reads only when *(its section is confirmed)* AND *(listing carries `attested_at`)*. Seller reads (`/mine`) return everything. `is_demo=1` exempt. This makes every rollout step backward compatible — unconfirmed data can exist unshown.

**D2 — Schema: 10 filterable columns + 1 JSON superset + 3 governance columns.**
- Discrete: `make, model, variant, vehicle_year (avoids era_year clash), mileage_km, transmission, fuel_type, body_type, drivetrain, colour`.
- `vehicle_specs TEXT` (JSON): engine_capacity_cc, kilowatts_kw, cylinder_layout, cylinders, aspiration, fuel_consumption_l100, fuel_tank_l, gears, tyre_front/rear, wheelbase_mm, co2_gkm, seats, doors, service_history, roadworthy_status, spare_key, maintenance_plan_until, warranty_until, condition_notes, features[], `_prov` per-field provenance (ai_guess | seller_entered).
- `spec_confirmed TEXT` (JSON section map — section-level ONLY per locked decision): details / performance / condition / features → ISO ts or null.
- `attested_at, attested_email` — set only by publish endpoints, never generic PUT.
- One constant `VEHICLE_SECTION_FIELDS` drives scrub + confirmation-reset; mirrored in ms.js.

**D3 — Publish gate (GUIDED-PUBLISH-1 safe).** `publish` gains optional `attested:int=0`. 409 ONLY when cars AND spec data present AND not attested. Legacy spec-less drafts publish as today. Superuser bypass mirrors EULA-gate pattern. `/advert-agent/publish`: stamp-if-present, never block.

**D4 — Free spec draft rides the existing vision call.** Add `"variant": null` + `"vehicle_specs": null` to the JSON contract (cars-only instruction, null-when-uncertain); server force-nulls vehicle_specs for non-cars; `max_tokens` 900→1200.

## Tasks (each independently shippable, anchor-asserted python drivers only — never Edit/Write)

**Task 1 — VSPEC-SCHEMA** *(bea_main.py)*: extend idempotent column loop (+14 cols after `grade_tier`); `VEHICLE_SECTION_FIELDS` + `_scrub_vehicle_specs()` helper beside `_rental_availability`; apply scrub in `get_listings` + `get_listing` (NOT `/mine`); extend `Listing` + `ListingUpdate` (+12 fields; do NOT add `listing_status` or `attested_*` to models); extend `create_listing` INSERT (arity check!); confirmation-reset hook in `update_listing` (editing a section's field clears that section's confirmation unless request sets `spec_confirmed`).
*Verify:* py_compile; POST cars draft w/ specs → `/mine` returns, public GET nulls them; PUT mileage → condition section cleared; non-cars listings byte-identical; price-check regression.
*Rollback:* revert file; columns inert.

**Task 2 — VSPEC-VISION** *(bea_main.py — AI call site 1/15)*: cars instruction += fill `vehicle_specs` from identified variant (drafts, null-when-uncertain); contract += `"variant": null` (after `"model": null`) + `"vehicle_specs": null`; `max_tokens` 900→1200 (truncation would 422 EVERY category — the flagged risk); sanitiser force-nulls vehicle_specs when category ≠ cars.
*Verify:* one real car vision-draft (~1 call) + one property draft (unchanged shape).

**Task 3 — VSPEC-CAPTURE** *(ms.js)*: variant field in both templates (AA done 3 Jul with sub-types; SB_FIELDS.Cars pending); sb publish body sends discrete vehicle fields + `vehicle_specs` JSON (`_prov: seller_entered`); guided flow: stash draft.variant/make/model/year/mileage/vehicle_specs onto goState (`_prov: ai_guess`), send in handoff POST/PUT when cat Cars.
*Verify:* node --check; car onboarding e2e → `/mine` persisted; Services onboarding unchanged.

**Task 4 — VSPEC-ATTEST** *(all three files)*: publish endpoints per D3 (409 detail: "Please confirm your vehicle details and accept the seller attestation before publishing."); marketsquare.html hidden `#sob-attest-wrap` (C4 wording verbatim from brief) before `#sob-p3-err`; sob render: 4 section-confirm cards (provenance chip "AI draft"/"You entered", one Confirm button per section — NEVER per-field ticks), publish disabled until populated sections confirmed + checkbox; sobGoLive appends `&attested=1`, surfaces 409 verbatim; dashboard publish: minimal confirm or 409-guided (decide at build).
*Verify matrix:* (a) legacy spec-less cars draft publishes unchanged (GUIDED-PUBLISH-1 regression); (b) spec-bearing draft blocked→confirmed→attested→live with `attested_at`; (c) public GET returns confirmed only; (d) non-cars untouched; (e) superuser bypass intact. Old-FEA/new-BEA and new-FEA/old-BEA both degrade safely.

**Task 5 — VSPEC-DISPLAY** *(ms.js)*: add `galThumbClick`/`syncGalThumbs` canonical + `adv*` one-line delegating aliases (inline onclick strings keep working); thumbnail gate `isAdv → (isAdv || isCars)`; replace cars chip block (anchor `l.cat==='Cars' && (l.prop_type` — verified unique) with 6-tile quick-spec strip (Mileage · Drivetrain · Transmission · Fuel · Consumption · Engine cc, present-values only) + 2×2 Vehicle Specs panel below description (hide empty rows/cards/panel — old listings pixel-identical) + "Seller-confirmed" note from `attested_at`; `loadLiveListings` mapper maps new columns (also makes existing cars filters work on live data — the Part B filter deliverable).
*Verify:* old cars listing pixel-identical; new confirmed listing shows strip+tiles+panel; Adventures gallery unchanged; demo unchanged; Make filter live.

**Task 6 — VSPEC-FILTERS** *(optional, deferrable)*: Variant/Fuel/Body/Drivetrain chips in cars filter sheet.

## Global risk flags
- **15 AI call sites:** only `vision_draft` touched. Truncation mitigated (1200); non-cars contamination force-nulled.
- **Price-check path:** zero-touch. Synergy: Task 1 columns give CARS-VERIFY-1 comps their structured keys (title-parse fallback already live 3 Jul).
- **Demo-mode:** scrub exempts `is_demo=1`; FEA demo branches untouched.
- **GUIDED-PUBLISH-1:** gate fires only on spec-bearing cars drafts (cannot exist before Task 3); 409 detail surfaces in existing `#sob-p3-err`.
- **Pydantic silent-drop trap:** do NOT add `listing_status` to `Listing` while adding vehicle fields (sb-path relies on it being dropped).
- **Deploy sequencing:** 1→2→3→4→5, every intermediate state live-safe via D1.

## Key anchors (verified this session)
bea_main.py: migration loop :124 · models :1271/:1310 · create :1544 · publish :1911 · update :2083 · reads :1422/:2050/:2070 · aa_publish :4342 · vision prompt :9652+ · vision call max_tokens :~9930
ms.js: gallery :845 · openDetail :2845-3046 · mapper :320 · sob flow :4538-4790 · go handoff :5376-5980 · sb publish :7127 · field templates SB :6296 / AA :9161+
marketsquare.html: `#sob-p3-err` (attest anchor)
*(Line numbers pre-date the 3 Jul batch-2 edits — re-verify each anchor by content before use.)*
