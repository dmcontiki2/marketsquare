#!/usr/bin/env python3
"""026_gate_down.py — GATE-DOWN-1 (19 Aug 2026, David's ruling).

THE RULING
----------
David: "How else am I going to have confidence that we are ready for the soft launch if we
can't give it to more people to test. We can not even give 3 people constant access to the
app?" The logic had inverted: the gate exists to protect an unfinished app, but it had become
the main thing preventing him from finding out whether the app IS finished. It comes down
today rather than 29 Aug (RUL-001's soft-launch date, which this brings forward for the GATE
only -- the launch dates themselves are unchanged).

WHY THIS IS AN NGINX-ONLY CHANGE
--------------------------------
The gate has two halves and BOTH hang off one endpoint:
  * server half -- nginx `auth_request /_review_gate`, which proxies to the app's /review/verify
  * client half -- marketsquare.html calls /review/verify and shows the overlay unless it gets
                   {"valid":true}
So making /review/verify answer 200 for everyone drops both halves at once, with NO application
deploy. That matters today because the deploy lane is not reaching the server; this change is
therefore independent of that fault and can go in over SSH.

WHAT IT DOES
  1. location = /_review_gate  -> `return 200;`  (auth_request always passes)
  2. location = /review/verify -> returns {"valid":true,"scope":"review"} to everyone
Nothing else is touched. The exempt locations, the app, the cookies and every credential path
stay exactly as they are.

REVERSING IT (one command, and it is a real rollback, not a rebuild)
    cp <printed backup> <site file> && nginx -t && nginx -s reload
The gate returns intact, cookies people already hold still work, nothing was deleted.

SAFETY: 019/025 skeleton -- enabled-first find_site; FUNCTIONAL idempotency; refusal rather
than guessing; backup OUTSIDE the globbed dir (NGINX-BAK-LOOP-1); nginx -t with auto-restore;
reload with auto-restore.

VERIFY after applying (anonymous, no cookie):
    curl -s https://trustsquare.co/review/verify     -> {"valid":true,"scope":"review"}
    curl -sI https://trustsquare.co/listings         -> 200 (was 401)
Regression ledger RG-0112 asserts exactly this.
"""
import os, re, shutil, subprocess, sys, glob
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

def say(m): print("[026_gate_down] " + m, flush=True)

def find_site():
    def _hits(pats):
        out = {}
        for pat in pats:
            for c in glob.glob(pat):
                if not os.path.isfile(c): continue
                if os.path.basename(c).find(".bak") != -1: continue
                try: t = open(c, encoding="utf-8", errors="replace").read()
                except Exception: continue
                if "trustsquare.co" in t and "server_name" in t and "127.0.0.1:8000" in t:
                    out.setdefault(os.path.realpath(c), c)
        return list(out.items())
    en = _hits(["/etc/nginx/sites-enabled/*"])
    return en if en else _hits(["/etc/nginx/sites-available/*", "/etc/nginx/conf.d/*.conf"])

OPEN_GATE = ("    location = /_review_gate { return 200; }   # GATE-DOWN-1: gate lowered "
             "19 Aug 2026 (David) -- restore from backup to re-arm\n")
OPEN_VERIFY = ("    location = /review/verify { default_type application/json; "
               "return 200 '{\"valid\":true,\"scope\":\"review\"}'; }   # GATE-DOWN-1\n")

RE_GATE_BLOCK = re.compile(r"[ \t]*location = /_review_gate \{.*?\n[ \t]*\}\n", re.S)
RE_GATE_ONELINE = re.compile(r"(?m)^[ \t]*location = /_review_gate \{[^\n]*\}[ \t]*\n")
RE_VERIFY = re.compile(r"(?m)^[ \t]*location = /review/verify[^\n]*\n")

def main():
    if not APPLY:
        say("dry run (no --apply) — nothing changed"); return 0
    sites = find_site()
    if not sites:
        say("FAILED: could not locate the trustsquare.co nginx site file"); return 3
    if len(sites) > 1:
        say("FAILED: multiple candidate site files, refusing to guess: "
            + ", ".join(p for p, _ in sites)); return 3
    real, _shown = sites[0]
    say("site file: " + real)
    text = open(real, encoding="utf-8", errors="replace").read()

    if "GATE-DOWN-1" in text and "return 200" in text:
        say("gate is ALREADY down (GATE-DOWN-1 present) — nothing to do"); return 0

    new = text
    n_gate = 0
    if RE_GATE_BLOCK.search(new):
        new = RE_GATE_BLOCK.sub(OPEN_GATE, new, count=1); n_gate = 1
    elif RE_GATE_ONELINE.search(new):
        new = RE_GATE_ONELINE.sub(OPEN_GATE, new, count=1); n_gate = 1
    if not n_gate:
        say("no `location = /_review_gate` block found — is the gate even armed here?")
        say("Refusing to guess. Nothing changed."); return 4
    if not RE_VERIFY.search(new):
        say("no `location = /review/verify` exempt line found — refusing (the client overlay")
        say("would stay up and users would still see the gate screen)."); return 4
    new = RE_VERIFY.sub(OPEN_VERIFY, new, count=1)

    _bakdir = "/root/nginx-site-backups"
    os.makedirs(_bakdir, exist_ok=True)
    backup = os.path.join(_bakdir, os.path.basename(real) + ".bak-gatedown-" + TS)
    shutil.copyfile(real, backup); say("backup: " + backup)
    open(real, "w", encoding="utf-8").write(new)
    t = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
    if t.returncode != 0:
        say("nginx -t FAILED — restoring. stderr:"); say((t.stderr or "")[:800])
        shutil.copyfile(backup, real); subprocess.run(["nginx", "-t"]); return 5
    say("nginx -t ok")
    r = subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
    if r.returncode != 0:
        say("reload FAILED — restoring"); say((r.stderr or "")[:400])
        shutil.copyfile(backup, real); subprocess.run(["nginx", "-s", "reload"]); return 6
    say("GATE IS DOWN — trustsquare.co is now open to anyone, no code, no link, no allow-list.")
    say("Verify: curl -s https://trustsquare.co/review/verify  -> {\"valid\":true,...}")
    say("        curl -sI https://trustsquare.co/listings      -> 200")
    say("RE-ARM (one command): cp %s %s && nginx -t && nginx -s reload" % (backup, real))
    return 0

if __name__ == "__main__":
    sys.exit(main())
