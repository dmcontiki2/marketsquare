## 2026-09-25 — Inspection fixes: introductions unlocked, seller text can no longer carry code, money and hand-off breakers closed (INSPECT-FIX-1)

David, 25 Sep 2026: "perform an inspection of the trustsquare and quick listing app code, check for bugs, interface fluid
hand offs in both directions, again for speed, fluidity, ease of use and generally language grammar and spelling. Do it in
depth and thoroughly." Nine reviewers read every line of quick.html, ms.js, marketsquare.html, ms.css, the service worker
and the backend routes Quick and the hand-offs use; four verifiers tried to disprove the findings; the live site was walked
at 390x844 and 360x640 with every write blocked or faked. 266 findings (9 critical, 46 high, 119 medium, 92 low) are on
`INSPECTION_2026-09-25.html` (data: `INSPECTION_2026-09-25_findings.json`). This change closes the criticals that sit in
files outside the Quick lane's lock (quick.html is locked by goods-fit-2026-09-25, so its items are recorded, not edited).

- **INTRO-GATE-MATCH-1 (ts4-01)** — the app locked the introduction button on the paid Home Affairs tick, while the server's
  real rule (`_seller_intro_gate`) accepts a verified ID document or a verified agency. Read-only production check: 44 of the
  65 live adverts belonged to sellers the server would serve, and all 65 showed "Introductions open once this seller
  verifies their ID". GET /listings/{id} now carries `seller_can_receive` (a yes/no from the server's own gate, never the
  seller's identity) and the app gates on it (`_msSellerCanReceive`, `msUnverifiedGate`).
- **CONTENT-GATE-2 (ts1-01, ts2-01, ts2-03, ts3-02, ts3-04)** — the output filter now also cleans subject, level, mode,
  service_type, service_class, availability, buyer_name, buyer_first_name, price, per, other_name, from_name, colour,
  variant, body_type, condition and destination, treats Buzz pair rows (`pair_id`) as records, and turns a straight double
  quote into a typographic one, so a title can no longer break out of `alt="…"`/`src="…"` and add its own handler. The
  Buzz list escapes names at render as well.
- **LM-DEEPLINK-1 + LM-PAID-GUARD-1 (ts1-03)** — a Local Market advert opened from a link (Quick's Find, a Status share)
  opened on the ordinary page and asked the buyer for 1T; it now opens on its own free page, and POST /intros refuses a
  Local Market advert before anything is held.
- **PLAN-RETURN-1 (ts1-02)** — the Plans screen sent Paystack back to `?sub_verify=1`, which nothing read, so a paid Starter
  or Pro upgrade was never applied; both upgrade paths now return to the handler that verifies and applies the plan.
- **CAR-ATTEST-SEED-1 (ts2-02)** — a Quick car advert could never publish: the hand-over to the Terms step seeded only id and
  title, so the vehicle-confirmation card never showed and every publish failed 409; the full row is seeded now.
- **PRICE-KEEP-1 (ts3-01)** — saving any edit to a Quick-made car, collectable or Local Market advert turned a price range such
  as "R1 000–R5 000" into R10,005,000; an untouched price box now leaves the stored price alone.
- **DRAFT-AFTER-SIGNIN-1 (ts1-06/backend-02)** — after signing in with the 6-digit code (or Google/Apple) the app reloaded to
  the home page and the promised draft never opened; a draft still waiting in the tab opens now, and a draft that cannot be
  found says so instead of giving up silently.
- **CITY-SWITCH-LOAD-1 (ts1-07)** — choosing another city now loads that city's adverts at once.
- **Share to Status (ts2-04)** — the hub button's handler was broken by an unescaped quote; it works again.
- **QUICK-LINK-CARRY-1 (ts1-12, quick-13)** — every link from the app into Quick now carries the way back (`from=app`) and the
  reader's language (`lang=`), which quick.html already reads.

Proof: patched files pass `node --check` / `py_compile`; a local browser run with a faked server showed the unlocked
"Request Introduction", the Local Market deep link on its own page and the carried Quick link, against the locked button,
paid page and bare link on the unpatched code. Live check after the deploy is recorded in OPEN_LOOPS.
Regression-ledger entries for these fixes wait for `scripts/regression_ledger.py` to leave the goods-fit lock.
