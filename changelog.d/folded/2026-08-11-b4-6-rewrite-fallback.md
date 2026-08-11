## 2026-08-11 — MAINT-B4-6: rewrite fallback + the first server Tier-2 verdict (honest NOT READY)

**Tier 2 ran on the server for the first time** (migration 011, 07:10Z, via David's 09:08 TSL):
the REAL brain, sandboxed and shadow. Verdict: **NOT READY — and that verdict is the system
working.** Routing was 6/6 PASS: the deterministic guard refused payment/anonymity/legal/safety
with a real brain behind it, design batched to Path B (source identified: openai/gpt-5.6-luna
via the swap seam), escalation escalated. The single failure was the known deferred risk, now
evidence: the real brain's unified diff "did not apply cleanly" against exact bytes — the agent
correctly ESCALATED and shipped nothing. Fail-safe spine: server-proven.

**MAINT-B4-6 — the fallback that evidence earned.** `propose_rewrite()` in
maintenance_agent.py: when (and only when) a diff fails to APPLY, re-ask the brain for the
COMPLETE corrected file (single candidate file, size-sanity capped, fence-stripped, must
differ) and take the mechanical diff ourselves. Stub-safe: rehearsal stubs never reach it;
Tier 1 re-run READY exit 0. **Proven offline in-process:** fake brain returning a
non-applying diff then a full corrected file → `via: rewrite-fallback` → py_compile gate
GREEN → shadow-held. The gates still judge everything; only the fix's EXPRESSION changed.
`migrations/015_maint_b4_tier2_rerun.py` re-runs Tier 2 on the next deploy — READY is now
that verdict flipping, then arming stays David's one paste.

**BIT-AIM-1 work order (not fixed tonight, deliberately).** The 013 timer works — BIT posts
every 15 min, UNKNOWN is gone — and its first honest board says degraded 5/8: all three
B-FEA-* fails share one root, the probes aim at BIT_BASE=localhost:8000 (the BEA app), where
no FEA lives: B-FEA-SHELL gets FastAPI's 404 on "/", and both AI-feature checks cascade off
`_feature_ids()` finding nothing there. Fix direction (needs on-box verification, queued for
the maintenance loop, NOT patched blind from a sandbox): give FEA probes their own base —
nginx on the box with the origin-gate token from the server env, or the edge with the named
UA — registry gains a per-probe base key, runner resolves it. BEA probes stay on 8000.
