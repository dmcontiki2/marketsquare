#!/usr/bin/env python3
"""041_credential_registry_seed.py -- FIDE-CLAIM-1 (CREDENTIAL_CLAIMS_DESIGN.md sec 1, RG-0216).

Creates credential_registry / credential_claims (purely additive, no existing table touched)
and seeds the FIDE Trainers' Commission registry from fide_registry_seed.json.gz beside main.py
(the CityLauncher fide_trainers export, 4,237 unique IDs, highest title kept). Idempotent upsert:
a re-run inserts nothing already present and only ever RAISES a title. ONE_DEPLOY conformant --
code and seed ride the deploy ref, nothing is scp'd.

Dry by default; --apply writes, after a backup.
"""
import gzip, json, os, shutil, sqlite3, sys
from datetime import datetime, timezone
APPLY = "--apply" in sys.argv
DB = os.environ.get("MS_DB", "/var/www/marketsquare/marketsquare.db")
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
RANK = {"FST": 5, "FT": 4, "FI": 3, "NI": 2, "DI": 1}

def _seed_path():
    for base in (os.getcwd(), os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "/var/www/marketsquare"):
        p = os.path.join(base, "fide_registry_seed.json.gz")
        if os.path.exists(p):
            return p
    return None

def main():
    if not os.path.exists(DB):
        print("041: database not found at %s -- nothing to do" % DB); return 0
    sp = _seed_path()
    if not sp:
        print("041: fide_registry_seed.json.gz not found beside main.py -- refusing (seed must ride the deploy)"); return 1
    with gzip.open(sp, "rt", encoding="utf-8") as fh:
        rows = json.load(fh)
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    try:
        if APPLY:
            bak = "%s.bak-credreg-%s" % (DB, TS)
            shutil.copy2(DB, bak); print("041: backup -> %s" % bak)
        conn.execute("""CREATE TABLE IF NOT EXISTS credential_registry(
            source TEXT NOT NULL, credential_id TEXT NOT NULL, name_norm TEXT NOT NULL, detail TEXT,
            federation TEXT, harvested_at TEXT, PRIMARY KEY(source, credential_id))""")
        conn.execute("""CREATE TABLE IF NOT EXISTS credential_claims(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, email TEXT NOT NULL,
            source TEXT NOT NULL, credential_id TEXT NOT NULL, claimed_name TEXT NOT NULL,
            tier TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active', similarity REAL,
            claimed_at TEXT NOT NULL, reviewed_at TEXT, reviewed_by TEXT,
            UNIQUE(source, credential_id))""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cred_claims_email ON credential_claims(email)")
        have = {r["credential_id"]: (r["detail"] or "") for r in conn.execute("SELECT credential_id, detail FROM credential_registry WHERE source='FIDE'")}
        ins = upd = 0
        for r in rows:
            cid = str(r["credential_id"]); det = str(r.get("detail") or "").upper()
            if cid not in have:
                ins += 1
                if APPLY:
                    conn.execute("INSERT INTO credential_registry (source, credential_id, name_norm, detail, federation, harvested_at) VALUES ('FIDE',?,?,?,?,?)",
                                 (cid, r["name_norm"], det, r.get("federation") or "", r.get("harvested_at") or TS[:8]))
            elif RANK.get(det, 0) > RANK.get(have[cid].upper(), 0):
                upd += 1
                if APPLY:
                    conn.execute("UPDATE credential_registry SET detail=?, name_norm=?, harvested_at=? WHERE source='FIDE' AND credential_id=?",
                                 (det, r["name_norm"], r.get("harvested_at") or TS[:8], cid))
        if APPLY:
            conn.commit()
        n = conn.execute("SELECT COUNT(*) FROM credential_registry WHERE source='FIDE'").fetchone()[0]
        print("041: seed rows %d, insert %d, upgrade %d, table total %d%s" % (len(rows), ins, upd, n, "" if APPLY else "  [dry]"))
        if APPLY and not (ins or upd):
            print("041: nothing to seed -- registry already complete")
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main())
