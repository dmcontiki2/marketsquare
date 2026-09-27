## 2026-09-25 — Adventure maps draw on first view again (MAP-FIRST-VIEW-1, TE-TEXT-1)

David: *"the in app maps used to show a map on the first view, but lately i need to either expand or open it and
even then i first have to press route for the map to appear. Showing it in the first view as it were is the view
we need?"*

- **Cause (probed in a rendered browser):** LIVE-MAP-1 (3 Sep) added a block that fetches today's stays and asks
  the map for its bounds before the map has a view. Leaflet threw "Set map center and zoom first", which stopped
  the rest of the page, so the map stayed blank until Route set a view. Live Botswana map: 0 tiles.
- **Fix:** the block uses the route's own points and never asks an unset map for bounds; on any failure it steps
  aside instead of stopping the page. All 15 maps and the generator template (scripts/journey_template.html).
  Patched Botswana map rendered: 8 tiles, 41 pins, no errors. ms.js map cache-busters bumped (12 maps).
- **Also on David's screenshot (TE-TEXT-1):** the "Before you go" itinerary showed raw `&nbsp;<a href=...>` —
  the day text is shared with the maps, where the fare link is HTML. The brief now shows the words only.
- Ledger RG-0485 (OPEN until live): no map may read its bounds unguarded; the brief shows no raw HTML.

Cost model impact: none.
