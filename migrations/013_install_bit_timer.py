#!/usr/bin/env python3
"""013_install_bit_timer.py — SERVER-BIT-1 (11 Aug 2026, David: the dashboard must
update itself when the BIT flags change; waiting for a human or a deploy won't
work after launch).

Root cause: the dashboard already polls GET /dashboard/bit every 60s, but the board
it reads (bit_status.json) was only POSTed when something ran bit_cycle.py — and the
*/15 scheduled task from 27 Jun was never created, so the lights froze between
manual runs. Class fix: the SERVER runs its own heartbeat. This migration installs
a systemd service+timer running the shipped copy (live root /bit/) every 15 min
against http://localhost:8000 — inside the origin gate, no Claude, no human, no
deploy in the loop. Mitigation stays OFF (detect-only): no BIT_APPLY, no token.

Idempotent: rewrites the units only when content differs; enable --now only when
not already active. Requires root (post_deploy context); a permission failure
exits non-zero so the deploy log shows it and the chain retries next deploy.
"""
import os, subprocess, sys

SERVICE = """[Unit]
Description=TrustSquare BIT self-test cycle (Claude-independent)
After=network-online.target marketsquare.service
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/var/www/marketsquare/bit
ExecStart=/usr/bin/python3 /var/www/marketsquare/bit/bit_cycle.py
Environment=BIT_BASE=http://localhost:8000
Nice=10
"""

TIMER = """[Unit]
Description=Run the TrustSquare BIT self-test every 15 minutes (Claude-independent)

[Timer]
OnBootSec=3min
OnUnitActiveSec=15min
AccuracySec=30s
Persistent=true

[Install]
WantedBy=timers.target
"""

def write_if_changed(path, content):
    try:
        if os.path.isfile(path) and open(path, encoding="utf-8").read() == content:
            print("013_bit_timer: unchanged", path)
            return False
    except OSError:
        pass
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print("013_bit_timer: wrote", path)
    return True

def main() -> int:
    apply = "--apply" in sys.argv
    if not apply:
        print("013_bit_timer: dry-run — would install trustsquare-bit.{service,timer}")
        return 0
    if not os.path.isfile("/var/www/marketsquare/bit/bit_cycle.py"):
        print("013_bit_timer: bit/bit_cycle.py not in live root — manifest didn't place it; failing so this retries")
        return 1
    try:
        changed = write_if_changed("/etc/systemd/system/trustsquare-bit.service", SERVICE)
        changed |= write_if_changed("/etc/systemd/system/trustsquare-bit.timer", TIMER)
    except PermissionError as e:
        print("013_bit_timer: need root to write systemd units (%s) — failing so this retries" % e)
        return 1
    if changed:
        subprocess.run(["systemctl", "daemon-reload"], check=True)
    r = subprocess.run(["systemctl", "is-active", "--quiet", "trustsquare-bit.timer"])
    if r.returncode != 0 or changed:
        subprocess.run(["systemctl", "enable", "--now", "trustsquare-bit.timer"], check=True)
        print("013_bit_timer: timer enabled + started")
    else:
        print("013_bit_timer: timer already active")
    subprocess.run(["systemctl", "list-timers", "trustsquare-bit.timer", "--no-pager"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
