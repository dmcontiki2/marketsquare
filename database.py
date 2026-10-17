import atexit
import os
import sqlite3
import threading
import time

DB_PATH = "/var/www/marketsquare/marketsquare.db"

# DB-ANCHOR-1 (17 Oct 2026 bug audit, BA-016). The app opens one connection per request, so whenever no request was
# running, the last connection to close deleted the -wal and -shm side files and the next one re-created them. A root
# process that touches the live database (the release safety gate, the nightly root jobs, a hand-run script) re-creates
# them as root for an instant before SQLite hands them to the database owner. An app connection that opens them in that
# instant is refused ("unable to open database file"), or falls back to a read-only shared-memory map, after which every
# write in the process fails ("attempt to write a readonly database") until all its connections close. Seen in
# production 7 times since 30 Sep 2026, all inside a release-gate window; reproduced on a copy of the database on
# 17 Oct (8 refusals and a read-only spell in 10 s without the anchor; none in 30 s with it). One connection that the
# app process holds open for its whole life keeps the side files present and writable, so nobody re-creates them; it
# also checkpoints the WAL every 30 s, so a plain file copy of the database is never more than ~30 s behind.
# Only the app holds it: never a root process, never a script pointed at another database file.
_LIVE_PATH = "/var/www/marketsquare/marketsquare.db"
_ANCHOR = {"conn": None, "started": False}
_ANCHOR_LOCK = threading.Lock()


def _anchor_open():
    a = sqlite3.connect(_LIVE_PATH, timeout=0.5, check_same_thread=False)
    try:
        a.execute("PRAGMA journal_mode=WAL;")
        a.execute("BEGIN IMMEDIATE;")   # proves this process's view of the shared memory is writable
        a.execute("ROLLBACK;")
        return a
    except Exception:
        try:
            a.close()
        except Exception:
            pass
        return None


def _anchor_loop():
    while True:
        if _ANCHOR["conn"] is None:
            a = _anchor_open()
            if a is None:
                time.sleep(2)
                continue
            _ANCHOR["conn"] = a
        time.sleep(30)
        try:
            _ANCHOR["conn"].execute("PRAGMA wal_checkpoint(PASSIVE);").fetchall()
        except Exception:
            pass


def _anchor_start():
    if _ANCHOR["started"] or DB_PATH != _LIVE_PATH or getattr(os, "geteuid", lambda: 1)() == 0:
        return
    with _ANCHOR_LOCK:
        if _ANCHOR["started"]:
            return
        _ANCHOR["started"] = True
    threading.Thread(target=_anchor_loop, name="db-anchor", daemon=True).start()


@atexit.register
def _anchor_close():
    c = _ANCHOR.get("conn")
    if c is not None:
        try:
            c.close()
        except Exception:
            pass


def get_db():
    _anchor_start()
    for attempt in range(3):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        try:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA temp_store=MEMORY;")
            return conn
        except sqlite3.OperationalError as e:
            try:
                conn.close()
            except Exception:
                pass
            if attempt == 2 or "unable to open database file" not in str(e):
                raise
            time.sleep(0.05 * (attempt + 1))   # the side-file window lasts microseconds

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price TEXT,
            category TEXT NOT NULL,
            city TEXT NOT NULL,
            area TEXT,
            description TEXT,
            claim_status TEXT DEFAULT 'unclaimed',
            trust_score INTEGER DEFAULT 0,
            safety_score INTEGER DEFAULT 25,
            fade_days INTEGER DEFAULT 0,
            thumb_url TEXT,
            medium_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            id_verified INTEGER DEFAULT 0,
            photo_uploaded INTEGER DEFAULT 0,
            trust_score INTEGER DEFAULT 40,
            safety_score INTEGER DEFAULT 25,
            referral_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS intro_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id INTEGER NOT NULL,
            buyer_email TEXT NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'pending',
            tuppence_charged INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (listing_id) REFERENCES listings(id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_listings_city ON listings(city);
        CREATE INDEX IF NOT EXISTS idx_listings_category ON listings(category);
        CREATE INDEX IF NOT EXISTS idx_listings_claim ON listings(claim_status);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_intros_listing ON intro_requests(listing_id);
        CREATE INDEX IF NOT EXISTS idx_intros_status ON intro_requests(status);
    """)
    conn.commit()
    conn.close()
    print("Database initialised successfully.")

if __name__ == "__main__":
    init_db()
