#!/usr/bin/env python3
"""036_agency_tier_resync.py -- AGENCY-REACH-1 (7 Sep 2026, RUL-108).

WHY THIS EXISTS. AGENCY-TIER-1 (3 Aug 2026) stamped a member's seller_tier at INVITE
time from the agency's verified flag, and nothing ever re-read it. PROBED on the live
database 7 Sep: 8 agencies, ALL verified, 25 members between them, and NOT ONE carried
the `agency` tier -- 8 sat on `free`, 17 on `starter`, because they were invited before
their agency was verified. So the benefit David has now extended (multi-city reach for
verified agencies, RUL-108) would have landed on an empty set.

The CODE half is fixed in bea_main.py: _sync_agency_member_tiers() makes the tier a
derived property with one writer, called from invite and from the new
POST /agencies/{id}/verify. This migration is the one-time catch-up for rows that were
stamped before that existed.

SAFETY, and it is the same rule the runtime uses -- not a second copy of it:
  * a member who bought their own seat (seat_paid, RUL-048) or holds a live
    subscription (billing_period_end) is NEVER touched;
  * only `free`/`starter`/`agency` move, and only to the tier their agency's
    verification says they should hold;
  * PROBED 7 Sep: zero members have seat_paid or billing_period_end, so nobody
    loses anything they paid for -- but the guard is here for the next run, not
    this one.
Idempotent: re-running moves 0 rows. Dry by default; --apply writes, after a backup.
"""
import os, shutil, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.environ.get("MS_DB", "/var/www/marketsquare/marketsquare.db")
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

def main():
    if not os.path.exists(DB):
        print("036: database not found at %s -- nothing to do" % DB); return 0
    if APPLY:
        bak = "%s.bak-agencytier-%s" % (DB, TS)
        shutil.copy2(DB, bak)
        print("036: backup -> %s" % bak)
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    try:
        for t in ("agencies", "agency_members", "users"):
            if not conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
                print("036: table %r absent -- skipping (nothing to resync)" % t); return 0
        rows = conn.execute(
            """SELECT m.agent_email, m.seat_paid, a.verified, u.seller_tier, u.billing_period_end
                 FROM agency_members m
                 JOIN agencies a ON a.id = m.agency_id
                 LEFT JOIN users u ON LOWER(u.email) = LOWER(m.agent_email)""").fetchall()
        moved = skipped = same = 0
        for r in rows:
            if (r["seat_paid"] or 0) or r["billing_period_end"]:
                skipped += 1; continue
            target = "agency" if r["verified"] else "starter"
            current = (r["seller_tier"] or "free")
            if current not in ("free", "starter", "agency") or current == target:
                same += 1; continue
            if APPLY:
                conn.execute("UPDATE users SET seller_tier=? WHERE LOWER(email)=?",
                             (target, (r["agent_email"] or "").lower()))
            moved += 1
        if APPLY:
            conn.commit()
        print("036: %s -- %d member(s) %s, %d already correct, %d left alone (paying)"
              % ("APPLIED" if APPLY else "DRY RUN", moved,
                 "moved" if APPLY else "would move", same, skipped))
        after = conn.execute(
            """SELECT COALESCE(u.seller_tier,'(none)') t, COUNT(*) n
                 FROM agency_members m LEFT JOIN users u ON LOWER(u.email)=LOWER(m.agent_email)
                GROUP BY t ORDER BY n DESC""").fetchall()
        print("036: member tiers now -> " + ", ".join("%s=%d" % (r["t"], r["n"]) for r in after))
    finally:
        conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
