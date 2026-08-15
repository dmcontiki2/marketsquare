#!/usr/bin/env python3
# test_pg_readiness.py - the Postgres-readiness RATCHET (29 Jul 2026, David's DB ruling:
# launch on SQLite; keep the later Postgres move CHEAP by never letting the
# SQLite-specific surface grow). Counts SQLite-isms in bea_main.py against the
# recorded baseline: growth FAILS (write the new code portably instead);
# shrinkage auto-tightens the baseline. Runs standalone or via predeploy_check.
import json, os, re, sys

HERE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "scripts", "pg_readiness_baseline.json")
PATTERNS = {
    "datetime_now": r"datetime\('now'",
    # PG-RATCHET-PRECISION-1 (15 Aug 2026): was r"strftime\(" -- which also matched PYTHON's
    # datetime.strftime(), a portable stdlib call with nothing to do with SQLite or the
    # Postgres move. 25 of the 40 hits were Python. Adding ordinary date formatting anywhere
    # in bea_main.py therefore tripped the ratchet, put DANGER on the pre-deploy scan, and in
    # STRICT mode (nightly_ship) aborted the unattended release. The guard measured a regex,
    # not the invariant. Negative lookbehind excludes the method call; bare strftime( is SQL.
    "strftime":     r"(?<!\.)strftime\(",
    "julianday":    r"julianday\(",
    "insert_or":    r"INSERT OR (?:IGNORE|REPLACE)",
}

def counts():
    src = open(os.path.join(HERE, "bea_main.py"), encoding="utf-8", errors="replace").read()
    return {k: len(re.findall(p, src)) for k, p in PATTERNS.items()}

def test_sqlite_surface_never_grows():
    cur = counts()
    if not os.path.isfile(BASE):
        json.dump(cur, open(BASE, "w"), indent=1, sort_keys=True); return
    base = json.load(open(BASE))
    grew = {k: (base.get(k, 0), v) for k, v in cur.items() if v > base.get(k, 0)}
    assert not grew, ("SQLite-specific surface GREW %s - write it portably "
                      "(helpers/portable SQL) so the Postgres move stays cheap" % grew)
    if any(v < base.get(k, 0) for k, v in cur.items()):
        json.dump(cur, open(BASE, "w"), indent=1, sort_keys=True)  # ratchet tightens

if __name__ == "__main__":
    try:
        test_sqlite_surface_never_grows()
        print("PASS  pg-readiness ratchet:", counts())
        sys.exit(0)
    except AssertionError as e:
        print("FAIL ", e); sys.exit(1)
