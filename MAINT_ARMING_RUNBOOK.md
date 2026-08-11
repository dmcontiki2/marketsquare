# ARMING THE MAINTENANCE AGENT — one paste, one lever (11 Aug 2026)

**Preconditions — check BOTH, in your Chrome (it carries the reviewer cookie):**
1. `https://trustsquare.co/static/maint/b4_tier2.json` shows `"ready": true`
   (written by migration 011 — the server-side Tier-2 rehearsal verdict).
2. A fresh /backup exists (belt and braces before any autonomy).

**ARM — paste this whole block into PowerShell, nothing to substitute:**

    ssh root@178.104.73.239 "set -e
    cp /opt/marketsquare-src/ops/maintenance/maintenance-agent.service /etc/systemd/system/
    cp /opt/marketsquare-src/ops/maintenance/maintenance-agent.timer   /etc/systemd/system/
    mkdir -p /etc/systemd/system/maintenance-agent.service.d
    printf '[Service]\nEnvironment=MAINTENANCE_AGENT_ENABLED=1\nEnvironment=MAINT_PHASE=prelaunch\n' \
        > /etc/systemd/system/maintenance-agent.service.d/armed.conf
    chmod 600 /etc/systemd/system/maintenance-agent.service.d/armed.conf
    systemctl daemon-reload
    systemctl enable --now maintenance-agent.timer
    echo '--- push-auth check (must say up to date / would push):'
    git -C /opt/marketsquare-src push --dry-run origin HEAD:deploy || echo 'PUSH AUTH MISSING: agent can gate+verify but not self-ship — fix deploy key first'
    systemctl list-timers maintenance-agent.timer --no-pager
    echo ARMED"

- `MAINT_PHASE=prelaunch` until 1 Sep, then change the drop-in line to `postlaunch`
  (strict trust-core guard + Path B batching return) and `systemctl daemon-reload`.
- Cadence: 05:20 / 11:20 / 17:20 UTC (3×/day, B2 spec). Rate cap 3 ships/hour on top.

**DISARM — the one lever, same shape:**

    ssh root@178.104.73.239 "systemctl disable --now maintenance-agent.timer; rm -f /etc/systemd/system/maintenance-agent.service.d/armed.conf; systemctl daemon-reload; echo DISARMED"

**What arming does NOT change:** every run still passes the full mechanical gates
(worktree → py_compile/node --check → ledger → predeploy), the deterministic
refuse guard still escalates legal/costly (+ trust core post-launch), the ONE
deploy engine still BIT-verifies and auto-rolls-back, and the run report still
feeds `scripts/escalation_brief.py`. Arming only lets green results ship.
