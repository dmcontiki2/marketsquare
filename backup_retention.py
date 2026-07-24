#!/usr/bin/env python3
# backup_retention.py <backups_dir> [--apply]
# GFS retention for MarketSquare dated archives named YYYY-MM-DD_HHMM(.zip or /):
#   * keep everything from the last 7 days           (daily)
#   * then the newest archive per ISO week, 4 weeks  (weekly)
#   * then the newest archive per calendar month     (monthly, indefinitely)
#   * the single newest archive is ALWAYS kept
#   * a redundant intermediate STAMP/ folder is removed when its STAMP.zip exists
# DRY RUN unless --apply. NEVER touches anything that is not a dated archive
# (loose DBs, super-photos, random files are left completely alone).
import os, re, sys, shutil
from datetime import datetime

STAMP_RE = re.compile(r'^(\d{4})-(\d{2})-(\d{2})_(\d{2})(\d{2})$')
DAILY_DAYS, WEEKLY_WEEKS = 7, 4

def parse_stamp(name):
    m = STAMP_RE.match(name)
    if not m: return None
    y, mo, d, h, mi = map(int, m.groups())
    try: return datetime(y, mo, d, h, mi)
    except ValueError: return None

def human(n):
    n = float(n)
    for u in ('B','KB','MB','GB'):
        if n < 1024: return "%.0f%s" % (n, u)
        n /= 1024
    return "%.1fTB" % n

def dirsize(p):
    t = 0
    for dp, _, fs in os.walk(p):
        for f in fs:
            try: t += os.path.getsize(os.path.join(dp, f))
            except OSError: pass
    return t

def main():
    args = sys.argv[1:]
    apply = "--apply" in args
    paths = [a for a in args if not a.startswith("--")]
    base = paths[0] if paths else "backups"
    if not os.path.isdir(base):
        print("retention: no backups dir at %s - nothing to do." % base); return 0

    now_s = os.environ.get("RETENTION_NOW")
    now = datetime.strptime(now_s, "%Y-%m-%d_%H%M") if now_s else datetime.now()

    items = {}
    for e in sorted(os.listdir(base)):
        full = os.path.join(base, e)
        if e.lower().endswith(".zip"):
            dt = parse_stamp(e[:-4])
            if dt: items.setdefault(e[:-4], {"dt":dt,"zip":None,"dir":None})["zip"] = full
        elif os.path.isdir(full):
            dt = parse_stamp(e)
            if dt: items.setdefault(e, {"dt":dt,"zip":None,"dir":None})["dir"] = full
        # anything else: untouched, on purpose
    if not items:
        print("retention: no dated archives found - nothing to prune."); return 0

    stamps = sorted(items, key=lambda s: items[s]["dt"], reverse=True)
    keep, reason = {stamps[0]}, {stamps[0]: "newest"}
    seen_week, seen_month = set(), set()
    for s in stamps:
        if s in keep: continue
        dt = items[s]["dt"]; age = (now - dt).days
        if age <= DAILY_DAYS:
            keep.add(s); reason[s] = "daily"
        elif age <= DAILY_DAYS + WEEKLY_WEEKS * 7:
            wk = dt.isocalendar()[:2]
            if wk not in seen_week:
                seen_week.add(wk); keep.add(s); reason[s] = "weekly"
        else:
            ym = (dt.year, dt.month)
            if ym not in seen_month:
                seen_month.add(ym); keep.add(s); reason[s] = "monthly"

    kept, pruned, freed = 0, 0, 0
    for s in stamps:
        it = items[s]
        if s in keep:
            kept += 1
            note = ""
            if it["dir"] and it["zip"] and os.path.getsize(it["zip"]) > 0:
                if apply: shutil.rmtree(it["dir"], ignore_errors=True)
                note = "   (removed redundant folder)"
            print("  keep  %s  [%s]%s" % (s, reason.get(s, ""), note))
        else:
            sz = (os.path.getsize(it["zip"]) if it["zip"] and os.path.exists(it["zip"]) else 0)
            sz += dirsize(it["dir"]) if it["dir"] else 0
            freed += sz; pruned += 1
            if apply:
                if it["zip"]:
                    try: os.remove(it["zip"])
                    except OSError as ex: print("  ! keep-failed remove %s: %s" % (it["zip"], ex))
                if it["dir"]:
                    shutil.rmtree(it["dir"], ignore_errors=True)
            print("  PRUNE %s  (%s)%s" % (s, human(sz), "" if apply else "  [dry-run]"))
    print("retention: kept %d, pruned %d, freed ~%s%s"
          % (kept, pruned, human(freed), "" if apply else "   (DRY RUN - pass --apply to delete)"))
    return 0

if __name__ == "__main__":
    sys.exit(main())
