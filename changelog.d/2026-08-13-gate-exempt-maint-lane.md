## 2026-08-13 — GATE-EXEMPT-MAINT-1: migration 018 + BRAIN-DEPS-2 (David: "lets fix both")

Both follow-ups from the 13:24Z maintenance loop, done same day on David's ruling.

**1. Migration 018 (migrations/018_gate_exempt_maint_lane.py)** removes the B2b lane's
credential dependency at the origin: exempts `location ^~ /admin/faults` and
`location = /dashboard/maint` from the review gate — and ONLY those; the other /admin/*
routes (login, users, flags, deploy-file…) stay gated. Scoped after a route audit: every
/admin/faults* route and the /dashboard/maint POST carry Depends(_require_maint)
(constant-time key compare, fails closed, bea_main.py:16366) — 007's machine-to-machine
doctrine verbatim, "exempting them at nginx removes no protection". GET /dashboard/maint
is no-auth by documented design and merely regains its pre-gate public posture.
016's proven skeleton throughout (enabled-first find_site, functional idempotency,
collision refusal, no-gate early exit, backup + nginx -t + reload with auto-restore);
transform proven against a synthetic post-016 conf before commit (gate detected, single
anchor, both lines land, idempotent re-run). Rides the next successful deploy — engine
stalled (DW-042), so likely tonight's revival or NIGHTLY-SHIP-1. RG-0065 OPEN watches it:
keyed-no-cookie intake currently 401s (expected); flips READY TO LOCK the run 018 lands.
GATE-COOKIE-1 stays in both consumers — belt (018) and braces (cookie) — so the loop
survives either lane failing.

**2. BRAIN-DEPS-2 (scheduled task amended via the task system):** maintenance-loop step 2
now runs the agent FOREGROUND (timeout_ms=600000) with an httpx pre-check/install, and
notes the agent self-mints the review credential. Supersedes BRAIN-DEPS-1's detached
pattern — the Cowork sandbox reaps background processes at the bash-call boundary
(setsid included; proven twice 13 Aug, log frozen at the banner). Heartbeat-confirm GET
carries the review cookie until 018 lands.
