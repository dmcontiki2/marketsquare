### Maintenance loop — 28 Aug 2026 (05:34 UTC, unattended)

Queue empty: **0 new / 0 fix-shipped**, 26 verified, 7 closed, 2 duplicate (35 rows).
No product fix was applied because no register rows arrived — the strict B2b contract
(rows in → gate-passing commits out) produces a report and nothing else on an empty queue.

- Shadow agent run `2026-08-28T05:34:44Z`, mode SHADOW (kill switch OFF, correct — arming is
  David's act alone), phase postlaunch, trust-core GUARDED, **0 seen / 0 acted**. Heartbeat
  PROBED at `GET /dashboard/maint`, received `05:35:01Z`, `brain_keyed=true` on the anthropic
  lane. Foreground per BRAIN-DEPS-2, ~18 s.
- Regression ledger **green pre and post**, exit 0 both runs. Post: **193 entries · 181 holding ·
  12 open · 0 REGRESSED · 0 UNVERIFIED**.
- Escalation brief: **none** — no escalations in the last 24h.
- **MAINT-DEPS-1 — the instrument debt is now fixed, not noted again.** The FIRST pre-run was
  *not* green: RG-0181/RG-0182 read `[ ???? ] NOT EVALUATED` for want of `fastapi`. The 27 Aug
  loop recorded this same finding and recommended the same fix — *"the loop's dependency step
  should install fastapi as well as httpx"* — and DW-071 was closed the same day while naming the
  residual in its close note. A recommendation with no owner produced an identical blind run
  24 hours later, so it was built instead: **`scripts/maint_deps.py`** (idempotent bootstrap,
  `--check` mode, names what goes blind without each module), **step 0 in MAINTENANCE_AGENT.md**,
  and **RG-0200 LOCKED** asserting the mechanism — including a behavioural check that detection
  is not a no-op. Boundary: a missing module reads INFO, never FAIL (RG-0187's rule applied to
  itself), so this can never red-block a deploy over an environment quirk.
- Evidence: `py_compile` clean on both touched scripts; synthetic-absent-module test makes
  `--check` exit 1 and the real check exit 0; ledger post-run exit 0 with RG-0200 `[  ok  ]`.
- Worktree was already dirty from concurrent launch-eve work (third-party sweep, contagion model,
  DAILY_WATCH). Staged explicitly, never `-A`. `scripts/regression_ledger.py` carries one
  change that is **not** this session's — another session's promotion of RG-0175 to LOCKED,
  complete and green on this run; it rides along because the two edits share a file.
- No push, no deploy — NIGHTLY-SHIP-1 carries committed work through the gates.
