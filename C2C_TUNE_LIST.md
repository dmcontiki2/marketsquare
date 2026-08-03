# C2C One-Map — Tune List (pilot before 9-map rollout)
_Agreed David + Claude, 3 Aug 2026. Doctrine: clean ONE map (C2C), learn, then stamp all nine.
Rollout waits for (a) this list green, (b) David's iPhone pass, (c) Wed 5 Aug re-review outcome
(GetYourGuide/Viator → Vic Falls/Zanzibar/Luxor partner pins appear by themselves)._

## Agreed items
1. **Stop-coordinate audit** — every pin's lat/lng verified against the real place. Pins are the
   handoff to Google Maps; a wrong pin sends a traveller to the wrong hillside. (Highest value.)
2. **"🧭 Open in Google Maps" link in every stop popup** — one line in the popup builder;
   `https://www.google.com/maps/dir/?api=1&destination=<lat>,<lng>`. Navigate with Google,
   book with our 🎫 — completes the buy-on-arrival pattern.
3. **Rail legs: add real inflection waypoints** — not full OSM rail geometry (heavy, unnecessary
   for the ad stage); just enough real bends that the line never does anything geographically
   absurd. Honest "illustrative format" caption stays. Full geometry deferred to the xTuppence
   Feature stage, per-leg, where a paying planner actually navigates.
4. **Air arcs bend through their real hub** — e.g. Dar→Cairo via Addis Ababa (already a town
   label on the map). Solves David's red-flag-airspace concern (a naive arc crosses Sudan —
   exactly the corridor the reality audit calls unbookable) AND matches how the ticket actually
   routes. No further flight fidelity — stylised dashed arc is the universal convention.

5. **🏛️ Heritage Site layer** (David, 3 Aug) — filter wonders.json (300 sites, coords + LICENSED
   photos + descriptions already on board; 19 African) to sites within ~150 km of the route;
   pin with popup: photo, blurb, link. Deep link into the app's wonder page needs a small
   `?wonder=<id>` URL handler in ms.js — same pattern as the D7 `?listing=` question, one
   handler serves both. Strategic role: funnel mouth for the Heritage Suite Tour Planner (5T)
   + TP trips to reach the sites.
6. **🤝 Travel guides nearby** (David, 3 Aug) — same intro-pin machinery, typed `guide`:
   demo pins in the tune pass; real version queries live listings (guided_tours category)
   near the route so actual guide sellers self-populate onto maps as they onboard.

7. **English-only map labels** (David, 3 Aug) — OSM base tiles show each country's LOCAL names
   (Arabic in Egypt etc.), reading as a language switch. Fix: swap the tile layer to a
   no-labels basemap (CARTO light_nolabels / voyager_nolabels, free with attribution) and let
   our OWN ◉ town-label layer (already English, already ours) be the only text on the map.
   Calmer, branded, and future-proof: when the app adds languages, only our label layer
   translates — tiles never change. REFINED (David): our towns layer GROWS, not shrinks —
   a curated ~20-town context set per map (e.g. around Kimberley: Bloemfontein, Upington,
   Mafikeng) so travellers can gauge where they are relative to other cities, in English,
   our styling. Plus L.control.scale() (built-in scale bar) so "how far" has a ruler at every
   zoom; precise distances belong to the 🧭 Google Maps handoff (item 2).

## Standing observations feeding the list
- Partner widget photos render ONLY on the live origin (S4 CORS + widget licence) — all visual
  QA happens on trustsquare.co, never file://.
- iPhone pass pending (David): panel width/close gesture, icon tap targets, legend chips.
- Klook = only tours inventory until re-review passes; empty cities correctly show no 🎫 pin.

## Done already (context)
- TP-C2C-1 live: 🤝 intro demo pins (2 stays + 2 tours, Mode B, DEMO-badged) + 🎫 partner pins
  (Cape Town, Cairo) with §6.1B disclosure panel; widget loads after panel slide-in (offscreen-
  iframe throttle guard). EULA v1.12 Partner Content clause live. RG-0025 guards the TP loader.
