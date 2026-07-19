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

## Step 0 — Bulk-onboard your agents (the roster)
Before adverts, send your people. One POST creates every agent's account, listing cap
AND their anonymous professional service profile — the profile MarketSquare shows to
private sellers and holiday searchers choosing an agent (Best Match ranked: 50%
listing quality + 50% trust score).

`POST https://trustsquare.co/agencies/{your_id}/agents/bulk` (same API key), JSON:
```json
{
  "vertical": "property",            // property | cars | travel — or per-agent
  "agents": [{
    "email": "ann@youragency.co.za", "name": "Ann Smith",
    "city": "Pretoria", "country": "ZA", "suburbs": "Waterkloof, Brooklyn",
    "years_experience": 12, "properties_sold": 240, "listing_cap": 10,
    "headline": "Waterkloof specialist — sectional title expert",
    "bio": "30+ words, anonymous — no names, no agency brand (we strip them anyway)",
    // property: "ppra_number", "ffc_year", "nqf_level" (4|5|6), "body_memberships"
    // cars:     "mira_number", "inspection_partner"
    // travel:   "asata_number", "iata_code", "cipc_number", "bonding_proof"
  }]
}
```
Credential claims land as **pending** — our ops team verifies each against the issuing
register before a single trust point is awarded. Until the gate credential is verified
(estate agents: **FFC** · car sales agents: **MIRA** · tour agents: **ASATA** + CIPC
submitted) the agent's service profile cannot go live. That verification IS the selling
point: your agents appear to prospects as *proven* professionals, ranked, with badges.

| Vertical | Gate (must verify) | Also scored | Leads come from |
|---|---|---|---|
| Estate agents | FFC | PPRA 15 · NQF4/5/6+ · prof. body | Private sellers in the Property sell flow |
| Car sales agents | MIRA dealer reg | Inspection partner | Private sellers in the Cars sell flow |
| Tour agents | ASATA (+ CIPC submitted) | IATA · bonding · insurance | Holiday searchers on the Adventures page |

Every accepted lead costs the agent 1 Tuppence — only on accept, replacing bought
leads, portal fees and cold calling. The prospect pays nothing.

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
