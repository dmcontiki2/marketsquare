## 2026-09-02 — Maintenance loop (scheduled, unattended): RG-0099 lockout healed, queue empty

- **RG-0099 REGRESSED → healed (SSH-LOCKOUT-1 class).** Ledger opened red: port 22 unreachable
  from the session vantage while a control host answered. `hetzner_fw_selfheal.py --check`
  showed the egress IP had moved to 197.185.137.157 (same ISP range as the 4 existing entries —
  home router/power reset). Ran the self-heal: added `/32` to the SSH rule, nothing removed
  (5 sources now — prune the old four with David at a calm moment). PROBED after: port 22 open,
  RG-0099 green. Cloudflare half still unarmed (no `.secrets/cf_waf_token.txt`) — edge serves
  this vantage fine, lower stakes post-launch.
- **Shadow agent run** `run_20260902T053722Z`: 0 new faults, 0 acted. Heartbeat PROBED on
  `GET /dashboard/maint` (anonymous — migration 018 is on the box). Queue: new 0 /
  fix-shipped 0 / verified 26. Email lane census: 15 total, 1 held (30d).
- **Escalation brief:** none in 24h — no brief written.
- **Ledger before:** 236 entries, 1 REGRESSED, 2 UNVERIFIED (httpx/fastapi missing —
  `maint_deps.py` installed them). **After:** 237 entries, 215 holding, 0 regressed,
  0 unverified, exit 0.
- **RG-0236 prints READY TO LOCK but stays OPEN by design** — its own scope says promote only
  on MEASURED triage accuracy, not on the build having shipped. Not promoted.
- Left untouched (another session's live work, not this run's): uncommitted RG-0244 in
  `regression_ledger.py` and the `attended-red-clear` fragments.
