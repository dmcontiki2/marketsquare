## 11 Aug 2026 — PARTNER-LINKS-1: the DATA & PARTNERS card stops lying (attended, David)

- **Fault David found by reading his own switch panel:** the Launch Switch "DATA & PARTNERS
  (back-end rollout)" card still offered **"Flights (Amadeus)"** — a vendor whose self-service
  portal shut **17 Jul 2026**. `bea_main.py` had been corrected to Travelpayouts on 1 Aug
  (TP-FLIGHTS-1); **both dashboards were never updated** and drifted for ten days. Class:
  dashboard-vs-backend drift on vendor identity.
- **Second finding, worse than the label:** all four flags (`data_ops`, `data_places`,
  `data_flights`, `data_mapbox`) are **dark switches with no consumer code anywhere** — they
  appear only in the schema, `/flags` read/write, the infra panel and the dashboard UI.
  Flipping any of them today changes nothing a user would see. Recorded so no session
  reports "activated" after a flip.
- **Change (dashboard.html + dashboard.server.html):** each partner row now carries a `↗`
  homepage link (Travelpayouts · Mapbox · Google Maps Platform console · our own operator
  onboarding guide); `Flights (Amadeus)` → `Flights — Travelpayouts / Aviasales`; Google
  Places carries a red **OUT** badge + `RETIRED 1 Aug 2026 — silent ~$360 bill`; flights
  carries an amber **KEY LIVE** badge; all four tooltips rewritten to spell out their own
  TO ACTIVATE steps so the answer lives on the switch. New `.ls-link` / `.ls-badge` CSS.
- **Method:** boundary-safe Python patch — walk BACK from each checkbox id to *its own*
  `ls-row`, with guards (one row / one checkbox / one name cell per slice, size must GROW).
  A first attempt used a regex with `.*?` across rows; it silently swallowed 3,151 chars of
  the Maintenance group. Caught by the shrink check, restored from backup byte-identical
  (md5 match), redone. **Lesson: never regex across sibling rows in these dashboards.**
- **Verified:** ls-row 9/9 and 13/13, checkbox 9/9 and 13/13, `</div>` 336/336 and 486/486
  identical before→after; 0 non-partner labels lost; `node --check` 8/8 local + 14/14 server
  inline blocks clean; tails intact. Backups `*.bak-partnerlinks-20260811-055029`.
- **Locked as `RG-0050`** — "The partner card names the partner we ACTUALLY have, and every
  partner is one click away." Proven both ways: **10 FAILs** when pointed at the pre-patch
  backups, **0** on the patched files. Ledger after: 50 entries · 47 holding · 0 REGRESSED ·
  3 open · exit 0.
- **Deliverable:** `Data & Partners — Activation per Partner (11 Aug 2026) — nice.docx`
  (Professional Navy) — per-partner activation steps, owner-tagged [D]/[C].
- **Not shipped:** `dashboard.server.html` is in the deploy manifest; rides the next publish
  of the `deploy` ref. David's trigger.
