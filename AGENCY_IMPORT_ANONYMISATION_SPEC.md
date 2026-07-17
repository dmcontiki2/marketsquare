# Agency Import — Anonymisation Pass (functional spec)
**Prepared for David · 7 July 2026 · status: spec, not yet built**

## Why this exists
TrustSquare's whole model is anonymity: a listing shows **no identifying detail until a buyer pays for an introduction and the seller accepts**. That is how we monetise agencies. But an agency's existing adverts (their website, Property24, their CRM export) are the *opposite* of anonymous — they carry the agent's name, phone, "call our office", agency branding, watermarked photos, for-sale boards, and sometimes the street number.

If we import those raw, we (a) break the anonymous-until-intro model and (b) let a buyer just phone the agent directly and skip the intro fee. **So import must anonymise before anything can go live.** The current `/agencies/{id}/import` endpoint only *stores* the advert as a draft — it does not clean it yet. This spec is that missing pass.

## The pipeline
`Agency feed → import → ANONYMISE → draft (agent reviews) → publish`
Nothing is ever auto-published. Everything lands as a **draft the agent confirms**, and anything we can't confidently clean is **held for manual review**, not shown to buyers.

## 1 · Text pass  (quick — reuses the AI coach)
- **Hard strip (regex):** phone numbers (all SA + international formats), emails, URLs/handles, street number + street name. Keep suburb / area only.
- **AI rewrite:** run the title + description through the existing listing-AI with an "anonymise" instruction — remove agent names, agency names, "contact/call/WhatsApp/viewing by appointment with…", office references, and any identifying phrasing; **keep** price, beds/baths/erf, condition, suburb, and the genuine selling points. Return clean copy.
- **Structured fields:** keep price, beds, baths, garages, floor/erf size, suburb, area, prop_type. Drop any direct-contact field. Area, never full address.

## 2 · Photo pass  (harder — reuses the vision stack)
- **Vision detect + redact:** contact overlays / phone-number bars, agency logos & boards, "For Sale by <Agency>" signage in the shot, watermarks, number plates, and visible house numbers.
- Redaction = blur or crop the offending region; if the whole image is a branded flyer, reject it and ask for a clean photo.
- **Confidence gate:** anything below a confidence threshold is flagged for **manual review** rather than auto-passed. First N imports per new agency get an ops spot-check.

## 3 · Review gate
- Cleaned advert shows the agent a **before/after** ("we removed a phone number and an agency board") so they trust it and can fix anything.
- Agent confirms → it publishes under *their* seller identity (anonymous), counting against their listing cap.

## Reuse (low new build)
- Text: the AI listing coach already exists.
- Photos: the vision auto-orient / draft-from-photo stack already exists.
- Draft + review + publish flow already exists.
The new work is the **orchestration** (run each imported advert through both passes) and the **photo redaction confidence/flagging**.

## Phasing
- **Phase A (now-ish):** text pass end-to-end. High value, low effort — makes text imports safe immediately.
- **Phase B:** photo redaction + confidence flagging. The harder piece; worth scoping the "blur vs crop vs reject" aggressiveness with you.

## Decisions for David
1. **Photo aggressiveness:** blur offending regions, crop them, or reject the photo and request a clean one? (Recommend: redact if localised, reject if the whole image is a flyer.)
2. **Manual-review threshold:** spot-check the first N per agency, or every advert until an agency is trusted? (Recommend: first N, then trust.)
3. **Agency brand:** fully hidden for anonymity (recommend), or a generic non-identifying label like "Listed via a verified agency" with no name?

*End spec.*


## §4 — Structured field mapping (IMPORT-SYNC-1, 17 Jul 2026)

Superseded: the §1 note "keep price, beds, baths, garages, floor/erf size, suburb,
area, prop_type" — now implemented AND extended to the full guided-sell-flow schema.
Each advert dict may carry, and agency_import now persists:

- All categories: listing_type, price (+derived price_num), suburb, area
- Property: prop_type, beds, baths, garages, floor_area, erf_size,
  rental_status + available_from (rentals ONLY — dropped on sales, RENT-GATE-1 parity;
  invalid values dropped, import continues)
- Tutors: subject, level, mode
- Services: service_class, service_type, availability
- Cars: make, model, variant, vehicle_year, mileage_km, transmission, fuel_type,
  body_type, colour, vehicle_specs (dict or JSON string)

Rows are stamped import_source='agency_import'.

## §5 — Publish quality gate (IMPORT-QUALITY-1, 17 Jul 2026)

Imported drafts face the same 50-point bar the wizard enforces client-side,
scored server-side in publish_listing from stored columns: photos ≈40
(10 first + 8 each), category required fields + 15-word description ≈50,
price 6 (POA scores 0), suburb/area 4. Below 50 → HTTP 422 with a fix list.
No superuser bypass (quality gate, not auth gate). Wizard-created listings
are unaffected (already gated in-app).
