#!/usr/bin/env python3
"""008_ts_fixback_batch.py — one-time server changes for the 5 Aug 2026 fixback batch
(TS-0012 + TS-0019, David's approval in session).

1. TS-0012 (HEIC photos): best-effort `pip install pillow-heif` so the guarded
   opener in bea_main.py activates. Failure is reported, never fatal — the app
   falls back to the old JPEG/PNG/WebP-only behaviour.
2. TS-0019 (\"Waterklof\"): repair the misspelling in listing title, description
   and structured_fields. Substring-safe: 'Waterkloof' does NOT contain
   'Waterklof' (…K-L-O-O-F vs …K-L-O-F), so correct spellings are untouched
   and the migration is idempotent.

Usage: python3 migrations/008_ts_fixback_batch.py --db marketsquare.db [--apply]
post_deploy.sh runs it as `python3 <m> --apply` with CWD = live web root.
"""
import argparse
import os
import sqlite3
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="marketsquare.db")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    args = ap.parse_args()

    # ── 1. pillow-heif (best effort) ──
    try:
        import pillow_heif  # noqa: F401
        print("pillow-heif already importable — nothing to install.")
    except Exception:
        print("Installing pillow-heif …")
        r = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "pillow-heif"],
                           capture_output=True, text=True, timeout=300)
        if r.returncode == 0:
            print("pillow-heif installed OK (restart picks it up).")
        else:
            print("WARN: pillow-heif install failed (HEIC stays unsupported, app unaffected):")
            print((r.stderr or r.stdout)[-400:])

    # ── 2. Waterklof → Waterkloof ──
    if not os.path.exists(args.db):
        print("NOTE: %s not found here — nothing to do (dev box?). Exiting green so the "
              "migration chain is not blocked." % args.db)
        return 0
    conn = sqlite3.connect(args.db)
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(listings)").fetchall()}
        target_cols = [c for c in ("title", "description", "structured_fields", "suburb") if c in cols]
        hits = 0
        for c in target_cols:
            n = conn.execute(
                "SELECT COUNT(*) FROM listings WHERE %s LIKE '%%Waterklof%%'" % c
            ).fetchone()[0]
            print("listings.%s rows containing 'Waterklof': %d" % (c, n))
            hits += n
            if args.apply and n:
                conn.execute(
                    "UPDATE listings SET %s = REPLACE(%s, 'Waterklof', 'Waterkloof') "
                    "WHERE %s LIKE '%%Waterklof%%'" % (c, c, c))
        if args.apply:
            conn.commit()
            print("APPLIED — %d field hits corrected." % hits)
        else:
            print("DRY RUN — nothing written. Re-run with --apply.")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
