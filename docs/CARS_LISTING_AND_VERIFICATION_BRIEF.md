# Cars — Listing Display, Spec Attestation & Lightstone Verification
**Build Brief v1.1 · 15 June 2026 · benchmarked vs WeBuyCars + weelee.co.za**
*Architect agent sign-off required before implementation*

---

## Core Principle: We present only what the seller stands behind

TrustSquare does not assert vehicle facts. Every spec is either **(a)** looked up from a real source, or **(b)** pre-filled as a draft that **the seller personally confirms, line by line**. The platform never says "this car has 331 kW" — the *seller* says so, and attests to it. This is the car-category expression of the existing integrity rule already enforced in the price-check: *the model writes the sentence, the system (or the seller) produces the number.*

This brief keeps the current advertising model unchanged (anonymous, peer-to-peer, intro-based). It only upgrades the listing display, the onboarding capture, and adds one paid verification tier.

---

## Decisions locked (this brief)

1. **Adopt** the WeBuyCars / weelee listing layout — large lead image + selectable thumbnail strip, structured spec panel beside it. *(Reuse existing gallery component — see Part A.)*
2. **Drop** the 360°/3D viewer. A walk-around photo set in the swipe gallery covers it.
3. **Adopt** the two-column "Vehicle Specs" panel (Details · Condition · Performance · Features).
4. **AI identifies the variant; specs are looked up or drafted; the seller agrees by section.** Publishing requires section-level confirmation plus a single liability attestation. Attestation is kept **light** (seller-experience priority — confirmed). The platform is not liable for seller representations.
5. **"Verified by Lightstone / TransUnion"** — a paid tier priced at **2 Tuppence**, deliver-then-charge, returning a real spec sheet + valuation. Slots into the existing fair-price machinery.
6. **Elevate Cars → Vehicles** with a "What are you selling?" sub-type selector (Car · Bike · Caravan · Trailer · Boat · Other).

---

## Part A — Listing display (reuse, don't rebuild)

The Adventures listings already implement the exact pattern WeBuyCars uses. Reuse it for Cars (and ideally generalise to all categories).

Existing pieces in `ms.js`:
- `advThumbClick(id, idx)` and `syncAdvThumbs(id, idx)` (~L829–846) — swipeable strip `#pstrip-{id}`, thumbnail row `#adv-thumbs-{id}`, active-thumb sync.
- Lightbox via `_listingPhotosCache[id]` (~L2807) — full-screen photo view.

**Work:** emit the same gallery DOM from the Cars detail renderer (`openDetail` → detail panel, ~L2806+). Order the car photo slots already captured in onboarding (front, side, interior, engine bay, service book) as the strip. Rename the `adv*` helpers to a category-neutral name (`galThumbClick` / `syncGalThumbs`) so Cars, Adventures, Property and Collectors share one component.

**Layout target (from benchmarked examples):**
- Left: lead image (≈60% width) + thumbnail strip beneath.
- Right: title · price · location + badges (Trust tier, condition) · a 6-tile quick-spec block (Mileage · Drivetrain · Transmission · Fuel · Consumption · Engine cc) · primary CTA (Request intro) + secondary (Compare, Set alert).
- Below: the full **Vehicle Specs** panel (Part B), rendered as a 2×2 card grid.

---

## Part B — Structured spec data model + marketplace filters

WeBuyCars' and weelee.co.za's spec sheets are **near-identical** — and they match what Lightstone/TransUnion expose. That confirms a **canonical, provider-agnostic schema**: define it once and any source (or seller attestation) populates it. One model serves four jobs: onboarding capture, the spec panel, the search filters, and the verified-data mapping.

### B0 — Vehicle category & sub-types ("What are you selling?")

Adopt the WeBuyCars-style sub-type selector and elevate **Cars → Vehicles** as the top-level category, with sub-types: **Car · Bike · Caravan · Trailer · Boat · Other** (Bus / Truck / Tractor). This matches TransUnion's coverage (cars, motorcycles, light/heavy commercial, tractors, buses), so one data feed serves every sub-type. Field sets vary by sub-type (a boat has no gearbox/drivetrain; a trailer has no engine) — render the schema below conditionally per sub-type.

### Field model (card record)

**Identity / Details**
`make` · `model` · `variant`*(new — key gap today)* · `year` · `colour` · `body_type` · `seats` · `doors` · `listing_ref` (internal, replaces "Stock Number")

**Performance (deterministic — lookup/attest)**
`engine_capacity_cc` · `kilowatts_kw` · `cylinder_layout` · `cylinders` (count) · `aspiration` (NA / Turbo / Supercharged) · `fuel_type` · `fuel_consumption_l100` · `fuel_tank_l` · `transmission` · `gears` · `drivetrain` (F / R / FR / 4x4 / 4x2)

**Dimensions & emissions (deterministic — lookup/attest; weelee superset)**
`tyre_front` · `tyre_rear` · `wheelbase_mm` · `co2_gkm`

**Condition (seller-declared + attested)**
`mileage_km` · `service_history` (Full / Partial / None) · `roadworthy_status` (maps to existing `cars.rwc` Trust signal) · `spare_key` (Y/N) · `maintenance_plan_until` (date, optional) · `warranty_until` (date, optional) · `condition_notes`

**Features (seller-declared checkboxes)**
e.g. CarPlay/Android Auto · Reverse camera · Auto stop-start · (extensible list)

> Render conditionally — hide empty fields. Benchmarked examples confirm not every car has Features / Maintenance plan / Warranty.

### Filters — adopt vs drop (P2P, not a dealer)

| WeBuyCars filter | TrustSquare |
|---|---|
| Price, Kilometres, Year, Make, Model, **Variant**, Body Type, Gearbox, Fuel Type, Fuel Consumption, Drive, Colour | **Adopt** — all map to fields above |
| Sub Category, Sort | Adopt (standard) |
| Province | Adopt → use your city/area model |
| Branch | **Drop** — no branches; anonymous sellers |
| Instalment / Finance-from | **Drop** — we are not a finance house |
| Promotions / "Best Buy" / "Certified" | **Remap** → Trust Score tier + "Lightstone-Verified" badge (Part D) |

---

## Part C — Onboarding: identify → draft → **agree per detail** → attest

The capture flow that produces a listing the seller fully owns.

**C1 — Capture & identify.** Seller enters make/model/year (+ photos). The Cars onboarding block already carries `transmission`, `fuel_type`, `body_type` (`ms.js` ~L9043–9066). **Add `variant`.** The vision draft (`_build_vision_prompt`, cars branch, `bea_main.py` ~L9385) is extended to *propose* the variant from photos/title — proposal only.

**C2 — Draft the spec sheet.** Deterministic Performance fields are pre-filled by either:
- the **free path** — AI best-guess from variant, every value flagged `unconfirmed`; or
- the **paid path** — Lightstone lookup (Part D), values flagged `lightstone`.

No value is shown to buyers until confirmed.

**C3 — Per-field agreement (the integrity gate).** Each spec line renders with its value and a **confirm control**. Implementation: per-field check that rolls up by section (Details · Performance · Condition · Features). A field stays hidden from the public listing until confirmed. UX keeps it light — "Confirm all in this section" with the option to edit any line first. Editing a value clears the `unconfirmed`/`lightstone` flag and marks it `seller_entered`. **Locked (seller-experience priority): section-level confirmation only — never 15 individual ticks.**

**C4 — Liability attestation (publish gate).** A single required checkbox before going live:

> *"I confirm I have personally verified every detail above and that all information — specifications, mileage, condition, history and photos — is accurate and true. These are my representations as the seller. TrustSquare does not independently verify or warrant these details and accepts no liability for them. Uploading a document means I also attest to its validity."*

Store `attested_at`, `attested_email`, and the field-level confirmation map on the listing record for audit. No publish without C4.

**Result:** every figure on the page is either a confirmed seller representation or a Lightstone-sourced figure — never a platform guess.

---

## Part D — "Verified by Lightstone" tier (2 Tuppence)

A paid action that returns a **real** spec sheet + valuation from Lightstone and badges the listing.

### Pricing & economics
- **Price: 2 Tuppence.** Top-up bundles are R180/5T (`topUpBundles`, `ms.js` ~L881) → **1T ≈ R36**, so **2T ≈ R72 / ~$4** in redemption value.
- **Cost:** a Lightstone valuation report ≈ **R20 incl VAT**. Comfortable margin at 2T to cover the report + API overhead.
- **Deliver-then-charge:** commit the 2T **only** when Lightstone returns a real report. A failed/empty lookup costs the user nothing — mirrors the current price-check rule.

### Two entry points, one integration
1. **Seller — "Verify my listing" (recommended lead).** On commit, pull spec sheet + value, populate the confirmed Performance fields as `lightstone`, and award a **"Lightstone-Verified"** badge (feeds Trust Score / buyer confidence). Still subject to the C4 attestation.
2. **Buyer — "Lightstone fair-price check."** On a live listing, returns the verified market value vs the asking price (the honest "is this fair?" answer cars currently can't get).

### Code integration
- Add a `lightstone_*` resolver in `bea_main.py` beside `scryfall_price_by_id` / the property feed, returning the `verified` shape already consumed by `_fair_price_resolve` (`official_range`, `floor_zar`, `block`).
- Route Cars through `ai_price_check` (`~L10356`): today the no-feed branch returns `cannot_verify`; with Lightstone wired, Cars returns a `verified` read. Keep `price_caution()` (`~L9829`) for the below-market safety note.
- Reuse `_require_tuppence` / `_deduct_tuppence` (`~L9900 / ~L9866`) and `TIER_TUPPENCE`; register the 2T tier for `fair_price` on Cars.
- Cache spec data per `make+model+year+variant` (specs are static) so repeat lookups don't re-bill; pay Lightstone per call only for the *valuation*, which is the part that actually moves.

### Free default (ships first, no cost)
Before/independent of Lightstone, fill today's `cannot_verify` gap with an **indicative range from your own comparable car listings** (same make/model/year ± mileage band), returned as an `area_guide` exactly like Property — labelled "indicative, not a verified valuation." This removes the dead end at zero cost and makes the 2T Lightstone tier a clear upgrade.

---

## Part E — Build checklist & open items

- [ ] Generalise gallery helpers (`adv*` → `gal*`) and render the strip + lightbox in the Cars detail view.
- [ ] Build the 2×2 Vehicle Specs panel; conditional field rendering.
- [ ] Add `variant` to Cars onboarding; extend vision draft to propose it.
- [ ] Extend listing schema with the Part B fields + the field-confirmation map + attestation columns.
- [ ] Implement C3 per-field confirm UI + C4 publish gate; persist `attested_at/email`.
- [ ] Ship free `area_guide` comps for Cars (fills `cannot_verify`).
- [ ] Build Lightstone resolver + 2T tier (seller verify + buyer check); deliver-then-charge.
- [ ] Spec cache keyed by make/model/year/variant.
- [ ] Map Promotions/Certified → Trust tier + Lightstone-Verified badge; drop Branch/Finance filters.
- [ ] Elevate Cars → Vehicles + sub-type selector (Car/Bike/Caravan/Trailer/Boat/Other); per-sub-type field sets.
- [ ] Extend schema with weelee superset (tyre sizes, CO2, wheelbase, aspiration, cylinder count).
- [ ] Open TransUnion/Imagin8 (and/or Lightstone) account; confirm redistribution + caching rights (Part F).

**Open items to confirm**
- Provider choice & licence model — **see Part F**; the per-report-vs-bulk-catalogue answer is the biggest economics lever.
- Multi-market: ZA first (TransUnion / Lightstone). The same resolver pattern extends to UK (CAP HPI), US (MarketCheck / comps), AUS (RedBook) — each its own `verified` resolver.
- Per-sub-type field sets (which fields apply to Bike / Caravan / Trailer / Boat).

---

## Part F — Data-provider procurement: what's required

Two viable SA providers. Both expose the same canonical fields; the commercial terms differ.

**Option 1 — TransUnion (via Imagin8) — lowest friction to start.**
- **Integration is free; you pay only for the data used** (pay-per-lookup, no monthly floor). Developer docs from Imagin8 Technical.
- Coverage: New / Retail / Trade prices, 100k+ models, 56 brands — incl. motorcycles and light/heavy commercial, tractors, buses (matches the new Vehicle sub-types).

**Option 2 — Lightstone Auto.**
- Self-serve developer portal on Azure API Management (`portal.apis.lightstone.co.za`): API docs, keys, app insights. Valuations from 2.8M bank-finalised transactions.
- Pricing bundle-based; individual valuation report ≈ R20 incl VAT.

**What's actually required (either provider):**
1. **Commercial account + data/reseller agreement.** This is the gating step — not the code. A signed data licence covering price + spec data.
2. **The one question that sets the economics — redistribution + caching rights:** *"May we display valuations and specs to our end-users in public listings, and cache static spec data per make/model/year/variant?"* If a **bulk spec-catalogue licence** is available, specs become free-to-display (only valuations metered per call) → full spec sheets on every listing. If **per-report only**, meter specs behind the 2T tier and use AI-draft + attestation on free listings.
3. **API credentials** — Azure APIM subscription key (Lightstone) or key via Imagin8 (TransUnion).
4. **POPIA compliance** — vehicle/owner data is personal information: a data-processing agreement and lawful basis to surface and store it.
5. **Technical** — map the provider response → canonical schema (Part B); deliver-then-charge (commit 2T only on a real report); cache specs; keep valuations live.

**Recommendation:** open a **TransUnion / Imagin8** account first (free integration, pay-per-data) to ship the 2T verified tier cheaply, and evaluate Lightstone's catalogue licence in parallel. **Decide per-report vs bulk-catalogue *before* building the resolver** — it determines whether specs are a free display layer or a paid feature.

**Sequence:** free own-listing comps (no provider, ships now) → TransUnion pay-per-lookup 2T verified tier → optional Lightstone / bulk-catalogue upgrade if the licence economics win.

---

*v1.1 — benchmarked vs WeBuyCars (Mustang 5.0 GT, Fiat Panda, BMW X3, Daihatsu Terios, Audi SQ8, Jeep Wrangler) and weelee.co.za (Audi A3). Added canonical spec schema, light section-level attestation, vehicle sub-types, and provider procurement (Part F). Architect agent sign-off required before implementation.*
