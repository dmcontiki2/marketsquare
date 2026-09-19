#!/usr/bin/env python3
"""
spend_gauge.py -- SPEND-GAUGE-1 (19 Sep 2026, David).

THE GAUGE, NOT ANOTHER METER. bea_main.py has carried /admin/ai-spend/summary since
11 Jun 2026 and ai_spend_log since May; the numbers were always there and NOTHING EVER
SHOWED THEM. On 19 Sep neither David nor Claude could answer "what did we spend
yesterday" without a live probe. That is the same shape as FUNNEL-DENOM-1 and
STATS-HUMAN-1 -- a correct instrument nobody reads -- and it is the shape this project
keeps paying for. So this file adds no new measurement. It makes the existing one
LEGIBLE, in one line, somewhere a human already looks.

  python3 scripts/spend_gauge.py            # one line: GREEN / AMBER / RED
  python3 scripts/spend_gauge.py --full     # the detail behind the line
  python3 scripts/spend_gauge.py --json     # machine-readable

READING ORDER (first that works wins), so this runs from the laptop, the sandbox, a
scheduled task or the server itself:
  1. MS_ADMIN_KEY in env      -> GET /admin/ai-spend/summary  (also reports the
                                 C1-FAILSAFE-1 breaker, which is process-local and
                                 CANNOT be seen any other way)
  2. ssh_hetzner_key on disk  -> read the live DB directly, read-only
  3. neither                  -> say so plainly. NEVER print a zero it did not measure:
                                 an unreadable gauge reports NOT MEASURED, because a
                                 confident "$0.00" from a broken probe is how a real
                                 overspend would hide (RG-0403's rule, applied here).

THRESHOLDS: amber at 50% of the platform ceiling, red at 85%, or ANY of -- the ceiling
already reached today, a user at their daily rail, the platform ceiling unset (spend
uncapped), or the C1-FAILSAFE-1 breaker reporting blind calls.
"""
import json, os, subprocess, sys, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = "178.104.73.239"
LIVE_DB = "/var/www/marketsquare/marketsquare.db"
AMBER_PCT, RED_PCT = 50.0, 85.0
LOG = os.path.join(REPO, "SPEND_LOG.md")


def _via_endpoint():
    key = os.getenv("MS_ADMIN_KEY")
    if not key:
        return None
    base = os.getenv("MS_BEA_URL", "https://trustsquare.co").rstrip("/")
    try:
        import urllib.request
        req = urllib.request.Request(base + "/admin/ai-spend/summary",
                                     headers={"X-Admin-Key": key,
                                              "User-Agent": "spend-gauge/1"})
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read().decode("utf-8"))
        d["_source"] = "endpoint"
        return d
    except Exception as exc:
        print("# endpoint unavailable (%s) -- falling back" % exc, file=sys.stderr)
        return None


_PROBE = r'''
import sqlite3, json, datetime
c = sqlite3.connect("file:%s?mode=ro", uri=True); c.row_factory = sqlite3.Row
o = {}
cfg = c.execute("SELECT daily_user_ceiling_usd u, daily_platform_ceiling_usd p "
                "FROM ai_spend_config WHERE id=1").fetchone()
o["daily_user_ceiling_usd"] = (cfg["u"] if cfg else 0) or 0
o["daily_platform_ceiling_usd"] = (cfg["p"] if cfg else 0) or 0
t = datetime.datetime.utcnow().strftime("%%Y-%%m-%%d")
y = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%%Y-%%m-%%d")
def day(d):
    r = c.execute("SELECT COALESCE(SUM(est_cost_usd),0) u, COUNT(*) n FROM ai_spend_log "
                  "WHERE substr(logged_at,1,10)=?", (d,)).fetchone()
    return round(r["u"], 6), r["n"]
o["today_usd"], o["today_calls"] = day(t)
o["yesterday_usd"], o["yesterday_calls"] = day(y)
o["days"] = [{"date": r["d"], "usd": round(r["u"], 6), "calls": r["n"]} for r in c.execute(
    "SELECT substr(logged_at,1,10) d, COALESCE(SUM(est_cost_usd),0) u, COUNT(*) n "
    "FROM ai_spend_log GROUP BY d ORDER BY d DESC LIMIT 14")]
o["top_users_today"] = [{"email": r["email"] or "(anon)", "usd": round(r["u"], 6), "calls": r["n"]}
    for r in c.execute("SELECT email, COALESCE(SUM(est_cost_usd),0) u, COUNT(*) n "
                       "FROM ai_spend_log WHERE substr(logged_at,1,10)=? GROUP BY email "
                       "ORDER BY u DESC LIMIT 5", (t,))]
o["by_endpoint"] = [{"endpoint": r["e"] or "?", "usd": round(r["u"], 6), "calls": r["n"]}
    for r in c.execute("SELECT endpoint e, COALESCE(SUM(est_cost_usd),0) u, COUNT(*) n "
                       "FROM ai_spend_log WHERE logged_at >= date('now','-7 day') "
                       "GROUP BY e ORDER BY u DESC LIMIT 8")]
a = c.execute("SELECT COALESCE(SUM(est_cost_usd),0) u, COUNT(*) n, MIN(logged_at) f "
              "FROM ai_spend_log").fetchone()
o["alltime_usd"], o["alltime_calls"], o["first_row"] = round(a["u"], 6), a["n"], a["f"]
print(json.dumps(o))
''' % LIVE_DB


def _via_ssh():
    key = os.path.join(REPO, "ssh_hetzner_key")
    if not os.path.exists(key):
        return None
    try:
        import tempfile, shutil, stat
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".key")
        tmp.close()
        shutil.copyfile(key, tmp.name)
        os.chmod(tmp.name, stat.S_IRUSR | stat.S_IWUSR)
        r = subprocess.run(
            ["ssh", "-i", tmp.name, "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes",
             "-o", "ConnectTimeout=15", "root@" + SERVER,
             # base64, not shell quoting: the probe contains newlines and quotes, and
             # `python3 -c "<json string>"` delivers literal \n rather than newlines.
             "python3 -c \"import base64;exec(base64.b64decode('%s').decode())\""
             % __import__("base64").b64encode(_PROBE.encode()).decode()],
            capture_output=True, text=True, timeout=90)
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
        if r.returncode != 0:
            print("# ssh probe failed: %s" % (r.stderr or "")[:200], file=sys.stderr)
            return None
        d = json.loads(r.stdout.strip().splitlines()[-1])
        d["_source"] = "ssh"
        return d
    except Exception as exc:
        print("# ssh probe error: %s" % exc, file=sys.stderr)
        return None


def verdict(d):
    """Returns (level, one_line). NEVER invents a number it did not measure."""
    if d is None:
        return "GREY", ("AI spend NOT MEASURED - no admin key and no server key reachable. "
                        "This is not zero; it is unknown.")
    cap = d.get("daily_platform_ceiling_usd") or 0
    today = d.get("today_usd") or 0.0
    yday = d.get("yesterday_usd") or 0.0
    pct = (100.0 * today / cap) if cap > 0 else None
    reasons, level = [], "GREEN"

    if cap <= 0:
        level = "RED"; reasons.append("the platform ceiling is UNSET - AI spend is uncapped")
    elif pct >= RED_PCT:
        level = "RED";   reasons.append("%.0f%% of the $%.0f daily ceiling used" % (pct, cap))
    elif pct >= AMBER_PCT:
        level = "AMBER"; reasons.append("%.0f%% of the $%.0f daily ceiling used" % (pct, cap))

    ucap = d.get("daily_user_ceiling_usd") or 0
    at_rail = [u for u in d.get("top_users_today") or [] if ucap and (u.get("usd") or 0) >= ucap]
    if at_rail:
        level = "AMBER" if level == "GREEN" else level
        reasons.append("%d user(s) at their $%.2f daily rail" % (len(at_rail), ucap))

    br = d.get("ceiling_breaker") or {}
    if br.get("closed"):
        level = "RED"
        reasons.append("the cost ceiling has CLOSED (accounting unreadable) - paid AI refused")
    elif br.get("blind_calls"):
        level = "RED" if level == "RED" else "AMBER"
        reasons.append("%d paid call(s) ran UNMETERED (C1-FAILSAFE-1 blind calls)" % br["blind_calls"])
    elif d.get("_source") == "ssh":
        reasons.append("breaker state not visible over ssh - set MS_ADMIN_KEY to see it")

    head = "AI spend today $%.4f" % today
    if pct is not None:
        head += " (%.2f%% of $%.0f)" % (pct, cap)
    head += " | yesterday $%.4f" % yday
    if d.get("alltime_usd") is not None:
        head += " | all time $%.2f over %d calls" % (d["alltime_usd"], d.get("alltime_calls") or 0)
    return level, head + (" | " + "; ".join(reasons) if reasons else "")


def main():
    d = _via_endpoint() or _via_ssh()
    level, line = verdict(d)

    if "--json" in sys.argv:
        print(json.dumps({"level": level, "line": line, "data": d}, indent=1)); return 0

    print("%s  %s" % (level, line))

    if "--full" in sys.argv and d:
        print("\n  source: %s" % d.get("_source"))
        print("  ceilings: user $%.2f/day  platform $%.2f/day"
              % (d.get("daily_user_ceiling_usd") or 0, d.get("daily_platform_ceiling_usd") or 0))
        if d.get("days"):
            print("\n  %-12s %12s %8s" % ("DAY (UTC)", "SPEND USD", "CALLS"))
            for r in d["days"]:
                print("  %-12s %12.6f %8d" % (r["date"], r["usd"], r["calls"]))
        if d.get("by_endpoint"):
            print("\n  TOP ENDPOINTS (7 days):")
            for r in d["by_endpoint"]:
                print("    %-36s $%9.6f  %5d calls" % (r["endpoint"][:36], r["usd"], r["calls"]))
        if d.get("top_users_today"):
            print("\n  TOP SPENDERS TODAY:")
            for r in d["top_users_today"]:
                print("    %-36s $%9.6f  %5d calls" % (str(r["email"])[:36], r["usd"], r["calls"]))
        br = d.get("ceiling_breaker")
        if br:
            print("\n  CEILING BREAKER: %s" % br.get("note"))

    # A durable trend, so the gauge is useful even on a day nobody runs it by hand.
    try:
        stamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        new = not os.path.exists(LOG)
        with open(LOG, "a", encoding="utf-8") as f:
            if new:
                f.write("# SPEND_LOG — one line per gauge run (SPEND-GAUGE-1)\n\n"
                        "*Appended by `scripts/spend_gauge.py`. NOT MEASURED is a real value "
                        "and is never written as zero.*\n\n")
            f.write("- `%s UTC` **%s** — %s\n" % (stamp, level, line))
    except Exception as exc:
        print("# could not append to SPEND_LOG.md: %s" % exc, file=sys.stderr)

    return 0 if level in ("GREEN", "AMBER") else 1


if __name__ == "__main__":
    sys.exit(main())
