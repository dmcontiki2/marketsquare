## 2026-08-20 — PLANNER-COST-1, HEARTBEAT-CEILING-1, LEDGER-STABLE-1 and the sweep's Fable blind spot

Closing-out pass on David's "close all open actions". Four instrument/cost debts fixed at
the class, each proven by re-running its own check.

**PLANNER-COST-1 (DW-048).** `planner_heritage_compose` reached the AI through the seam but
carried neither of the other two rails, so the sweep graded it CRITICAL — UNWRAPPED &
UNMETERED. It is FREE class (no Tuppence), which means nothing else capped it either; the
$0 exposure was only because the flag is dark. Added `_check_cost_ceiling(email)` before the
attempt loop and `_log_ai_spend(...)` on the successful parse, attributing provider+model
from the AIResult so a failover costs at the lane that actually served.

**HEARTBEAT-CEILING-1 (DW-021).** The breaker heartbeat logged spend but never checked the
ceiling, and it runs unattended forever. It now checks — and because a background loop must
not die on a 429, breaching the ceiling SKIPS THE TICK rather than raising.

**DW-047 — the sweep had never been taught the Fable family.** Four files WARNed daily as
"unknown model family" since 16 Aug purely because of a missing name. Fable is now classified
like any premium family: a real call site WARNs, reference text is INFO. Also added
`SKIP_FILES` for `.ledger_state.json` — the ledger's own exhaust, the same self-referential
loop DW-043 closed for the watch files.

**LEDGER-STABLE-1 (DW-053).** Twice in one morning the ledger cried "previously-fixed
issue(s) HAVE COME BACK. Do not deploy over this." with nothing rotted — once across a deploy
restart, once because an attended session was rewriting `bea_main.py`,
`scripts/regression_ledger.py` and `ai_funnel_snapshot.json` mid-run. The run now fingerprints
the mtimes of the seven repo files its assertions read and, if any moved while it ran AND it
recorded a regression, reports **UNSTABLE RUN** with the moved files named and exits **3**.
It never suppresses a regression — it refuses to be trusted in either direction and asks for a
re-run, which is the honest verdict when the evidence came off a moving target.

Also: ruff F401 (unused `RedirectResponse` in `_oauth_complete`) and B905 (`zip(..., strict=True)`
in migration 025) cleared — deep scan 184 -> 182, 0 new.

Evidence: cost sweep now grades all three bea_main.py lanes `ceiling ✓ spend-log ✓`;
deep scan 4/4 tools, 0 new; ledger exit 0, 118 entries, 114 holding, 0 regressed;
LEDGER-STABLE-1's detector unit-proven to fire on a mid-run write and stay silent otherwise.
