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
import os, sys, json, hashlib, subprocess, re

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
    # DRIFT-FILEMAP-1 (15 Aug 2026): the SERVED dashboard.html is built from
    # dashboard.server.html (deploy_manifest.txt:72), not from the local dashboard.html,
    # which is a different file and is not deployed at all. Comparing the wrong source
    # meant this row could NEVER match -- the same phantom-drift class as DRIFT-CACHEBUST-1,
    # a different cause. Compare what actually ships.
    "dashboard.server.html":  "dashboard.html",
    "ms.js":                  "static/ms.js",
    "ms.css":                 "static/ms.css",
    "privacy.html":           "privacy.html",
    "terms.html":             "terms.html",
    "support.html":           "support.html",
    "wonders.json":           "wonders.json",
    "demo_listings.json":     "demo_listings.json",
    "demo_sellers.json":      "demo_sellers.json",
}

# DRIFT-MANIFEST-1 (27 Sep 2026, RIPPLE-2): the 19 files above were the ONLY ones compared, so a change to any
# other shipped file (ripple_features.py, join.html, tier_resolvers.py ...) read "clean - in sync" and the nightly
# / on-request ship said SHIPPED while shipping nothing. Every "src | dest" line of the deploy manifest is now
# compared as well; FILEMAP stays as the explicit base.
def _manifest_map():
    out = {}
    try:
        with open(os.path.join(HERE, "ops", "autodeploy", "deploy_manifest.txt"), encoding="utf-8") as f:
            for ln in f:
                ln = ln.split("#", 1)[0].strip()
                if "|" not in ln:
                    continue
                src, dst = [x.strip() for x in ln.split("|", 1)]
                # binaries ride the media lane (git ignores them), so only text sources are compared here
                if os.path.splitext(src)[1].lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".webm",
                                                        ".gz", ".zip", ".pdf", ".ico", ".woff", ".woff2", ".mp3"):
                    continue
                if src and dst and not dst.endswith("/") and "*" not in src and os.path.isfile(os.path.join(HERE, src)):
                    out[src] = dst
    except Exception:
        return {}
    return out

for _src, _dst in _manifest_map().items():
    FILEMAP.setdefault(_src, _dst)

_CACHEBUST_RE = re.compile(rb"\?v=[0-9]+")

def _md5(path):
    """md5 of the file with CRLF normalised to LF (DRIFT-CRLF-1, 3 Aug 2026).

    The ONE-deploy engine places files by `git checkout` on the box, which writes
    LF. Windows working-copy files here are CRLF, so a raw byte md5 can NEVER
    match live for a CRLF file (ms.js: local 1049997B vs live 1033905B = exactly
    its 16092 line endings) and this monitor reported permanent phantom drift.
    Normalising both sides compares CONTENT, which is what "is live behind?" means.
    Server files are already LF, so normalising is a no-op there."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        data = f.read()
    data = data.replace(b"\r\n", b"\n")
    data = _CACHEBUST_RE.sub(b"?v=N", data)   # DRIFT-CACHEBUST-1
    h.update(data)
    return h.hexdigest()

def _server_md5s(remote_paths):
    """One SSH round-trip: md5sum every served file. Returns {remote_path: md5}."""
    quoted = " ".join(remote_paths)
    # DRIFT-CACHEBUST-1 (14 Aug 2026): server_deploy.sh rewrites `?v=N` in the SERVED
    # index.html (sed -i, monotonic bump) so a raw md5sum of the served file can NEVER
    # equal the source's. Normalise the cache-buster on the box before hashing, exactly
    # as DRIFT-CRLF-1 normalises line endings, so we compare CONTENT not the bump.
    cmd = ["ssh", "-o", "ConnectTimeout=15", "-o", "BatchMode=yes", SERVER,
           f"cd {REMOTE} && for f in {quoted}; do "
           f"printf '%s %s\\n' \"$(sed -E 's/\\?v=[0-9]+/?v=N/g' \"$f\" 2>/dev/null | md5sum | cut -d' ' -f1)\" \"$f\"; "
           f"done 2>/dev/null"]
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
    # SYNC-ORIGIN-1 (RUL-193, 1 Oct 2026): a file that differs is not necessarily newer HERE. Cloud sessions ship
    # straight to GitHub, so live can be the side that moved: on 1 Oct live was 61 commits ahead and this line said
    # 'local-ahead'. Count what GitHub's deploy ref holds that this laptop does not, and say which side moved.
    behind = 0
    try:
        _env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
        subprocess.run(["git", "fetch", "-q", "origin", "deploy"], cwd=HERE, env=_env, capture_output=True, timeout=60)
        _r = subprocess.run(["git", "rev-list", "--count", "HEAD..origin/deploy"], cwd=HERE, env=_env,
                            capture_output=True, text=True, timeout=30)
        behind = int((_r.stdout or "0").strip() or 0) if _r.returncode == 0 else 0
    except Exception:
        behind = 0
    if not drift:
        line = f"DEPLOY DRIFT: clean - all {n} tracked files match live"
    else:
        bits = []
        if ahead:         bits.append(", ".join(sorted(ahead)))
        if not_on_server: bits.append(", ".join(f"{f} (never deployed)" for f in sorted(not_on_server)))
        if behind:
            # no parentheses in this line: cmd re-parses a piped echo and chokes on them (DRIFT-PIPE-1)
            line = (f"DEPLOY DRIFT: {len(drift)} files differ from live - LIVE IS AHEAD by {behind} commits not on this "
                    f"laptop yet - the next ship takes them in first [SYNC-ORIGIN-1]: " + "; ".join(bits))
        else:
            line = f"DEPLOY DRIFT: {len(drift)} file(s) local-ahead of live - run /ship: " + "; ".join(bits)

    if as_json:
        print(json.dumps({
            "status": "clean" if not drift else "drift",
            "tracked": n, "ahead": sorted(ahead), "live_ahead_commits": behind,
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
