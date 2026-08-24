### Indicative fares built for the journey maps — dark, waiting on the flag (TP-FARES-1)

David: *"build them now, then I will flip the flag. It is still a zero cost?"* — **Yes, zero, and
structurally so.** Travelpayouts' flight **Data** API is token-only and free (the 50k-MAU gate is on
their *Search* API); no per-query billing, so nothing can run away like the ~$360 Google burn.

**Probed live, 25 Aug:** all 10 unique map routes returned real ZAR fares with real deeplinks —
JNB→CPT R1,187 · MPM R1,608 · GBE R1,683 · WDH R2,373 · NBO R2,989 · CAI R4,246 · LHR R5,287 ·
FRA R5,929 · SYD R7,662 · JFK R8,449.

**Built:** `data_flights.py` (cache + swappable adapter — reads touch our SQLite only, a cron is the
sole thing that contacts the supplier) · `GET /flights/indicative` (404 while dark) · `ts_fares.js` on
all 15 adventures maps (first-party; renders nothing when dark/uncached/stale; age beside every price;
indicative disclaimer and "not a travel agency" line non-optional; link is nofollow sponsored with the
commission disclosure in the card) · `migrations/032` (daily 06:20 refresh + first fill so the cache is
warm before the flip) · `scripts/prove_fares_lane.py` (13/13, dark case first).

**Ledger RG-0182 OPEN** — and it can tell "not deployed" from "dark", because both answer 404; it reads
the body. Right now it says NOT DEPLOYED, which is true.

**Verification:** ledger exit 0 · 175 entries · 0 regressed · rulings 0 FAIL · remote-code guard clean.

**Needs David, in order:** (1) the deploy — carries this lane *and* migration 031, the CSP + naked-index
fix, which is still the highest-value item in the ship; (2) then flip `data_flights` on the +1 page.
