
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

## 2026-09-03 — /ship: PRICE-UNIT-1 + INVITE-VISION-1 live, and WALK-1 pass 2 found the THIRD blocker

- 03:35Z the STAYS-NEARBY release (49fb579) already carried ms.js/bea_main.py from the nightly checkpoint;
  PROBED live ms.js v=574 states the price basis → **RG-0249 READY TO LOCK**. RG-0250 stayed red: 106 of
  the first 500 emailed prospects carry `emailed_at NULL` (the event handler advances status without
  stamping it) — the gate now keys on status too (INVITE-VISION-1b), shipped 0a553b3 via the RUL-092 relay
  lane, DEPLOY OK 03:45Z, rollback tag `ship-20260903-0544`. Live: invited address passes (400 on an
  invalid photo, zero spend), stranger 401 → **RG-0250 READY TO LOCK**. Smoke: index 200 / 0.5 s, /health ok.
- **WALK-1 pass 2 (live, v=575):** `cat=teachers_trainers` → Tutors ✓ · photo ✓ · six steps ✓ · draft **#381**
  saved with `R350 / hour` ✓ · photo uploaded ✓ · plan ✓ · EULA scrolled + 3 attestations ✓ · **Go live →
  403 "EULA not accepted"**. uvicorn: `POST /users/<email>/eula 404` fired BEFORE `POST /users` created
  the account; the miss was swallowed. **EULA-ORDER-1 (RG-0253, OPEN):** register first, then stamp;
  failed stamp now logs. Every FIRST-TIME seller, both routes, has hit this — David's own accounts already
  existed, so no earlier walk could see it. Listing 381 stays draft until the re-walk after this ships.
- Seen, not fixed: the "✨ new version just shipped — tap to refresh" pill (bottom:74px) sits ON TOP of the
  Go live / primary button on the seller-onboard screen.
