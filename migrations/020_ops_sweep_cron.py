#!/usr/bin/env python3
"""020: install the OPS-SWEEP-1 cron (Report & Fix, David 15 Aug 2026).

Idempotent: rewrites /etc/cron.d/marketsquare-ops-sweep. The sweep itself is
deployed by the manifest as <live>/ops_sweep.py; it emails David on amber/red
state changes and queues his FIX/REVIEW email replies for Fable's pickup run.
"""
import os, sys

CRON = "/etc/cron.d/marketsquare-ops-sweep"
LINE = ("*/15 * * * * root cd /var/www/marketsquare && "
        "python3 ops_sweep.py --cron >> /var/log/ops_sweep.log 2>&1\n")

def main():
    if "--apply" not in sys.argv:
        print("dry: would write", CRON); return 0
    with open(CRON, "w") as f:
        f.write("# OPS-SWEEP-1 - amber/red email reports for David (migrations/020)\n" + LINE)
    os.chmod(CRON, 0o644)
    # cron.d is picked up automatically; touch the log so it exists with sane perms
    open("/var/log/ops_sweep.log", "a").close()
    print("installed", CRON)
    return 0

if __name__ == "__main__":
    sys.exit(main())
