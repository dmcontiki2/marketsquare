#!/usr/bin/env python3
"""035_orchestrator_live_map.py -- MAP-LIVE-1 nginx half (30 Aug 2026, D15 fallback).

D15 (push-scoped GitHub PAT) was declined-by-silence, so this is the recorded
fallback: /orchestrator/defence_map.html and /orchestrator/watch_register.md are
served by the APP (bea_main.py MAP-LIVE-1 routes, this same deploy) which reads
`git show origin/main:<file>` from the server's repo checkout at request time --
the deploy timer fetches origin every ~2 min, so the gated ops map now trails a
PUSH by minutes instead of trailing a full deploy.

WHAT THIS MIGRATION DOES: inserts two EXACT-MATCH proxy locations inside the
"TrustSquare Orchestrator" Basic-Auth realm, directly above the static prefix
block `location /orchestrator/ {`. Exact-match outranks the prefix block, so
only these two URLs move to the app; everything else under /orchestrator/ stays
deploy-placed static. Auth stays at nginx on the new blocks -- byte-for-byte
the same auth_basic pair the realm already uses (the /orchestrator/approve
proxy is the in-file precedent).

DISCOVERY per RG-0186: the site file is found via `nginx -T` (every file nginx
actually reads), never a hand-written glob. Idempotent via the MAP-LIVE-1
marker. nginx -t + restore-on-failure + reload, then the effect is PROVEN:
  (a) the app on loopback answers 200 with an X-Map-Source header on both
      routes (the code half is alive),
  (b) the public URL over TLS+SNI answers 401 anonymously (the gate still
      fronts it -- serving the watch register ungated would be a leak).

REVERSING IT: the rollback command is printed on apply.
"""
import os, re, shutil, subprocess, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
BAK_DIR = "/root/nginx-backups"
MARK = "MAP-LIVE-1"

BLOCKS = """    # MAP-LIVE-1 30 Aug 2026: these two ops documents are served by the app,
    # which reads them from the repo checkout's fetched origin/main at request
    # time (fallback: the deploy-placed copy). Exact match outranks the static
    # prefix block below; the Basic-Auth gate is unchanged.
    location = /orchestrator/defence_map.html {
        auth_basic "TrustSquare Orchestrator";
        auth_basic_user_file /etc/nginx/.htpasswd_orch;
        add_header Cache-Control "no-store";
        expires -1;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    location = /orchestrator/watch_register.md {
        auth_basic "TrustSquare Orchestrator";
        auth_basic_user_file /etc/nginx/.htpasswd_orch;
        add_header Cache-Control "no-store";
        expires -1;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

"""


def say(m):
    print("[035_map] " + m, flush=True)


def _nginx_T_files():
    found = []
    try:
        r = subprocess.run(["nginx", "-T"], capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            for line in (r.stdout or "").splitlines():
                m = re.match(r"^#\s*configuration file\s+(/\S+?):\s*$", line)
                if m:
                    found.append(m.group(1))
    except Exception as ex:
        say("nginx -T unavailable: " + repr(ex)[:80])
    return found


RE_PREFIX = re.compile(r'^([ \t]*)location\s+/orchestrator/\s*\{', re.M)


def find_site():
    """The one nginx-read file that declares `location /orchestrator/ {`."""
    hits = {}
    for c in _nginx_T_files():
        try:
            rp = os.path.realpath(c)
            if not os.path.isfile(rp) or ".bak" in os.path.basename(rp):
                continue
            t = open(rp, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if RE_PREFIX.search(t):
            hits[rp] = t
    return hits


def _probe_app(path):
    """Loopback app probe: (status, x-map-source)."""
    import http.client
    conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=15)
    try:
        conn.request("GET", path, headers={"Host": "trustsquare.co",
                                           "User-Agent": "TrustSquare-Migration/035"})
        r = conn.getresponse()
        src = r.getheader("X-Map-Source") or ""
        r.read()
        return r.status, src
    finally:
        conn.close()


def _probe_public(path):
    """Anonymous public probe over TLS+SNI on loopback: status only."""
    import http.client, socket, ssl as _ssl
    ctx = _ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = _ssl.CERT_NONE
    conn = http.client.HTTPSConnection("127.0.0.1", 443, timeout=15, context=ctx)
    _raw = socket.create_connection(("127.0.0.1", 443), timeout=15)
    conn.sock = ctx.wrap_socket(_raw, server_hostname="trustsquare.co")
    try:
        conn.request("GET", path, headers={"Host": "trustsquare.co",
                                           "User-Agent": "TrustSquare-Migration/035"})
        r = conn.getresponse()
        r.read()
        return r.status
    finally:
        conn.close()


def main():
    sites = find_site()
    if not sites:
        say("REFUSING: no nginx-read file declares `location /orchestrator/ {`. Not guessing.")
        return 1
    if len(sites) > 1:
        say("REFUSING: %d files declare the orchestrator prefix block (%s) -- ambiguous."
            % (len(sites), ", ".join(sites)))
        return 1
    site, text = next(iter(sites.items()))
    say("site file: " + site)

    if MARK in text:
        say("marker already present -- nginx half applied earlier.")
    elif not APPLY:
        say("DRY RUN -- would insert the two gated proxy locations. Re-run with --apply.")
        return 0
    else:
        m = RE_PREFIX.search(text)
        os.makedirs(BAK_DIR, exist_ok=True)
        dest = os.path.join(BAK_DIR, os.path.basename(site) + ".bak-035-" + TS)
        shutil.copy2(site, dest)
        new = text[:m.start()] + BLOCKS + text[m.start():]
        open(site, "w", encoding="utf-8").write(new)
        assert MARK in open(site, encoding="utf-8").read(), "write did not land"
        say("inserted blocks (backup %s)" % dest)
        r = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
        if r.returncode != 0:
            say("nginx -t FAILED -- restoring: " + (r.stderr or r.stdout)[:200])
            shutil.copy2(dest, site)
            return 1
        r = subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
        if r.returncode != 0:
            say("reload FAILED -- restoring: " + (r.stderr or r.stdout)[:200])
            shutil.copy2(dest, site)
            subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
            return 1
        say("rollback: cp %s %s && nginx -t && nginx -s reload" % (dest, site))

    # PROVE both halves.
    ok = True
    for path in ("/orchestrator/defence_map.html", "/orchestrator/watch_register.md"):
        try:
            status, src = _probe_app(path)
            if status == 200 and src:
                say("app half PROVEN  %s -> 200, X-Map-Source=%s" % (path, src))
            else:
                say("app half FAILED  %s -> %s (X-Map-Source=%r). Is the deploy that "
                    "carries MAP-LIVE-1 in bea_main.py live yet?" % (path, status, src))
                ok = False
        except Exception as ex:
            say("app half UNREACHABLE %s: %s" % (path, repr(ex)[:80]))
            ok = False
        try:
            pstatus = _probe_public(path)
            if pstatus == 401:
                say("gate PROVEN      %s -> 401 anonymous (Basic Auth fronts it)" % path)
            else:
                say("gate CHECK       %s -> %s anonymous -- expected 401. NOT claiming the "
                    "gate; investigate before relying on it." % (path, pstatus))
                ok = False
        except Exception as ex:
            say("gate probe error %s: %s" % (path, repr(ex)[:80]))
            ok = False
    if not ok:
        say("NOT claiming success -- one or more proofs failed (nginx change, if made, "
            "was left in place: it is gate-preserving and inert without the app half).")
        return 1
    say("APPLIED AND PROVEN: live-map lane serving, gate intact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
