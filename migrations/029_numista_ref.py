#!/usr/bin/env python3
"""029_numista_ref.py — N#-REFERRAL-1 (22 Aug 2026): store the catalogue IDENTIFIER, never the data.

David's design, recorded in FEED_LICENCES.md and N_REFERRAL_DESIGN.md. Numista's licence
forbids storing or caching catalogue data (permitted metadata max 7 days) but explicitly
allows storing N# identifiers WITHOUT a time limit. So a listing keeps the identifier and
links out; the price is read by the user on Numista, under Numista's terms.

Four nullable columns, additive and safe. DELIBERATELY ABSENT: any price, estimate, mintage
or other catalogue field — if a later migration adds one, the design has been broken and
RG-0150 goes red.

Idempotent; safe to re-run.
"""
import os as _os, sys as _sys
if _os.getcwd() not in _sys.path:
    _sys.path.insert(0, _os.getcwd())

COLUMNS = (
    ("numista_id",         "INTEGER"),  # the N# — the one thing we may keep forever
    ("numista_title",      "TEXT"),     # catalogue title the SELLER confirmed; the link label
    ("numista_matched_at", "TEXT"),     # when the human confirmed it
    ("numista_matched_by", "TEXT"),     # 'seller' or 'admin' — a match is never a guess
)

# Anything that would hold a catalogue FIGURE. Present = the licence design is broken.
FORBIDDEN = ("numista_price", "numista_value", "numista_estimate", "numista_mintage")


def main():
    try:
        import main as bea
    except Exception as e:
        print("[029_numista] REFUSE: cannot import main (%s)" % e); return 3
    conn = bea.database.get_db()

    have = {r[1] for r in conn.execute("PRAGMA table_info(listings)").fetchall()}

    bad = [c for c in FORBIDDEN if c in have]
    if bad:
        print("[029_numista] REFUSE: listings already carries catalogue-figure column(s): %s"
              % ", ".join(bad))
        print("               N#-REFERRAL-1 stores an IDENTIFIER, never a price.")
        return 4

    added = []
    for name, typ in COLUMNS:
        if name in have:
            continue
        conn.execute("ALTER TABLE listings ADD COLUMN %s %s" % (name, typ))
        added.append(name)

    try:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_numista ON listings(numista_id)")
    except Exception as e:
        print("[029_numista] index note: %s" % e)

    conn.commit()
    print("[029_numista] columns added: %s" % (", ".join(added) if added else "none (already present)"))
    print("[029_numista] OK — identifier-only, no catalogue figures stored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
