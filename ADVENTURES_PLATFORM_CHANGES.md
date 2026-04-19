# Adventures — Platform-Wide Change Notice
**Version 1.1 · 18 April 2026**
*Read this document when beginning Adventures implementation work in any project.*
*This notice is the authoritative record of all platform-level decisions made during Adventures design.*
*When PRINCIPLE_REQUIREMENTS.md is next regenerated from the Codex, incorporate all items below.*

---

## What Changed and Why

The Adventures category (subcategories: Accommodation and Experiences) introduces five platform-level departures from existing behaviour. These are not bugs or gaps — they are deliberate decisions made by David on 18 April 2026. Every agent and every project must implement them consistently.

---

## Change 1 · Trust Score — No Penalty Rule for Adventures

**Existing rule (A3):** Tutors and Services use Soft Queue. If a seller ignores an introduction, Trust Score −3 applies.

**Adventures exception:** Adventures uses Soft Queue with **no Trust Score penalty** for ignoring or declining an introduction.

**Why:** Accommodation operators have legitimate seasonal constraints, blackout dates, and capacity limits. Penalising non-response conflates unavailability with bad behaviour. The penalty rule is designed for service providers who are always theoretically available — it does not translate to accommodation and experiences.

**Where this must be implemented:**

- **BEA** — `intros/accept` and `intros/decline` logic must branch on category prefix. If `category` starts with `adventures_`, skip the −3 penalty calculation entirely.
- **FEA** — Trust Score penalty messaging ("Seller ignored your request") must not appear for Adventures listings.
- **Admin Tool** — Onboard wizard trust explainer copy must not reference the ignore penalty for Adventures sellers.
- **PRINCIPLE_REQUIREMENTS.md** — A3 must be updated to document this exception. Mark as: *Adventures exception — 18 Apr 2026.*

---

## Change 2 · Tuppence — Standard 1T Confirmed for Adventures

**Decision:** 1 Tuppence ($2) applies to Adventures introductions. No Adventures-specific pricing tier. This is final and intentional.

**Why it matters:** This was an open question because a $2 intro fee on a lodge booking at R5,000/night could seem incongruously cheap. The decision is that the model's disruption to commission-based booking platforms (15–25% per booking) is the value proposition — MarketSquare earns from volume across all categories, not from a percentage of any single transaction.

**Where this must be confirmed:**

- **BEA** — Tuppence deduction on `/intros/accept` already uses the 1T standard. No change needed — just confirm Adventures listings are not accidentally excluded from the deduction flow.
- **FEA** — Any "how pricing works" copy for Adventures listings must state 1T = $2 flat fee, not a booking percentage.
- **No change to A1.** The Tuppence principle is unchanged.

---

## Change 3 · Location Field — Opportunity Type Taxonomy Replaces Suburb

**Existing model:** All listings have a `suburb` field, populated from the BEA geo hierarchy (`geo_suburbs` table). Suburb is a geographic unit within a city.

**Adventures model:** Adventures listings do not map to suburbs. Their location is described by two new fixed-value fields:

| Field | Purpose | Example values |
|---|---|---|
| `activity_type` | What the seller offers — the primary filter | `hiking_and_trails`, `water_sports`, `wildlife_and_birding` |
| `environment_type` | Where it happens — geographic/terrain context | `bush_and_wildlife`, `coastal_and_beach`, `mountain_and_highlands` |

**Full taxonomy** is defined in `ADVENTURES_PIPELINE_PLAN.md` Section 5e. These are fixed strings — never freetext. The controlled vocabulary is what makes filter searching reliable on the buyer platform.

**Where this must be implemented:**

- **BEA** — Two new columns on the `listings` table: `activity_type TEXT` and `environment_type TEXT`. Nullable for non-Adventures categories. New filter params on `GET /listings`: `?activity_type=X` and `?environment_type=Y`. Both are optional, combinable.
- **FEA** — Two new filter dropdowns in the Adventures browse section. Dropdowns are populated from the fixed taxonomy (hardcoded in the FEA data layer — these values change only via a controlled update, not dynamically from the DB). Suburb filter is hidden for Adventures listings.
- **Admin Tool** — Onboard wizard for Adventures skips the suburb autocomplete step. Replaces it with two dropdowns: Environment Type and Activity Type. These pre-fill the magic link `suburb` param with the activity type value (for CityLauncher compatibility) and write `environment_type` separately.
- **CityLauncher** — `prospects.db` gets a new `environment_type` column. The scraper assigns both taxonomy values during enrichment. `suburb` column stores `activity_type` value for Adventures records (reuses existing column — no schema change to the suburb column itself).
- **PRINCIPLE_REQUIREMENTS.md** — New D8 section for Adventures principles. Document the taxonomy and the suburb field substitution.

---

## Change 4 · Multi-Property Paste-Assist Onboard (Admin Tool)

**Context:** Chain operators (hotels, safari lodge groups) will receive a single outreach email covering all their properties scraped by CityLauncher. Each property is a separate prospect record in `prospects.db` and should become a separate listing in the BEA (for wider buyer search coverage).

**New onboard flow for chain operators:**

- Magic link for chain operators includes `?multi=1` param
- Admin Tool detects `multi=1` and presents a paste-assist screen
- Operator can paste a list of property names/locations; the wizard generates individual magic links for each, pre-filled with the operator's email and category
- Each property completes as a separate BEA listing
- The standard single-property magic link flow is unchanged

**Where this must be implemented:**

- **Admin Tool** — New `?multi=1` param handling. Paste-assist UI screen. Individual magic link generation per pasted property.
- **CityLauncher** — Email templates for chain operators reference the paste-assist flow in the CTA. Template `accommodation_chain.html` and `experiences_chain.html` include a "List all your properties in one go" link with `?multi=1`.
- **BEA** — No schema change needed. Each pasted property creates a standard listing via the existing POST /listings flow.

---

## Change 5 · Trust Score — Certification Uplift for Adventures

**Decision (18 Apr 2026):** Adventures sellers who upload verifiable certification earn a **Trust Score bonus** that increases their listing visibility. This is a new positive Trust Score pathway — the first category where credentials actively lift a seller's score rather than simply protecting it from decline.

**Why:** Adventures operators deal in physical safety and quality assurance in a way that other categories do not. A certified mountain guide, a TGCSA-graded lodge, or a SATSA-registered tour operator represents a meaningfully lower risk to a buyer than an uncredentialled equivalent. Rewarding certification with visibility aligns the platform's incentives with buyer confidence — and gives MarketSquare a differentiated trust signal that OTA platforms do not surface in the same way.

**Certification types and proposed Trust Score bonus values** (exact values to be confirmed in Codex):

| Certification type | Applies to | Proposed bonus |
|---|---|---|
| TGCSA grading (1–5 star) | Accommodation | +5 per star (max +25 for 5-star) |
| SATSA membership | Accommodation + Experiences | +10 |
| FEDHASA membership | Accommodation | +8 |
| SA Mountain Club / UIAA guide cert | Experiences (hiking, climbing) | +12 |
| SAMSA / PADI / NAUI dive certification | Experiences (water sports, scuba) | +12 |
| Registered tourism guide (CATHSSETA) | Experiences (tours, cultural) | +10 |
| Liquor licence (WSET or national) | Experiences (food, wine) | +6 |
| First aid / wilderness first aid cert | Experiences (adventure/outdoor) | +5 |
| SABOA / PDP operator licence | Experiences (tours, transport) | +8 |

**How verification works:**
- Seller uploads a photo or PDF of the certificate during onboarding or from their seller profile
- Certificate is marked `pending_review` — the Trust Score bonus is **not applied until reviewed**
- David (or a designated admin) reviews and approves via the Admin Tool
- On approval, BEA applies the bonus to the seller's Trust Score and the listing re-ranks
- If a certificate expires or is revoked, the bonus is withdrawn and Trust Score adjusts accordingly
- Certificates are stored as metadata on the listing — never exposed to buyers directly (A2 anonymity still applies until introduction is accepted)

**Important — this is an Adventures-specific mechanism. It does not apply to other categories.** Do not extend certification uplift to Estate Agents, Tutors, Services, or Casuals without a separate council decision.

**Where this must be implemented:**

- **BEA** — New `certifications` table: `{ id, listing_id, cert_type, cert_value, status (pending/approved/expired), reviewed_by, reviewed_at, bonus_points }`. Trust Score calculation must sum approved certification bonuses on top of the base score. New endpoint: `POST /listings/{id}/certifications` (upload). `PATCH /listings/{id}/certifications/{cert_id}` (admin approve/reject).
- **FEA** — Certified listings display a **certification badge** on the listing card (e.g. a shield icon with a star count or cert type abbreviation). Badge is visible to buyers before introduction. This is an exception to the anonymity rule — the badge signals verified quality without revealing identity. Badge tooltip: "Verified credentials on file."
- **Admin Tool** — Certification review queue: list of `pending_review` certificates with upload preview, approve/reject buttons, and expiry date field. Notifications when new certs are submitted.
- **Admin Tool onboard wizard** — Certification upload step added to Adventures onboarding flow. Optional at onboarding — can be added later from seller profile. Copy: "Upload your certifications to unlock a higher Trust Score and appear higher in search results."
- **PRINCIPLE_REQUIREMENTS.md** — A5 must be updated to note the certification uplift extension for Adventures. Document bonus ranges and Codex confirmation requirement.

---

## Change 6 · EULA Acceptance Gate — At Onboarding, Not At Email Response

**Decision (18 Apr 2026):** The EULA must be presented and explicitly accepted by the prospect **at the moment they click the magic link and commit to going live** — not assumed from the email response. Specifically: EULA acceptance is the first screen presented after the prospect clicks "Go Live" or the magic link, and before any registration or listing data is written.

**Why:** Adventures is photo-heavy. The platform's rights over uploaded images — how they can be displayed, shared, cached, and used in platform marketing — need to be explicitly agreed to, not buried in email boilerplate or assumed from an outbound click. This also protects the platform legally: a timestamped, IP-logged EULA acceptance at the point of registration is a far stronger consent record than an email click event.

**This is not Adventures-only.** The EULA gate applies to **all categories** going forward. Adventures is the trigger for implementing it properly because of the photo-rights exposure, but the mechanism must be universal.

**The exact gate position in the onboarding flow:**

```
Prospect clicks magic link
        ↓
Admin Tool loads pre-filled onboard screen
        ↓
  ┌─────────────────────────────────┐
  │  EULA ACCEPTANCE SCREEN         │  ← NEW — must complete before any further step
  │  "Before you list, please read  │
  │   and accept our terms."        │
  │  [ View full terms ]            │
  │  [ ✓ I agree — Continue ]       │
  └─────────────────────────────────┘
        ↓
Registration begins (name, email confirmed)
        ↓
Listing details (category, photos, title, price)
        ↓
Go Live → POST /listings → BEA creates record
```

**EULA content must cover (at minimum for Adventures):**
- Platform usage rights for uploaded photos and media — MarketSquare may display, cache, and use listing photos for platform promotion
- Seller responsibility for accuracy of certification claims
- Introduction model terms (Soft Queue, 1T fee, 48hr window)
- No penalty for declining (Adventures exception)
- Data handling and privacy

**Where this must be implemented:**

- **Admin Tool** — EULA screen inserted as Step 0 of the onboarding wizard. Cannot be skipped. "Continue" button is disabled until the checkbox is ticked. EULA version number is recorded.
- **BEA** — New field on `users` / `listings` table: `eula_accepted_at DATETIME`, `eula_version TEXT`. `POST /listings` must reject requests where `eula_accepted_at` is null. BEA records the acceptance timestamp and version at the point the seller submits.
- **FEA** — If a seller somehow reaches the publish flow without a recorded EULA acceptance (e.g. legacy account), they are gated and prompted before their next listing goes live.
- **All categories** — The EULA gate is universal. Existing onboarded sellers are not retroactively gated (they accepted implicitly), but all new onboards from this point forward must pass the gate.
- **PRINCIPLE_REQUIREMENTS.md** — New principle under Part A or Part D: "EULA acceptance is a hard gate before any listing is created. The acceptance timestamp and version are recorded in the BEA. This applies to all categories."

---

## Implementation Priority Order

Work should be sequenced so that BEA changes land first (they are the dependency for everything else):

1. **BEA** — schema (`activity_type`, `environment_type`, `certifications` table, `eula_accepted_at`/`eula_version` fields), intro model branch (no Adventures penalty), filter params, Trust Score certification sum
2. **CityLauncher** — DB migration (add `environment_type` to `prospects.db`), scraper taxonomy tagging, email templates
3. **Admin Tool** — EULA gate (Step 0 of wizard, all categories), Adventures onboard fields (environment/activity dropdowns, cert upload step), paste-assist multi-property flow, certification review queue
4. **FEA** — Adventures browse section, filter dropdowns, Trust Score penalty messaging suppression, certification badge on listing cards
5. **PRINCIPLE_REQUIREMENTS.md** — Regenerate from Codex incorporating A3 exception, A5 certification uplift, D7 update, new D8, EULA gate principle

---

## Codex Update Required

The following items must be incorporated into `Solar_Council_Codex_v4_4.docx` (or its successor) at the next council review session. Until the Codex is updated, this document and `ADVENTURES_PIPELINE_PLAN.md` are the authoritative sources.

- A3 exception: Adventures Soft Queue, no Trust penalty for ignore/decline
- A5 extension: Certification uplift mechanism for Adventures — bonus values to be confirmed
- A7 or new A8: Adventures category introduction (subcategories, intro model, taxonomy, certification, EULA)
- New EULA principle: hard gate before listing creation, all categories, timestamped and versioned
- D7 update: Add `adventures_accommodation`, `adventures_experiences` to category list
- New D8: Adventures pipeline principles

*Flag to David when Codex update session is due.*

---

*End of ADVENTURES_PLATFORM_CHANGES.md v1.1*
*This document does not replace PRINCIPLE_REQUIREMENTS.md — it supplements it until the Codex is updated.*
*Place a copy of this file in: CityLauncher/, MarketSquare/, and AdminTool/ project roots.*
