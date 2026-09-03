
## 2026-09-03 — WALK-1: a real Tutors magic link walked end-to-end in David's Chrome — TWO faults found, both fixed on disk

The walk (photo → 6 steps → score 65/100 → "Continue to publish") proved the invited-seller path is
**broken at the last step**, which is why the few humans who did click could never have listed:

- **PRICE-UNIT-1 (RG-0249, OPEN→deploy).** The sell-flow price field is `type=number` ("e.g. 500"), so a
  tutor can only ever submit `350`; the BEA (JNR-FIX-5B, 22 Jul) rejects every rate-based amount without
  a basis: **422 "Rate-based listings must state the price basis — e.g. R450 / hour"** — a message the
  seller has no way to act on — and the flow then dumps them on the plan-picker with "tap Continue to try
  again". Every self-serve Tutors / Services / Adventures listing since 22 Jul died here. Fix: `SF_CATS`
  gains `priceUnit` ('/ hour', '/ call-out', '/ person', '/ night'); `_sfPriceWithUnit()` at `sfFinish`
  turns `350` into `R350 / hour` (empty → POA, an entered basis passes untouched). Node-tested.
- **INVITE-VISION-1 (RG-0250, OPEN→deploy).** `POST /listings/vision-draft` answered **401** to the
  invited seller (Session-90 existence gate: users table only; a magic-link arrival is not a user until
  publish) and the flow silently fell back to "fill in the details manually" — the AI draft the outreach
  email promises never appears for any invitee. Fix: `_is_invited_prospect()` — read-only lookup in
  CityLauncher's `prospects.db` (same box, `emailed_at IS NOT NULL`); strangers still 401 (spend guard
  intact); missing DB / any error → closed. Tested on a temp DB. Ledger live leg probes the gate with an
  invalid photo (400 after the gate, zero AI spend) and a stranger (must stay 401).
- **INVITE-CAT-1** (no ledger entry; cosmetic): `sfInit` now maps the outreach vocabulary
  (`teachers_trainers`, `us_university_tutors`, `Car Dealers`, `Estate Agency`, `adventures_*`, tour /
  travel, collector shops, service companies) so an invitee skips the tile screen.
- Also seen, not fixed: the "✨ A new version is ready — Refresh" bar shows on a FRESH magic-link arrival
  (edge index v=571 vs origin v=572) and a mid-flow refresh loses all in-memory state; `src=`/`draft_id=`
  still unread by ms.js.

**Ledger after:** 243 entries · 0 REGRESSED · exit 0 (RG-0248/0249/0250 OPEN on their live legs only).
**Deploy debt (David's /ship):** ms.js, bea_main.py, api/server.py (CityLauncher). Backups:
`ms.js.bak-priceunit-*`, `bea_main.py.bak-invitegate-*`. The walkthrough left NO listing on the server
(the 422 stopped it) — re-walk after deploy is the proof, and RG-0249/0250 turn green on the same deploy.

**03:25 SAST — CityLauncher deployed (David).** PROBED: `/launch-api/prospects/human-clicks` 401, register
self-refreshed on the server 20 s after restart (2 human_click / 52 human_open / 14 uncertain / 60 machine).
**RG-0248 → LOCKED.** RG-0249/0250 still wait on the MarketSquare /ship (ms.js + bea_main.py).
