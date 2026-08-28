#!/usr/bin/env python3
"""DAVID QUEUE — serve David's open actions ONE AT A TIME, verified against evidence.

Why this exists (DAVID-QUEUE-1, 27 Aug 2026)
--------------------------------------------
David works in gaps between other work and asked for the open actions one at a time. The
failure mode that had to be designed out is not "forgetting the list" -- it is the list
going STALE across a session break, which is the project's oldest recurring fault. Two items
sat in the David column for six days across five sweeps and NEITHER was David's (the Google
consent screen and the domain registrar); both closed in minutes once somebody actually
looked. A queue that only a human reconciles reproduces exactly that.

So every item carries a VERIFY method and this script RE-CHECKS it on every run:

  LEDGER:<id>   the regression-ledger entry -- done when it stops failing.  Strongest.
  FIELD:<name>  a MACHINE-READ field in THIRD_PARTY_LAUNCH_REGISTER.md -- done when filled.
  DAVID         nothing can see it. Closes only on David's word, and the date is recorded.

The grades are deliberately unequal and are printed, because a DAVID-verified "done" is a
weaker fact than a probed one and must never be reported as though it were the same thing
(the CLAUDE.md evidence ladder). An item whose VERIFY says DAVID and whose STATE says OPEN is
simply unknown -- this script says so rather than guessing.

Exit codes:  0 = nothing open  ·  1 = at least one item open (normal during a launch run)
"""
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(REPO, "DAVID_QUEUE.md")
REGISTER = os.path.join(REPO, "THIRD_PARTY_LAUNCH_REGISTER.md")
UNKNOWN = ("", "unknown", "tbd", "-", "none")


def _items():
    """Parse the queue. One dict per '## Dn · title' block."""
    if not os.path.exists(QUEUE):
        sys.exit("DAVID_QUEUE.md is missing -- the queue is the artefact, not this script.")
    raw = open(QUEUE, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"^## (D\d+) · (.+?)$(.*?)(?=^## D\d+ ·|\Z)",
                         raw, re.M | re.S):
        body = m.group(3)

        def f(name, default=""):
            g = re.search(r"^%s:\s*(.+)$" % name, body, re.M)
            return g.group(1).strip() if g else default

        out.append({"id": m.group(1), "title": m.group(2).strip(),
                    "state": f("STATE", "OPEN").upper(), "time": f("TIME", "?"),
                    "verify": f("VERIFY", "DAVID"), "why": f("WHY_DAVID"),
                    "steps": _block(body, "STEPS"), "context": _block(body, "CONTEXT")})
    return out


def _block(body, name):
    m = re.search(r"^%s:\s*(.*?)(?=^[A-Z_]+:|\Z)" % name, body, re.M | re.S)
    return m.group(1).strip() if m else ""


def _register_field(name):
    if not os.path.exists(REGISTER):
        return None
    m = re.search(r"^%s:\s*(.+)$" % name, open(REGISTER, encoding="utf-8").read(), re.M)
    return m.group(1).strip() if m else ""


_LEDGER_CACHE = {}


def _ledger_state(rid):
    """Read the ledger board once. Returns 'ok' / 'open' / None (could not run)."""
    if not _LEDGER_CACHE:
        led = os.path.join(REPO, "scripts", "regression_ledger.py")
        if not os.path.exists(led):
            _LEDGER_CACHE["__dead__"] = True
            return None
        try:
            p = subprocess.run([sys.executable, led], cwd=REPO, timeout=600,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout.decode("utf-8", "replace").splitlines():
                g = re.match(r"^\[([^\]]+)\]\s+(RG-\d+)", line)
                if g:
                    _LEDGER_CACHE[g.group(2)] = g.group(1).strip().lower()
        except Exception:
            _LEDGER_CACHE["__dead__"] = True
            return None
    if _LEDGER_CACHE.get("__dead__"):
        return None
    return _LEDGER_CACHE.get(rid)


def evaluate(it):
    """(done, evidence). done=None means UNKNOWN -- never treated as done."""
    v = it["verify"]
    if v.startswith("LEDGER:"):
        rid = v.split(":", 1)[1].strip()
        st = _ledger_state(rid)
        if st is None:
            return None, "ledger could not be run here -- UNVERIFIED, not done"
        if st == "ok":
            return True, "%s is holding on the live board" % rid
        return False, "%s still reports open" % rid
    if v.startswith("FIELD:"):
        name = v.split(":", 1)[1].strip()
        val = _register_field(name)
        if val is None:
            return None, "register not found -- UNVERIFIED"
        if val.strip().lower() in UNKNOWN or val.upper().startswith("UNKNOWN"):
            return False, "%s is still UNKNOWN in the register" % name
        return True, "%s = %s" % (name, val[:70])
    # DAVID: only his word closes it, and the file records that word.
    if it["state"].startswith("DONE"):
        return True, "David confirmed (%s)" % it["state"]
    return False, "no instrument can see this -- awaiting David's word"


def main():
    show_all = "--all" in sys.argv
    items = _items()

    # --check is for MACHINERY (ledger RG-0199), not for David. It answers only
    # "is this runner sound and is every item verifiable" and so exits 0 even with
    # a full queue -- an open queue is the normal state and must never read as a
    # broken instrument. The human modes below keep exit 1 = work outstanding.
    if "--check" in sys.argv:
        bad = [i["id"] for i in items
               if not (i["verify"].startswith(("LEDGER:", "FIELD:")) or i["verify"] == "DAVID")]
        if not items:
            print("CHECK FAIL: queue parses to zero items")
            return 1
        if bad:
            print("CHECK FAIL: no usable VERIFY on %s" % ", ".join(bad))
            return 1
        print("CHECK OK: %d item(s), every one with a stated verification method" % len(items))
        return 0

    rows = []
    for it in items:
        done, why = evaluate(it)
        rows.append((it, done, why))

    open_rows = [r for r in rows if r[1] is not True]

    print("=" * 78)
    print("DAVID QUEUE — %d item(s), %d still open" % (len(rows), len(open_rows)))
    print("=" * 78)

    if show_all or not open_rows:
        for it, done, why in rows:
            mark = "DONE" if done else ("????" if done is None else "open")
            print("  [%s] %-4s %-58s %s" % (mark, it["id"], it["title"][:58], it["time"]))
        print()

    if not open_rows:
        print("Nothing open. Every item verified.")
        return 0

    it, done, why = open_rows[0]
    print()
    print("NEXT — %s · %s" % (it["id"], it["title"]))
    print("-" * 78)
    print("Takes:        %s" % it["time"])
    print("Only you:     %s" % (it["why"] or "—"))
    print("Closes when:  %s   (now: %s)" % (it["verify"], why))
    if it["steps"]:
        print("\nDO:\n%s" % it["steps"])
    if it["context"]:
        print("\nWHY IT MATTERS:\n%s" % it["context"])
    print("-" * 78)
    rest = [r[0]["id"] for r in open_rows[1:]]
    if rest:
        print("Then, in order: %s" % ", ".join(rest))
    return 1


if __name__ == "__main__":
    sys.exit(main())
