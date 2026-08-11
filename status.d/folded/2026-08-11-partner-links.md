## 11 Aug 2026 — DATA & PARTNERS card corrected + per-partner activation brief (PARTNER-LINKS-1)

David asked what activating the four DATA & PARTNERS toggles actually needs. Answer, per lane:

- **Signed-operator photos** (`data_ops`) — internal, no vendor, no key, R0. Blocked on
  **paper, not code**: the Featured Operator Showcase Agreement is still a DRAFT (21 Jun) and
  no operator has signed. Then build upload+render, then flip. [D] counsel sign-off.
- **Google Places** (`data_places`) — **CLOSED**, not pending. Out by David's 1 Aug ruling
  after a silent ~$360 bill. No activation path; row kept as a tombstone so it cannot return
  by accident. Link now points at the billing console.
- **Flights — Travelpayouts / Aviasales** (`data_flights`) — **the only lane with runway.**
  Account live (partner 758984), `TRAVELPAYOUTS_TOKEN` live on the server (re-verified 5 Aug),
  EULA v1.11 §6.1A live, R0 cost, no money through the till. Remaining gap is *entirely our
  own code*: fare-cache adapter (empty `{}` = no fare, NOT an error) → Expedition fare UI with
  the indicative/agency caveat + click-out disclosure → token joins the live probes → flip.
  Tours shelf (~8% vs 1.1–1.3%) still blocked on the 5 Aug review decline — resubmit moment
  is David's (OPEN_LOOPS D10).
- **Mapbox** (`data_mapbox`) — optional; the only row that adds a paid metered dependency,
  for prettier tiles and no trust gain. Recommendation: leave off.

**Cross-cutting finding:** none of the four flags has consumer code. They are wiring-only
placeholders — flipping one changes nothing on the live site. No session should report
"activated" on the strength of a flag flip alone.

Dashboard patched both sides (links, corrected vendor, OUT/KEY-LIVE badges, TO-ACTIVATE
tooltips), locked as RG-0050, ledger green (50 · 47 holding · 0 regressed · exit 0).
Unshipped — rides the next `deploy` ref publish.
