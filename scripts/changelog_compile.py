#!/usr/bin/env python3
"""changelog_compile.py — CHANGELOG-COLLISION-1 (2 Aug 2026).

THE single writer for CHANGELOG.md. Sessions never rewrite CHANGELOG.md
directly; they drop entries as NEW files in changelog.d/ (YYYY-MM-DD-<slug>.md,
newest-relevant content per file). This compiler folds every pending fragment
into the TOP of CHANGELOG.md (fragments sorted newest-first by filename), then
moves each folded fragment to changelog.d/folded/ so a re-run is a no-op.

Why: two concurrent sessions doing whole-file read-modify-write on CHANGELOG.md
silently destroyed each other's entries (last-writer-wins, no error). Creating a
new file per session cannot collide; one compiler = one writer.

Run from the MarketSquare project folder (or via the release wrapper):
    python scripts/changelog_compile.py          # fold pending fragments
    python scripts/changelog_compile.py --check  # exit 1 if fragments pending (no writes)
Safe: no-op when changelog.d/ is empty; preserves CHANGELOG.md line endings.
"""
import os, sys, shutil, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAG_DIR = os.path.join(ROOT, "changelog.d")
FOLDED = os.path.join(FRAG_DIR, "folded")
LOG = os.path.join(ROOT, "CHANGELOG.md")

def main():
    check = "--check" in sys.argv
    if not os.path.isdir(FRAG_DIR):
        print("changelog.d/ absent — nothing to fold."); return 0
    frags = sorted(
        (f for f in os.listdir(FRAG_DIR)
         if f.lower().endswith(".md") and os.path.isfile(os.path.join(FRAG_DIR, f))),
        reverse=True)   # newest-first by name (YYYY-MM-DD-... sorts naturally)
    if not frags:
        print("no pending fragments."); return 0
    if check:
        print("%d pending fragment(s): %s" % (len(frags), ", ".join(frags))); return 1

    with open(LOG, "rb") as fh:
        raw = fh.read()
    nl = b"\r\n" if b"\r\n" in raw[:4096] else b"\n"

    log_flat = raw.replace(b"\r\n", b"\n")
    parts, folded_names = [], []
    for f in frags:
        p = os.path.join(FRAG_DIR, f)
        with open(p, "rb") as fh:
            body = fh.read().replace(b"\r\n", b"\n").strip(b"\n")
        # DEDUP GUARD (2 Aug 2026): a re-armed fragment must be safe. If this fragment's
        # first heading line already sits in CHANGELOG.md, it is folded already - archive
        # without prepending (protects against double-fold after a wipe/restore cycle).
        head_line = body.split(b"\n", 1)[0].strip()
        if head_line and head_line in log_flat:
            print("skip (already present): %s" % f); folded_names.append(f); continue
        parts.append(body.replace(b"\n", nl)); folded_names.append(f)
    if parts:
        block = (nl + nl).join(parts) + nl + nl
        tmp = LOG + ".compile-tmp"
        with open(tmp, "wb") as fh:
            fh.write(block + raw)
        os.replace(tmp, LOG)          # atomic on the same filesystem
    else:
        block = b""

    os.makedirs(FOLDED, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for f in folded_names:
        dst = os.path.join(FOLDED, f)
        if os.path.exists(dst):
            dst = os.path.join(FOLDED, "%s.%s" % (f, stamp))
        shutil.move(os.path.join(FRAG_DIR, f), dst)

    # verify our own write landed (the incident class was a SILENT loss)
    ok = True
    if parts:
        with open(LOG, "rb") as fh:
            head = fh.read(len(block) + 64)
        ok = parts[0][:60] in head
    print("folded %d, skipped %d (already present) · verify %s"
          % (len(parts), len(folded_names) - len(parts), "OK" if ok else "FAILED"))
    return 0 if ok else 2

if __name__ == "__main__":
    sys.exit(main())
