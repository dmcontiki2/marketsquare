#!/usr/bin/env python3
"""025_gate_nolock.py — GATE-NOLOCK-1 (19 Aug 2026, David's ruling after a real lockout).

THE FAULT
---------
David, the super admin, could not get into his own app or dashboard on his LAPTOP:
  * He entered his email; the one-time link arrived and he opened it on his PHONE.
    A magic link can only ever unlock the browser that OPENS it, so the phone got
    the ts_review cookie and the laptop stayed locked. There was no way to finish
    entry on the device he was actually working on.
  * His admin password could not rescue him either: GATE-ENFORCE-2 gates the
    catch-all `location /`, and /admin/login was NOT exempt, so nginx refused the
    request at the ORIGIN with 401 before the app ever saw the password. The gate
    screen reported that 401 as "Incorrect reviewer code" — the strongest credential
    in the system reading back as a wrong one.
  * dashboard.server.html then told him to "enter the reviewer code at trustsquare.co
    first" — instructions to perform the very step that was impossible.

Maroushka is about to hand this link to agencies. A gate that can lock out the super
admin will lock out testers, and every one of those is a lost first impression.

WHAT THIS MIGRATION DOES (nginx half; the app half ships in bea_main.py)
-----------------------------------------------------------------------
Exempts four endpoints from the review gate so a LOCKED browser can complete an
entry it is entitled to complete:
  location = /review/claim-code   POST {email, code}  -> ts_review cookie   (cross-device)
  location = /admin/login         POST {password}     -> admin token + cookie (never locked out)
  location = /admin/change-pin    POST                -> finishes forced PIN change
  location = /admin/verify        GET  X-Admin-Token  -> lets a held token re-assert

CONTAINMENT — these do NOT weaken the gate:
  * None of them serve content. They accept a credential and answer 200/401.
  * /review/claim-code needs a 6-digit code that was mailed only to an allowlisted
    address, lives 30 minutes, works once, and has a 6-guess budget.
  * /admin/login and /admin/change-pin are bcrypt/constant-string credential checks
    and are now behind the per-IP limiter (8 attempts / 10 min) — see bea_main.py.
  * /admin/verify only validates a token the caller already holds.
  * The catch-all stays armed; every content path still needs the cookie (RG-0028,
    GATE-ENFORCE-2 unchanged).

SAFETY — 019's skeleton verbatim: enabled-first find_site; FUNCTIONAL idempotency
(the exempt line itself, not a marker — the 007 green-no-op lesson); collision
refusal with inventory; no-armed-gate early exit 0; backup OUTSIDE the globbed dir
(NGINX-BAK-LOOP-1) + `nginx -t` with auto-restore + reload with auto-restore.

VERIFY after deploy (anonymous, no cookie):
  POST https://trustsquare.co/admin/login {"password":"wrong"}      -> 401 JSON from the APP
       (an nginx HTML 401 means the exemption did not land)
  POST https://trustsquare.co/review/claim-code {"email":"x@y.z","code":"000000"} -> 401 JSON
  GET  https://trustsquare.co/wonders                                -> still 401 (gate holds)
Regression ledger RG-0086/RG-0087 assert exactly this.

ROLLBACK: cp <printed backup> <site file> && nginx -t && nginx -s reload
"""
import os, re, shutil, subprocess, sys, glob
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

def say(m): print("[025_gate_nolock] " + m, flush=True)

def find_site():
    """016/018/019's proven lookup verbatim: sites-enabled candidates win outright."""
    def _hits(pats):
        out = {}
        for pat in pats:
            for c in glob.glob(pat):
                if not os.path.isfile(c): continue
                if os.path.basename(c).find(".bak") != -1: continue   # NGINX-BAK-LOOP-1
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
WANT = ["/review/claim-code", "/admin/login", "/admin/change-pin", "/admin/verify"]
LINES = "".join(
    "    location = %-19s { proxy_pass http://127.0.0.1:8000; %s }\n" % (p, HDRS)
    for p in WANT)

FUNCTIONAL_GATE = re.compile(r"location\s*/\s*\{[^}]*auth_request\s+/_review_gate;", re.S)
ANCHOR = re.compile(r"(?m)^([ \t]*)location = /review/enter[^\n]*\n")

def main():
    if not APPLY:
        say("dry run (no --apply) — nothing changed"); return 0
    sites = find_site()
    if not sites:
        say("FAILED: could not locate the trustsquare.co nginx site file"); return 3
    if len(sites) > 1:
        say("FAILED: multiple candidate site files, refusing to guess: "
            + ", ".join(p for p, _ in sites)); return 3
    real, shown = sites[0]
    say("site file: " + real)
    text = open(real, encoding="utf-8", errors="replace").read()

    # 1. FUNCTIONAL idempotency — the exempt locations themselves, not a marker
    have = ["location = " + p in text for p in WANT]
    if all(have):
        say("no-lock exemptions already FUNCTIONALLY present — nothing to do")
        return 0

    # 2. No armed gate -> nothing to exempt from; the endpoints answer as-is.
    if not FUNCTIONAL_GATE.search(text):
        say("no armed review gate in this conf — nothing to exempt; the endpoints answer as-is.")
        return 0

    # 3. Collision refusal — a partial/manual variant means a human reconciles first.
    collisions = [p for p, h in zip(WANT, have) if h]
    if collisions:
        say("REFUSING (fails safe): the conf already exempts " + "; ".join(collisions))
        say("but not all four — adding ours would duplicate nginx locations.")
        say("Hand this log to Claude: one manual reconciliation, then re-deploy.")
        return 7

    # 4. Anchor: the /review/enter exempt line 019 wrote — insert directly after it.
    matches = ANCHOR.findall(text)
    if len(matches) != 1:
        say("FAILED: expected exactly ONE `location = /review/enter` exempt line, found %d —"
            % len(matches))
        say("migration 019 has not run, or the gate block is a variant this migration")
        say("does not know. Not editing.")
        return 4
    new = ANCHOR.sub(lambda m: m.group(0) + LINES, text, count=1)
    if not all("location = " + p in new for p in WANT):
        say("FAILED: substitution did not land all four exempt lines"); return 4
    if not FUNCTIONAL_GATE.search(new):
        say("FAILED: the catch-all gate is no longer functional after the edit — not writing")
        return 4

    _bakdir = "/root/nginx-site-backups"   # NGINX-BAK-LOOP-1: outside the globbed dir
    os.makedirs(_bakdir, exist_ok=True)
    backup = os.path.join(_bakdir, os.path.basename(real) + ".bak-nolock-" + TS)
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
    say("NO-LOCK LANE OPEN — the 6-digit cross-device code and the admin password now")
    say("reach the app from a locked browser; every content path stays gated.")
    say("Rollback: cp %s %s && nginx -t && nginx -s reload" % (backup, real))
    return 0

if __name__ == "__main__":
    sys.exit(main())
