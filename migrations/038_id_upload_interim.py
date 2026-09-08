#!/usr/bin/env python3
"""038_id_upload_interim.py -- ID-UPLOAD-INTERIM-1 (8 Sep 2026, RUL-113, closes DW-109).

WHY THIS EXISTS. Until today an ID upload stored the document, wrote a 'pending'
credential, granted nothing and left /id-status saying "No ID on file" -- so the
seller uploaded again (David did, twice, on 6 Sep). With the Home Affairs lane
parked (RUL-105, Didit unfunded) nothing was ever going to confirm those uploads.
David's ruling 8 Sep: the upload itself is worth 12 of the 15 identity points at
once, with the note "Waiting confirmation to add an extra 3 points."

The CODE half is in bea_main.py (_grant_id_upload_interim, called by the upload
handler). This migration is the one-time catch-up for sellers who uploaded BEFORE
it shipped: every universal.id_verified credential still 'pending' that has an
id_doc document on file becomes 'declared' with the interim points.

SAFETY: an 'earned' credential is never touched (no downgrade -- same rule as the
runtime's _upsert_credential); a 'pending' row WITHOUT a document is left alone
(nothing was uploaded, nothing is owed). Idempotent: re-running moves 0 rows.
Dry by default; --apply writes, after a backup. Points are NOT hand-added to
users.trust_score -- the scorer recomputes from the declaration on the next read,
exactly as it does for a fresh upload.
"""
import os, shutil, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.environ.get("MS_DB", "/var/www/marketsquare/marketsquare.db")
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
POINTS = max(0, min(15, int(os.environ.get("ID_UPLOAD_INTERIM_POINTS", "12") or 0)))
NOTE = "Waiting confirmation to add an extra %d points." % (15 - POINTS)

def main():
    if not os.path.exists(DB):
        print("038: database not found at %s -- nothing to do" % DB); return 0
    if POINTS <= 0:
        print("038: ID_UPLOAD_INTERIM_POINTS is 0 -- interim grant is off, nothing to do"); return 0
    if APPLY:
        bak = "%s.bak-idinterim-%s" % (DB, TS)
        shutil.copy2(DB, bak)
        print("038: backup -> %s" % bak)
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    try:
        for t in ("user_credentials", "user_declarations", "seller_documents"):
            if not conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
                print("038: table %r absent -- skipping (nothing to convert)" % t); return 0
        rows = conn.execute(
            """SELECT c.email, c.status,
                      (SELECT COUNT(*) FROM seller_documents d
                        WHERE LOWER(d.email)=LOWER(c.email) AND d.doc_type='id_doc') AS docs
                 FROM user_credentials c
                WHERE c.signal_id='universal.id_verified' AND c.status='pending'""").fetchall()
        moved = nodoc = 0
        for r in rows:
            if not r["docs"]:
                nodoc += 1; continue
            em = (r["email"] or "").lower().strip()
            if APPLY:
                conn.execute(
                    """UPDATE user_credentials SET status='declared',
                              updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now')
                        WHERE LOWER(email)=? AND signal_id='universal.id_verified' AND status='pending'""",
                    (em,))
                conn.execute(
                    """INSERT INTO user_declarations (email, signal_id, declaration, points_awarded)
                       VALUES (?, 'universal.id_verified', ?, ?)
                       ON CONFLICT(email, signal_id) DO UPDATE SET
                           points_awarded = excluded.points_awarded,
                           declaration    = excluded.declaration""",
                    (em, "ID document uploaded before ID-UPLOAD-INTERIM-1 shipped (migration 038). " + NOTE, POINTS))
            moved += 1
        if APPLY:
            conn.commit()
        print("038: %s -- %d pending upload(s) %s to declared/%d pts, %d pending row(s) without a document left alone"
              % ("APPLIED" if APPLY else "DRY RUN", moved, "converted" if APPLY else "would convert", POINTS, nodoc))
        after = conn.execute(
            """SELECT status, COUNT(*) n FROM user_credentials
                WHERE signal_id='universal.id_verified' GROUP BY status ORDER BY n DESC""").fetchall()
        print("038: universal.id_verified now -> " + ", ".join("%s=%d" % (r["status"], r["n"]) for r in after))
    finally:
        conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
