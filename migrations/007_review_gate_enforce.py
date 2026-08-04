#!/usr/bin/env python3
"""007_review_gate_enforce.py — GATE-ENFORCE-1 (5 Aug 2026, David's ruling: proper token gate).

WHAT
----
Makes nginx actually ENFORCE the existing /review/login reviewer token on every data request,
via auth_request -> /review/verify. Until now the token was issued but nothing checked it (the
pre-launch screen was a client-side curtain). Pairs with the bea_main.py change (GATE-ENFORCE-1)
that sets an HttpOnly `ts_review` cookie on login and lets /review/verify read it.

Adds to the live trustsquare.co server block:
  * location = /_review_gate  — internal auth check, proxies to /review/verify with the cookie
  * exempt locations (NO gate): /review/login, /review/verify, /health, /payment/webhook,
    /.well-known/  (login, health-check/rollback, Paystack, certbot must stay open)
  * auth_request on the catch-all `location /` (the API) — every other path needs a valid cookie

Deliberately does NOT gate the static document (`location = /`) or /static/ — the page shell holds
no data (everything sensitive is fetched through the now-gated API), and gating static adds risk
with no confidentiality gain. Add later if belt-and-braces is wanted.

ORDER MATTERS: deploy the bea_main.py cookie change FIRST. If this gate is live before login sets
the cookie, authenticated users cannot pass auth_request. Run this only after the app is updated.

SAFETY
------
Idempotent (marker GATE-ENFORCE-1). Backs up the config, runs `nginx -t`, and RESTORES the backup
if the test fails, so nginx can never be left unable to start. Refuses if the anchor is not found
exactly once (fails safe, no change).

ROLLBACK
--------
    cp <printed backup> <site file>  &&  nginx -t && nginx -s reload
"""
import os, re, shutil, subprocess, sys, glob
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
MARK = "GATE-ENFORCE-1"

def say(m): print("[007_gate] " + m, flush=True)

def find_site():
    cands = []
    for pat in ("/etc/nginx/sites-enabled/*", "/etc/nginx/sites-available/*", "/etc/nginx/conf.d/*.conf"):
        cands.extend(glob.glob(pat))
    hits = {}
    for c in cands:
        if not os.path.isfile(c): continue
        try: t = open(c, encoding="utf-8", errors="replace").read()
        except Exception: continue
        if "trustsquare.co" in t and "server_name" in t and "127.0.0.1:8000" in t:
            hits.setdefault(os.path.realpath(c), c)
    return list(hits.items())

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
    "    location ^~ /.well-known/   { proxy_pass http://127.0.0.1:8000; " + HDRS + " }\n\n"
    "    # " + MARK + " gated catch-all (API): every other path needs a valid review cookie\n"
    "    location / {\n"
    "        auth_request /_review_gate;\n"
    "        proxy_pass http://127.0.0.1:8000;\n"
)

# match the existing catch-all: `location / {` ... `proxy_pass http://127.0.0.1:8000;`
ANCHOR = re.compile(r"location\s*/\s*\{\s*\n\s*proxy_pass\s+http://127\.0\.0\.1:8000;\s*\n", re.M)

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
    if MARK in text:
        say("already applied — nothing to do"); return 0
    matches = ANCHOR.findall(text)
    if len(matches) != 1:
        say("FAILED: expected exactly ONE catch-all `location / { proxy_pass 8000 }`, found %d. "
            "Not editing. Send the config to review." % len(matches)); return 4
    new = ANCHOR.sub(lambda m: BLOCK, text, count=1)
    if MARK not in new:
        say("FAILED: substitution produced no change"); return 4
    backup = real + ".bak-gate-" + TS
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
    say("GATE LIVE. Data API now requires a valid review cookie; login/health/webhook/acme exempt.")
    say("Rollback: cp %s %s && nginx -t && nginx -s reload" % (backup, real))
    return 0

if __name__ == "__main__":
    sys.exit(main())
