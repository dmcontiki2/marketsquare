## 2026-09-25 — The deploy gate could not see the app, and passed anyway (QA-GATE-BLIND-1)

OPEN_LOOPS L18, opened this morning: both 25 Sep QA Bot gate reports answered **403 to every
probe before the request reached the app** — 640/640 at 08:07Z, 629/629 at 07:18Z — public
routes such as `GET /quick/me` and `POST /listings/quick-publish` included.

- **Why a wall read as perfect security.** `judge()` turns 401/403 into `PASS "refused"`, which is
  right for a route that refuses a stranger and wrong for a wall in front of the whole app. Every
  route "passed", `regressions()` therefore found nothing, and the gate returned 0.
- **The damage was not the passed gate, it was the baseline.** `accept()` then wrote that blind run
  over `last.json`. `regressions()` skips any route whose previous verdict was `PASS` or
  `UNPROVEN`, so one accepted blind run disarms the gate for **every route** until a clean run
  replaces it. Proven, not argued: driving the pre-fix `accept()` with the 25 Sep run shape
  replaces a real baseline with 640 routes reading `PASS`.
- **Fix — the bot must prove it can see the app before it may grade it.** (1) A pre-flight canary:
  a known-public route (`/health`) must answer 2xx through the *same* client, vantage and pinning
  the probes use. (2) A concentration check: one status shared by ≥90% of persona answers is one
  wall, not N verdicts. (3) On either, the run is **NOT MEASURED** — `accept()` refuses it (guarded
  at the writer, not only at the call sites), and `probe`/`gate`/`nightly` exit 2, which
  `server_deploy.sh` already fails CLOSED on.
- **And it does not freeze the pipeline, which an unconditional hard stop would have.** A gate that
  cannot see must not certify — but making that an absolute stop would have rolled back *every*
  release until someone with server hands fixed the vantage, unattended, overnight. So the bot now
  picks a door it can actually see the app through: the front door first (nginx → app, where
  nginx-level locks count), and if that refuses it before the app, the app's own loopback port —
  which it already trusts enough to read the route list from. That is a **narrower** measurement,
  not a blind one, and the run says so in as many words: *"NOT COVERED by this run: nginx and the
  Cloudflare edge"*. Only when **no** door reaches the app is the run NOT MEASURED.
- **Not a weakening.** A genuinely locked-down app still PASSes route by route and still gates:
  the test pins a 300×403 + 200×401 + 60×404 + 40×200 board as *measured*. Only a run in which the
  bot never reached the app is refused a verdict. Same class as BIT-EDGE-BLIND-1 (23 Sep) and
  RG-0401: an edge refusal is BLIND, never a verdict.
- `scripts/test_qa_gate_blind1.py` is **red on the pre-fix source** and prints the baseline damage
  verbatim; green on the fix.
- **What still needs server hands (not guessed here):** the cause of the 403 itself. RG-0028's own
  scope text names the mechanism — the origin takes connections only from Cloudflare's published
  ranges — so a loopback-pinned request arriving without Cloudflare's origin-pull credentials is
  refused before nginx reaches the app. The bot now says so instead of certifying; pointing it at a
  vantage that can actually see the app is the remaining half of L18.

**No ledger entry yet:** `scripts/regression_ledger.py` is inside lane `goods-fit-2026-09-25`'s
work lock (taken 11:21:58Z). RUL-140 is a stand-off, not a preference — recorded in OPEN_LOOPS
rather than raced.
