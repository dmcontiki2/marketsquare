#!/usr/bin/env python3
"""
mint_enrol_link.py -- DEVICE-ENROL-1 (3 Sep 2026). Runs ON THE SERVER (writes marketsquare.db).

    python3 scripts/mint_enrol_link.py "David phone"        -> prints a one-time URL, valid 20 min

Scan it on the phone once: it sets a revocable 180-day device cookie and lands on /m.
List / revoke devices: GET /admin/devices, POST /admin/devices/<id>/revoke (admin token).
"""
import os, sqlite3, secrets, sys
from datetime import datetime, timedelta, timezone

DB = os.environ.get("MS_DB_PATH", "/var/www/marketsquare/marketsquare.db")
label = " ".join(sys.argv[1:]).strip() or "phone"
conn = sqlite3.connect(DB)
conn.execute("""CREATE TABLE IF NOT EXISTS admin_enrol_tokens (
    token TEXT PRIMARY KEY, label TEXT, created_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT, used_at TEXT)""")
tok = secrets.token_urlsafe(24)
exp = (datetime.now(timezone.utc) + timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
conn.execute("INSERT INTO admin_enrol_tokens (token, label, expires_at) VALUES (?, ?, ?)", (tok, label, exp))
conn.commit(); conn.close()
print("https://trustsquare.co/admin/enrol?t=" + tok)
print("valid until %s UTC, single use, label=%r" % (exp, label))
