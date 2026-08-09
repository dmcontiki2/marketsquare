## 2026-08-09 — MAINT-AGENT-1: the Path A autonomous fix-agent, built + shadow-proven (B2b)

David's ruling: "build the Path A autonomous fix-agent now." Built to the 29 Jul canon
(MAINTENANCE_AGENT.md), bound to what already exists rather than reinvented.

`scripts/maintenance_agent.py` (≈285 lines, py_compile green). One run =
intake -> classify -> (Path A) brain -> apply-in-worktree -> real gates -> ship -> AIK-verify.
- INTAKE: GET /admin/faults?status=new (localhost + MS_MAINT_KEY, same resolution as fault_reconcile).
- BRAIN = the IDENTIFIED source: ai_provider.complete(); provider+model recorded on every fix and
  written into the commit message and fix_note. Swappable by one config line — the independence ruling
  made concrete. It is not "AI fixed it", it is "the agent fixed it via <named engine>".
- DEPLOY: reuses the ONE engine (git mirror -> server_deploy.sh); never re-implements upload or rollback (RG-0023).
- VERIFY: AIK-VERIFY-1 — a live probe reproduces the failing action; named evidence in fix_note; only
  then status=verified. No evidence => left 'fix-shipped', never 'verified'. Tonight's lesson, as code.

THE FOUR LAUNCH-BLOCKING REQUIREMENTS, all wired fail-safe:
1. gates-are-tests — a commit is proposed ONLY if py_compile/node --check + regression_ledger +
   predeploy_check all pass in a throwaway `git worktree`.
2. auto-rollback — delegated to server_deploy.sh's BIT probe + revert; no second rollback story.
3. rate-limit + kill switch — MAINTENANCE_AGENT_ENABLED (default "0" = OFF) is David's one lever;
   LIVE requires BOTH that env AND --live, so an accident stays in shadow. MAINT_MAX_SHIPS_PER_HOUR caps runaway.
4. act-safest-first — a deterministic REFUSE guard the AI cannot bypass keeps payment, auth, session,
   schema, ANONYMITY (seller_email), legal and safety out of autonomous reach; those ESCALATE, never ship.

PROVEN this session (not claimed — run):
- Safety guard asserted against the 3 real open tickets + synthetic payment/anonymity/schema/legal:
  the trust core REFUSES every time; a benign design ticket (TS-0027) passes the guard to the batched lane.
- Mechanical spine on a throwaway repo: good patch -> GREEN -> withheld in shadow; BROKEN patch -> RED -> held.
- Two real bugs found BY proving instead of claiming, and fixed: py_compile silently skipped when no .py
  changed; `git diff` missed `git apply --3way`'s STAGED files, which would have let a broken Python fix
  ship ungated. Both fixed; the second is why the tripwire exists.
- Tripwire RG-0046 (repo-side, offline-safe): fails if the default flips on or any trust-core marker
  leaves the guard. Green.

NOT done, and honestly labelled (this is B4, the spec's pre-arm rehearsal, needs the server + API key):
- The brain generating a genuinely CORRECT patch for a real ticket (needs ai_provider with the server key).
- A real green-gate self-ship + BIT-verify + auto-revert (needs a live deploy).
- The synthetic-complaint storm (B4) that signs the loop READY.
ARMING is one deliberate act, David's alone: after B4 signs READY, set MAINTENANCE_AGENT_ENABLED=1 on
the server and schedule the run 3x/day. Nothing here arms itself. Cost model impact: none (shadow).
