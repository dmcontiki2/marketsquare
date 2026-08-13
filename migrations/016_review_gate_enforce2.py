#!/usr/bin/env python3
"""016_review_gate_enforce2.py — GATE-ENFORCE-2 (13 Aug 2026, David's ruling: close DW-023/RG-0029).

WHY A SECOND MIGRATION
----------------------
007 ran on the 13 Aug deploy, exited 0, and the gate did NOT rise: anonymous /wonders
still answers 200 at the ORIGIN (cache-busted, proven). 007's idempotency check is
`if "GATE-ENFORCE-1" in text: already applied` — a MARKER test. If the marker string
sits anywhere in the server conf (e.g. a comment left by the 5–7 Aug SSH work that
DW-020 planned), 007 declares victory on a label and records itself done. The exact
green-no-op class STATUS.md documents six times over on 11 Aug.

THIS migration asserts the THING, not the label: the gate is applied ONLY if the
catch-all `location /` actually carries `auth_request /_review_gate;`. Everything
else (anchor, exempt list, backup, nginx -t with auto-restore) is 007 unchanged.

SAFETY
------
* Functional idempotency: real auth_request present -> exit 0, nothing touched.
* COLLISION REFUSAL: if fragments of the gate block already exist (location =
  /review/login etc., a partial manual paste) WITHOUT the functional line, it
  refuses with a precise inventory rather than creating duplicate-location nginx
  errors. The inventory lands in the deploy log; nothing is changed.
* Backup + `nginx -t` + restore-on-failure, as 007.

ROLLBACK:  cp <printed backup> <site file>  &&  nginx -t && nginx -s reload
"""
import os, re, shutil, subprocess, sys, glob
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
MARK = "GATE-ENFORCE-1"

def say(m): print("[016_gate] " + m, flush=True)

def find_site():
    """nginx SERVES sites-enabled; sites-available is inventory. On this box the two are
    DUPLICATE REAL FILES (not symlinks), so realpath dedup saw two candidates and 007
    refused rc 3 (13 Aug deploy log, twice). Rule: sites-enabled candidates win outright;
    the other dirs are consulted only when enabled yields nothing. A refusal now means
    multiple ENABLED matches -- a real ambiguity, not the copy-vs-symlink artifact."""
    def _hits(pats):
        out = {}
        for pat in pats:
            for c in glob.glob(pat):
                if not os.path.isfile(c): continue
                try: t = open(c, encoding="utf-8", errors="replace").read()
                except Exception: continue
                if "trustsquare.co" in t and "server_name" in t and "127.0.0.1:8000" in t:
                    out.setdefault(os.path.realpath(c), c)
        return list(out.items())
    en = _hits(["/etc/nginx/sites-enabled/*"])
    if en:
        return en
    return _hits(["/etc/nginx/sites-available/*", "/etc/nginx/conf.d/*.conf"])

HDRS = ("proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr; "
        "proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;")

BLOCK = (
    "    # " + MARK + " internal auth check + exempt endpoints (do not gate these)\n"
    "    location = /_review_gate {\n"
    "        internal;\n"
    "        proxy_pass http://127.0.0.1:8000/review/verify;\n"
    "        proxy_pass_request_body off;\n"
    "        proxy_set_header Content-Length \"\";\n"
    "        proxy_set_header Cookie $http_cookie;\n"
    "    }\n"
    "    location = /review/login    { proxy_pass http://127.0.0.1:8000; " + HDRS + " }\n"
    "    location = /review/verify   { proxy_pass http://127.0.0.1:8000; " + HDRS + " }\n"
    "    location = /health          { proxy_pass http://127.0.0.1:8000; " + HDRS + " }\n"
    "    location = /payment/webhook { proxy_pass http://127.0.0.1:8000; " + HDRS + " }\n"
    "    location = /email/inbound   { proxy_pass http://127.0.0.1:8000; " + HDRS + " }\n"
    "    location = /intro/relay     { proxy_pass http://127.0.0.1:8000; " + HDRS + " }\n"
    "    location ^~ /.well-known/   { proxy_pass http://127.0.0.1:8000; " + HDRS + " }\n\n"
    "    # " + MARK + " gated catch-all (API): every other path needs a valid review cookie\n"
    "    location / {\n"
    "        auth_request /_review_gate;\n"
    "        proxy_pass http://127.0.0.1:8000;\n"
)

ANCHOR = re.compile(r"location\s*/\s*\{\s*\n\s*proxy_pass\s+http://127\.0\.0\.1:8000;\s*\n", re.M)
FUNCTIONAL = re.compile(r"location\s*/\s*\{[^}]*auth_request\s+/_review_gate;", re.S)
FRAGMENTS = ["location = /_review_gate", "location = /review/login", "location = /review/verify",
             "location = /health", "location = /payment/webhook", "location = /email/inbound",
             "location = /intro/relay"]

def main():
    if not APPLY:
        say("dry run (no --apply) — nothing changed"); return 0
    sites = find_site()
    if not sites:
        say("FAILED: could not locate the trustsquare.co nginx site file"); return 3
    if len(sites) > 1:
        say("FAILED: multiple candidate site files, refusing to guess: " + ", ".join(p for p,_ in sites)); return 3
    real, shown = sites[0]
    say("site file: " + real)
    text = open(real, encoding="utf-8", errors="replace").read()

    # 1. FUNCTIONAL idempotency — the thing, not the label
    if FUNCTIONAL.search(text):
        say("gate is FUNCTIONALLY present (auth_request /_review_gate inside the catch-all) — nothing to do")
        return 0
    if MARK in text:
        say("STALE MARKER FOUND: '%s' is in the conf but the catch-all carries NO auth_request." % MARK)
        say("This is why 007 no-opped green. Proceeding to apply the REAL gate.")

    # 2. Collision inventory — refuse rather than create duplicate-location errors
    collisions = [f for f in FRAGMENTS if f in text]
    if collisions:
        say("REFUSING (fails safe): partial gate fragments already in the conf, adding ours would")
        say("duplicate nginx locations. Inventory: " + "; ".join(collisions))
        say("Hand this log to Claude: the conf needs one manual reconciliation, then re-deploy.")
        return 7

    # 3. Apply via the same anchor as 007
    matches = ANCHOR.findall(text)
    if len(matches) != 1:
        say("FAILED: expected exactly ONE catch-all `location / { proxy_pass 8000 }`, found %d. "
            "Not editing. Send the config to review." % len(matches)); return 4
    new = ANCHOR.sub(lambda m: BLOCK, text, count=1)
    if not FUNCTIONAL.search(new):
        say("FAILED: substitution did not produce a functional gate"); return 4
    backup = real + ".bak-gate2-" + TS
    shutil.copyfile(real, backup); say("backup: " + backup)
    open(real, "w", encoding="utf-8").write(new)
    t = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
    if t.returncode != 0:
        say("nginx -t FAILED — restoring backup. stderr:"); say((t.stderr or "")[:800])
        shutil.copyfile(backup, real); subprocess.run(["nginx", "-t"]); return 5
    say("nginx -t ok")
    r = subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
    if r.returncode != 0:
        say("reload FAILED — restoring backup"); say((r.stderr or "")[:400])
        shutil.copyfile(backup, real); subprocess.run(["nginx", "-s", "reload"]); return 6
    twin = "/etc/nginx/sites-available/" + os.path.basename(real)
    if os.path.isfile(twin) and os.path.realpath(twin) != os.path.realpath(real):
        say("NOTE: %s is a duplicate REAL file (not a symlink) and is now STALE vs sites-enabled." % twin)
        say("      nginx serves sites-enabled; consider symlinking at the next /housekeep.")
    say("GATE LIVE — functionally verified in the new conf. Data API now requires the review cookie;")
    say("exempt: login/verify, health, payment webhook, email-inbound, intro-relay, acme.")
    say("Rollback: cp %s %s && nginx -t && nginx -s reload" % (backup, real))
    return 0

if __name__ == "__main__":
    sys.exit(main())
