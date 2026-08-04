#!/usr/bin/env python3
"""005_prelaunch_server_side_gate.py — GATE-SERVERSIDE-1 (3 Aug 2026, David's ruling:
"close it immediately").

THE DEFECT
----------
The pre-launch "MARKETPLACE PREVIEW / Pre-launch access only" screen is a client-side
overlay: a <div id="admin-gate" style="display:none"> living inside marketsquare.html,
revealed by JavaScript. nginx serves that file straight off disk:

    location = / { root /var/www/marketsquare; try_files /index.html =404; }

so the COMPLETE page is handed to anyone who asks, with no credential checked, and JS
then paints a curtain over content that has already arrived. View-source, curl, or
disabling JavaScript reads the whole marketplace. It is a curtain, not a door.

Proven 3 Aug 2026: a page load with the gate showing and NO password entered still
returned 200 on /wonders, /flags, /local-market/listings, /geo/cities and
/tuppence/balance, and executed every script in <head>.

THE FIX
-------
Put a REAL server-side gate in front of the static HTML documents, so nginx refuses to
send the bytes at all without credentials. HTTP Basic Auth over TLS, applied ONLY to the
five document locations.

DELIBERATELY NOT GATED (gating these breaks the platform):
  * the catch-all API proxy `location /`  -> keeps /health alive, which server_deploy.sh
    health-checks and auto-rolls-back on; also keeps POST /payment/webhook reachable so
    Paystack settlements do not fail silently.
  * /.well-known/  -> certbot renewal.
  * /static/, /media/  -> assets the gate page itself needs.
NOTE: the API leak above is therefore NOT closed by this migration. That is phase 2 and
needs the exemptions handled one at a time. This migration closes the document leak only,
and says so rather than implying more.

ARMING
------
Refuses to run unless a password is supplied, so it can never lock anyone out by accident:
    MS_PRELAUNCH_PASS env var, or /var/www/marketsquare/.prelaunch_pass (file, one line).
Set it BEFORE deploying:
    printf 'your-chosen-password' > /var/www/marketsquare/.prelaunch_pass && chmod 600 $_
If absent the migration exits NON-ZERO, is NOT recorded, and retries on the next deploy.

SAFETY
------
Idempotent; backs the nginx conf up; runs `nginx -t` and restores the backup if the test
fails, so a bad edit can never leave nginx unable to start.

ROLLBACK
--------
    cp /etc/nginx/<backup printed below> <the site file>  &&  nginx -t && nginx -s reload
"""
import os, re, shutil, subprocess, sys, glob
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
TS    = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
HTPW  = "/etc/nginx/.htpasswd-prelaunch"
REALM = "TrustSquare - pre-launch access"
MARK  = "# GATE-SERVERSIDE-1"
DOCS  = ["= /", "= /rental.html", "= /dashboard.html", "= /admin.html", "= /command.html"]

def say(m): print("[005_gate] " + m, flush=True)

def find_site():
    cands = []
    for pat in ("/etc/nginx/sites-enabled/*", "/etc/nginx/sites-available/*", "/etc/nginx/conf.d/*.conf"):
        cands.extend(glob.glob(pat))
    hits = []
    for c in cands:
        if not os.path.isfile(c):
            continue
        try:
            t = open(c, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if "server_name" in t and "trustsquare.co" in t and "location = /" in t:
            hits.append((os.path.realpath(c), c))
    uniq = {}
    for real, c in hits:
        uniq.setdefault(real, c)
    return list(uniq.items())

def get_password():
    p = (os.environ.get("MS_PRELAUNCH_PASS") or "").strip()
    if p:
        return p, "env MS_PRELAUNCH_PASS"
    f = os.path.join(os.getcwd(), ".prelaunch_pass")
    for cand in (f, "/var/www/marketsquare/.prelaunch_pass"):
        try:
            v = open(cand, encoding="utf-8").read().strip()
            if v:
                return v, cand
        except Exception:
            pass
    return None, None

def write_htpasswd(pw):
    """apr1 via openssl — the format nginx auth_basic supports everywhere."""
    r = subprocess.run(["openssl", "passwd", "-apr1", pw], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError("openssl passwd -apr1 failed: " + (r.stderr or "")[:200])
    line = "preview:" + r.stdout.strip() + "\n"
    with open(HTPW, "w", encoding="utf-8") as fh:
        fh.write(line)
    os.chmod(HTPW, 0o640)
    say("wrote %s (user 'preview')" % HTPW)

def patch(text):
    """Insert auth_basic into each document location block. Returns (newtext, n)."""
    n = 0
    out = text
    for loc in DOCS:
        pat = re.compile(r"(location\s+" + re.escape(loc) + r"\s*\{)", re.I)
        m = pat.search(out)
        if not m:
            say("  location '%s' not found — skipped" % loc)
            continue
        head = m.group(1)
        tail = out[m.end():]
        close = tail.find("}")
        if close == -1:
            say("  location '%s' has no closing brace — skipped" % loc)
            continue
        if "auth_basic" in tail[:close]:
            say("  location '%s' already gated" % loc)
            continue
        ins = ("\n        " + MARK + " server-side pre-launch gate (3 Aug 2026)"
               "\n        auth_basic \"" + REALM + "\";"
               "\n        auth_basic_user_file " + HTPW + ";")
        out = out[:m.end()] + ins + tail
        n += 1
        say("  gated location '%s'" % loc)
    return out, n

def main():
    if not APPLY:
        say("dry run (no --apply) — nothing changed"); return 0

    pw, src = get_password()
    if not pw:
        say("NO PASSWORD SUPPLIED. Refusing to run so nobody is locked out.")
        say("Set it, then re-deploy:")
        say("  printf 'your-password' > /var/www/marketsquare/.prelaunch_pass && chmod 600 /var/www/marketsquare/.prelaunch_pass")
        return 2
    say("password source: " + src)

    sites = find_site()
    if not sites:
        say("FAILED: could not locate the trustsquare.co nginx site file"); return 3
    if len(sites) > 1:
        say("FAILED: multiple candidate site files, refusing to guess: "
            + ", ".join(p for p, _ in sites)); return 3
    real, shown = sites[0]
    say("site file: %s" % real + ("" if real == shown else "  (via %s)" % shown))

    text = open(real, encoding="utf-8", errors="replace").read()
    if MARK in text:
        say("already applied — refreshing password only")
        write_htpasswd(pw)
        subprocess.run(["nginx", "-s", "reload"])
        return 0

    new, n = patch(text)
    if n == 0:
        say("FAILED: no document locations were gated"); return 4

    backup = real + ".bak-gate-" + TS
    shutil.copyfile(real, backup)
    say("backup: " + backup)

    write_htpasswd(pw)
    with open(real, "w", encoding="utf-8") as fh:
        fh.write(new)

    t = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
    if t.returncode != 0:
        say("nginx -t FAILED — restoring backup. stderr:")
        say((t.stderr or "")[:600])
        shutil.copyfile(backup, real)
        subprocess.run(["nginx", "-t"])
        return 5
    say("nginx -t ok")
    r = subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
    if r.returncode != 0:
        say("reload FAILED — restoring backup"); say((r.stderr or "")[:400])
        shutil.copyfile(backup, real)
        subprocess.run(["nginx", "-s", "reload"])
        return 6

    say("GATE LIVE on %d document location(s). Username 'preview'." % n)
    say("Rollback: cp %s %s && nginx -t && nginx -s reload" % (backup, real))
    say("NOTE: the JSON API is NOT gated by this migration (phase 2) — /health and")
    say("      /payment/webhook must stay reachable, so those need per-path exemptions.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
