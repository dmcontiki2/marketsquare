#!/usr/bin/env python3
"""
onboarding_number.py -- THE scorer for the onboarding goal (RUL-096 / ONBOARDING_GOAL.md).

WHY THIS EXISTS (found 4 Sep 2026, first unattended run)
--------------------------------------------------------
The contract names probe A as:

    SELECT COUNT(*) FROM prospects WHERE published_at IS NOT NULL

Run against the LIVE server database on 4 Sep 2026 that returns **2**.
Both rows are `source='e2e_test'` seed records -- David himself, his family, and one
hand-added contact. None of them was ever emailed (`emailed_at IS NULL`), so none of
them came from outreach. ONBOARDING_GOAL.md section 3 bars exactly these rows:

    "The seller must be a real person who came from our outreach. Not David, not you,
     not a friend, not a staff account, not a seeded or test record."

So the contract's own probe, taken literally, reports 2 when the honest number is 0.
An instrument that reads high by default is the failure mode CLAUDE.md's evidence
ladder was written to stop -- and the one a goal-driven agent is most tempted by.
This script is the instrument the goal is actually scored on. It reports the honest
number AND the naive number side by side, so the gap can never go quiet again.

WHAT QUALIFIES (all four, no exceptions)
  1. published_at IS NOT NULL      -- they published
  2. emailed_at IS NOT NULL        -- WE COLD-CONTACTED THEM. This is the anti-gaming
                                      leg: a row nobody emailed did not come from
                                      outreach, whatever else is true of it.
  3. source is not a test/seed tag -- e2e_test, and anything containing test/seed/demo
  4. probe B agrees               -- that seller has at least one live listing that a
                                      logged-out member of the public can actually see

The reported number is min(A, B). On disagreement the LOWER one is the truth
(ONBOARDING_GOAL.md section 2).

Usage:  python3 scripts/onboarding_number.py [--json]
Exit 0 always -- this is an instrument, not a gate. It never guesses: anything it
could not measure is printed as UNVERIFIED, never as a healthy zero-shaped number.
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
import sqlite3
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)                    # MarketSquare/
PROJECTS = os.path.dirname(REPO)                # Projects/
LOCAL_PROSPECTS = os.path.join(PROJECTS, "CityLauncher", "data", "prospects.db")

SERVER = "root@178.104.73.239"
SRV_PROSPECTS = "/var/www/citylauncher/data/prospects.db"
SRV_MARKETSQUARE = "/var/www/marketsquare/marketsquare.db"
PUBLIC = "https://trustsquare.co"

# Source tags that are ours, not the public's. Substring match, case-folded.
TEST_SOURCE_MARKERS = ("e2e_test", "test", "seed", "demo", "fixture", "sample")


def _is_test_source(source: str | None) -> bool:
    s = (source or "").strip().lower()
    return any(m in s for m in TEST_SOURCE_MARKERS)


def qualifies(row: dict) -> tuple[bool, list[str]]:
    """THE anti-gaming filter, as one pure function so the ledger can test it directly.

    Returns (counts_toward_the_goal, reasons_it_does_not). Keep it pure and keep it
    here: the moment this logic is inlined somewhere it stops being testable, and an
    untested filter on the goal's own scoreboard is how a manufactured 20 gets born."""
    why: list[str] = []
    if not row.get("published_at"):
        why.append("has not published")
    if not row.get("emailed_at"):
        why.append("never emailed by us -- did not come from outreach")
    if _is_test_source(row.get("source")):
        why.append("test/seed source tag (%s)" % row.get("source"))
    return (not why), why


# --------------------------------------------------------------------------
# transport
# --------------------------------------------------------------------------
def _ssh(script: str, timeout: int = 60) -> str | None:
    """Run python3 on the origin, return stdout, or None if SSH is not available."""
    try:
        # ssh joins argv into a REMOTE SHELL command, so a multi-line script passed
        # as `python3 -c <script>` is word-split by the remote bash and dies. Feed it
        # on stdin to `python3 -` instead -- proven 4 Sep 2026, the first version of
        # this file silently fell back to the stale LOCAL copy because of exactly this.
        r = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=15", "-o", "BatchMode=yes", SERVER,
             "python3", "-"],
            input=script, capture_output=True, text=True, timeout=timeout,
        )
        if r.returncode != 0:
            return None
        return r.stdout
    except Exception:
        return None


def _ensure_ssh() -> None:
    """SSH-BOOTSTRAP-1: the key is on the mount; load it rather than reporting a blocker."""
    loader = os.path.join(REPO, "load_sandbox_ssh.sh")
    if os.path.exists(loader):
        try:
            subprocess.run(["bash", loader], capture_output=True, text=True, timeout=90)
        except Exception:
            pass


def _get(url: str, timeout: int = 25):
    req = urllib.request.Request(url, headers={"User-Agent": "trustsquare-onboarding-number/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception:
        return None, b""


# --------------------------------------------------------------------------
# probe A -- the prospect ledger
# --------------------------------------------------------------------------
SRV_QUERY = r'''
import sqlite3, json
c = sqlite3.connect("file:%s?mode=ro", uri=True)
rows = [dict(zip(("id","email","name","source","city","country","emailed_at","onboarded_at","published_at"), r))
        for r in c.execute(
            "SELECT id,email,name,source,city,country,emailed_at,onboarded_at,published_at "
            "FROM prospects WHERE published_at IS NOT NULL")]
naive = c.execute("SELECT COUNT(*) FROM prospects WHERE published_at IS NOT NULL").fetchone()[0]
funnel = c.execute("SELECT COUNT(*), SUM(emailed_at IS NOT NULL), SUM(onboarded_at IS NOT NULL), "
                   "SUM(published_at IS NOT NULL) FROM prospects").fetchone()
print(json.dumps({"rows": rows, "naive": naive, "funnel": list(funnel)}))
''' % SRV_PROSPECTS


def probe_a() -> dict:
    """Returns {source, naive, rows, qualifying, funnel, note}."""
    out = _ssh(SRV_QUERY)
    if out is None:
        _ensure_ssh()
        out = _ssh(SRV_QUERY)

    if out is not None:
        try:
            data = json.loads(out.strip().splitlines()[-1])
            data["source"] = "server (live)"
            data["note"] = ""
        except Exception:
            data = None
    else:
        data = None

    if data is None:
        # Fall back to the local copy, and SAY it is a fallback. The local file is a
        # pull, not the truth -- on 4 Sep 2026 it read 0 while the server read 2.
        if not os.path.exists(LOCAL_PROSPECTS):
            return {"source": "UNVERIFIED", "naive": None, "rows": [], "qualifying": [],
                    "funnel": None, "note": "no server reachable and no local prospects.db"}
        c = sqlite3.connect(f"file:{LOCAL_PROSPECTS}?mode=ro", uri=True)
        rows = [dict(zip(("id", "email", "name", "source", "city", "country",
                          "emailed_at", "onboarded_at", "published_at"), r))
                for r in c.execute(
                    "SELECT id,email,name,source,city,country,emailed_at,onboarded_at,published_at "
                    "FROM prospects WHERE published_at IS NOT NULL")]
        naive = c.execute("SELECT COUNT(*) FROM prospects WHERE published_at IS NOT NULL").fetchone()[0]
        funnel = list(c.execute("SELECT COUNT(*), SUM(emailed_at IS NOT NULL), "
                                "SUM(onboarded_at IS NOT NULL), SUM(published_at IS NOT NULL) "
                                "FROM prospects").fetchone())
        data = {"rows": rows, "naive": naive, "funnel": funnel,
                "source": "LOCAL COPY (server unreachable) -- may be stale",
                "note": "server unreachable; local copy read instead"}

    qualifying, excluded = [], []
    for r in data["rows"]:
        ok, why = qualifies(r)
        (qualifying if ok else excluded).append({**r, "excluded_because": why})
    data["qualifying"] = qualifying
    data["excluded"] = excluded
    return data


# --------------------------------------------------------------------------
# probe B -- the public's own eyes
# --------------------------------------------------------------------------
def probe_b(emails: list[str]) -> dict:
    """For each qualifying seller email: does the logged-out public see a live listing?"""
    if not emails:
        return {"count": 0, "detail": [], "note": "no qualifying sellers to look for"}

    lit = ",".join("'" + e.replace("'", "''") + "'" for e in emails)
    script = (
        'import sqlite3, json\n'
        f'c = sqlite3.connect("file:{SRV_MARKETSQUARE}?mode=ro", uri=True)\n'
        'q = ("SELECT lower(seller_email), id, listing_status FROM listings '
        f'WHERE lower(seller_email) IN ({lit})")\n'
        'print(json.dumps([list(r) for r in c.execute(q)]))\n'
    )
    out = _ssh(script)
    if out is None:
        return {"count": None, "detail": [], "note": "UNVERIFIED -- could not read listings on the origin"}
    try:
        rows = json.loads(out.strip().splitlines()[-1])
    except Exception:
        return {"count": None, "detail": [], "note": "UNVERIFIED -- unreadable listings response"}

    # The public feed is the arbiter: a row marked live in the DB still has to RENDER.
    status, body = _get(f"{PUBLIC}/listings?limit=500")
    public_ids = set()
    if status == 200:
        try:
            public_ids = {int(x.get("id")) for x in json.loads(body.decode("utf-8", "replace"))
                          if x.get("id") is not None}
        except Exception:
            pass

    detail, seen = [], set()
    for email, lid, lstatus in rows:
        visible = (str(lstatus).lower() == "live") and (int(lid) in public_ids)
        detail.append({"email": email, "listing_id": lid, "listing_status": lstatus,
                       "visible_to_public": visible})
        if visible:
            seen.add(email)
    return {"count": len(seen), "detail": detail,
            "note": "" if status == 200 else f"public feed returned {status}"}


# --------------------------------------------------------------------------
def main() -> int:
    a = probe_a()
    qual_emails = [str(r["email"]).lower() for r in a.get("qualifying", []) if r.get("email")]
    b = probe_b(qual_emails)

    a_n = len(a.get("qualifying", [])) if a["source"] != "UNVERIFIED" else None
    b_n = b["count"]
    if a_n is None or b_n is None:
        number = "UNVERIFIED"
    else:
        number = min(a_n, b_n)

    if "--json" in sys.argv:
        print(json.dumps({"number": number, "probe_a": a_n, "probe_b": b_n,
                          "naive_probe_a": a.get("naive"), "detail": {"a": a, "b": b}},
                         indent=2, default=str))
        return 0

    bar = "=" * 78
    print(bar)
    print("  THE ONBOARDING NUMBER -- people we contacted cold who published by their own hand")
    print(bar)
    print(f"  read from : {a['source']}")
    if a.get("note"):
        print(f"  note      : {a['note']}")
    print()
    print(f"  NUMBER TODAY : {number}        (target 20 by Fri 31 Oct 2026)")
    print()
    print(f"  probe A -- prospect ledger, qualifying rows only : {a_n}")
    print(f"  probe B -- seen by a logged-out visitor           : {b_n}")
    if b.get("note"):
        print(f"           {b['note']}")
    print()
    naive = a.get("naive")
    if naive is not None and a_n is not None and naive != a_n:
        print(f"  !! the contract's raw query would say {naive}. It is wrong by {naive - a_n}.")
        print("     Rows it counts that the goal bars (ONBOARDING_GOAL.md section 3):")
        for r in a.get("excluded", []):
            print(f"       - {r.get('name')} <{r.get('email')}>  [{r.get('source')}]")
            for w in r["excluded_because"]:
                print(f"           {w}")
        print()
    f = a.get("funnel")
    if f:
        total, emailed, onboarded, published = (f + [None] * 4)[:4]
        print(f"  funnel : {total} on the list · {emailed} emailed · "
              f"{onboarded or 0} registered · {published or 0} published (raw)")
    print(bar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
