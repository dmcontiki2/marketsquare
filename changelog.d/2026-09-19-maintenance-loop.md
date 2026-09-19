## 2026-09-19 — maintenance-loop: empty queue, board green, nothing to fix

Daily B2b maintenance session (Claude-by-hand, pre/post-launch contract: register rows in
→ gate-passing commits out, nothing else).

**Fault queue — nothing to act on.** `GET /admin/faults` PROBED live 19 Sep 05:39 UTC with
the maintenance key through the armed review gate: `status=new` → `[]`, `status=open` → `[]`,
`status=fix-shipped` → `[]`. Historical rows remain in `verified` (TS-0035 and earlier) and
`closed` (TS-0034 and earlier). No fault was fixed this run because none was waiting; the
shadow agent's run report `.maint_agent/run_20260919T053647Z.json` records `seen: 0, acted: 0`.

**Shadow agent.** `MS_BEA_URL=https://trustsquare.co python3 scripts/maintenance_agent.py`
ran FOREGROUND (BRAIN-DEPS-2) and completed in ~25 s. Kill switch OFF as always — arming is
David's act alone, never a session's. It minted the review credential itself (GATE-COOKIE-1),
so the origin gate did not block the lane. Email lane census: 24 total, 6 held in the last
30 days (legal 1, other 5, spam 1, support 7) — counts only, not a fix lane (RG-0222).

**Heartbeat PROBED, not assumed.** `GET /dashboard/maint` (with the ts_review cookie minted
from `.secrets/review_code.txt`) returns `"run":"20260919T053646Z"` — this run's own stamp —
so the dashboard's B2b readiness row is reading today's session and not a stale one.

**Brain lane reported honestly as NOT_EVALUATED.** The agent printed
`brain NOT_EVALUATED:remote  vantage:local-only` and `arming NOT MEASURED (off-box vantage)`.
That is the RG-0187 contract behaving correctly: an instrument that cannot see the box says
so instead of painting a colour. It is NOT a red and must not be reported as one.

**Escalation brief.** `scripts/escalation_brief.py` → "no escalations in the last 24h — no
brief written". Nothing for David to read.

**Regression ledger — green either side of the run.** Run in shards (LEDGER-SHARD-1) before
the fault work: 404 entries, 0 regressed, 23 known defects OPEN. Re-run after: same verdict,
exit 0. No LOCKED entry rotted, no OPEN entry printed READY TO LOCK.

**No new ledger entry this session, and that is correct:** the rule is one entry per FIX, and
no fix was made. Nothing was shipped, nothing deployed, nothing pushed — NIGHTLY-SHIP-1 (the
05:45 TSL on David's machine) carries committed work through the gates.
