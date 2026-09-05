## 2026-09-04 — Maintenance loop: the instruments that were lying about themselves

**Fault queue: empty.** 35 rows, none new, none awaiting a fix (26 verified · 7 closed ·
2 duplicate). No tester fix work existed, so the session's items were the two instruments
that were quietly misreporting their own state — the class this loop exists to catch.

### CODE-STAMP-2 — the maintenance run could not say which code it ran (RG-0259, LOCKED)
`/dashboard/maint` published `"code":"unknown (TimeoutExpired)"` on every sandbox run —
on the one surface STALE-CODE-1 exists to keep truthful. Cause measured, not guessed:
`_code_stamp()` ran three git legs inside ONE `try`, and `git status --porcelain` takes
**21.0 s** on the /Projects FUSE mount against a **20 s** timeout, so the timeout escaped
past a SHA that had already been read cleanly in 0.1 s. The legs are now independent, the
slow one carries 300 s, and dirtiness we cannot measure reports `DIRTY-UNKNOWN` rather
than defaulting to clean.
*Evidence:* the failing action reproduced clean in-session — live `/dashboard/maint` for
run `2026-09-04T05:48:17Z` reads `b26ca4d  DIRTY-WORKTREE  Daily watch 2026-09-04…`, where
the run 13 minutes earlier read `unknown (TimeoutExpired)`.

### LEDGER-BOOTSTRAP-1 — the board can no longer read blind (RG-0260, LOCKED)
This session's first ledger run demoted RG-0181/RG-0182 to NOT EVALUATED for want of
`fastapi` — the **third** recorded instance (DW-082 29 Aug, DW-083 30 Aug whose residual
predicted the repeat, and today). MAINT-DEPS-1 built the cure and MAINTENANCE_AGENT.md
ordered it "step 0, before the ledger", but that ordering lived only in prose, and the
sandbox is ephemeral, so prose loses every time the tree is fresh. `main()` now calls
`_ensure_instrument_deps()` before the first assertion — the same entry-point self-heal as
`ssh_bootstrap.ensure_ssh()` and `git_unlock`. Never fatal, stderr only, `--no-bootstrap`
opts out, RG-0187's honest demotion untouched.
*Evidence:* re-run evaluated both entries with no separate bootstrap step — **0 UNVERIFIED**.

### RG-0187 assertion CORRECTED, not weakened
The new bootstrap tripped RG-0187 (`harness call site(s) still run a subprocess directly`)
— its scanner was over-broad. A second carve-out now sits beside the BRAIN-PATH-1 one,
keyed to the installer script's **name** (the call site was renamed `maint_deps_script` so
the exception cannot be inherited by pasting a comment). Rationale recorded in the entry's
ref: that call site is the dependency *installer*, it runs outside every entry so it
colours no verdict, and it swallows its own failures. Anything that does colour a verdict
is still caught.

### RG-0236 — a FALSE "ready to lock" removed
The board offered RG-0236 (outreach reply triage) for promotion while the entry's own ref
sets the bar at *"PROBED on real traffic … shipped is not measured"*. The source checks
could only see the lane was BUILT, so the board was nudging each session toward exactly the
silent green this file exists to prevent. The bar is now machine-visible: absent
`Records/OUTREACH_TRIAGE_MEASURED.md`, the entry stays honestly open. **Not promoted.**

### Promotions (3) — passing OPEN entries locked per canon
- **RG-0252** AUTODEPLOY-AGENT-1 — agent registered and ticking (log 2 min old), first request shipped.
- **RG-0255** DEVTOGGLE-REMOVE-1 — served index carries no dev-toggle markup.
- **RG-0258** LIVE-MAP-1 — `GET /geo/stays` answers with `as_of` (read 2026-09-04T05:34Z); every served map carries the layer.

**Ledger:** before — 0 regressed but **2 NOT EVALUATED** ("not a green board"). After —
**253 entries · 235 holding · 0 REGRESSED · 18 open · 0 ready to lock · 0 UNVERIFIED · exit 0**.
**Rulings:** 93 checked, 0 FAIL, 3 WARN (RUL-093/094/095 carry no reflection assertions — pre-existing).
**Escalation brief:** none written — no escalations in 24h.
