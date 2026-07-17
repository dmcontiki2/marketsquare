#!/usr/bin/env python3
# check_deploy_drift.py - MarketSquare DAILY DEPLOY-DRIFT MONITOR (added 17 Jul 2026)
# -----------------------------------------------------------------------------
# Read-only. Compares the md5 of each tracked LOCAL file against the copy actually
# SERVED on the Hetzner box, and prints ONE verdict line for the daily loop:
#
#   DEPLOY DRIFT: clean - all N tracked files match live
#   DEPLOY DRIFT: 2 file(s) local-ahead of live - run /ship: ms.js, dashboard.html
#
# WHY: the daily conductor is deliberately SHADOW (deploys nothing). This is the
# safe half of a deploy: it never pushes, it just tells David when local is ahead
# of live so he can /ship intentionally - closing the silent-drift gap
# (cf. FEA-MSJS-DRIFT-09JUL, BASELINE-12JUN-1) without ever auto-deploying.
#
# NON-FATAL BY DESIGN (same rule as predeploy_check.py): always exits 0 so it can
# never break a loop run. --json emits a machine-readable blob for the loop.
import os, sys, json, hashlib, subprocess

HERE   = os.path.dirname(os.path.abspath(__file__))
SERVER = os.environ.get("MS_SERVER", "msdeploy@178.104.73.239")  # read-only md5 reads; matches the daily-loop SSH user
REMOTE = "/var/www/marketsquare"

# local filename -> path served on the box (relative to REMOTE).
# Kept in step with deploy_marketsquare.bat / predeploy_check.py TARGETS.
FILEMAP = {
    "bea_main.py":            "main.py",
    "auth.py":                "auth.py",
    "database.py":            "database.py",
    "storage.py":             "storage.py",
    "payments.py":            "payments.py",
    "ai_provider.py":         "ai_provider.py",
    "ai_service_tiers.py":    "ai_service_tiers.py",
    "launch_redemption.py":   "launch_redemption.py",
    "marketsquare.html":      "index.html",
    "marketsquare_admin.html":"admin.html",
    "dashboard.html":         "dashboard.html",
    "ms.js":                  "static/ms.js",
    "ms.css":                 "static/ms.css",
    "privacy.html":           "privacy.html",
    "terms.html":             "terms.html",
    "support.html":           "support.html",
    "wonders.json":           "wonders.json",
    "demo_listings.json":     "demo_listings.json",
    "demo_sellers.json":      "demo_sellers.json",
}

def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def _server_md5s(remote_paths):
    """One SSH round-trip: md5sum every served file. Returns {remote_path: md5}."""
    quoted = " ".join(remote_paths)
    cmd = ["ssh", "-o", "ConnectTimeout=15", "-o", "BatchMode=yes", SERVER,
           f"cd {REMOTE} && md5sum {quoted} 2>/dev/null"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    except Exception as e:
        return None, f"ssh failed: {e}"
    if out.returncode != 0 and not out.stdout.strip():
        return None, (out.stderr or "ssh returned no output").strip()
    got = {}
    for line in out.stdout.splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            got[parts[1].strip()] = parts[0].strip()
    return got, None

def main():
    as_json = "--json" in sys.argv
    local = {}          # local_name -> (md5, remote_rel)
    missing_local = []
    for lname, rrel in FILEMAP.items():
        lpath = os.path.join(HERE, lname)
        if os.path.isfile(lpath):
            local[lname] = (_md5(lpath), rrel)
        else:
            missing_local.append(lname)

    server, err = _server_md5s([rrel for _, rrel in local.values()])
    if server is None:
        line = f"DEPLOY DRIFT: unknown - could not reach server ({err})"
        print(json.dumps({"status": "unreachable", "error": err, "line": line}) if as_json else line)
        return 0

    ahead, not_on_server = [], []
    for lname, (lmd5, rrel) in local.items():
        smd5 = server.get(rrel)
        if smd5 is None:
            not_on_server.append(lname)
        elif smd5 != lmd5:
            ahead.append(lname)

    drift = ahead + not_on_server
    n = len(local)
    if not drift:
        line = f"DEPLOY DRIFT: clean - all {n} tracked files match live"
    else:
        bits = []
        if ahead:         bits.append(", ".join(sorted(ahead)))
        if not_on_server: bits.append(", ".join(f"{f} (never deployed)" for f in sorted(not_on_server)))
        line = f"DEPLOY DRIFT: {len(drift)} file(s) local-ahead of live - run /ship: " + "; ".join(bits)

    if as_json:
        print(json.dumps({
            "status": "clean" if not drift else "drift",
            "tracked": n, "ahead": sorted(ahead),
            "never_deployed": sorted(not_on_server),
            "missing_local": sorted(missing_local), "line": line,
        }))
    else:
        print(line)
        if missing_local:
            print("  (note: not found locally, skipped: " + ", ".join(sorted(missing_local)) + ")")
    return 0

if __name__ == "__main__":
    sys.exit(main())
