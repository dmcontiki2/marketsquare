## 2026-08-31 — OPTOUT-LANE-1: people could not opt out at all; lane built, verifier written, RG-0229 RED until proven live

David: *"the blocker is the false acknowledgement of the opt out database, which doesn't exist… This is a project kill risk."*

### What was actually true (probed, 31 Aug)
- Every outreach email since 24 Aug carries an unsubscribe link → `{api_base}/optout?email=…`
- **No `/optout` route existed anywhere.** bea_main.py, main.py, the Cloudflare worker and ops configs all swept.
- **No server-side `suppression` table DDL existed** either.
- The local register had never been created.
- `_is_suppressed()` — docstring: *"the opt-out register is verified before ANY single email"* — returned `False` ("not suppressed, send it") whenever the table was absent.

**110 emails went out carrying a dead unsubscribe link, and the guard that was supposed to honour opt-outs had never once consulted real data.**

### Built this session
- **SUPPRESS-FAILCLOSED-1** — the absent-register path now returns `True` and refuses. *An absent register is not permission.* Verified: `_is_suppressed()` → `True` with no table, where it returned `False` before.
- **`/optout` GET + POST** in bea_main.py — one click, no login, idempotent, never errors to the caller, does not reveal whether the address was on a list; writes the register (creating it if absent) and sets the prospect's status so the existing pulldown carries it. GET *and* POST because RFC 8058 List-Unsubscribe-Post uses POST; a false opt-out costs one prospect, a missed one costs a breach — asymmetric on purpose.
- **`/optout/status`** — counts only, never addresses. The proof endpoint.
- **`verify_optout_lane.py`** — five gates along the path a real opt-out travels: anonymous 200 → click recorded → register reaches the local pool → guard refuses a real opted-out address → guard refuses when the register is missing.

### A live catch worth recording
`py_compile` passed on the new route while `HTMLResponse` was not imported at that point in the file (the only import is an alias 17 000 lines lower). The first real request would have raised `NameError`. Caught by **running** the route logic against a temp DB rather than compiling it — *"it compiles" is not "it works"*, which is the same gap this entire lane exists because of.

### Status: NOT LIVE
`RG-0229` is OPEN and **RED — 1 of 5 gates passing.** The route is staged in `bea_main.py` and needs David's deploy. The live probe returns **404, not 403**, so `/optout` is *not* behind the review gate and a deploy should be sufficient — to be **proven by gate 1**, never assumed.

**Nothing sends until the verifier prints 5/5.** That is now machinery, not a promise: RG-0229 fails red and names the failing gates.

Files: `bea_main.py` (OPTOUT-LANE-1 route block) · `../CityLauncher/emailer/emailer.py` (SUPPRESS-FAILCLOSED-1) · `../CityLauncher/verify_optout_lane.py` · `scripts/regression_ledger.py` RG-0229.
