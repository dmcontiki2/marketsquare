#!/usr/bin/env python3
"""039_functional_tier_names.py -- TIER-NAME-1 (17 Sep 2026, David).

WHY. The task tiers were keyed by one vendor's model names ("haiku", "sonnet",
"sonnet_vision", "sonnet_rewrite") -- in the seam, the baseline, the price-card gates,
the breaker, the spend log and the dashboard. A label that IS a model name makes that
model "the agent" by perception, and a silent reversion is one habit away. David's
ruling: tiers are named for the FUNCTION they serve; which model serves a tier is the
register's decision, re-selected as prices and capability move (cheapest passer wins).
Code, JSON and the dashboard were renamed in the same release; this migration is the
one-time catch-up for STORED rows so spend history and breaker state stay continuous.

  fast   <- haiku            everyday text
  reason <- sonnet, sonnet_rewrite
  vision <- sonnet_vision    (already had a functional twin)

Idempotent: re-running moves 0 rows. Dry by default; --apply writes, after a backup.
"""
import os, shutil, sqlite3, sys
from datetime import datetime, timezone
APPLY = "--apply" in sys.argv
DB = os.environ.get("MS_DB", "/var/www/marketsquare/marketsquare.db")
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
MAP = {"haiku": "fast", "sonnet": "reason", "sonnet_rewrite": "reason", "sonnet_vision": "vision"}
TARGETS = (("ai_spend_log", "model"), ("ai_breaker", "task"), ("ai_breaker_stats", "task"),
           ("ai_scoreboard_probes", "task"))

def main():
    if not os.path.exists(DB):
        print("039: database not found at %s -- nothing to do" % DB); return 0
    conn = sqlite3.connect(DB)
    try:
        plan = []
        for table, col in TARGETS:
            if not conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone():
                continue
            cols = [r[1] for r in conn.execute("PRAGMA table_info(%s)" % table)]
            if col not in cols:
                continue
            for old, new in MAP.items():
                n = conn.execute("SELECT COUNT(*) FROM %s WHERE %s=?" % (table, col), (old,)).fetchone()[0]
                if n:
                    plan.append((table, col, old, new, n))
        if not plan:
            print("039: nothing to rename -- all tier keys already functional"); return 0
        for table, col, old, new, n in plan:
            print("039: %s.%s  %s -> %s  (%d rows)%s" % (table, col, old, new, n, "" if APPLY else "  [dry]"))
        if not APPLY:
            return 0
        bak = "%s.bak-tiernames-%s" % (DB, TS)
        shutil.copy2(DB, bak); print("039: backup -> %s" % bak)
        for table, col, old, new, n in plan:
            # the breaker keys (provider, task) uniquely -- merge on collision rather than fail
            if table == "ai_breaker":
                conn.execute("DELETE FROM %s WHERE %s=? AND provider IN (SELECT provider FROM %s WHERE %s=?)"
                             % (table, col, table, col), (old, new))
            conn.execute("UPDATE %s SET %s=? WHERE %s=?" % (table, col, new, old), (new, old))
        conn.commit(); print("039: applied")
    finally:
        conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
