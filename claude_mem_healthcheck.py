#!/usr/bin/env python3
"""
claude_mem_healthcheck.py  --  truthful health verdict for claude-mem.

WHY THIS EXISTS
---------------
The old daily check only looked at "newest session summary age" and shouted
"claude-mem has STOPPED RECORDING" whenever that was >36h old. But an old
newest-summary is AMBIGUOUS: it looks identical whether (a) the worker is dead,
or (b) the worker is perfectly healthy and simply no Claude *Code* CLI session
has run recently (summaries are only written by CLI sessions; Cowork-only work
produces none). That false alarm is what kept making a healthy system look
broken. This check separates those states using several signals instead of one.

It is READ-ONLY. It copies the DB read-only (never touches the live file),
reads runtime files over the mount, and (best-effort) pings the worker's HTTP
health endpoint if it happens to be reachable from where this runs.

Exit codes:  0 = OK/QUIET (no action)   1 = WARN/DOWN (action suggested)
"""
import argparse, glob, json, os, re, shutil, sqlite3, sys, tempfile, urllib.request
from datetime import datetime, timezone, timedelta

NOW = datetime.now(timezone.utc)

def parse_iso(s):
    if not s: return None
    s = str(s).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        try:
            dt = datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

def hours_since(dt):
    return None if dt is None else (NOW - dt).total_seconds() / 3600.0

def newest_summary(db_path):
    """Newest session_summaries.created_at, WAL-inclusive, via a read-only copy."""
    if not os.path.exists(db_path):
        return None, "claude-mem.db not found"
    tmp = tempfile.mkdtemp(prefix="cmhc_")
    try:
        base = os.path.join(tmp, "cm.db")
        shutil.copy2(db_path, base)
        for ext in ("-wal", "-shm"):
            if os.path.exists(db_path + ext):
                shutil.copy2(db_path + ext, base + ext)
        con = sqlite3.connect(base)
        try:
            row = con.execute("SELECT MAX(created_at) FROM session_summaries").fetchone()
            n = con.execute("SELECT COUNT(*) FROM session_summaries").fetchone()[0]
            return (row[0] if row else None), f"{n} summaries"
        finally:
            con.close()
    except Exception as e:
        return None, f"db read error: {e}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def latest_log_dt(mem):
    """Most recent activity timestamp from the worker's daily log files."""
    logs = sorted(glob.glob(os.path.join(mem, "logs", "claude-mem-*.log")))
    if not logs:
        return None
    newest = logs[-1]
    # try the last timestamped line, else the file mtime
    try:
        with open(newest, "r", encoding="utf-8", errors="ignore") as f:
            tail = f.readlines()[-400:]
        for line in reversed(tail):
            m = re.search(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
            if m:
                return parse_iso(m.group(1))
    except Exception:
        pass
    try:
        return datetime.fromtimestamp(os.path.getmtime(newest), tz=timezone.utc)
    except Exception:
        return None

def try_http_health(port):
    if not port:
        return None
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=3) as r:
            return r.status == 200
    except Exception:
        return None  # unreachable from here (e.g. worker is on a different host) — inconclusive

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mem", default=os.path.expanduser("~/.claude-mem"),
                    help="path to the .claude-mem dir")
    ap.add_argument("--stale-hours", type=float, default=36.0)
    ap.add_argument("--down-hours", type=float, default=48.0,
                    help="no worker activity for this long => treat worker as down")
    args = ap.parse_args()
    mem = args.mem
    db  = os.path.join(mem, "claude-mem.db")

    # --- gather signals ---
    settings = {}
    try:
        with open(os.path.join(mem, "settings.json"), encoding="utf-8") as f:
            settings = json.load(f)
    except Exception:
        pass
    chroma_off = str(settings.get("CLAUDE_MEM_CHROMA_ENABLED", "true")).lower() == "false"

    pid_info, pid_started = {}, None
    try:
        with open(os.path.join(mem, "worker.pid"), encoding="utf-8") as f:
            pid_info = json.load(f)
        pid_started = parse_iso(pid_info.get("startedAt"))
    except Exception:
        pass

    summ_iso, summ_note = newest_summary(db)
    summ_dt = parse_iso(summ_iso)
    summ_age = hours_since(summ_dt)
    log_dt = latest_log_dt(mem)
    log_age = hours_since(log_dt)
    pid_age = hours_since(pid_started)
    http_ok = try_http_health(pid_info.get("port"))

    # worker considered "showing recent activity" if the HTTP ping worked, OR
    # a log line / pid start is within down-hours.
    recent_activity = (http_ok is True) or \
        (log_age is not None and log_age <= args.down_hours) or \
        (pid_age is not None and pid_age <= args.down_hours)

    # --- classify ---
    if not pid_info:
        status, action = "DOWN", "No worker.pid — worker not running. Run repair_claude_mem.ps1."
    elif http_ok is False:
        status, action = "DOWN", "Worker HTTP health failed. Run repair_claude_mem.ps1."
    elif not recent_activity and (summ_age is None or summ_age > args.stale_hours):
        status, action = ("WARN",
            "No worker activity and no recent summaries. If you HAVE run Claude Code CLI "
            "sessions since then, the worker is likely stuck — run repair_claude_mem.ps1.")
    elif summ_age is not None and summ_age > args.stale_hours:
        status, action = ("QUIET",
            "Worker looks alive; the old newest-summary just means no Claude Code CLI "
            "session has been recorded recently (normal during Cowork-only / quiet periods). "
            "Not a fault.")
    else:
        status, action = "OK", "Recording is current."

    # --- report ---
    def fmt(dt, age):
        if dt is None: return "unknown"
        return f"{dt.date()} ({age:.0f}h ago)" if age is not None else str(dt.date())

    print(f"claude-mem healthcheck @ {NOW.isoformat(timespec='seconds')}")
    print(f"  mode             : {'SQLite-only (Chroma disabled ✓)' if chroma_off else 'Chroma ENABLED (fragile vector path active)'}")
    print(f"  worker.pid       : {'present, pid '+str(pid_info.get('pid'))+', started '+fmt(pid_started,pid_age) if pid_info else 'MISSING'}")
    print(f"  last log activity: {fmt(log_dt, log_age)}")
    print(f"  http /health     : {'ok' if http_ok is True else ('FAILED' if http_ok is False else 'not reachable from here (inconclusive)')}")
    print(f"  newest summary   : {fmt(summ_dt, summ_age)}  [{summ_note}]")
    print(f"  VERDICT          : {status} — {action}")
    if not chroma_off:
        print("  NOTE             : Chroma is still enabled. Running repair_claude_mem.ps1 "
              "switches to the reliable SQLite-only mode.")
    return 0 if status in ("OK", "QUIET") else 1

if __name__ == "__main__":
    sys.exit(main())
