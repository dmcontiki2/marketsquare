## 2026-08-05 — D8 grew into the 4-layer map vision; working concept built

- David's ruling: B&Bs are a gap to close AND one of four map layers — ROUTE driving pins + HERITAGE sites + near-by B&B INTRO options + Travelpayouts partner referrals = the full interactive phone-map experience (geolocation, drive-between pins, browse buttons).
- Concept page built reusing the existing map engine (inlined Leaflet, OSM tiles, zero third-party scripts — RG-0025-compatible): ADVENTURES_FULLMAP_CONCEPT.html — 4 colour-coded layers with legend, dashed drive route, My-location control, per-layer popup buttons (Navigate geo:, Request introduction 1T, heritage card, partner link-out marked pending TP approval).
- Not deployed, not in the manifest; indexed into Projects/Visuals. D8 in OPEN_LOOPS updated to carry the full vision so it cannot be lost between sessions.
- CORRECTION same day (David): introductions are ALWAYS 1T — the concept first showed 20T (taken from a CLAUDE.md pricing example); fixed in the concept page and the evening session prompt.
- ADDITION same day (David): selective LAYER SWITCHES — each of the 4 layers now toggles on/off via a colour-dotted checkbox panel (Leaflet layer control, always visible, top-right). The visitor composes their own map: route only, route+stays, everything.
