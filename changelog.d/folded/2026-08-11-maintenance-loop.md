## 2026-08-11 — UA-EDGE-1: the maintenance loop was reading NOTHING (green-looking no-op), fixed at class level

- **The fault (found by the daily maintenance loop, on itself):** `scripts/maintenance_agent.py`
  intake returned `HTTP Error 403: Forbidden` on `GET /admin/faults?status=new`. Not the
  reviewer gate and not a bad key — **Cloudflare error 1010, "banned browser signature"**:
  `urllib` sends no `User-Agent`, so the request was refused AT THE EDGE before the origin
  or the maint key were ever consulted.
- **Why it mattered more than a 403 usually does:** the agent then did exactly what it is
  built to do — `"intake FAILED -- nothing read; failing safe, doing nothing."` — and
  **exited 0**. An unattended nightly run therefore looked GREEN while processing an empty
  queue. Faults sat unread; nothing said so. Silent no-ops are the one failure mode an
  autonomous loop cannot afford.
- **The fix (class, not instance):** every repo script that calls OUR OWN edge now names
  itself with a `User-Agent`, the same way `regression_ledger.py` always has (which is
  precisely why the ledger kept working while the agent went blind):
  `scripts/maintenance_agent.py` (`UA_HEADER` + `api()`), `scripts/fault_reconcile.py`,
  `scripts/cost_compliance_sweep.py`, `deploy_web.py`, `run_collections_validation.py`.
  Third-party callers (`peer_review.py`, `golden_openai_v1.py` → api.openai.com) are out of
  scope — not our edge, not our Cloudflare rules.
- **Evidence (AIK-VERIFY-1):** the failing action reproduced clean. Same key, same URL —
  without UA `403 / "error code: 1010"`; with UA `200` and **7 queued faults returned**
  (TS-0001, TS-0006, TS-0018, TS-0021, TS-0024, TS-0027, TS-0030). Run report
  `.maint_agent/run_20260811T051107Z.json` (7 seen, 7 acted) vs the earlier same-session
  report of the same run reading zero.
- **RG-0053 LOCKED** — two halves so this cannot rot: source-side, none of the five
  our-edge callers may construct a `urllib` Request without a `User-Agent`; live-side, the
  maintenance agent's *exact* header set must still get HTTP 200 from
  `/admin/faults?status=new`. If either goes, the ledger goes red instead of the loop going
  quiet.
- Ledger before **and** after: 0 REGRESSED. 53 entries · 50 holding · 3 open (RG-0003,
  RG-0004, RG-0029 — all pre-existing, unchanged by this session).
