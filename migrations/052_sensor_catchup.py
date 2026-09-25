#!/usr/bin/env python3
"""052_sensor_catchup.py -- SENSOR-CATCHUP-1 (25 Sep 2026, DW-157).

The cron sensor runs once a day at 01:30 UTC. On 25 Sep the security assessment's one-time
kernel reboot landed at 01:30:06Z, the run never started, and the daily watch had no parity
reading. This installs /etc/cron.d/marketsquare-sensor-catchup (from ops/sensor/), which
re-invokes `sensor.py --catch-up` after every boot and hourly from 02:45 UTC; the flag makes
it a no-op once today's findings.cron.json exists. Idempotent: re-copies the file.
Reversible without a deploy: rm /etc/cron.d/marketsquare-sensor-catchup
"""
import os, shutil, sys

APPLY = "--apply" in sys.argv
SRC = os.environ.get("MS_SRC", "/opt/marketsquare-src")
UNIT = os.path.join(SRC, "ops", "sensor", "marketsquare-sensor-catchup.cron")
DEST = "/etc/cron.d/marketsquare-sensor-catchup"


def main():
    if not os.path.isfile(UNIT):
        print("052: %s missing" % UNIT)
        return 1
    if not APPLY:
        print("052: dry run -- would install %s" % DEST)
        return 0
    shutil.copyfile(UNIT, DEST)
    os.chmod(DEST, 0o644)      # cron.d files must not be group/world-writable
    ok = "sensor.py --catch-up" in open(DEST).read()
    print("052: sensor catch-up cron installed -- %s" % ("ok" if ok else "CONTENT MISMATCH"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
