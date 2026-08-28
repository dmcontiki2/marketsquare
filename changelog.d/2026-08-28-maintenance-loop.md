## 2026-08-28 — maintenance-loop: empty queue, first 0-UNVERIFIED board, MAINT-DEPS-1 (RG-0200 LOCKED)

**Queue: nothing to fix.** `GET /admin/faults` — 35 rows total: **0 new · 0 fix-shipped ·
26 verified · 7 closed · 2 duplicate**. The shadow maintenance agent agreed: run
`2026-08-28T05:34:44Z`, mode SHADOW (kill switch OFF — arming is David's act alone),
phase postlaunch, trust-core GUARDED, **0 seen / 0 acted**. Heartbeat confirmed live at
`GET /dashboard/maint` — `received_at 2026-08-28T05:35:01Z`, `brain_keyed: true`,
`brain_lane: anthropic`. Report: `.maint_agent/run_20260828T053444Z.json`.
Escalation brief: **none written** — `escalation_brief.py` reported *"no escalations in the
last 24h"*, which on this lane really is green.

**BRAIN-DEPS-2 ran clean in the FOREGROUND**, ~18 s, well inside the cap. `httpx` was absent
and installed as the runbook prescribes; the origin gate never 401'd the lane.

### MAINT-DEPS-1 — the instrument debt that could never go red, so it never got fixed

With an empty fault queue, instrument debt is the only thing left to find, and there was some.
The **first** pre-run of the regression ledger came back **not green**: RG-0181 and RG-0182 read
`[ ???? ] NOT EVALUATED` because this machine lacked `fastapi`, so both harnesses died at their
import line having run **zero** assertions. RG-0187 demoted them honestly and named the cause —
working exactly as designed — and the run signed off *"that is not a green board — do not deploy
on this result"*.

The recurrence is the point. `httpx` gets installed every session because the shadow agent **dies**
without it — a loud failure, so BRAIN-DEPS-2 fixed it within a day. `fastapi` fails **quietly**:
nothing goes red, so nothing forces the fix. Those two entries had been blind on every sandbox run
since 26 Aug, and **DW-071 was closed on 27 Aug while recording the residual in its own close note**
(*"fastapi is absent from the sandbox bootstrap"*). A defect that is written down and assigned to
nobody is a defect that keeps running. **A blind instrument that never complains is worse than a red
one, because a red one gets fixed.**

Installing `fastapi` and re-running produced the result that had been unavailable for three days:
**RG-0181 and RG-0182 both `[  ok  ]`, and the board came back 0 UNVERIFIED for the first time.**
The two harnesses were never broken — nobody could see them.

**Fixed at class level, not by installing a package:**
- **`scripts/maint_deps.py` (new)** — one idempotent command (~1 s warm) that gives the lane every
  third-party module its *instruments* import. `--check` reports without installing and exits 1.
  `REQUIRED` names the module, its pip name, and **what goes blind without it** — so the cost of a
  missing dependency is legible at the point of failure instead of three files away.
- **`MAINTENANCE_AGENT.md`** — MAINT-DEPS-1 clause makes it **step 0 of every run**, before the
  ledger. An uncalled bootstrap is a decoration.
- **RG-0200, LOCKED** — asserts the MECHANISM: bootstrap present, covers `httpx` + `fastapi`,
  **provably detects a missing module** (a synthetic absent module must make `--check` exit 1 — a
  bootstrap that reports ok unconditionally is the same silent-blindness fault wearing a different
  hat), and the canon still routes step 0 through it. CLASS property: any module the lane's
  instruments import belongs in `REQUIRED`, so a new harness cannot be silently blind for a
  fortnight first.

**The deliberate boundary, and it is the whole entry:** a module *missing on the machine* reads
**INFO, never FAIL**. That is RG-0187's own boundary applied to itself — an absent third-party
package is an instrument limit, not a rotted fix, and a red there would block a deploy over an
environment quirk on launch eve. What CAN go red is the mechanism: bootstrap deleted, coverage
narrowed, detection turned into a no-op, or the canon clause removed.

### Verification (AIK-VERIFY-1, named machine evidence)
- `python3 -m py_compile` clean on `scripts/maint_deps.py` and `scripts/regression_ledger.py`.
- **Negative + positive test**: with a synthetic absent module injected into `REQUIRED`,
  `--check` exits **1** and names it; with it removed, exits **0**. Detection is not a no-op.
- **Ledger post-run: exit 0 — 193 entries · 181 holding · 12 open · 0 REGRESSED · 0 UNVERIFIED.**
  RG-0200 reads `[  ok  ]`.

### Not done, and why
- **No fault-row updates** — the queue held no `new` or `fix-shipped` row to update. Nothing was
  fixed in the product, so nothing was declared verified.
- **No push, no deploy** — NIGHTLY-SHIP-1 (05:45 nightly TSL) carries committed work through the
  gates. This session commits only.
