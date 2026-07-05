# Trips, Tours & Stays — Listing Display & Structured Facts
**Build Brief v1.0 · 3 July 2026 · benchmarked vs GetYourGuide + Viator (+ SafariBookings for the African context)**
*Companion to `CARS_LISTING_AND_VERIFICATION_BRIEF.md` (v1.1) — same integrity model, same reuse rules. Architect sign-off before implementation.*

---

## Core principle — and the one strategic finding

Same rule as Cars/Property: TrustSquare asserts no facts; the seller attests every claim (duration, inclusions, group size, min age).

The strategic finding: GetYourGuide and Viator are **booking engines** — but **SafariBookings, the largest African-safari marketplace (18k+ tours, 3k+ operators), is a quote-request marketplace**. Its CTA is "Request a Quote — your request will be sent directly to the operator", and every page carries the disclaimer *"This tour is offered by [operator], not SafariBookings."* That is structurally the TrustSquare intro model, operating at scale, in our launch category. **Adopt GYG/Viator's information architecture (the best-tested listing format in the industry) with SafariBookings' transaction posture (intros, platform holds no inventory).**

---

## How this was benchmarked (sourcing note)

- **GetYourGuide supplier docs, fetched in full**: *Activity Quality Guidelines* (title/content/image/pricing/policy rules), *Describing your product* (the exact field-by-field product-creation form), *10 Steps to Optimize Your Tours* (conversion guidance + stats).
- **Viator**: *Product Acceptance Criteria & Quality Standards* article fetched (operatorresources.viator.com); PDP field list from docs.viator.com and partner-resources **search snippets** (title, images, description, inclusions, exclusions, additionalInfo, cancellationPolicy, languageGuides, itinerary, ticketInfo, logistics/start-end points). ⚠ Viator's consumer pages block fetching — consumer-page section names are snippet-sourced.
- **SafariBookings**: live tour page fetched in full (t108, 3-Day Classic Kruger) — complete page anatomy.
- ⚠ GetYourGuide consumer activity pages also block fetching; their section labels come from GYG's own supplier docs (which name the public sections) + snippets. No field names are fabricated.

---

## Decisions proposed (this brief)

1. **Adopt** the GYG/Viator listing anatomy: quick-facts chips → Highlights → Full description → Includes/Excludes → Itinerary → Meeting/Area → Know before you go → Cancellation terms.
2. **Adopt** SafariBookings' **Tour Features icon grid** for the quick-facts row — it is the best at-a-glance encoding for African trips (comfort tier · private/shared · group max · min age · customizable · start-any-day).
3. **Adopt** the multi-day extension (SafariBookings): day-by-day itinerary + per-night accommodation & meals table. Single-day experiences render the simple GYG shape; `days > 1` unlocks the safari shape.
4. **Drop** everything booking-engine: availability calendars, cut-off times, instant confirmation, mobile tickets, skip-the-line, cart/checkout, "reserve now pay later". Intros only.
5. **Remap** "free cancellation" filters → a seller-stated **cancellation & weather policy** displayed as information (buyers transact off-platform; the policy is part of the seller's representations).
6. **Meeting point stays suburb/area-level pre-intro** (anonymity); exact meeting point + operator contact are intro-handover payload, mirroring Property's street-address rule.

---

## Part A — Listing page layout (benchmarked anatomy)

**GetYourGuide activity page** (per GYG's own supplier docs + snippets ⚠): title (location-first) · rating · gallery · "About this activity" chip list (duration · live guide/languages · pickup · wheelchair etc.) · **Highlights** (3–5 bullets) · **Full description** · **Includes / Not included** · **Not suitable for** · **Meeting point** · **Important information / Know before you go** · cancellation terms · reviews.

**Viator product page** (API PDP sections, snippet-sourced ⚠): Overview + photos · **What's Included** (inclusions/exclusions) · **Meeting and Pickup** (logistics: start/end points) · **What to Expect** (rendered from the structured `itinerary` object) · **Additional Info** (accessibility, physical difficulty) · **Cancellation Policy** · reviews · Q&A.

**SafariBookings tour page** (observed live, t108): title · operator card (rating · review count · founded · office country) · price pp with currency toggle (USD/ZAR) · **Request a Quote** CTA · tab nav **Overview / Day by Day / Rates / Inclusions / Getting There / Offered By** · **Route table** (Start → Day 1–2 Kruger NP → End) · **Tour Features icon grid**: *Mid-range tour (lodges) · Shared tour, max 6 per vehicle · Can start any day · Cannot be customized · Not for single travelers (min 2) · Minimum age 6* · **Activities & Transportation** (game drives · vehicle types · airport transfer included · book-own-flights note) · **Accommodation & Meals** day-by-day table (lodge name + tier + meals) · disclaimer block · reviews.

**TrustSquare target:** reuse the Adventures gallery (already the WeBuyCars pattern per Cars brief Part A). Right rail: title · price-from + basis · area + badges (Trust tier) · **6-chip quick-facts row (Duration · Private/Shared + group max · Comfort tier · Languages · Min age · Fitness)** · Request-intro CTA. Below: Highlights → Description → Includes/Excludes (two-column) → Itinerary (day-by-day table when multi-day) → Area & meeting info (suburb-level) → Know before you go → Seller's cancellation & weather terms.

---

## Part B — Canonical field schema + filters

### Field model (listing record)

**Identity**
`listing_ref` · `title` (location-first formula, ≤60 chars) · `category_subtype` (Day tour / Multi-day tour & safari / Experience & class / Ticket & attraction / Stay) · `location_tags[]` (areas + points of interest) · `keywords[]` (≤15, GYG cap)

**Logistics (deterministic — attest)**
`duration_hours` **or** `days` + `nights` · `start_times` / `operating_window` · `seasonality_months` · `meeting_type` (meet-on-site / pickup offered) · `meeting_area_public` (suburb-level) · `meeting_point_exact` (**private — intro handover**) · `languages[]` · `private_or_shared` · `group_size_max` · `min_participants_to_run` · `customizable` (Y/N) · `start_any_day` (Y/N)

**Pricing**
`price_from_pp` · `price_basis` (per person / per group / per vehicle) · `child_pricing_note` · `rates_by_party_size` (optional table, SafariBookings pattern)

**Suitability**
`min_age` · `max_age_note` · `fitness_level` (Easy / Moderate / Strenuous — Viator's "physical difficulty") · `wheelchair_accessible` (Y/N) · `not_suitable_for[]` (pregnancy, back problems, vertigo…)

**Inclusions (the trust core)**
`includes[]` · `excludes[]` · `food_drinks` (meals provided + dietary options) · `transport` (type + pickup included Y/N + airport transfer Y/N) · `guide_type` (guide / driver only / host-greeter / nobody — GYG's exact enum)

**Preparation**
`what_to_bring[]` · `not_allowed[]` · `pet_policy` · `documents_required` (passport/permits) · `insurance_required` (Y/N + note) · `weather_policy`

**Multi-day extension (SafariBookings shape; renders when `days > 1`)**
`itinerary[]` (per day: title · description · park/area) · `accommodation[]` (per night: name-or-type + `comfort_tier` Budget / Mid-range / Luxury + meals B/L/D) · `route_summary` (start → stops → end)

**Policy**
`cancellation_policy` (structured presets + free note — must not contradict itself; GYG enforces consistency, we coach it)

### Mandatory vs optional

| Field | GYG / Viator | TrustSquare |
|---|---|---|
| Title, category, location tags | **Required** | **Required** |
| Short description (2–3 sentences) + full description | **Required** (GYG: original copy, no contact details, no price talk in title) | Required; anonymity scrub in prose |
| Duration | Required (GYG title conventions: Half-Day = 4–7 h, Full-Day = 8 h+) | **Required** |
| Includes / excludes | Required (Viator acceptance) | **Required** — min 1 each, coach nudges 3+3 |
| Meeting point w/ address | Required (Viator) | **Area required; exact point private** |
| Photos | Viator min 3; GYG first-4 quality bar | Keep one-photo onboarding; coach nudges 7–10+ |
| Cancellation policy | Required, must match free text | Required as *stated seller terms* (info, not engine) |
| Physical difficulty / min age / not-suitable-for | Required-ish (acceptance criteria) | Required for Strenuous/adventure sub-types; else optional |
| Languages, guide type, food, transport | Structured prompts in GYG form | Optional, coach-nudged |
| Itinerary + accommodation table | Optional (GYG visual itinerary; SafariBookings core) | Required when `days > 1` |
| Availability calendar, cut-offs | Required (booking engines) | **Dropped** |

### Filters — adopt vs drop (intros, not bookings)

| GYG / Viator / SafariBookings filter | TrustSquare |
|---|---|
| Category/theme · Duration band · Price band | **Adopt** |
| Private vs shared/group · Group size | **Adopt** (SafariBookings: Private / Group is a top-level facet) |
| Comfort tier (Budget / Mid-range / Luxury / Luxury+) | **Adopt** for multi-day (SafariBookings's primary facet) |
| Languages · Family-friendly / min age · Wheelchair | **Adopt** |
| Trip type (safari / walking / photo / honeymoon / birding / camping / fly-in / self-drive…) | **Adopt** as tags — mirrors SafariBookings type taxonomy |
| Start location / "Getting there" | **Adopt** at city/area level only |
| Rating / review count | **Remap** → Trust-tier badge (no review corpus at launch; post-intro feedback feeds Trust Score) |
| Free cancellation | **Remap** → "states cancellation terms" quality chip |
| Instant confirmation · Mobile ticket · Skip-the-line · Deals | **Drop** — booking-engine concepts |
| "Likely to sell out" · Bestseller ranks | **Drop** (engagement theatre; contradicts flat-status ethos) |
| Operator name filter | **Drop** — anonymous sellers |

---

## Part C — What the seller guidelines say converts (distilled, with sources)

1. **Title formula** — *Location: Type of Experience + Duration + one USP*, ≤60 chars, no ALL CAPS, no pricing in title (GYG quality guidelines; e.g. "New York: Private 2-Hour Walking Tour of Dumbo with Free Cocktail").
2. **Photos** — Viator's own data: **10 photos ≈ 160% more bookings than 1**; 6+ converts ~40% better than the minimum 3 (partner guides ⚠); GYG: first 4 photos carry the weight, authentic beats stock, no watermarks/text overlays.
3. **Reviews** — GYG: moving 3→4 stars ≈ **+40% conversion**; 15+ reviews ≈ up to **10×** performance. (For us: post-intro feedback → Trust Score is the equivalent flywheel.)
4. **Short description is the hook** — 2–3 active sentences; most buyers never read the full description (GYG).
5. **Highlights** — 3–5 bullets, each starting with a verb (See / Explore / Taste) (GYG form guidance).
6. **Includes/excludes in plain nouns** — "Guide", not "A friendly and knowledgeable guide" (GYG's literal example); operators get burned by omitted exclusions.
7. **Meeting instructions are the #1 low-review cause** — one missing word ("inside the bar") costs a star (GYG optimization guide). For TrustSquare this moves to the intro-handover payload — coach it there.
8. **Visual itinerary ≈ +25% bookings** (GYG) — justifies the day-by-day table as a first-class component.
9. **Small-group honesty** — GYG only permits "Small Group" for ≤10 (general), ≤15 (day trips), ≤18 (multi-day). Adopt as coach vocabulary rules.
10. **No direct contact details in listing text** (both platforms hard-block) — aligned with our anonymity scrub; ours extends to operator names and branded vehicles in photos.

## Part D — Verification options (lighter than Cars; open item)

No Lightstone equivalent exists for experiences. Verifiable credentials in ZA: CIPC company registration · provincial tourist-guide registration · SATSA membership · public-liability insurance certificate · operating licence for transfers. Proposed: attested document upload → AI plausibility check → "Credentialed operator" badge feeding Trust Score (same deliver-then-charge pattern if it ever costs money). Not scoped here — flag for the agency-layer work, where tour/travel companies are already the category aggregator.

---

## Soft AI guidance implications (free Advert Coach — guidance, never enforcement)

1. **Title coach** — rewrite toward *Area: Experience + Duration + USP*; warn on ALL CAPS, prices in title, >60 chars, and "Small Group" claims that exceed the honesty thresholds above.
2. **"State duration, group max and min age"** — the three chips buyers filter on first; SafariBookings surfaces all three as icons.
3. **Includes/excludes completeness** — nudge to ≥3 + ≥3 plain-noun bullets; specifically prompt the classic omissions: park/entrance fees, meals, drinks, transfers, tips.
4. **"Say who runs it"** without identity leaks — guide vs driver-only vs self-guided (GYG's guide-type enum) tells buyers what they're paying for; coach flags operator names/brands in text and photos.
5. **Fitness & suitability honesty** — Easy/Moderate/Strenuous + not-suitable-for list; over-claiming ease is the category's classic dispute source.
6. **Seasonality** — nudge a best-months note (African category norm; SafariBookings guides lead with it).
7. **Multi-day: fill the per-night table** — accommodation tier + meals per day; the single highest-information-density block in the safari format.
8. **What to bring + weather policy** — cheap to write, prevents the worst intro-stage disappointments.
9. **Photo sequence** — lead with the peak moment (the view, the animal, the plate), then vehicle/venue, then people enjoying it; 7–10+ authentic photos, no stock, no watermarks.
10. **Cancellation terms stated plainly** — one preset + one sentence; coach checks the free text doesn't contradict the preset (GYG's consistency rule, softened to a nudge).

---

*v1.0 — benchmarked vs GetYourGuide (Activity Quality Guidelines, "Describing your product" product-form docs, 10-step optimization guide — all fetched), Viator (product acceptance/quality standards article fetched; PDP schema + consumer sections snippet-sourced ⚠), and SafariBookings (t108 Kruger tour page fetched live). Consumer pages of GYG/Viator block fetching — noted where used. Architect sign-off required before implementation.*
