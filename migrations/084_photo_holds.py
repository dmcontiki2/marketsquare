#!/usr/bin/env python3
"""084_photo_holds.py -- PHOTO-KIND-1 (RUL-239, David 18 Oct 2026).

Seller photos the anonymity check cannot clear by itself are kept PRIVATELY for David's one-tap check: a file in
/var/lib/marketsquare/photo_holds (outside the web root, owned by the app user msdeploy, mode 700) and a row in
photo_holds. The BEA also creates the table on first use (_photo_holds_ensure); this pass makes the folder (the app user
cannot create it under /var/lib itself) and the table exist before the first held photo. Idempotent, additive only.
Dry by default; --apply writes.
"""
import os, sqlite3, sys, pwd

APPLY = "--apply" in sys.argv
DB = os.environ.get("MS_DB", "/var/www/marketsquare/marketsquare.db")
DIR = os.environ.get("PHOTO_HOLD_DIR", "/var/lib/marketsquare/photo_holds")
TABLE = """CREATE TABLE IF NOT EXISTS photo_holds (
    id INTEGER PRIMARY KEY AUTOINCREMENT, listing_id INTEGER, seller_email TEXT, category TEXT,
    is_primary INTEGER NOT NULL DEFAULT 0, caption TEXT, file_name TEXT NOT NULL, reason TEXT, labels TEXT, regions TEXT,
    source TEXT, status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','approved','declined')),
    created_at TEXT NOT NULL, alerted_at TEXT, decided_at TEXT, decided_how TEXT, photo_url TEXT)"""
INDEX = "CREATE INDEX IF NOT EXISTS ix_photo_holds_status ON photo_holds(status, created_at)"


def main():
    print("084_photo_holds: folder %s, table photo_holds in %s (%s)" % (DIR, DB, "APPLY" if APPLY else "dry run"))
    if not APPLY:
        return 0
    try:
        u = pwd.getpwnam("msdeploy")
        uid, gid = u.pw_uid, u.pw_gid
    except KeyError:
        uid = gid = -1
    for d in (os.path.dirname(DIR), DIR):
        os.makedirs(d, mode=0o700, exist_ok=True)
        os.chmod(d, 0o700)
        if uid >= 0:
            os.chown(d, uid, gid)
    c = sqlite3.connect(DB)
    try:
        c.execute(TABLE); c.execute(INDEX); c.commit()
    finally:
        c.close()
    print("084_photo_holds: done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
