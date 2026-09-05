#!/usr/bin/env python3
"""sync_admin_gate.py -- inline the ONE admin-gate source into every admin surface.

GATE-ONESOURCE-1 (5 Sep 2026), closing RG-0196 -- the consolidation RG-0075 was
written for and that had been deferred since 27 Aug.

THE PROBLEM IT RETIRES
  The admin gate was written once in May 2026 and COPIED into three admin surfaces.
  Every fix since had to be made three times, and repeatedly was not: on 27 Aug two
  copies were eight days behind a correction that told David his CORRECT password was
  a wrong reviewer code, on the copy he actually opens. On 5 Sep they had drifted
  again -- DEVICE-ENROL-1 (3 Sep) had reached two of the three.

WHY INLINE INSTEAD OF <script src>
  dashboard.html is opened over file://. A page at origin 'null' cannot load
  /static/admin_gate.js, so the obvious fix would break the very consumer that has
  been missing every gate fix. Inlining from one source gives the single-edit
  property without changing how any page is served. This was the stated blocker in
  RG-0196's own ref; it is answered here rather than argued with.

USAGE
  python3 scripts/sync_admin_gate.py            # write the source into every copy
  python3 scripts/sync_admin_gate.py --check    # report divergence, change nothing

SAFETY
  * Byte-exact: every copy gets the source verbatim, then the file is re-read and the
    block compared again. A write that did not land is an error, not a shrug -- this
    repo's mount has truncated large writes before.
  * A backup is written beside each file before it is touched (*.bak-* is gitignored).
  * The markers are installed once, on first run, by locating the existing block with
    the same anchors the ledger uses. After that the markers are the contract.
"""
import argparse, difflib, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "shared" / "admin_gate.js"
TARGETS = ("dashboard.server.html", "dashboard.html", "marketsquare_admin.html")

BEGIN = "/* ADMIN-GATE-SRC:BEGIN -- generated from shared/admin_gate.js by scripts/sync_admin_gate.py. DO NOT EDIT BELOW; edit the source and re-run. (GATE-ONESOURCE-1) */"
END   = "/* ADMIN-GATE-SRC:END */"


def source_body() -> str:
    """The gate code itself -- the file's own banner comment is documentation for a
    human reading the source, not something to paste into three HTML files."""
    t = SOURCE.read_text(encoding="utf-8")
    marker = "   ═══════════════════════════════════════════════════════════════════════════ */\n"
    return t.split(marker, 1)[1].rstrip("\n") if marker in t else t.rstrip("\n")


def locate(lines):
    """Find the gate block. Markers win; otherwise fall back to the structural anchors
    (first run only). Returns (start, end) inclusive indices, or None."""
    b = next((i for i, l in enumerate(lines) if BEGIN.strip() in l), None)
    if b is not None:
        e = next((i for i in range(b + 1, len(lines)) if END.strip() in lines[i]), None)
        if e is None:
            raise SystemExit("REFUSE: a BEGIN marker with no END -- hand-repair needed")
        return b, e
    try:
        a = next(i for i, l in enumerate(lines) if l.strip().startswith("function showLoginError("))
        p = next(i for i, l in enumerate(lines) if "window.adminGateChangePIN = function()" in l)
    except StopIteration:
        return None
    ind = len(lines[p]) - len(lines[p].lstrip())
    e = next((i for i in range(p + 1, len(lines))
              if lines[i].strip() == "};" and (len(lines[i]) - len(lines[i].lstrip())) == ind), None)
    return (a, e) if e is not None else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    a = ap.parse_args()
    if not SOURCE.exists():
        print("REFUSE: %s is missing -- there is no source to sync from" % SOURCE)
        return 2
    body = source_body()
    want = BEGIN + "\n" + body + "\n" + END
    rc, changed = 0, []
    for rel in TARGETS:
        p = REPO / rel
        if not p.exists():
            print("[skip] %-26s not in the repo" % rel)
            continue
        text = p.read_text(encoding="utf-8")
        lines = text.splitlines()
        span = locate(lines)
        if span is None:
            print("[FAIL] %-26s no admin gate found -- anchors gone, hand-repair needed" % rel)
            rc = 1
            continue
        s, e = span
        have = "\n".join(lines[s:e + 1])
        if have == want:
            print("[ ok ] %-26s in sync" % rel)
            continue
        if a.check:
            d = list(difflib.unified_diff(have.splitlines(), want.splitlines(),
                                          "copy", "source", lineterm="", n=0))
            print("[DIFF] %-26s %d differing line(s)" % (rel, sum(1 for l in d if l[:1] in "+-" and l[:3] not in ("+++", "---"))))
            rc = 1
            continue
        p.with_suffix(p.suffix + ".bak-gate-%s" % time.strftime("%Y%m%d-%H%M%S")).write_text(text, encoding="utf-8")
        out = "\n".join(lines[:s] + want.splitlines() + lines[e + 1:])
        if text.endswith("\n"):
            out += "\n"
        p.write_text(out, encoding="utf-8")
        # PROVE it landed. This mount has silently truncated large writes before.
        back = p.read_text(encoding="utf-8")
        if want not in back:
            print("[FAIL] %-26s the write did NOT land -- restore from the .bak beside it" % rel)
            rc = 1
            continue
        changed.append(rel)
        print("[sync] %-26s updated from shared/admin_gate.js" % rel)
    if changed:
        print("\n%d file(s) updated. The gate now has ONE source: shared/admin_gate.js" % len(changed))
    elif rc == 0:
        print("\nAll copies match the source. Nothing to do.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
