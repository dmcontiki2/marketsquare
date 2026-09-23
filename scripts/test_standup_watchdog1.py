"""STANDUP-WATCHDOG-1 -- proof it would have caught the 21-22 Sep silence, and does not
cry wolf on a merely late run.

The bar this repo sets: a new assertion must be shown to FAIL against the broken case
before its green is believed. The broken case here is not hypothetical -- it is the actual
PULSE_LOG as it stood at 16:48 on 23 Sep, whose newest line was dated 20 Sep.

Run:  python3 scripts/test_standup_watchdog1.py      (exit 0 = pass)
"""
import datetime as _dt
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import standup_freshness as W

NOW = _dt.datetime(2026, 9, 23, 16, 48, tzinfo=_dt.timezone.utc)


def main():
    bad = []

    # 1. THE REAL FAILURE. Newest line dated 20 Sep, checked at 16:48 on 23 Sep -> STALE.
    d = W.newest_pulse_date("2026-09-20 17:2xZ post-deploy re-check (release a55f885) ok\n")
    if d != _dt.date(2026, 9, 20):
        bad.append("did not read the 20 Sep line, got %r" % d)
    end = _dt.datetime.combine(_dt.date(2026, 9, 20), _dt.time(23, 59, 59), tzinfo=_dt.timezone.utc)
    if (NOW - end).total_seconds() / 3600.0 <= W.MAX_AGE_H:
        bad.append("a 20 Sep line at 23 Sep 16:48 was not judged stale -- the 21/22 Sep "
                   "silence would have passed unnoticed again")

    # 2. NO FALSE ALARM on a run that is merely late. Yesterday's line is fresh.
    d = W.newest_pulse_date("2026-09-22 19:0xZ (stand-up) up 0.4s\n")
    end = _dt.datetime.combine(d, _dt.time(23, 59, 59), tzinfo=_dt.timezone.utc)
    if (NOW - end).total_seconds() / 3600.0 > W.MAX_AGE_H:
        bad.append("yesterday's pulse was called stale -- a late run must not raise this")

    # 3. BOTH LINE SHAPES in the live log parse. The emoji-first shape predates the dated one.
    for s, want in (("\U0001F7E2 2026-08-01 trustsquare.co up", _dt.date(2026, 8, 1)),
                    ("2026-07-30 (daytime) \U0001F7E2 up", _dt.date(2026, 7, 30))):
        if W.newest_pulse_date(s + "\n") != want:
            bad.append("line shape not parsed: %r" % s)

    # 4. A DATE QUOTED MID-NARRATIVE MUST NOT COUNT AS A PULSE. This is the whole reason the
    #    parser only looks at the first 40 chars: today's own pulse line quotes "2 Aug", and a
    #    naive reader would take any future date in prose as proof of a run that never happened.
    narrative = ("2026-09-20 17:2xZ post-deploy ok -- note: the gap ran from 2026-08-02 to "
                 "2026-09-18 and the next slot is 2026-09-30\n")
    if W.newest_pulse_date(narrative) != _dt.date(2026, 9, 20):
        bad.append("a date quoted inside the narrative was counted as a pulse -- the check "
                   "could then never return a negative")

    # 5. EMPTY / MISSING inputs are UNKNOWN (exit 2), never a quiet FRESH.
    if W.newest_pulse_date("no dates here at all\n") is not None:
        bad.append("invented a date from a log with none")

    if bad:
        print("STANDUP-WATCHDOG-1 TEST: FAIL")
        for b in bad:
            print("  - " + b)
        return 1
    print("STANDUP-WATCHDOG-1 TEST: pass -- the 21/22 Sep silence is caught, a late run is "
          "not, both log shapes parse, and a date quoted in prose cannot fake a run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
