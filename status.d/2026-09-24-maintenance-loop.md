### Maintenance loop — 24 Sep 2026 (07:40–08:20Z)

Fault queue empty (0 new · 0 fix-shipped · 26 verified · 12 closed); heartbeat 20260924T075001Z
read back from `/dashboard/maint`; no escalation brief; backup lane skipped (archive 14.8 h old).

Board started RED with 3 regressions and ends GREEN: 438 entries · 417 holding · 0 regressed ·
21 open · 0 ready to lock · 0 unverified. One was real (PHONE-KEY-1 re-introduced the SQLite
clock in `bea_main.py` -- fixed, rides tonight's TSL); two were spelling-checks broken by
legitimate code changes (RG-0413, RG-0431 -- now assert the property). Of four READY TO LOCK
prints, two were malformed entries (date in the state slot -- new guard RG-0451 refuses that at
import) and one (RG-0437) was a false print over an unbuilt fix -- built it (rulings_check now
reads through settled_read), then locked. Committed, not pushed (NIGHTLY-SHIP-1 ships it).
