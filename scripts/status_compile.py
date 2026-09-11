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
import datetime, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAG_DIR = os.path.join(ROOT, "status.d")
FOLDED = os.path.join(FRAG_DIR, "folded")
STATUS = os.path.join(ROOT, "STATUS.md")
ANCHOR = b"## Current Session"

# DASH-FEED-1 (11 Sep 2026) -- the managed dashboard-feed block.
# GET /dashboard/summary reads the FIRST "## Last Completed" heading anywhere in this
# 300 KB append-only file. Sessions write under "## Current Session", so for 22 days the
# dashboard faithfully rendered work from 2026-08-20 while every session added fresh
# paragraphs the endpoint could not see (RG-0127 red). CLASS fix, not a re-date: every
# fold now also rewrites ONE marker-delimited block placed ABOVE the first existing
# "## Last Completed", so whatever a session actually folded is what the dashboard reads.
# The block is rewritten wholesale each run, so it can never accumulate.
FEED_BEGIN = "<!-- DASH-FEED-1:BEGIN (managed by scripts/status_compile.py - do not edit by hand) -->"
FEED_END = "<!-- DASH-FEED-1:END -->"


def _fragment_title(fname, body_text):
    """A short human title for the managed heading: the fragment's own bold lead if it
    has one, else the filename slug."""
    # A real markdown heading in the fragment is the best title available.
    m = re.search(r"^#{2,4}\s+(.+?)\s*$", body_text, re.MULTILINE)
    if m:
        t = m.group(1).strip().rstrip("#").strip()
        if 3 <= len(t) <= 90:
            return t
    m = re.search(r"\*\*(.+?)[:\*]", body_text)
    if m:
        t = m.group(1).strip()
        if 3 <= len(t) <= 90:
            return t
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", os.path.splitext(fname)[0])
    return slug.replace("-", " ")


def refresh_feed_block(raw, nl, iso_date, title, body):
    """Return raw with the managed feed block rewritten. Placement: immediately above the
    FIRST unmanaged '## Last Completed' heading, which is the one the endpoint matches."""
    flat = raw.replace(b"\r\n", b"\n").decode("utf-8", "replace")
    block_txt = "%s%s## Last Completed (%s - %s)%s%s%s%s%s" % (
        FEED_BEGIN, "\n\n", iso_date, title, "\n\n",
        body.decode("utf-8", "replace").strip(), "\n\n", FEED_END, "\n\n")
    block = block_txt.replace("\n", nl.decode()).encode("utf-8")

    b = raw.find(FEED_BEGIN.encode())
    if b >= 0:
        e = raw.find(FEED_END.encode(), b)
        if e < 0:
            print("REFUSED: feed block has BEGIN but no END - not guessing.")
            return None
        e += len(FEED_END.encode())
        while raw[e:e + len(nl)] == nl:
            e += len(nl)
        return raw[:b] + block + raw[e:]

    # First insertion: sit above the first "## Last Completed" heading.
    m = re.search(r"^## Last Completed", flat, re.MULTILINE)
    if not m:
        print("REFUSED: no '## Last Completed' heading to sit above.")
        return None
    # Translate the flat offset back to the raw offset (CRLF-safe).
    prefix_newlines = flat.count("\n", 0, m.start())
    i = 0
    for _ in range(prefix_newlines):
        i = raw.find(nl, i) + len(nl)
    return raw[:i] + block + raw[i:]



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
    feed_src = None           # (iso_date, title, body) of the NEWEST fragment this run
    for f in frags:
        with open(os.path.join(FRAG_DIR, f), "rb") as fh:
            body = fh.read().replace(b"\r\n", b"\n").strip(b"\n")
        body_text = body.decode("utf-8", "replace")
        if feed_src is None:
            d = re.match(r"(\d{4}-\d{2}-\d{2})", f)
            feed_src = (d.group(1) if d else datetime.date.today().isoformat(),
                        _fragment_title(f, body_text), body)
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
        merged = raw[:j] + block + raw[j:]
        if feed_src is not None:
            fed = refresh_feed_block(merged, nl, feed_src[0], feed_src[1], feed_src[2])
            if fed is None:
                print("WARNING: feed block not refreshed - the dashboard will keep "
                      "reading the older section (RG-0127).")
            else:
                merged = fed
        tmp = STATUS + ".compile-tmp"
        with open(tmp, "wb") as fh:
            fh.write(merged)
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
        # Read the WHOLE file: the managed feed block shifts every offset, so a
        # byte-budgeted head read can report a correct fold as FAILED.
        with open(STATUS, "rb") as fh:
            head = fh.read()
        ok = parts[0][:60] in head
        if feed_src is not None and FEED_BEGIN.encode() not in head:
            ok = False
            print("verify: managed feed block MISSING - /dashboard/summary will read a "
                  "stale section (RG-0127).")
    print("folded %d, skipped %d (already present) - verify %s"
          % (len(parts), len(folded_names) - len(parts), "OK" if ok else "FAILED"))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
