## 09 September 2026 — AI PA "Porthole" interface concept, working prototype

David's idea, from a hand-assembled picture: keep the full app (categories, sell wizard,
browse grid) exactly as it is, and put a **single round window with one open question** in
front of the Adventures entry point. Rotating AI adventure stills inside a black circle,
one free-text question ("What would you like…"), then up to four short follow-ups that
branch to anything adventure-shaped — a train trip, a B&B listing, selling a tour, a
heritage read, shark diving, taking leave — landing on a summarised visual result with a
live link into the 5T activation or the guided listing.

**Built:** `MarketSquare/ai_pa_porthole_CONCEPT.html` — self-contained, no external JS.

- Porthole rotates 12 real stills from `assets/journey/` (path resolves from either
  `MarketSquare/` or the `Visuals/MarketSquare/` copy, via a candidate-prefix retry chain).
- Router: 8 lanes, keyword-weighted, with an explicit disambiguating question for anything
  it cannot place — it asks rather than guesses.
- Journey outcome is COMPOSED from real leg data in `journeys/cape_cairo.json`: the
  duration answer selects legs 1–2 / 1–4 / 1–6, distance is summed from the real `dist`
  fields, and the highlights block is filtered from the real stops by the "what do you
  want" answer (scenery → view, wildlife → matched sights, heritage → the 5 UNESCO
  entries mapped to legs, food → food stops, comfort → overnights). Nothing invented.
- "Open the leg map" deep-links to the existing `adventures_c2c_map.html`.
- Other outcomes: guided-listing handoff (stays), claim-a-journey-page (tour operators —
  uses the positioning already in the cape_cairo `cap` string), free heritage read,
  1T introduction (experience).
- Canon respected on every card: no money for the trip through the till, fixed Tuppence
  prices never ad-valorem, price shown before confirm, pre-information free, main app intact.
- Right-hand column answers "is this doable": a 15-row build table graded HAVE / WIRE UP /
  NEW against what is actually on disk, plus the narrow-vs-wide scope call.

**Verified in the rendered page** (headless Chromium, both file locations): porthole photo
paints, all 6 lanes route correctly, 6-leg and 4-leg journey variants produce different
itineraries and different highlight sets, all CTAs render, unknown input falls to the
disambiguator, JS console clean apart from the photos absent from the test sandbox.

**Not done:** nothing deployed, no app code touched. `Visuals/index.html` was hand-patched
with the tile (330 items, MarketSquare group to the top) because the Cowork sandbox mount
to /Projects is down this session and `refresh_visuals.py` could not be run — the next
normal run regenerates the same entry.
