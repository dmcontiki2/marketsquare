## 2026-08-18 — HERITAGE-RAIL-1: +19 sites along the three rail journeys; /wonders goes gzipped

- wonders.json 332 -> 351 (485 KB -> 529 KB raw). David approved "all core" from the
  Heritage Rail Expansion doc: 6 Ghan sites (Ikara-Flinders, Tjoritja/West MacDonnell,
  Nitmiluk, Karlu Karlu, SA Museum, MAGNT), 7 Great British (Durham Castle & Cathedral,
  NRM York, Hadrian's Wall, Lindisfarne, Forth Bridge, Antonine Wall, Loch Lomond &
  Trossachs NP), 6 American Crossing (Robie House, Art Institute, Rocky Mountain NP,
  Arches NP, Golden Spike NHP, California State Railroad Museum). Every photo is a
  verified Wikimedia Commons free-licence file (CC BY/BY-SA/CC0/PD/FAL) with author,
  licence and source captured — same mold as the existing 332. IDs np_098-104, un_143-147,
  nm_048-052, ar_047-048. Europe: no route touches the Continent — no additions, by design.
- WONDERS-GZIP-1: GZipMiddleware(minimum_size=1024) added to bea_main.py — the catalog
  fetch drops ~485 KB -> ~144 KB once deployed; found while confirming expansion impact
  is negligible (~1.5 KB/site on a deferred background fetch; photos lazy-load from
  Wikimedia CDN and never bundle). Ledger RG-0101 (OPEN) locks it at next deploy.
  NB: RG-0100 was already taken (CityLauncher coverage) — new entry took RG-0101.
- Local only until the deploy ref publishes (rides tonight's TSL or the next /ship).
  Post-deploy: run relink_wonders.py on the server to re-match live listings against
  the expanded set. Rail-map pins do not yet deep-link the 19 new ids (follow-up).
