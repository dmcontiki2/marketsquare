#!/usr/bin/env python3
"""session_counter.py -- SESSION-COUNTER-1 (22 Aug 2026).

THE single source of truth for "which session number is this".

WHY THIS EXISTS
---------------
David raised it on 22 Aug 2026: the dashboard badge had read "Session 155"
for three weeks and he was certain the real count had gone "way past" it.
He was right, and the reason was worse than a stale number.

There was never a counter. GET /dashboard/summary did this:

    sm = _re2.search(r"Session (\\d+)", status)     # main.py:8545

-- a regex for the FIRST occurrence of the literal text "Session <digits>"
anywhere in STATUS.md, a 329 KB / 2431-line append-only prose file. The line
it happened to land on was line 1650, dated 1 Aug 2026, whose own text reads
"SESSION COUNTER CORRECTED 150 -> 155". The badge was pinned to a sentence
ABOUT the counter having previously frozen.

So freezing was not the failure mode -- freezing was the DEFAULT. Nothing in
the codebase ever incremented anything. The number could only ever change if
a human hand-edited that paragraph. It had been "permanently fixed" twice
before (139->141 in Session 141, 150->155 in Session 155) and both fixes
edited the NUMBER, never the MECHANISM, so each fix had a shelf life of
exactly one session.

THE FIX (two parts, both necessary)
-----------------------------------
1. DERIVE, don't transcribe. The number is computed from evidence that every
   session unavoidably leaves on disk: the status.d/ and changelog.d/
   fragments that STATUS-COLLISION-1 and CHANGELOG-COLLISION-1 make the only
   legal way to record a session. A session that wrote nothing did not
   happen; a session that happened wrote a fragment. The same act that proves
   a session occurred is the act that advances the counter, so it cannot
   silently freeze while work continues.

2. CARRY THE AS-OF DATE. A number alone can lie indefinitely. A number beside
   its own computed_at date confesses: if the badge stops moving, the date
   beside it visibly stops moving too. The dashboard renders both, and
   RG-0154 trips red when the counter falls behind the evidence.

HONESTY ABOUT PRECISION
-----------------------
Distinct session-DAYS is a FLOOR, not an exact count -- two sittings in one
day (Session 154 daytime / 155 evening on 1 Aug is the recorded precedent)
count as one. That is deliberate: an under-count that is provably a floor
beats a confident number nobody can check. Where a session knows it was a
second sitting, it adds a dated entry to "extra_sittings" -- data, not prose.

USAGE
    python3 scripts/session_counter.py            # recompute + write JSON
    python3 scripts/session_counter.py --check    # exit 1 if stale/behind
    python3 scripts/session_counter.py --quiet    # write, print nothing
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
COUNTER = os.path.join(REPO, "SESSION_COUNTER.json")

# Fragment directories. A session records itself in at least one of these --
# that is not a convention, it is enforced by STATUS-COLLISION-1 (status.d)
# and CHANGELOG-COLLISION-1 (changelog.d), both of which forbid editing the
# compiled file directly.
FRAG_DIRS = [
    os.path.join(REPO, "status.d"),
    os.path.join(REPO, "status.d", "folded"),
    os.path.join(REPO, "changelog.d"),
    os.path.join(REPO, "changelog.d", "folded"),
]

DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-")

# The anchor is the last hand-corrected number that David and the record agree
# on: STATUS.md line 1650, 1 Aug 2026 evening. Everything after it is derived.
# NEVER move the anchor to "fix" a number -- that is the old failure. If the
# derivation is wrong, fix the derivation or add an extra_sitting.
DEFAULT_ANCHOR = {"session": 155, "date": "2026-08-01"}


def _load():
    if os.path.exists(COUNTER):
        try:
            with open(COUNTER, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass
    return {}


def sitting_dates(anchor_date):
    """Distinct YYYY-MM-DD fragment dates strictly after the anchor date."""
    seen = set()
    for d in FRAG_DIRS:
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if not name.endswith(".md"):
                continue
            m = DATE_RE.match(name)
            if not m:
                continue
            iso = "%s-%s-%s" % m.groups()
            if iso > anchor_date:
                seen.add(iso)
    return sorted(seen)


def compute():
    prev = _load()
    anchor = prev.get("anchor") or DEFAULT_ANCHOR
    extra = prev.get("extra_sittings") or {}
    dates = sitting_dates(anchor["date"])
    extra_n = sum(int(v) for v in extra.values())
    session = int(anchor["session"]) + len(dates) + extra_n
    return {
        "session": session,
        "computed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "basis": "derived",
        "anchor": anchor,
        "sittings_after_anchor": len(dates),
        "extra_sittings": extra,
        "newest_evidence": dates[-1] if dates else anchor["date"],
        "precision": "floor -- distinct session-days; two sittings in one day count once",
        "source": "scripts/session_counter.py (SESSION-COUNTER-1). Do NOT hand-edit "
                  "this file and do NOT reinstate a prose regex in /dashboard/summary.",
    }


def write(payload):
    if os.path.exists(COUNTER):
        # FUSE mount blocks unlink; a copy-back .bak is the only safe undo.
        try:
            with open(COUNTER, "r", encoding="utf-8") as fh:
                old = fh.read()
            with open(COUNTER + ".bak", "w", encoding="utf-8") as fh:
                fh.write(old)
        except Exception:
            pass
    with open(COUNTER, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    # Prove it landed rather than assuming it did.
    with open(COUNTER, "r", encoding="utf-8") as fh:
        back = json.load(fh)
    assert back["session"] == payload["session"], "SESSION_COUNTER.json write did not land"
    return back


def check():
    """Exit 1 if the stored counter has fallen behind the evidence."""
    stored = _load()
    fresh = compute()
    problems = []
    if not stored:
        problems.append("SESSION_COUNTER.json missing -- the badge has no derived source")
    else:
        if int(stored.get("session", 0)) < fresh["session"]:
            problems.append(
                "counter says %s, evidence on disk says %s -- %d sitting(s) unrecorded"
                % (stored.get("session"), fresh["session"],
                   fresh["session"] - int(stored.get("session", 0))))
        if stored.get("basis") != "derived":
            problems.append("basis is %r, not 'derived' -- something reintroduced a "
                            "hand-set or prose-scraped number" % stored.get("basis"))
    for p in problems:
        print("FAIL: %s" % p)
    if problems:
        return 1
    print("OK: session %s, %d sitting(s) since anchor %s, newest evidence %s"
          % (fresh["session"], fresh["sittings_after_anchor"],
             fresh["anchor"]["date"], fresh["newest_evidence"]))
    return 0


def main(argv):
    if "--check" in argv:
        return check()
    payload = write(compute())
    if "--quiet" not in argv:
        print("session %s (anchor %s + %d sitting(s)%s) computed_at %s"
              % (payload["session"], payload["anchor"]["session"],
                 payload["sittings_after_anchor"],
                 " + %d extra" % sum(int(v) for v in payload["extra_sittings"].values())
                 if payload["extra_sittings"] else "",
                 payload["computed_at"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
