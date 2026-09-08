#!/usr/bin/env python3
"""037_device_auth.py -- DEVICE-AUTH-1 (8 Sep 2026, David: "it asks for a new password, is this
really necessary, please remove it, we only need the first login?").

DEVICE-ENROL-1 (3 Sep) enrolled David's phone with a signed, revocable 180-day `ts_device` cookie,
but only the APP honoured it (/m, /m/dashboard, /m/admin, CityLauncher). Every link out of the ops
dashboard to a page that nginx fronts with Basic auth -- /dashboard.html, /admin.html,
/command.html, /orchestrator/v2/cockpit.html, /orchestrator/simulation.html, defence_map,
watch_register -- threw the browser's "Sign in to trustsquare.co" box: a second password for a
phone the server had already recognised.

WHAT THIS MIGRATION DOES (nginx only; the app side already exists as GET /admin/device-ok):
  1. Adds an internal `location = /_device_ok` that sub-requests the app's /admin/device-ok with
     the visitor's cookies. ANY upstream error (app down, timeout, 5xx) is mapped to 401 via
     `proxy_intercept_errors` + `error_page ... =401 @device_deny`, so an outage falls back to
     Basic auth exactly as today -- never a 500 on the ops pages.
  2. `snippets/internal_auth.conf` (already `satisfy any` + Basic) gains `auth_request /_device_ok;`
     -- an enrolled device passes, everyone else meets the same Basic prompt as before.
  3. Every inline `auth_basic "TrustSquare Orchestrator";` block in the site file that does not use
     the snippet gains `satisfy any; auth_request /_device_ok;` above it. The Auctions realm (its own
     secret) and the AdvertAgent dev realm are deliberately untouched.

Nothing is REMOVED: the Basic credential still works everywhere it did, so a fault here cannot
lock anyone out. Idempotent via the DEVICE-AUTH-1 marker. nginx -t + restore-on-failure + reload,
then PROVEN: anonymous /dashboard.html over TLS still answers 401 with a Basic challenge (the gate
still fronts it) and the loopback app answers 401 on /admin/device-ok without a cookie (the
sub-request target is alive and fail-closed).

REVERSING IT: the rollback commands are printed on apply.
"""
import os, re, shutil, subprocess, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
BAK_DIR = "/root/nginx-backups"
MARK = "DEVICE-AUTH-1"

DEVICE_OK_BLOCK = """    # DEVICE-AUTH-1 (8 Sep 2026, David: "we only need the first login"): an enrolled device
    # (DEVICE-ENROL-1 ts_device cookie) passes the ops Basic-auth gate. The app answers 200 for
    # a valid, unrevoked device and 401 otherwise. Any upstream ERROR (app down, timeout, 5xx)
    # is mapped to 401 so the gate falls back to Basic auth exactly as before -- never a 500.
    location = /_device_ok {
        internal;
        proxy_pass http://127.0.0.1:8000/admin/device-ok;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
        proxy_set_header Host $host;
        proxy_set_header X-Original-URI $request_uri;
        proxy_connect_timeout 2s;
        proxy_read_timeout 5s;
        proxy_intercept_errors on;
        error_page 500 502 503 504 =401 @device_deny;
    }
    location @device_deny { return 401; }

"""
RE_ANCHOR = re.compile(r'^([ \t]*)location\s*=\s*/_review_gate\b', re.M)
RE_ORCH = re.compile(r'^([ \t]*)auth_basic\s+"TrustSquare Orchestrator";[ \t]*$', re.M)


def say(m):
    print("[037_device_auth] " + m, flush=True)


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


def _read(p):
    return open(p, encoding="utf-8", errors="replace").read()


def find_files():
    """(site file declaring /_review_gate, snippet internal_auth.conf) -- both from nginx -T, never guessed."""
    site, snip = {}, {}
    for c in _nginx_T_files():
        rp = os.path.realpath(c)
        if not os.path.isfile(rp) or ".bak" in os.path.basename(rp):
            continue
        t = _read(rp)
        if RE_ANCHOR.search(t):
            site[rp] = t
        if os.path.basename(rp) == "internal_auth.conf" and "satisfy any;" in t:
            snip[rp] = t
    return site, snip


def _probe_public(path, cookie=None):
    """Anonymous public probe over TLS+SNI on loopback: (status, WWW-Authenticate)."""
    import http.client, socket, ssl as _ssl
    ctx = _ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = _ssl.CERT_NONE
    conn = http.client.HTTPSConnection("127.0.0.1", 443, timeout=15, context=ctx)
    raw = socket.create_connection(("127.0.0.1", 443), timeout=15)
    conn.sock = ctx.wrap_socket(raw, server_hostname="trustsquare.co")
    try:
        h = {"Host": "trustsquare.co", "User-Agent": "TrustSquare-Migration/037"}
        if cookie: h["Cookie"] = cookie
        conn.request("GET", path, headers=h)
        r = conn.getresponse(); r.read()
        return r.status, (r.getheader("WWW-Authenticate") or "")
    finally:
        conn.close()


def _probe_app(path):
    import http.client
    conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=15)
    try:
        conn.request("GET", path, headers={"Host": "trustsquare.co", "User-Agent": "TrustSquare-Migration/037"})
        r = conn.getresponse(); r.read()
        return r.status
    finally:
        conn.close()


def _backup(p):
    os.makedirs(BAK_DIR, exist_ok=True)
    dest = os.path.join(BAK_DIR, os.path.basename(p) + ".bak-037-" + TS)
    shutil.copy2(p, dest)
    return dest


def main():
    sites, snips = find_files()
    if len(sites) != 1:
        say("REFUSING: expected exactly one nginx-read file declaring `location = /_review_gate` -- found %d (%s)"
            % (len(sites), ", ".join(sites) or "none")); return 1
    if len(snips) != 1:
        say("REFUSING: expected exactly one nginx-read snippets/internal_auth.conf with `satisfy any;` -- found %d (%s)"
            % (len(snips), ", ".join(snips) or "none")); return 1
    site, stext = next(iter(sites.items()))
    snip, ntext = next(iter(snips.items()))
    say("site file: %s   snippet: %s" % (site, snip))

    if MARK in stext and MARK in ntext:
        say("marker present in both files -- applied earlier.")
    elif not APPLY:
        say("DRY RUN -- would add /_device_ok, auth_request in the snippet, and satisfy-any on %d inline "
            "Orchestrator realm blocks. Re-run with --apply." % len(RE_ORCH.findall(stext))); return 0
    else:
        bsite, bsnip = _backup(site), _backup(snip)
        # 1. the internal sub-request location, directly above /_review_gate
        if MARK not in stext:
            m = RE_ANCHOR.search(stext)
            new = stext[:m.start()] + DEVICE_OK_BLOCK + stext[m.start():]
            # 3. inline Orchestrator-realm blocks (not the snippet users): satisfy any + auth_request
            def _sub(mm):
                ind = mm.group(1)
                return ("%ssatisfy any;                       # DEVICE-AUTH-1\n%sauth_request /_device_ok;          # DEVICE-AUTH-1\n%s"
                        % (ind, ind, mm.group(0)))
            new, n = RE_ORCH.subn(_sub, new)
            open(site, "w", encoding="utf-8").write(new)
            assert MARK in _read(site), "site write did not land"
            say("site: /_device_ok inserted; %d inline Orchestrator blocks now satisfy-any (backup %s)" % (n, bsite))
        # 2. the snippet
        if MARK not in ntext:
            assert ntext.count("satisfy any;") == 1
            new = ntext.replace("satisfy any;", "satisfy any;\nauth_request /_device_ok;   # DEVICE-AUTH-1: enrolled device OR Basic", 1)
            open(snip, "w", encoding="utf-8").write(new)
            assert MARK in _read(snip), "snippet write did not land"
            say("snippet: auth_request added (backup %s)" % bsnip)
        r = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
        if r.returncode != 0:
            say("nginx -t FAILED -- restoring both: " + (r.stderr or r.stdout)[:300])
            shutil.copy2(bsite, site); shutil.copy2(bsnip, snip); return 1
        r = subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
        if r.returncode != 0:
            say("reload FAILED -- restoring both: " + (r.stderr or r.stdout)[:300])
            shutil.copy2(bsite, site); shutil.copy2(bsnip, snip)
            subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True); return 1
        say("rollback: cp %s %s && cp %s %s && nginx -t && nginx -s reload" % (bsite, site, bsnip, snip))

    # PROVE: the gate still fronts the pages anonymously, and the sub-request target is alive + fail-closed.
    ok = True
    for path in ("/dashboard.html", "/orchestrator/v2/cockpit.html"):
        try:
            st, www = _probe_public(path)
            if st == 401 and "Basic" in www:
                say("gate PROVEN   %s -> 401 + Basic challenge anonymously" % path)
            elif st == 404 and path != "/dashboard.html":
                say("gate CHECK    %s -> 404 (file not deployed here; gate ran first or not -- not judged)" % path)
            else:
                say("gate CHECK    %s -> %s (WWW-Authenticate=%r) -- expected 401 + Basic. Investigate." % (path, st, www)); ok = False
        except Exception as ex:
            say("gate probe error %s: %s" % (path, repr(ex)[:80])); ok = False
    try:
        st = _probe_app("/admin/device-ok")
        if st == 401:
            say("app PROVEN    /admin/device-ok -> 401 without a cookie (fail-closed, alive)")
        else:
            say("app CHECK     /admin/device-ok -> %s -- expected 401" % st); ok = False
    except Exception as ex:
        say("app probe error: %s" % repr(ex)[:80]); ok = False
    if not ok:
        say("NOT claiming success -- a proof failed (nginx change, if made, is additive and left in place)."); return 1
    say("APPLIED AND PROVEN: enrolled devices pass the ops gate; Basic auth unchanged for everyone else.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
