#!/usr/bin/env python3
"""scripts/backup_db_sandbox.py - the DB-archive lane, SANDBOX half (BACKUP-UNATTENDED-1).

Why this exists: backup_marketsquare.bat is native-Windows only, nothing schedules it,
and the lane therefore stops the moment nobody remembers to run it -- 27 days stale
before 1 Sep, 9 days stale by 10 Sep, with RG-0234 red the whole time. A freshness
assertion with no producer behind it can only ever report the same failure again.

This half needs no host click: it snapshots the live DB on the box with sqlite3 .backup
(consistent, read-only), pulls it, zips it as backups/YYYY-MM-DD_HHMM.zip in exactly the
shape RG-0234 restores, PRAGMA-integrity-checks the pulled copy, and appends the dated
proof to backups/RESTORE_PROOF.md. It DELETES NOTHING -- retention stays with the host
bat, because deletions are David's (RUL-095).
"""
import hashlib, os, shutil, subprocess, sqlite3, sys, tempfile, zipfile
from datetime import datetime, timezone

REPO   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = "root@178.104.73.239"
REMOTE = "/var/www/marketsquare/marketsquare.db"


def _run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300, **kw)


def main():
    # the sandbox loses ~/.ssh between sessions -- SSH-BOOTSTRAP-1 self-heals it
    loader = os.path.join(REPO, "load_sandbox_ssh.sh")
    if os.path.isfile(loader):
        _run(["bash", loader])

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    snap  = "/tmp/ms_%s.db" % stamp
    r = _run(["ssh", "-o", "ConnectTimeout=20", SERVER,
              "sqlite3 %s '.backup %s'" % (REMOTE, snap)])
    if r.returncode != 0:
        print("FAIL  server snapshot: %s" % (r.stderr or r.stdout).strip()[:300]); return 1

    tmpd = tempfile.mkdtemp(prefix="msbak-")
    local = os.path.join(tmpd, "marketsquare.db")
    r = _run(["scp", "-o", "ConnectTimeout=20", "%s:%s" % (SERVER, snap), local])
    if r.returncode != 0 or not os.path.isfile(local):
        print("FAIL  scp: %s" % (r.stderr or r.stdout).strip()[:300]); return 1

    # md5 both ends -- a truncated pull must never wear the word 'backup'
    rm = _run(["ssh", SERVER, "md5sum %s" % snap]).stdout.split()[:1]
    lm = hashlib.md5(open(local, "rb").read()).hexdigest()
    if rm and rm[0] != lm:
        print("FAIL  md5 mismatch: server=%s local=%s" % (rm[0], lm)); return 1
    _run(["ssh", SERVER, "rm -f %s" % snap])          # our own /tmp scratch on the box

    con = sqlite3.connect("file:%s?mode=ro" % local, uri=True)
    ok  = con.execute("PRAGMA integrity_check").fetchone()[0]
    if ok != "ok":
        print("FAIL  integrity_check on the pulled DB: %s" % ok); return 1
    counts = {}
    for t in ("users", "listings"):
        try:
            counts[t] = con.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
        except Exception:
            counts[t] = "?"
    con.close()

    bdir = os.path.join(REPO, "backups")
    os.makedirs(bdir, exist_ok=True)
    arc = os.path.join(bdir, "%s.zip" % stamp)
    with zipfile.ZipFile(arc, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(local, "marketsquare.db")

    # prove the ARCHIVE restores, not merely the file we happened to hold
    vd = tempfile.mkdtemp(prefix="msver-")
    with zipfile.ZipFile(arc) as z:
        z.extractall(vd)
    vcon = sqlite3.connect("file:%s?mode=ro" % os.path.join(vd, "marketsquare.db"), uri=True)
    vok  = vcon.execute("PRAGMA integrity_check").fetchone()[0]
    vcon.close()
    shutil.rmtree(vd, ignore_errors=True); shutil.rmtree(tmpd, ignore_errors=True)
    if vok != "ok":
        print("FAIL  the ARCHIVE did not restore: %s" % vok); return 1

    proof = os.path.join(bdir, "RESTORE_PROOF.md")
    with open(proof, "a", encoding="utf-8") as fh:
        fh.write("\n## %s — archive %s.zip\n"
                 "- restored from archive to temp, PRAGMA integrity_check: ok\n"
                 "- rows: users=%s, listings=%s\n"
                 "- source: live DB snapshot via sqlite3 .backup on the box, md5-matched "
                 "after scp\n- made by: scripts/backup_db_sandbox.py (unattended, "
                 "maintenance loop)\n"
                 % (stamp[:10], stamp, counts["users"], counts["listings"]))
    print("OK  archive %s (%d bytes), restores clean, users=%s listings=%s"
          % (os.path.basename(arc), os.path.getsize(arc), counts["users"], counts["listings"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
