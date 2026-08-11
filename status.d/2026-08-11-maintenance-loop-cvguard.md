- **Maintenance loop, 11 Aug (second run today):** ledger green before and after — **54
  entries, 51 holding, 0 regressed, 3 open** (RG-0003, RG-0004, RG-0029, all pre-existing
  and unchanged). Escalation brief: none written — no safety/legal/cost items in 24h.
- **Fixed: CV-GUARD-1 — the seller CV blanked on an empty roster or an off-city card.**
  `openSellerCV` dereferenced `s.headline`/`s.trustScore` with `SELLERS` empty, and `l.trust`
  twice in its markup after having already guarded `l` one line above for the arithmetic.
  `renderProfilePreview` had the same `SELLERS[0]` deref plus an unguarded `CATS[s.cat].icon`.
  RG-0031 missed both because it scoped to "the openDetail call graph" and these are **sibling
  entry points** — same class, different door. Verified by reproducing the failing action
  clean: `scripts/repro_cv_guard.js` gives **3/3 CRASH (exit 1)** on the pre-fix backup and
  **3/3 pass (exit 0)** on the fix. **RG-0054 LOCKED.**
- **Verified: TS-0001** ("the 15 matching list button doesnt work") — fixed 5 Aug, but the
  row was never updated and sat in `new` for six days. Live-probed the deployed asset
  (`GET /static/ms.js`, HTTP 200, 1,056,818 bytes, contains `upBox.onclick`) and moved to
  `verified`. Queue hygiene, not new work — worth watching that fixes get their row closed.
- **Fault queue: 30 total · 6 new · 20 verified · 2 duplicate · 1 closed · 1 stale
  `awaiting-retest` (TS-0022, status retired by NO-RETEST-1 — still not touched, still for
  `fault_reconcile`).** The 6 new all now carry an honest `fix_note` saying what the loop did
  and, more importantly, what it deliberately did **not** claim, so next session does not
  re-triage them from scratch: TS-0006 and TS-0027 are Path B design calls; TS-0021 is a
  model-selection question that is David's by standing rule; TS-0024's root cause was never
  established (though all three AI lanes read available from `/flags` and the breaker is
  empty, so the likely single-vendor cause is structurally closed by RG-0032); **TS-0018
  needs one sentence from David** — "if we dont use this, can we remove it?" has no referent
  in the text and removal is irreversible, so the loop will not guess.
- **Standing finding, now twice in one day: the brain is not reachable from where the loop
  runs.** Both runs today had `maintenance_agent.py` route every fault to PATH_B with
  `ai_provider unavailable -- defaulting to the batched design lane`. That is RG-0049
  degrading correctly rather than dying, but the effect is that **real mechanical faults get
  binned as design work** and nothing ever reaches "gates GREEN, patch ready". Everything
  fixed today was found by Claude reading the queue directly, not by the harness's triage.
  Until an `ai_provider` lane is reachable from the loop's environment, the 3×/day scheduled
  sessions are doing shadow bookkeeping, not triage — this is the B2b binding gap, and it is
  the single thing most worth closing before the launch rush.
