#!/usr/bin/env python3
"""019_gate_email_link.py — GATE-EMAIL-1 (15 Aug 2026, David's ruling: gate entry
becomes EMAIL-LINKED, "like normal apps"; the reviewer code stays as break-glass).

WHAT
----
1. nginx: exempt the two new gate-entry endpoints from the review gate, exactly as
   016 exempted /review/login — a tester without a cookie must be able to REQUEST a
   link and CLICK it:
     location = /review/request-link   (POST: email in, one-time link mailed out)
     location = /review/enter          (GET: link claim -> ts_review cookie -> /)
2. Seed /var/www/marketsquare/review_emails.txt (0600) with the known reviewers if
   the file does not exist. The app re-reads it every call (same pattern as
   review_code.hash) — add/revoke a tester = edit the file, no restart.

CONTAINMENT UNCHANGED: origin lockdown (RG-0028), the armed catch-all
(GATE-ENFORCE-2), the per-IP rate limit and the code path all stay. These two
locations only let an anonymous browser ASK for a link (allowlist decides, no
enumeration) and REDEEM one (signed, 30-min, single-use).

SAFETY — 018's skeleton verbatim: enabled-first find_site; FUNCTIONAL idempotency
(the exempt line, not a marker); collision refusal with inventory; no-armed-gate
early exit 0 for the nginx half (nothing to exempt from — but the seed file is
still written); backup OUTSIDE the globbed dir (NGINX-BAK-LOOP-1) + nginx -t with
auto-restore + reload with auto-restore.

VERIFY after deploy: anonymous POST https://trustsquare.co/review/request-link
with an off-list email answers JSON {"ok":true}; anonymous GET /review/enter?t=x
answers 302 -> /?gate=expired. Regression ledger RG-0081 flips READY TO LOCK.
ROLLBACK: cp <printed backup> <site file> && nginx -t && nginx -s reload
"""
import os, re, shutil, subprocess, sys, glob
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

def say(m): print("[019_gate_email] " + m, flush=True)

EMAILS_FILE = "/var/www/marketsquare/review_emails.txt"
EMAILS_SEED = """# TrustSquare reviewer allowlist — GATE-EMAIL-1 (one email per line, # = comment)
# The app re-reads this file on EVERY request: edit + save = live, no restart.
davidconradie1234@gmail.com
dmcontiki2@gmail.com
miconradie1@gmail.com
conradiedm@gmail.com
marietjie.marais59@gmail.com
"""

def seed_emails():
    if os.path.isfile(EMAILS_FILE):
        say("allowlist already present: %s (not touched)" % EMAILS_FILE)
        return
    os.makedirs(os.path.dirname(EMAILS_FILE), exist_ok=True)
    with open(EMAILS_FILE, "w", encoding="utf-8") as f:
        f.write(EMAILS_SEED)
    os.chmod(EMAILS_FILE, 0o600)
    say("allowlist SEEDED with 5 reviewers: %s" % EMAILS_FILE)

def find_site():
    """016/018's proven lookup verbatim: sites-enabled candidates win outright."""
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
LINES = ("    location = /review/request-link { proxy_pass http://127.0.0.1:8000; " + HDRS + " }\n"
         "    location = /review/enter    { proxy_pass http://127.0.0.1:8000; " + HDRS + " }\n")

FUNCTIONAL_GATE = re.compile(r"location\s*/\s*\{[^}]*auth_request\s+/_review_gate;", re.S)
ANCHOR = re.compile(r"(?m)^([ \t]*)location = /review/verify[^\n]*\n")

def main():
    if not APPLY:
        say("dry run (no --apply) — nothing changed"); return 0
    seed_emails()   # always: the app half needs the list whether or not a gate is armed
    sites = find_site()
    if not sites:
        say("FAILED: could not locate the trustsquare.co nginx site file"); return 3
    if len(sites) > 1:
        say("FAILED: multiple candidate site files, refusing to guess: " + ", ".join(p for p, _ in sites)); return 3
    real, shown = sites[0]
    say("site file: " + real)
    text = open(real, encoding="utf-8", errors="replace").read()

    # 1. FUNCTIONAL idempotency — the exempt location itself, not any marker
    if "location = /review/request-link" in text and "location = /review/enter" in text:
        say("email-link exemptions already FUNCTIONALLY present — nothing to do")
        return 0

    # 2. No armed gate -> nothing to exempt from; endpoints are reachable anyway.
    if not FUNCTIONAL_GATE.search(text):
        say("no armed review gate in this conf — nothing to exempt; the endpoints answer as-is.")
        return 0

    # 3. Collision refusal — a partial/manual variant means a human must reconcile
    collisions = [f for f in ("/review/request-link", "/review/enter") if f in text]
    if collisions:
        say("REFUSING (fails safe): the conf already mentions " + "; ".join(collisions))
        say("outside our exact block. Hand this log to Claude: one manual reconciliation, then re-deploy.")
        return 7

    # 4. Anchor: the /review/verify exempt line 016 wrote — insert directly after it
    matches = ANCHOR.findall(text)
    if len(matches) != 1:
        say("FAILED: expected exactly ONE `location = /review/verify` exempt line, found %d —"
            % len(matches))
        say("the gate block is a variant this migration does not know. Not editing.")
        return 4
    new = ANCHOR.sub(lambda m: m.group(0) + LINES, text, count=1)
    if "location = /review/request-link" not in new or "location = /review/enter" not in new:
        say("FAILED: substitution did not land both exempt lines"); return 4

    _bakdir = "/root/nginx-site-backups"   # NGINX-BAK-LOOP-1: outside the globbed dir
    os.makedirs(_bakdir, exist_ok=True)
    backup = os.path.join(_bakdir, os.path.basename(real) + ".bak-gateemail-" + TS)
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
    say("EMAIL-LINK LANE OPEN — /review/request-link and /review/enter answer without a cookie;")
    say("everything else stays gated. Verify: off-list POST answers {\"ok\":true}; garbage")
    say("GET /review/enter?t=x answers 302 -> /?gate=expired. RG-0081 flips READY TO LOCK.")
    say("Rollback: cp %s %s && nginx -t && nginx -s reload" % (backup, real))
    return 0

if __name__ == "__main__":
    sys.exit(main())
