#!/usr/bin/env python3
# tsl_gate.py - TrustSquare Load (/TSL) PRE-DEPLOY GATE + CONCURRENCY LOCK
# =============================================================================
# The two things /ship does NOT already do, and nothing more. /TSL is a thin
# guarded front door: this file supplies (1) a real preventive concurrency LOCK
# so two deploys can never race, and (2) a pre-deploy GATE that confirms the
# change-management docs (CM) and the live databases are OK *before* a push.
# Everything after the gate - rollback tag, the scp/ssh upload via
# deploy_marketsquare.bat, smoke test, auto-rollback, CHANGELOG/STATUS record -
# is /ship's job and is not duplicated here.
#
# HOUSE RULES (same as predeploy_check.py / check_deploy_drift.py):
#   * Read-only. This script changes NOTHING on the server and never deploys.
#   * Non-fatal by design. Default mode = 'warn' -> always exits 0 so a monitor
#     can never break a good deploy. Set TSL_MODE=strict to exit non-zero on a
#     genuinely dangerous state (torn CM file, bad DB, or - in strict - a DB it
#     could not prove healthy) so a caller can abort.
#   * Every run appends one line to tsl_audit.log. A gate is never lost to luck.
#
# The private SSH key stays on David's machine: this script only ever *calls*
# ssh as the READ-ONLY msdeploy@ user (same user check_deploy_drift.py uses).
# Nothing here needs, reads, or copies the key itself.
#
# SUBCOMMANDS
#   acquire    create the local lock, or abort if a fresh one is held
#              (a stale lock older than the TTL is stolen, with an audit note)
#   gate       run the CM + DB checks and print a verdict (no lock change)
#   release    remove the local lock (always safe to call, even if absent)
#   status     show the current lock and a one-line summary
#   preflight  acquire + gate in one step (this is what /TSL runs first);
#              default when no subcommand is given
#
# TYPICAL /TSL FLOW (driven by the SKILL, on David's machine):
#   python tsl_gate.py preflight   # lock held + CM/DB proven -> go / no-go
#   ...  /ship  (deploy + smoke + record)  ...
#   ...  /pulse (final live confirm)  ...
#   python tsl_gate.py release      # ALWAYS, even if the deploy failed
# =============================================================================
import os
import re
import sys
import json
import time
import socket
import argparse
import subprocess
from datetime import datetime, timezone, date

HERE = os.path.dirname(os.path.abspath(__file__))
LOCK = os.path.join(HERE, ".tsl.lock")
LOG = os.path.join(HERE, "tsl_audit.log")

MODE = os.environ.get("TSL_MODE", "warn").lower()          # 'warn' | 'strict'
LOCK_TTL_MIN = int(os.environ.get("TSL_LOCK_TTL_MIN", "30"))
STATUS_STALE_DAYS = int(os.environ.get("TSL_STATUS_STALE_DAYS", "14"))

# Read-only SSH user (md5/stat/integrity reads only) - matches check_deploy_drift.py.
SERVER = os.environ.get("MS_SERVER", "msdeploy@178.104.73.239")
REMOTE = os.environ.get("MS_REMOTE", "/var/www/marketsquare")

# The change-management trio. "CM ok" = these three agree and record the ship.
CM_DOCS = ["STATUS.md", "CHANGELOG.md", "CHANGE_REGISTER.md"]

# The ONE authoritative live database. Other *.db files on the box (stray/empty
# leftovers) are reported but never gate a deploy. Override if it is renamed.
PRIMARY_DB = os.environ.get("MS_DB", "marketsquare.db")

# A subset of the deploy targets - enough to answer "is a real ship pending?"
# Kept in step with deploy_marketsquare.bat / predeploy_check.py.
DEPLOY_TARGETS = [
    "marketsquare.html", "marketsquare_admin.html", "ms.js", "ms.css",
    "bea_main.py", "auth.py", "database.py", "storage.py", "payments.py",
    "ai_provider.py", "launch_redemption.py",
]

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}


# ── small helpers ────────────────────────────────────────────────────────────
def _now_utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _audit(kind, verdict, detail=""):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("%s %-9s verdict=%-7s %s\n"
                    % (_now_utc_stamp(), kind, verdict, detail))
    except Exception:
        pass


def _git(args):
    try:
        r = subprocess.run(["git"] + args, cwd=HERE, capture_output=True,
                           text=True, timeout=20)
        return r.stdout if r.returncode == 0 else ""
    except Exception:
        return ""


def _read(rel):
    p = os.path.join(HERE, rel)
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return None


def _is_torn(rel):
    """True if a text file ends mid-line AND is shorter than its committed
    version - the same torn-file heuristic predeploy_check.py uses."""
    p = os.path.join(HERE, rel)
    try:
        size = os.path.getsize(p)
        if size <= 1:
            return False
        with open(p, "rb") as f:
            f.seek(-1, 2)
            last = f.read(1)
        if last == b"\n":
            return False
        r = subprocess.run(["git", "cat-file", "-s", "HEAD:" + rel], cwd=HERE,
                           capture_output=True, text=True, timeout=15)
        if r.returncode == 0 and r.stdout.strip().isdigit():
            return size < int(r.stdout.strip())
    except Exception:
        pass
    return False


def _newest_iso_date(text, not_after=None):
    """Newest YYYY-MM-DD found (STATUS.md session lines). Dates after
    `not_after` (e.g. today) are ignored - a forward-looking target date in the
    prose is a plan, not a session stamp, and must not read as 'fresh'."""
    best = None
    for y, m, d in re.findall(r"\b(20\d{2})-(\d{2})-(\d{2})\b", text or ""):
        try:
            cur = date(int(y), int(m), int(d))
        except ValueError:
            continue
        if not_after is not None and cur > not_after:
            continue
        if best is None or cur > best:
            best = cur
    return best


def _newest_changelog_date(text):
    """Newest '## DD Mon YYYY' header date (CHANGELOG.md)."""
    best = None
    for line in (text or "").splitlines():
        m = re.match(r"^\s*#{1,3}\s+(\d{1,2})\s+([A-Za-z]{3,})\s+(20\d{2})", line)
        if not m:
            continue
        mon = MONTHS.get(m.group(2)[:3].lower())
        if not mon:
            continue
        try:
            cur = date(int(m.group(3)), mon, int(m.group(1)))
        except ValueError:
            continue
        if best is None or cur > best:
            best = cur
    return best


def _dirty_paths():
    dirty = set()
    for line in _git(["status", "--porcelain"]).splitlines():
        if line.strip():
            dirty.add(line[3:].strip().replace("\\", "/"))
    return dirty


# ── the LOCK (FUSE-safe: never depends on unlink) ────────────────────────────
# The Projects folder is a virtiofs/FUSE bridge; on the cloud side os.remove/
# unlink is blocked ("Operation not permitted"). So release/steal must NOT depend
# on deleting the file: a released lock is one that is absent, empty, or marked
# {"released": true}. Staleness is read from the in-file 'acquired' stamp, not
# mtime (overwriting to release would otherwise reset the age).

def _age_min_from_stamp(stamp):
    try:
        t = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - t).total_seconds() / 60.0
    except Exception:
        return None


def _lock_status():
    """(state, info): state in absent|free|held. 'held' info carries _age_min;
    the caller compares that to the TTL to decide block vs reclaim."""
    if not os.path.isfile(LOCK):
        return ("absent", {})
    try:
        raw = open(LOCK, "r", encoding="utf-8").read().strip()
    except Exception:
        return ("absent", {})
    if not raw:
        return ("free", {})
    try:
        data = json.loads(raw)
    except Exception:
        return ("free", {})            # unparseable -> treat as free, never wedge
    if data.get("released"):
        return ("free", data)
    data["_age_min"] = _age_min_from_stamp(data.get("acquired"))
    return ("held", data)


def _take_lock(payload):
    """Prefer an atomic exclusive create (race-safe on a native filesystem);
    fall back to an in-place overwrite when the file already exists (released/
    stale) or when unlink is unavailable (FUSE)."""
    body = json.dumps(payload).encode("utf-8")
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        try:
            os.write(fd, body)
        finally:
            os.close(fd)
        return
    except FileExistsError:
        pass
    with open(LOCK, "wb") as f:         # overwrite in place - no unlink needed
        f.write(body)


def cmd_acquire():
    payload = {
        "acquired": _now_utc_stamp(),
        "host": socket.gethostname(),
        "pid": os.getpid(),
        "ttl_min": LOCK_TTL_MIN,
    }
    state, info = _lock_status()
    if state == "held":
        age = info.get("_age_min")
        held_by = info.get("host", "?")
        since = info.get("acquired", "?")
        if age is not None and age <= LOCK_TTL_MIN:
            print("  [LOCK] BLOCKED - a TrustSquare Load is already in progress")
            print("         held by %s since %s (%.0f min ago, TTL %d min)."
                  % (held_by, since, age, LOCK_TTL_MIN))
            print("         If you are certain no deploy is running, delete")
            print("         %s and retry." % LOCK)
            _audit("acquire", "BLOCKED", "held_by=%s age_min=%.0f" % (held_by, age))
            return 1
        agestr = ("%.0f" % age) if age is not None else "unknown"
        print("  [LOCK] Stale lock (%s min > TTL %d) from %s - reclaiming it."
              % (agestr, LOCK_TTL_MIN, held_by))
        _audit("acquire", "STOLEN", "prev_host=%s age_min=%s" % (held_by, agestr))
    try:
        _take_lock(payload)
    except Exception as e:
        # Non-fatal: never block a deploy because the lock file couldn't be written.
        print("  [LOCK] could not write lock: %r (continuing unlocked)" % e)
        _audit("acquire", "ERROR", repr(e))
        return 0
    print("  [LOCK] acquired by %s (pid %d), TTL %d min."
          % (payload["host"], payload["pid"], LOCK_TTL_MIN))
    _audit("acquire", "OK", "host=%s pid=%d" % (payload["host"], payload["pid"]))
    return 0


def cmd_release():
    if not os.path.isfile(LOCK):
        print("  [LOCK] no lock to release.")
        _audit("release", "NONE")
        return 0
    # Prefer a clean unlink (keeps the next acquire's atomic create race-safe).
    try:
        os.remove(LOCK)
        print("  [LOCK] released.")
        _audit("release", "OK")
        return 0
    except Exception:
        pass
    # Unlink unavailable (FUSE 'Operation not permitted') -> mark released in place.
    try:
        with open(LOCK, "w", encoding="utf-8") as f:
            json.dump({"released": True, "at": _now_utc_stamp()}, f)
        print("  [LOCK] released (marked in place; unlink not available here).")
        _audit("release", "OK", "marked")
        return 0
    except Exception as e:
        print("  [LOCK] could not release lock: %r" % e)
        _audit("release", "ERROR", repr(e))
        return 0


def cmd_status():
    state, info = _lock_status()
    if state in ("absent", "free"):
        print("  [LOCK] free (no deploy in progress).")
        return 0
    age = info.get("_age_min")
    fresh = age is not None and age <= LOCK_TTL_MIN
    print("  [LOCK] %s - held by %s since %s (%s min ago)."
          % ("FRESH" if fresh else "STALE", info.get("host", "?"),
             info.get("acquired", "?"),
             ("%.0f" % age) if age is not None else "unknown"))
    return 0


# ── the GATE: CM + databases ─────────────────────────────────────────────────
def check_cm():
    """Change-management trio. Returns (verdict, lines). verdict in
    ok | REVIEW | DANGER. DANGER only for a missing/torn doc (strict-abortable)."""
    lines, danger, review = [], [], []
    for doc in CM_DOCS:
        p = os.path.join(HERE, doc)
        if not os.path.isfile(p) or os.path.getsize(p) == 0:
            danger.append("%s missing/empty" % doc)
            lines.append("    - %-20s [MISSING/EMPTY]" % doc)
        elif _is_torn(doc):
            danger.append("%s torn" % doc)
            lines.append("    - %-20s [TORN - ends mid-line, shorter than committed]" % doc)
        else:
            lines.append("    - %-20s [ok]" % doc)

    # Is a real ship pending? (any deploy target dirty)
    dirty = _dirty_paths()
    pending = sorted(t for t in DEPLOY_TARGETS if t in dirty)

    status_txt = _read("STATUS.md")
    changelog_txt = _read("CHANGELOG.md")
    today = datetime.now().date()
    s_date = _newest_iso_date(status_txt, not_after=today) if status_txt else None
    c_date = _newest_changelog_date(changelog_txt) if changelog_txt else None

    if s_date:
        stale_days = (today - s_date).days
        if stale_days > STATUS_STALE_DAYS:
            review.append("STATUS.md newest date %s is %d days old"
                          % (s_date.isoformat(), stale_days))
        lines.append("    - STATUS newest date : %s (%d days ago)"
                     % (s_date.isoformat(), stale_days))
    else:
        review.append("could not read a date from STATUS.md")

    if c_date:
        lines.append("    - CHANGELOG newest    : %s" % c_date.isoformat())

    if pending:
        lines.append("    - Ship pending        : %s" % ", ".join(pending))
        # The core CM rule: "a ship that is not recorded did not happen."
        changelog_dirty = ("CHANGELOG.md" in dirty)
        recorded_today = (c_date == today)
        if not (changelog_dirty or recorded_today):
            review.append("code is shipping but CHANGELOG's newest entry is %s, "
                          "not today, and CHANGELOG.md is not itself modified - "
                          "record this ship first" % (c_date.isoformat() if c_date else "unknown"))
        if "CHANGE_REGISTER.md" not in dirty and c_date != today:
            # Advisory only - not every ship needs a register ticket.
            lines.append("    - (note) CHANGE_REGISTER.md not modified this session")
    else:
        lines.append("    - Ship pending        : none detected (working tree clean)")

    verdict = "DANGER" if danger else ("REVIEW" if review else "ok")
    if danger:
        lines.append("    !! " + "; ".join(danger))
    for r in review:
        lines.append("    >> " + r)
    return verdict, lines


def _ssh_read(remote_cmd, timeout=40):
    """One read-only SSH round-trip as the msdeploy@ user. Returns
    (stdout, err). err is None on success."""
    cmd = ["ssh", "-o", "ConnectTimeout=15", "-o", "BatchMode=yes", SERVER,
           remote_cmd]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except Exception as e:
        return "", "ssh failed: %s" % e
    if r.returncode != 0 and not r.stdout.strip():
        return "", (r.stderr or "ssh returned no output").strip()
    return r.stdout, None


def check_db():
    """Live databases, read-only. Returns (verdict, lines). verdict in
    ok | REVIEW | DANGER. Unreachable = REVIEW (in strict, that blocks:
    the gate exists to *prove* the DB, and it could not)."""
    lines = []
    # One round-trip: discover *.db, integrity-check each, ping redis.
    remote = (
        "cd %s 2>/dev/null; "
        "for f in *.db; do "
        "  [ -e \"$f\" ] || continue; "
        "  sz=$(stat -c%%s \"$f\" 2>/dev/null || echo 0); "
        "  ic=$(sqlite3 \"$f\" 'PRAGMA integrity_check;' 2>/dev/null | head -n1); "
        "  echo \"DB|$f|$sz|${ic:-noread}\"; "
        "done; "
        "if command -v redis-cli >/dev/null 2>&1; then "
        "  echo \"REDIS|$(redis-cli ping 2>/dev/null || echo NOPING)\"; "
        "else echo \"REDIS|absent\"; fi"
    ) % REMOTE
    out, err = _ssh_read(remote)
    if err:
        lines.append("    - server            : UNREACHABLE (%s)" % err)
        lines.append("    >> could not prove the databases healthy this run")
        return "REVIEW", lines

    danger, review, note = [], [], []
    saw_primary = False
    for line in out.splitlines():
        parts = line.strip().split("|")
        if parts[0] == "DB" and len(parts) >= 4:
            name, sz, ic = parts[1], parts[2], parts[3]
            try:
                szn = int(sz)
            except ValueError:
                szn = 0
            if name == PRIMARY_DB:
                saw_primary = True
                if szn <= 0:
                    danger.append("PRIMARY db %s is 0 bytes" % name)
                    lines.append("    - %-18s [ZERO BYTES - PRIMARY]" % name)
                elif ic.lower() == "ok":
                    lines.append("    - %-18s [ok, %d bytes, integrity ok] (primary)"
                                 % (name, szn))
                elif ic == "noread":
                    review.append("%s: integrity_check returned nothing "
                                  "(sqlite3 missing on server, or DB locked)" % name)
                    lines.append("    - %-18s [%d bytes, integrity UNKNOWN]" % (name, szn))
                else:
                    danger.append("PRIMARY db %s integrity_check = %s" % (name, ic))
                    lines.append("    - %-18s [INTEGRITY: %s]" % (name, ic))
            else:
                # A non-primary *.db is a stray/secondary file: report, never gate.
                if szn <= 0:
                    note.append("%s is 0 bytes (stray/empty - ignored)" % name)
                    lines.append("    - %-18s [empty - ignored, not the primary]" % name)
                else:
                    lines.append("    - %-18s [%d bytes - secondary, not gated]" % (name, szn))
        elif parts[0] == "REDIS":
            val = parts[1] if len(parts) > 1 else "?"
            if val == "PONG":
                lines.append("    - redis             [ok, PONG]")
            elif val == "absent":
                lines.append("    - redis             [not installed - skipped]")
            else:
                review.append("redis did not answer PONG (%s)" % val)
                lines.append("    - redis             [%s]" % val)

    if not saw_primary:
        review.append("primary db '%s' not found under %s - set MS_DB if it is "
                      "named differently or lives elsewhere" % (PRIMARY_DB, REMOTE))
        lines.append("    - %-18s [PRIMARY NOT FOUND under %s]" % (PRIMARY_DB, REMOTE))

    verdict = "DANGER" if danger else ("REVIEW" if review else "ok")
    for d in danger:
        lines.append("    !! " + d)
    for r in review:
        lines.append("    >> " + r)
    for n in note:
        lines.append("    -- " + n)
    return verdict, lines


def _worst(*verdicts):
    order = {"ok": 0, "REVIEW": 1, "DANGER": 2}
    return max(verdicts, key=lambda v: order.get(v, 1))


def cmd_gate():
    print("  ------------------------------------------------------------")
    print("  TSL PRE-DEPLOY GATE   %s   mode=%s" % (_now_utc_stamp(), MODE))
    print("  [CM] change-management docs")
    cm_v, cm_lines = check_cm()
    for l in cm_lines:
        print(l)
    print("  [DB] live databases (read-only, %s)" % SERVER)
    db_v, db_lines = check_db()
    for l in db_lines:
        print(l)

    overall = _worst(cm_v, db_v)
    print("  Verdict: CM=%s  DB=%s  ->  %s   (logged -> tsl_audit.log)"
          % (cm_v, db_v, overall))
    print("  ------------------------------------------------------------")
    _audit("gate", overall, "cm=%s db=%s" % (cm_v, db_v))

    # Exit code: warn always 0; strict blocks on anything that is not clean-ok.
    if MODE == "strict" and overall != "ok":
        return 1 if overall == "DANGER" else 2  # 2 = REVIEW (couldn't prove)
    return 0


def cmd_preflight():
    rc = cmd_acquire()
    if rc != 0:
        return rc            # lock is held by a live deploy - do not proceed
    print()
    return cmd_gate()


def main():
    ap = argparse.ArgumentParser(description="TrustSquare Load pre-deploy gate + lock")
    ap.add_argument("cmd", nargs="?", default="preflight",
                    choices=["preflight", "acquire", "gate", "release", "status"])
    args = ap.parse_args()
    return {
        "preflight": cmd_preflight,
        "acquire": cmd_acquire,
        "gate": cmd_gate,
        "release": cmd_release,
        "status": cmd_status,
    }[args.cmd]()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:   # a monitor must never break a deploy
        print("  [tsl_gate] non-fatal error: %r (continuing)" % e)
        _audit("error", "ERROR", repr(e))
        sys.exit(0)
