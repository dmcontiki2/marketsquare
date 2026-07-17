# MarketSquare Agency Import Guide
*Give this to the agency's IT person or systems administrator. One-time setup: ±1 hour.*

## How it works
1. TrustSquare invites your agents (each gets a sign-in link). Every advert you send
   must carry the `agent_email` of an invited agent — unmatched emails are skipped.
2. You map your system's export to the JSON below (once).
3. POST it to `https://trustsquare.co/agencies/{your_id}/import` with your API key.
4. You get a per-advert report back: imported / skipped / needs_review, with reasons.
5. Adverts land as DRAFTS under each agent. Publishing requires a 50/100 quality
   score (photos + complete fields) — thin rows are blocked with a fix list, so a
   bad mapping can never put a weak advert in front of buyers.

## Payload
```json
{
  "api_key": "tsq_agency_...",
  "adverts": [{
    "agent_email": "agent@youragency.co.za",     // REQUIRED, must be invited
    "category": "Property",                       // Property | Cars | Tutors | Services | Collectors | Adventures
    "title": "...", "description": "...",         // will be anonymised (phones/emails stripped, AI-rewritten)
    "price": "R 2 450 000",                       // free text; digits are parsed for filtering
    "city": "Pretoria", "suburb": "Elarduspark", "area": "Pretoria East",
    "photos": ["https://...jpg"],                 // scanned; branded/flyer images are held, never stored

    // Property
    "listing_type": "For Sale",                   // or "To Rent"
    "prop_type": "House", "beds": 3, "baths": 2, "garages": 2,
    "floor_area": 180, "erf_size": 800,
    "rental_status": "available",                 // rentals only: available | reserved | occupied
    "available_from": "2026-09-01",               // rentals only, ISO date

    // Cars
    "make": "Toyota", "model": "Hilux", "variant": "2.8 GD-6",
    "vehicle_year": 2019, "mileage_km": 98500,
    "transmission": "Automatic", "fuel_type": "Diesel",
    "body_type": "Double cab", "colour": "White",
    "vehicle_specs": {"engine_capacity_cc": 2755, "kilowatts_kw": 150},

    // Tutors: "subject", "level", "mode"
    // Services: "service_class", "service_type", "availability"
  }]
}
```

## Rules worth knowing
- Send only the fields that apply — missing optional fields are fine (but lower the
  quality score; the publish gate needs 50/100).
- Sale listings: rental fields are ignored by design.
- Contact details in titles/descriptions are stripped — MarketSquare introductions
  replace direct contact by design.
- Each agent has a listing cap; adverts over cap are skipped and reported.
- Re-running an import creates duplicates — send each advert once, or delete drafts first.

*Questions: support@trustsquare.co*
