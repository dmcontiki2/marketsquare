#!/usr/bin/env python3
"""scripts/standup_freshness.py -- STANDUP-WATCHDOG-1 (23 Sep 2026).

WHY THIS EXISTS
---------------
The daily stand-up is the safety net. Twice in ten days the net itself vanished and
NOTHING NOTICED:

  * 14-18 Sep 2026 -- five days. Recorded in the onboarding-goal task's own prompt:
    "the scheduled task was then lost and no run happened 14-18 Sep".
  * 21-22 Sep 2026 -- two days. No PULSE_LOG line, no OPEN_LOOPS reconciliation, and
    zero commits. Both scheduled tasks show updated_at = 2026-09-23T16:47:38Z -- the
    same second -- and the stand-up then fired at 16:48 instead of its 19:00 slot.
    Its cron ("0 19 * * *") was correct the whole time; the REGISTRATION was lost.

The canon already says "an unlogged pulse is an unrun pulse". It had no way to tell.
A missing run leaves no trace anywhere except an absence, and nobody reads absences.

WHAT THIS DOES
--------------
Turns the absence into a positive assertion: the newest dated line in PULSE_LOG.md must
be younger than MAX_AGE_H. It needs no scheduler of its own -- it is meant to be called by
something that has ALREADY PROVEN it runs when the stand-up does not. That is the
maintenance loop: it ticked 05:21 / 11:20 / 17:20 on 21 and 22 Sep, the exact two days
the stand-up was missing, and the +1 dashboard carries its heartbeat.

Deliberately NOT wired into scripts/maintenance_agent.py in the session that wrote this:
that file was being edited by another lane at the time (RUL-140 stand-off). The wiring is
one line next to the backup lane's -- report["standup"] = ... -- and belongs in whichever
session next holds that file with a quiet tree.

Exit 0 = fresh.  Exit 1 = STALE (the stand-up has stopped).  Exit 2 = cannot tell.
Run:  python3 scripts/standup_freshness.py [--max-age-h 30] [--json]
"""
import datetime as _dt
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(REPO, "PULSE_LOG.md")
MAX_AGE_H = 30.0          # one daily slot + a 6 h grace, so a late run is not a false alarm

# A pulse line begins with, or contains early on, an ISO date. Both shapes exist in the log:
#   "2026-09-23 16:5xZ (stand-up) ..."   and   "\U0001F7E2 2026-08-01 trustsquare.co up ..."
_DATE = re.compile(r"(20\d\d)-(\d\d)-(\d\d)")


def newest_pulse_date(text):
    """Latest date mentioned at the START of any line (first 40 chars). Reading the whole
    line would pick up dates quoted inside a narrative and report a freshness that is not
    there -- the same class of mistake as a probe that cannot return a negative."""
    best = None
    for line in text.splitlines():
        head = line.strip()[:40]
        m = _DATE.search(head)
        if not m:
            continue
        try:
            d = _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        if best is None or d > best:
            best = d
    return best


def check(max_age_h=MAX_AGE_H, now=None):
    now = now or _dt.datetime.now(_dt.timezone.utc)
    if not os.path.isfile(LOG):
        return {"state": "UNKNOWN", "reason": "PULSE_LOG.md missing", "age_h": None,
                "newest": None}
    text = open(LOG, encoding="utf-8", errors="replace").read()
    newest = newest_pulse_date(text)
    if newest is None:
        return {"state": "UNKNOWN", "reason": "no dated pulse line found", "age_h": None,
                "newest": None}
    # Compare against END of that day: a line dated today is 0 h old whatever time it was written.
    end = _dt.datetime.combine(newest, _dt.time(23, 59, 59), tzinfo=_dt.timezone.utc)
    age_h = max(0.0, (now - end).total_seconds() / 3600.0)
    state = "STALE" if age_h > max_age_h else "FRESH"
    reason = ("newest pulse line is dated %s, %.1f h ago -- the stand-up has stopped running; "
              "its scheduled task has been lost twice (14-18 Sep, 21-22 Sep 2026)"
              % (newest.isoformat(), age_h)) if state == "STALE" else \
             "newest pulse line is dated %s (%.1f h)" % (newest.isoformat(), age_h)
    return {"state": state, "reason": reason, "age_h": round(age_h, 1),
            "newest": newest.isoformat()}


def main():
    max_age = MAX_AGE_H
    if "--max-age-h" in sys.argv:
        max_age = float(sys.argv[sys.argv.index("--max-age-h") + 1])
    r = check(max_age)
    if "--json" in sys.argv:
        print(json.dumps(r))
    else:
        print("STANDUP-WATCHDOG-1: %s -- %s" % (r["state"], r["reason"]))
    return {"FRESH": 0, "STALE": 1}.get(r["state"], 2)


if __name__ == "__main__":
    sys.exit(main())
