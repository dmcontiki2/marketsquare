#!/usr/bin/env python3
"""021_open_legal_docs.py — RUL-020 (16 Aug 2026, David's ruling, final and binding).

THE RULING
----------
The EULA is decreed FINAL AND BINDING and must be AVAILABLE TO USERS. No legal-review
hold, no counsel gate, no further discussion. The reviewer gate (GATE-ENFORCE-1) must
therefore stop answering 401 on the legal documents: /terms (the EULA v1.13, carrying
the UK/US/AU Country Schedules) and /privacy.

Everything else stays gated exactly as GATE-ENFORCE-1/2 left it.

MECHANISM
---------
Adds two exempt `location =` blocks (proxying to the app, same shape as /health) ABOVE
the gated catch-all in the nginx site. The app itself already serves both pages openly
(bea_main.py /terms + /privacy FileResponse routes, "Public legal pages" since 2 Jul).

SAFETY (the 016 lessons, kept)
------------------------------
* Functional idempotency: if an ungated `location = /terms` block already exists in the
  served site, exit 0 untouched. The test is the THING (a location block without
  auth_request between it and the catch-all), not a marker string.
* Collision refusal: a `location = /terms` block that carries auth of any kind refuses
  with an inventory rather than duplicating locations.
* Backup + `nginx -t` + restore-on-failure + reload.

ROLLBACK: cp <printed backup> /etc/nginx/sites-enabled/marketsquare && nginx -t && nginx -s reload
"""
import os, re, shutil, subprocess, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
SITE = "/etc/nginx/sites-enabled/marketsquare"
ANCHOR = "# GATE-ENFORCE-1 gated catch-all"
PROXY = ("proxy_pass http://127.0.0.1:8000; proxy_set_header Host $host; "
         "proxy_set_header X-Real-IP $remote_addr; "
         "proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;")
BLOCK = (
    "    # RUL-020 (16 Aug 2026): legal docs are PUBLIC -- EULA final & binding, released to users\n"
    "    location = /terms   { " + PROXY + " }\n"
    "    location = /privacy { " + PROXY + " }\n\n    "
)

def say(m): print("[021_legal] " + m, flush=True)

def main():
    if not os.path.isfile(SITE):
        say("REFUSE: %s not found" % SITE); return 3
    text = open(SITE, encoding="utf-8", errors="replace").read()

    # Functional idempotency / collision analysis on any existing /terms location
    m = re.search(r"location\s*=\s*/terms\b[^{]*\{([^}]*)\}", text)
    if m:
        blk = m.group(1)
        if "auth_request" in blk or "auth_basic" in blk or "internal_auth" in blk:
            say("REFUSE: an AUTH-carrying location = /terms already exists -- manual review needed")
            return 3
        say("already applied (ungated location = /terms present) -- nothing to do")
        return 0

    if text.count(ANCHOR) != 1:
        say("REFUSE: catch-all anchor %r found %d times (expected 1)" % (ANCHOR, text.count(ANCHOR)))
        return 3

    if not APPLY:
        say("dry-run OK: would insert /terms + /privacy exempt blocks above the catch-all")
        return 0

    bak = SITE + ".bak-021-" + TS
    shutil.copy2(SITE, bak)
    say("backup: " + bak)

    new = text.replace(ANCHOR, BLOCK + ANCHOR)
    open(SITE, "w", encoding="utf-8").write(new)

    t = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
    if t.returncode != 0:
        shutil.copy2(bak, SITE)
        say("nginx -t FAILED -- restored backup. stderr:\n" + t.stderr)
        return 1
    r = subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
    if r.returncode != 0:
        say("reload failed rc %d: %s" % (r.returncode, r.stderr)); return 1
    say("applied: /terms + /privacy now exempt from the reviewer gate (RUL-020)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
