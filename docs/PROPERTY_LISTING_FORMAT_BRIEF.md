# Property — Listing Display & Structured Facts
**Build Brief v1.0 · 3 July 2026 · benchmarked vs Property24 + Private Property**
*Companion to `CARS_LISTING_AND_VERIFICATION_BRIEF.md` (v1.1) — same integrity model, same reuse rules. Architect sign-off before implementation.*

---

## Core principle: we present only what the seller stands behind

Same rule as Cars: TrustSquare does not assert property facts. Every spec (erf size, levies, rates) is either looked up from a real source or pre-filled as a draft **the seller confirms and attests to**. The platform never says "the levy is R3 457" — the seller says so.

Property adds one finding the portals prove out for us: **both incumbents already support hiding the street address.** Private Property renders *"Contact agent for street address"* on live listings; the PropData feed that agencies use for BOTH portals has an explicit *"Publish Location As: Suburb"* option (pin dropped mid-suburb). Suburb-level publishing is an accepted industry norm — TrustSquare's pre-intro anonymity is a stricter version of an existing pattern, not an alien one.

---

## How this was benchmarked (sourcing note)

- **Property24** — live listing fetched in full (P24-116534163, 4-bed townhouse, North Riding): complete page anatomy + exact field labels of every spec section.
- **Private Property** — live listing fetched in full (T5424747, Lenham) plus a results page: details/features panels + search-card anatomy.
- **PropData Manage** residential-listing docs (docs.propdata.net) — the syndication form SA agencies fill in to feed *both* portals. It marks **required vs optional ("quality") fields explicitly**; treated here as the industry's canonical mandatory/optional split.
- ⚠ P24 *filter* list is partly from search-result snippets (advanced-search page not fetched directly); snippet-sourced rows are marked ⚠. No field names are fabricated.

---

## Decisions proposed (this brief)

1. **Adopt** the two-portal common page shape: gallery + quick-facts strip (Beds · Baths · Parking · Erf · Floor) + a "Key Facts" overview panel + grouped feature sections, rendered conditionally (hide empty).
2. **Adopt** the SA-specific **monthly-costs block — Levies + Rates & Taxes** — as first-class optional fields. This is the #1 hidden-cost anxiety for SA buyers and both portals surface it in the overview panel.
3. **Adopt** suburb-level location as the only public location (we already do this); keep street address as a **private field handed over only at introduction**.
4. **Drop** agent/agency machinery, bond/affordability calculators, home-loan referrals, On Show scheduling, WhatsApp-agent, travel-time calculator.
5. **Adopt** the PropData integrity convention for room counts: a count field that doesn't apply is **0, never blank** — distinguishes "none" from "not answered" and keeps filters honest.
6. **Sub-types**: House · Apartment/Flat · Townhouse/Cluster · Vacant Land · Farm/Smallholding (+ `property_title` Freehold/Sectional driving which cost fields show). Mirrors the Vehicles sub-type selector from the Cars brief.

---

## Part A — Listing page layout (benchmarked anatomy)

**Property24 detail page, top to bottom (observed live):**
1. Gallery: lead image + strip, tabs **Photos (40) · Photo Grid · Map · Video · 3D Tour** (Matterport), fullscreen lightbox.
2. Title block: `4 Bedroom Townhouse for Sale in North Riding` + street address + price + quick icons (beds 4 · baths 3 · parking 2 · erf 35 823 m² with m²/ha/acres toggle).
3. Description: marketing heading + long body, collapsed behind "Read full description +".
4. Features icon row: Bedrooms · Bathrooms · Garages · Pet Friendly · Garden.
5. **Property Overview** panel: Listing Number · Type of Property · Street Address · Description (e.g. "Double Storey, Duplex") · Lifestyle (e.g. "Security Complex") · Listing Date · Erf Size · Floor Size · Levies · Rates and Taxes · Pets Allowed.
6. **Rooms** panel: Bedrooms · Bathrooms · Kitchens · Lounges · Dining Rooms.
7. **External Features**: Garage · Parking (type, e.g. "Secure parking") · Gardens.
8. **Building**: Roof (Tile) · Wall (Plaster) · Window (Aluminium).
9. **Other Features**: Security · Special Feature (e.g. "Built in Braai").
10. Points of Interest (nearby amenities) · Bond Calculator · On Show block · agent/agency panel · share/print/report.

**Private Property detail page (observed live):** price + "calculate bond costs" · title · *"Contact agent for street address"* · quick strip `2 | 1 | 2 | 471 m² | 102 m²` · description with feature bullets · **Property details** (Listing number · Property type · Listing date · Land size · Floor size · Rates and taxes) · **Property features** (Bedrooms · Bathrooms · Open parking · Storeys · Pet friendly) · photo-gallery grid. Search cards carry: type, price, suburb, beds/baths/parking icons, size, snippet, badges (Promoted · Under Offer · Reduced · New · HD Media).

**TrustSquare target:** reuse the shared gallery component (`gal*` helpers per Cars brief Part A). Left: lead image + thumb strip. Right: title · price · suburb + badges (Trust tier, Fair-price chip) · **5-tile quick-spec block (Beds · Baths · Parking · Erf m² · Floor m²)** · Request-intro CTA. Below: Key Facts panel then Rooms / Exterior / Building / Security & Policies cards (2×2 grid like the Vehicle Specs panel). Map = suburb-level pin only.

---

## Part B — Canonical field schema + filters

The P24 and PP spec sheets are near-identical (both are fed by the same PropData/agency feeds), confirming a canonical, provider-agnostic schema — define once, populate from seller attestation or (later) a deeds/valuation source.

### Field model (listing record)

**Identity / Key facts**
`listing_ref` · `property_type` (House / Apartment / Townhouse / Vacant Land / Farm) · `property_style` (free short text: "Double Storey, Duplex") · `property_title` (Freehold / Sectional) · `lifestyle_tag` (Security Complex / Estate / Golf / Retirement) · `listing_date` · `suburb_area` (public) · `street_address` + `unit_no` + `complex_name` (**private — intro handover only**)

**Sizes (deterministic — attest; display toggle m²/ha above 10 000 m²)**
`erf_size_m2` · `floor_size_m2`

**Monthly costs (SA-specific, optional but high-trust)**
`levies_zar_pm` (sectional/estate) · `rates_taxes_zar_pm` — PropData rule adopted verbatim: *only fill if actually known; never guess a placeholder.*

**Rooms (counts; 0 allowed and meaningful; halves allowed for bathrooms)**
`bedrooms` · `bathrooms` (2.5 ok) · `kitchens` · `lounges` · `dining_rooms` · `studies` · `flatlet` (Y/N)

**Exterior**
`garages` · `open_parkings` · `parking_type` (multi-select) · `gardens` · `pool` (Y/N) · `storeroom` (Y/N) · `view_scenery` (Y/N) · `patio_balcony`

**Building**
`roof` · `walls` · `windows` · `flooring` (multi-select) · `storeys` · `furnished` (rentals; default unfurnished)

**Security & policies (Trust-relevant)**
`security_features` (multi: alarm · electric fence · access control · guards · beams) · `pets_allowed` (Y/N + body-corporate note)

**Rental-only**
`monthly_rent` · `deposit` · `lease_period` · `available_from` · `lease_excludes`

**Special features (free tags, PropData pattern)**
e.g. "10 000L JoJo tank" · "Off-grid solar" · "Fibre" · "Built-in braai" — extensible chips, not schema.

### Mandatory vs optional (PropData's industry split → TrustSquare)

| Field | Portals (via PropData) | TrustSquare |
|---|---|---|
| Listing type (sale/rent), property type, location | **Required** | **Required** |
| Street number + name | **Required** (for the feed; can still be *published* as suburb-only) | **Optional at listing, required at intro** — never public |
| Unit no + complex name | Required if sectional title | Same rule, private |
| Description | **Required**, ideally >250 chars, **no contact details** (portals block the listing) | Required; anonymity scrub is already our rule — coach flags names/numbers/addresses in prose |
| Price | **Required** (POA display optional but real price still captured) | Required (no POA at launch — price honesty feeds fair-price) |
| Room/exterior counts | **Required but 0 allowed — never blank** | Adopt verbatim |
| Erf + floor size | Optional "**quality fields**" (land size required for Vacant Land) | Optional; coach-nudged; required for Vacant Land |
| Levies / rates & taxes | Optional quality fields; "only add if you know the amounts" | Same |
| Marketing heading | Optional, <100 chars (PP doesn't accept one) | Adopt as `headline`, coach-drafted |
| Photos | ≥1 to publish (3 for rentals); P24 caps floor plans at 5 | Keep one-photo onboarding; coach nudges to 10+ |
| Rental: lease period, available-from | **Required** | Required for rentals |

### Filters — adopt vs drop (P2P, anonymous, intros only)

| Portal filter | TrustSquare |
|---|---|
| Price min/max, Property type, Beds (1+…5+), Baths, Parking/garages | **Adopt** — all map to fields above |
| Erf size m², Floor size m² (preset bands) ⚠ | **Adopt** |
| Suburb / province | **Adopt** → existing city/area model |
| Pet friendly · Garden · Pool · Furnished (rentals) ⚠ | **Adopt** as toggles |
| Security estate / cluster ⚠ | **Adopt** → `lifestyle_tag` facet |
| On Show | **Drop** — no open houses pre-intro; remap to Request intro |
| Repossessions · Auctions · Bank-assisted | **Drop** (auctions parked platform-wide) |
| Retirement / New developments | **Defer** — density decision, not schema |
| Agency / agent / "list with an agent" | **Drop** — anonymous sellers (agency layer stays invisible as credential, not filter) |
| Bond calculator · finance-from · home-loan referral (ooba/BetterBond) | **Drop** — we are not a finance house |
| Promoted / HD Media / Featured badges | **Remap** → Trust-tier badge + fair-price chip (never paid prominence) |

---

## Part C — Onboarding: identify → draft → agree per section → attest

Reuses the Cars C1–C4 gates unchanged:

- **C1 Capture.** One-photo onboarding stays. Vision draft proposes `property_type`, `property_style`, room counts, obvious exterior features from photos — proposal only.
- **C2 Draft.** No free deterministic source for sizes/costs at launch → all values flagged `unconfirmed` until the seller edits/confirms (→ `seller_entered`). Note: **Lightstone covers property too** (PropData's lookup pulls erf number, sectional scheme, coordinates from it) — the Cars Part D/F provider work extends here later with the same deliver-then-charge 2T pattern (deeds-verified erf/floor size + valuation = "Lightstone-Verified" property badge). Not in this brief's scope; free `area_guide` comps already serve Property fair-price.
- **C3 Section-level confirm.** Key Facts · Rooms · Exterior · Building · Security & Policies — confirm per section, never 20 ticks.
- **C4 Attestation.** Same single liability checkbox + `attested_at/email` + confirmation map. Zeros are attested too ("0 garages" is a representation).

Publish floor (matches the portals' minimum, minus address): type + suburb + price + description + 1 photo + room counts (with explicit zeros).

---

## Soft AI guidance implications (free Advert Coach — guidance, never enforcement)

Fields and phrasings the coach should nudge toward, ranked by observed conversion/trust value:

1. **"Add erf size and floor size"** — the portals literally call these *quality fields* that make listings rank and filter better; a size-less listing is invisible to size-filtered searches.
2. **"State the levy and rates & taxes if you know them"** — SA buyers' biggest hidden-cost anxiety; honest numbers pre-empt intro-stage fallout. Coach must add: *only if known — never estimate* (portal rule: no placeholder values).
3. **"Describe the flow and the lifestyle, not a room inventory"** — PropData's own description guidance; ≥250 characters; the structured panel already carries the counts.
4. **Anonymity scrub** — portals block listings with contact details in the description; for us it's doubly load-bearing: coach flags names, phone numbers, street addresses, complex names and estate-identifying photos *before* publish.
5. **Photo depth** — benchmark listing carried 40 photos; nudge toward 10+ with front elevation as lead, then living areas → kitchen → bedrooms → garden/security.
6. **Explicit pet policy and security features** — both portals surface these as first-class facts; they are also the two facts buyers most often ask first in an intro.
7. **Headline discipline** — <100 chars, sentence case, one "!" max (portals strip shouty punctuation silently).
8. **Zeros beat blanks** — "no garage, 2 open parkings" reads honest; blank reads evasive. The coach can phrase this positively.

---

*v1.0 — benchmarked vs Property24 (P24-116534163 North Riding + site nav/search) and Private Property (T5424747 Lenham + Phoenix results page), with the PropData Manage residential-listing schema as the mandatory/optional ground truth. Filter rows marked ⚠ are snippet-sourced. Architect sign-off required before implementation.*
