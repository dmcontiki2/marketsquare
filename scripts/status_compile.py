#!/usr/bin/env python3
"""status_compile.py — STATUS-COLLISION-1 (5 Aug 2026).

THE single writer for STATUS.md's session narrative, modelled exactly on
scripts/changelog_compile.py (CHANGELOG-COLLISION-1, 2 Aug).

WHY THIS EXISTS
---------------
On 5 Aug a session wrote an addendum into STATUS.md at 15:57Z. By the 18:09
release commit the paragraph was GONE — clobbered on disk, not lost in git, no
error raised. The changelog fragment written in the same minute survived and
folded correctly. The difference was not luck: CHANGELOG.md had a fragment
mechanism and STATUS.md did not. This closes that asymmetry.

HOW TO USE IT
-------------
Never edit the `## Current Session` block by hand. Drop a NEW file:

    status.d/YYYY-MM-DD-<slug>.md

containing the dated paragraph(s) exactly as they should appear. Creating a new
file cannot collide with another session. This compiler folds every pending
fragment in directly beneath the `## Current Session` heading (newest-first by
filename) and archives each to status.d/folded/, so a re-run is a no-op.

    python scripts/status_compile.py           # fold pending fragments
    python scripts/status_compile.py --check   # exit 1 if fragments pending (no writes)

Safe: no-op when status.d/ is empty; preserves STATUS.md line endings; refuses to
write if the anchor heading is missing rather than guessing where to insert.
"""
import datetime, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAG_DIR = os.path.join(ROOT, "status.d")
FOLDED = os.path.join(FRAG_DIR, "folded")
STATUS = os.path.join(ROOT, "STATUS.md")
ANCHOR = b"## Current Session"


def main():
    check = "--check" in sys.argv
    if not os.path.isdir(FRAG_DIR):
        print("status.d/ absent - nothing to fold.")
        return 0
    frags = sorted(
        (f for f in os.listdir(FRAG_DIR)
         if f.lower().endswith(".md") and os.path.isfile(os.path.join(FRAG_DIR, f))),
        reverse=True)
    if not frags:
        print("no pending fragments.")
        return 0
    if check:
        print("%d pending fragment(s): %s" % (len(frags), ", ".join(frags)))
        return 1

    with open(STATUS, "rb") as fh:
        raw = fh.read()
    nl = b"\r\n" if b"\r\n" in raw[:4096] else b"\n"

    flat = raw.replace(b"\r\n", b"\n")
    if flat.count(ANCHOR) != 1:
        # Refuse rather than guess. A wrong insertion point in STATUS.md breaks the
        # dashboard's session-counter parse, which reads the FIRST match in the file.
        print("REFUSED: '%s' appears %d times in STATUS.md - expected exactly 1."
              % (ANCHOR.decode(), flat.count(ANCHOR)))
        return 2

    parts, folded_names = [], []
    for f in frags:
        with open(os.path.join(FRAG_DIR, f), "rb") as fh:
            body = fh.read().replace(b"\r\n", b"\n").strip(b"\n")
        head_line = body.split(b"\n", 1)[0].strip()
        if head_line and head_line in flat:
            print("skip (already present): %s" % f)
            folded_names.append(f)
            continue
        parts.append(body.replace(b"\n", nl))
        folded_names.append(f)

    if parts:
        block = (nl + nl).join(parts) + nl + nl
        i = raw.find(ANCHOR.replace(b"\n", nl))
        if i < 0:
            i = raw.find(ANCHOR)
        j = raw.find(nl, i)
        if j < 0:
            print("REFUSED: could not find the end of the anchor line.")
            return 2
        j += len(nl)
        while raw[j:j + len(nl)] == nl:          # skip the blank line after the heading
            j += len(nl)
        tmp = STATUS + ".compile-tmp"
        with open(tmp, "wb") as fh:
            fh.write(raw[:j] + block + raw[j:])
        os.replace(tmp, STATUS)                  # atomic on the same filesystem

    os.makedirs(FOLDED, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for f in folded_names:
        dst = os.path.join(FOLDED, f)
        if os.path.exists(dst):
            dst = os.path.join(FOLDED, "%s.%s" % (f, stamp))
        shutil.move(os.path.join(FRAG_DIR, f), dst)

    ok = True
    if parts:
        with open(STATUS, "rb") as fh:
            head = fh.read(len(raw[:raw.find(ANCHOR)]) + len(block) + 4096)
        ok = parts[0][:60] in head
    print("folded %d, skipped %d (already present) - verify %s"
          % (len(parts), len(folded_names) - len(parts), "OK" if ok else "FAILED"))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
