#!/usr/bin/env python3
"""050_qa_bot_nightly.py -- QA-BOT-1 (David, 24 Sep 2026, in chat: "the tester should not be a
human tester. I am a one man owner, i need you to create an independent QA Bot to perform the audit").

Installs the QA Bot's nightly run on the box: ops/qabot/trustsquare-qabot.{service,timer} into
/etc/systemd/system, then enables the timer (02:30 SAST). The bot itself ships in qa_bot/ and runs
from the deployed source clone; its rulings and history live only in /var/lib/trustsquare-qabot.
Idempotent: re-copies the units and re-enables the timer. Reversible without a deploy:
  systemctl disable --now trustsquare-qabot.timer
"""
import os, shutil, subprocess, sys

APPLY = "--apply" in sys.argv
SRC = os.environ.get("MS_SRC", "/opt/marketsquare-src")
UNITS = ("trustsquare-qabot.service", "trustsquare-qabot.timer")


def main():
    missing = [u for u in UNITS if not os.path.isfile(os.path.join(SRC, "ops", "qabot", u))]
    if missing:
        print("050: unit files missing from %s/ops/qabot: %s" % (SRC, missing))
        return 1
    if not APPLY:
        print("050: dry run -- would install %s and enable the timer" % ", ".join(UNITS))
        return 0
    os.makedirs("/var/lib/trustsquare-qabot", exist_ok=True)
    for u in UNITS:
        shutil.copyfile(os.path.join(SRC, "ops", "qabot", u), os.path.join("/etc/systemd/system", u))
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", "--now", "trustsquare-qabot.timer"], check=True)
    out = subprocess.run(["systemctl", "is-active", "trustsquare-qabot.timer"], capture_output=True, text=True).stdout.strip()
    print("050: QA Bot nightly timer installed -- %s" % out)
    return 0 if out == "active" else 1


if __name__ == "__main__":
    sys.exit(main())
