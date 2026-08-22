#!/usr/bin/env python3
"""030_intro_hold.py — INTRO-HOLD-1 (22 Aug 2026): make the shipped promise true.

The EULA tells every buyer, in four separate clauses, that 1 Tuppence is COMMITTED (HELD)
when the request is made, BURNED only on delivery (seller acceptance), and RELEASED IN FULL
on decline, expiry or withdrawal. The ECT Act s44 cooling-off argument rests on exactly that
distinction: "Until delivery, the Tuppence is only held, not spent."

No hold existed. create_intro charged nothing and accept_intro deducted at the end — so the
user agreed to a mechanism the code did not implement (RG-0145). The wording is not the thing
to change: it is legally load-bearing and RUL-020 released it as final. The CODE changes.

Two nullable columns, additive and safe. Idempotent; safe to re-run.
"""
import os as _os, sys as _sys
if _os.getcwd() not in _sys.path:
    _sys.path.insert(0, _os.getcwd())

COLUMNS = (
    ("tuppence_held",    "INTEGER DEFAULT 0"),  # 1 = a hold was placed at request time
    ("hold_released_at", "TEXT"),               # set once, when the hold is returned
)


def main():
    try:
        import main as bea
    except Exception as e:
        print("[030_intro_hold] REFUSE: cannot import main (%s)" % e); return 3
    conn = bea.database.get_db()
    have = {r[1] for r in conn.execute("PRAGMA table_info(intro_requests)").fetchall()}
    added = []
    for name, typ in COLUMNS:
        if name in have:
            continue
        conn.execute("ALTER TABLE intro_requests ADD COLUMN %s %s" % (name, typ))
        added.append(name)
    conn.commit()
    print("[030_intro_hold] columns added: %s" % (", ".join(added) if added else "none (already present)"))
    # Existing pending intros pre-date the hold: they carry tuppence_held = 0 and are
    # charged the legacy way on accept. We do NOT retro-hold money from live wallets.
    n = conn.execute("SELECT COUNT(*) AS n FROM intro_requests WHERE status='pending' "
                     "AND COALESCE(tuppence_held,0)=0").fetchone()[0]
    print("[030_intro_hold] %d pending intro(s) pre-date the hold — legacy charge-on-accept" % n)
    print("[030_intro_hold] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
