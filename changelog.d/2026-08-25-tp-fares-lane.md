## 2026-08-25 — TP-FARES-1: indicative fares on the journey maps, cache-only, dark until David's flag

**David:** *"Please build them now Claude, then i will flip the flag. It is still a zero cost?"*

**Cost: zero, and structurally so — not zero-for-now.** The Travelpayouts flight **Data** API is
token-only and free; the 50k-MAU gate people quote applies to their **Search** API, which we do not
use. There is no per-query billing, so no bill can run away the way Google's silent ~$360 did. Duffel
search ($0.005/query, hard cap) stays the unwired standby adapter. Commission flowing **in** is income,
not a variable cost — the 1 Aug pricing rule bars variable costs, not income.

**Probed live with the project token, 25 Aug.** All 10 unique map routes returned real fares in native
ZAR, each with a real deeplink: JNB→CPT **R1,187**, MPM R1,608, GBE R1,683, WDH R2,373, NBO R2,989,
CAI R4,246, LHR R5,287, FRA R5,929, SYD R7,662, JFK R8,449. `v3/prices_for_dates` returns a relative
`link` — and *that* is where the Aviasales deeplink in `travelpayouts_partners.py` came from. Read from
the API, not invented, which is what RG-0181 demanded.

### Built

- **`data_flights.py`** — fare cache + swappable supplier adapter. Two paths that never touch:
  `get_indicative()` reads our SQLite **only** and contains no network code at all (asserted); `refresh()`
  is the sole caller of a supplier and runs on a schedule, never on a customer request. Supplier loss
  therefore ages the cache instead of breaking the page — the 1 Aug supplier-fallback doctrine, made
  mechanical. Politeness cap of 40 calls per run; their courtesy is what's being protected, since
  there's no bill to protect.
- **`GET /flights/indicative`** in `bea_main.py` — 404s while dark, matching the planner lane's rule
  that an off flag answers 404 and never 500. Import wrapped so a monetisation side-lane can never take
  the app down at boot.
- **`ts_fares.js`** on all 15 adventures maps — first-party only; its one network call is our own
  endpoint. Travelpayouts is contacted by our server on a schedule, never by a traveller's browser.
  **Renders nothing** when dark, uncached, stale, or on any error — no spinner, no placeholder, no
  "loading fares…", because an empty state that promises a price is a small lie. Every price prints its
  **age**; *"Indicative only. Not a quote and not live availability"* cannot be omitted; the outward link
  is `rel="nofollow sponsored"` with the commission disclosure **in the card**; and it says plainly that
  MarketSquare is not a travel agency (RUL-038 positioning).
- **`migrations/032_fares_refresh_cron.py`** — daily 06:20 refresh + first fill, so the cache is warm
  *before* the flag flips rather than empty on the day. Skips the fill safely if the token isn't in the
  environment; the lane just stays dark and silent, which is the safe state.
- **`scripts/prove_fares_lane.py`** — 13/13, offline. Tests the **dark** case first, because a lane
  only ever tested lit is a lane whose "off" is a hope. Also proves: a 400-day-old fare is withheld
  rather than shown stale; a thin route falls back to the agency card with no number; and a poisoned
  deeplink planted in the cache yields **no** link rather than a bad one.

### Ledger

**RG-0182 OPEN.** Its live half reads the 404 **body**, not just the status code — because "flag is off"
and "never deployed" both return 404, and a ledger that reads a missing feature as a correctly-dark one
is precisely the silent green the ledger exists to prevent. It currently reports, correctly:
*"the fares endpoint is NOT DEPLOYED — 404 body is `{"detail":"Not Found"}`, not our dark guard."*

**Verification:** ledger exit 0 · 175 entries · 155 holding · **0 regressed** · rulings 56/0 FAIL ·
remote-code guard clean across 63 deployable files · fares harness 13/13 · `node --check` clean.

**Sequence from here:** the code rides David's next deploy → RG-0182 flips to *"deployed and dark"* →
David flips `data_flights` → fares appear on the maps.
