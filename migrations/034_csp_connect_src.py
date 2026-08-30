#!/usr/bin/env python3
"""034_csp_connect_src.py -- CSP-CONNECT-1 activation (RG-0180), 30 Aug 2026.

Tightens the served CSP connect-src from the blanket `'self' https:` (shipped by
031/033 as a recorded honest limit) to a NAMED allowlist, closing the
exfiltration half of the 3-4 Aug TP-Drive breach class: script-src already
blocks foreign CODE (RG-0178 LOCKED); this blocks a script that somehow DID run
from TALKING to arbitrary HTTPS hosts (the 3 Aug loader POSTed to /collect --
exactly this channel).

THE ALLOWLIST WAS MEASURED, NOT GUESSED (the draft's activation procedure,
executed 30 Aug 2026 in David's Chrome against the LIVE site):
  walked: index (/), adventures ZA map incl. the heritage layer toggle, a
  listing detail with photos (openDetail bea_264), dashboard.html (in-gate).
  Read via performance resource entries filtered to initiatorType
  fetch/xmlhttprequest/beacon/eventsource, cross-checked with the network log:
  EVERY connect-class request resolved to https://trustsquare.co -- zero
  cross-origin fetch/XHR targets at runtime. This agrees with the 27 Aug static
  inventory recorded on RG-0180.
CROSS-ORIGIN HOSTS SEEN (all NON-connect subjects, already named in their own
directives): unpkg.com (script/style), fonts.googleapis.com/gstatic.com
(style/font), {a,b,c}.tile.openstreetmap.org (img -- Leaflet element loads).

THE POLICY: RG-0180's recorded decision, shipped EXACTLY as recorded -- three
CDN hosts kept only because a Leaflet plugin can fetch() rather than <img>.
(The a/b/c tile subdomains were measured as img loads, never fetch; if a
plugin ever fetches them it will surface as a console error and gets its own
named entry then -- no wildcard ships today.) Everything else is 'self'.
An attacker's host is refused by the browser.

MACHINERY: inherited verbatim from 033 (CSP-SCRIPT-SRC-2..7 lessons, RG-0186):
discovery via nginx -T + recursive walk (never a hand-written glob), staleness
judged on DIRECTIVE VALUES with comments stripped, nginx -t + restore-on-failure,
and the effect PROVEN on the SERVED response over TLS-with-SNI on loopback --
polling for the EXPECTED state, never a stable one -- on BOTH / and /terms
(033's lesson: measure the page, not the port-80 redirect).

REVERSING IT: per-file rollback commands are printed on apply.
VERIFY:  curl -sI 'https://trustsquare.co/?cb=1' | grep -i content-security-policy
         curl -sI  https://trustsquare.co/terms  | grep -i content-security-policy
Ledger RG-0180 asserts the served connect-src allowlist live; it prints
READY TO LOCK on the first green run after this ships -- promote same session.
"""
import glob, os, re, shutil, subprocess, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
BAK_DIR = "/root/nginx-backups"

# Measured 30 Aug 2026 (procedure above) + RG-0180's recorded plugin-fetch allowance.
ALLOWED = ["'self'",
           "https://unpkg.com",
           "https://cdnjs.cloudflare.com",
           "https://tile.openstreetmap.org"]
CONNECT = "connect-src " + " ".join(ALLOWED)

POLICY = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdnjs.cloudflare.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com https://cdnjs.cloudflare.com; "
    "font-src 'self' https://fonts.gstatic.com data:; "
    "img-src 'self' data: blob: https:; "
    + CONNECT + "; "
    "frame-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'self'"
)
RE_CSP = re.compile(r'^([ \t]*)add_header\s+Content-Security-Policy\b[^;]*;[^\n]*$', re.M | re.I)
SEARCH = ("/etc/nginx/*.conf", "/etc/nginx/snippets/*", "/etc/nginx/conf.d/*",
          "/etc/nginx/includes/*", "/etc/nginx/sites-enabled/*", "/etc/nginx/sites-available/*")


def say(m):
    print("[034_csp] " + m, flush=True)


def _nginx_T_files():
    """Every file nginx ACTUALLY reads, from `nginx -T` (RG-0186 discovery rule)."""
    found = []
    try:
        r = subprocess.run(["nginx", "-T"], capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            for line in (r.stdout or "").splitlines():
                m = re.match(r"^#\s*configuration file\s+(/\S+?):\s*$", line)
                if m:
                    found.append(m.group(1))
    except Exception as ex:
        say("nginx -T unavailable (%s) -- falling back to the fixed globs" % repr(ex)[:60])
    return found


def csp_files():
    """{realpath: text} for every nginx file that DECLARES a CSP (union of three sources)."""
    cands = list(_nginx_T_files())
    for root, _dirs, names in os.walk("/etc/nginx"):
        for n in names:
            cands.append(os.path.join(root, n))
    for pat in SEARCH:
        cands.extend(glob.glob(pat))
    out, seen = {}, set()
    for c in cands:
        try:
            rp = os.path.realpath(c)
        except Exception:
            continue
        if rp in seen:
            continue
        seen.add(rp)
        if not os.path.isfile(rp) or ".bak" in os.path.basename(rp):
            continue
        try:
            t = open(rp, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if RE_CSP.search(t):
            out[rp] = t
    return out


def _csp_once(port, use_tls, path="/"):
    """One measurement of the SERVED header. Returns (status, csp)."""
    import http.client, socket, ssl as _ssl
    if use_tls:
        ctx = _ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = _ssl.CERT_NONE      # loopback, not the world
        # SNI must say trustsquare.co while TCP goes to loopback (CSP-SCRIPT-SRC-7).
        conn = http.client.HTTPSConnection("127.0.0.1", port, timeout=10, context=ctx)
        _raw = socket.create_connection(("127.0.0.1", port), timeout=10)
        conn.sock = ctx.wrap_socket(_raw, server_hostname="trustsquare.co")
    else:
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    try:
        conn.request("GET", path, headers={"Host": "trustsquare.co",
                                           "User-Agent": "TrustSquare-Migration/034"})
        r = conn.getresponse()
        val = r.getheader("Content-Security-Policy") or ""
        status = r.status
        r.read()
        return status, val
    finally:
        conn.close()


def served_csp(path="/", settle=0):
    """Poll the served CSP on `path` for the EXPECTED state (CSP-SCRIPT-SRC-5/6 lessons):
    TLS+SNI on loopback so the real vhost answers; a 3xx is an ERROR, never evidence;
    poll until CONNECT appears or the deadline passes, then report what IS served."""
    import time as _t
    deadline = _t.time() + settle
    while True:
        try:
            status, val = _csp_once(443, True, path)
            if 300 <= status < 400:
                return "ERROR:https-redirected(%d)" % status
            if CONNECT in val:
                return val
            if _t.time() < deadline:
                _t.sleep(1)
                continue
            return val
        except Exception as ex:
            if _t.time() < deadline:
                _t.sleep(1)
                continue
            return "ERROR:" + repr(ex)[:80]


def main():
    files = csp_files()
    if not files:
        say("REFUSING: no add_header Content-Security-Policy found anywhere under /etc/nginx. "
            "Not guessing where to write one.")
        return 1

    def _directive_values(text):
        """Every CSP directive value in `text`, comments removed (CSP-SCRIPT-SRC-4)."""
        uncommented = "\n".join(
            ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
        return [m.group(0) for m in RE_CSP.finditer(uncommented)]

    stale = {}
    for p, t in files.items():
        vals = _directive_values(t)
        if not vals:
            continue
        if any(CONNECT not in v for v in vals):
            stale[p] = t
    say("CSP declared in %d file(s); %d still carry the blanket connect-src"
        % (len(files), len(stale)))
    for p in files:
        say("   %s  %s" % ("NEEDS FIX" if p in stale else "already ok", p))

    before = served_csp("/")
    say("served CSP BEFORE: %r" % before[:140])
    if CONNECT in before and not stale:
        say("already applied and PROVEN on the served response. Nothing to do.")
        return 0
    if not APPLY:
        say("DRY RUN -- re-run with --apply.")
        return 0

    os.makedirs(BAK_DIR, exist_ok=True)
    backups = {}
    try:
        for p, t in stale.items():
            dest = os.path.join(BAK_DIR, os.path.basename(p) + ".bak-034-" + TS)
            shutil.copy2(p, dest)
            backups[p] = dest
            new = RE_CSP.sub(lambda m: '%sadd_header Content-Security-Policy "%s" always;'
                                       '   # CSP-CONNECT-1 30 Aug 2026' % (m.group(1), POLICY), t)
            open(p, "w", encoding="utf-8").write(new)
            assert CONNECT in open(p, encoding="utf-8").read(), "write did not land in " + p
            say("rewrote %s (backup %s)" % (p, dest))

        r = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("nginx -t failed:\n" + (r.stderr or r.stdout))
        r = subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("reload failed:\n" + (r.stderr or r.stdout))

        # PROVE the effect on BOTH pages the draft names: the index AND /terms
        # (033's lesson generalized -- the two documents are served through
        # different location blocks and one of them once dropped the whole set).
        for path in ("/", "/terms"):
            after = served_csp(path, settle=45)
            say("served CSP AFTER %-6s: %r" % (path, after[:140]))
            if CONNECT not in after:
                for _p, _t in sorted(csp_files().items()):
                    for _v in _directive_values(_t):
                        say("   STILL DECLARES CSP: %s :: %s" % (_p, _v.strip()[:90]))
                raise RuntimeError("MEASURED=%r on %s after reload (named connect-src absent) "
                                   "-- the server does not SERVE it. Not claiming success."
                                   % (after[:120], path))
    except Exception as ex:
        say("FAILED (%s) -- restoring %d file(s) and reloading" % (str(ex)[:180], len(backups)))
        for p, dest in backups.items():
            shutil.copy2(dest, p)
        subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
        say("restored. The site is exactly as it was before this migration ran.")
        return 1

    say("APPLIED AND PROVEN on the served response (/ and /terms).")
    for p, dest in backups.items():
        say("rollback: cp %s %s && nginx -t && nginx -s reload" % (dest, p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
