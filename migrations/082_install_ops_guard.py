#!/usr/bin/env python3
"""082_install_ops_guard.py -- OPS-GUARD-1 (14 Oct 2026, RUL-230). Installs two systemd timers that run the released
copy of ops/guard/ops_guard.py from /opt/marketsquare-src (read-only checks, no Claude in the loop):
  trustsquare-opsguard-page.timer     hourly  -> orchestrator/v2/subscriptions.html (subscriptions, onboarding, real listers)
  trustsquare-opsguard-nightly.timer  01:40 SAST -> money / data / config checks, guard.html, e-mail to David only when red
Idempotent: rewrites units only when content differs. Needs root (post_deploy); failing exits non-zero so it retries."""
import os, subprocess, sys

PY = "/opt/marketsquare-src/ops/guard/ops_guard.py"
UNITS = {
    "trustsquare-opsguard-page.service": """[Unit]
Description=TrustSquare Ops: subscriptions + onboarding page (OPS-GUARD-1, read-only)
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 %s page
Nice=10
""" % PY,
    "trustsquare-opsguard-page.timer": """[Unit]
Description=Rebuild the Ops subscriptions page every hour (OPS-GUARD-1)

[Timer]
OnBootSec=5min
OnCalendar=*-*-* *:07:00
Persistent=true

[Install]
WantedBy=timers.target
""",
    "trustsquare-opsguard-nightly.service": """[Unit]
Description=TrustSquare nightly checks and balances: money, data, config (OPS-GUARD-1, read-only)
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 %s nightly
TimeoutStartSec=1200
Nice=10
""" % PY,
    "trustsquare-opsguard-nightly.timer": """[Unit]
Description=Run the TrustSquare nightly checks at 01:40 SAST (OPS-GUARD-1)

[Timer]
OnCalendar=*-*-* 23:40:00 UTC
Persistent=true

[Install]
WantedBy=timers.target
""",
}


def main() -> int:
    if "--apply" not in sys.argv:
        print("082_ops_guard: dry-run -- would install", ", ".join(UNITS))
        return 0
    if not os.path.isfile(PY):
        print("082_ops_guard: %s missing -- failing so this retries" % PY)
        return 1
    os.makedirs("/var/lib/trustsquare-ops", exist_ok=True)
    changed = False
    try:
        for name, body in UNITS.items():
            p = "/etc/systemd/system/" + name
            if not (os.path.isfile(p) and open(p, encoding="utf-8").read() == body):
                open(p, "w", encoding="utf-8").write(body)
                changed = True
                print("082_ops_guard: wrote", p)
    except PermissionError as e:
        print("082_ops_guard: need root (%s)" % e)
        return 1
    if changed:
        subprocess.run(["systemctl", "daemon-reload"], check=True)
    for t in ("trustsquare-opsguard-page.timer", "trustsquare-opsguard-nightly.timer"):
        if changed or subprocess.run(["systemctl", "is-active", "--quiet", t]).returncode != 0:
            subprocess.run(["systemctl", "enable", "--now", t], check=True)
    subprocess.run(["systemctl", "start", "trustsquare-opsguard-page.service"])   # first page now, not in an hour
    subprocess.run(["systemctl", "list-timers", "trustsquare-opsguard-*", "--no-pager"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
