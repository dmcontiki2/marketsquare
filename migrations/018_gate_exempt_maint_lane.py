#!/usr/bin/env python3
"""018_gate_exempt_maint_lane.py — GATE-EXEMPT-MAINT-1 (13 Aug 2026, David's ruling:
"Lets fix both" — remove the B2b lane's credential dependency on the review gate).

WHY
---
Migration 016 armed `auth_request /_review_gate;` on the catch-all (~05:4x 13 Aug) and
the exempt list — 007 unchanged — never carried the maintenance lane, so the 13:17Z
maintenance run 401'd at the ORIGIN before the app ever saw X-Maint-Key ("intake
FAILED", failed safe, B2b loop dark). Same-day client-side fix GATE-COOKIE-1 taught
maintenance_agent.py / fault_reconcile.py to carry the ts_review credential; THIS
migration makes the origin honest about the lane so the key alone is enough again.
The cookie fallback STAYS in both consumers — belt (this exemption) and braces
(the credential) — so neither future gate work nor a lost exemption goes dark silently.

WHAT — two locations, scoped to the lane, nothing wider (the /admin/ surface holds
27 routes incl. login/users/flags/deploy-file; those all STAY behind the gate):
  location ^~ /admin/faults    — the 4 fault-queue routes (GET list, PUT row,
                                 close-draft, close-send)
  location = /dashboard/maint  — heartbeat POST + card GET
SAFE per 007's own machine-to-machine doctrine (verbatim: "exempting them at nginx
removes no protection — the app still refuses a wrong secret"), audited 13 Aug:
every /admin/faults* route and the /dashboard/maint POST carry
Depends(_require_maint) — constant-time X-Maint-Key compare, FAILS CLOSED when
unconfigured (bea_main.py:16366). GET /dashboard/maint is no-auth BY DOCUMENTED
DESIGN ("obscure URL, facts-only by the POST whitelist", RG-0061 posture) — this
restores the exact public readability it had every day before the gate armed.

SAFETY — 016's skeleton unchanged: enabled-first find_site; FUNCTIONAL idempotency
(the exempt line, not a marker); collision refusal with inventory; no-gate-in-conf
early exit 0 (nothing to exempt from; GATE-COOKIE-1 remains the working lane);
backup + `nginx -t` with auto-restore + reload with auto-restore.

VERIFY after deploy: GET https://trustsquare.co/admin/faults?limit=1 with ONLY the
X-Maint-Key header answers JSON — regression ledger RG-0065 flips READY TO LOCK.
ROLLBACK: cp <printed backup> <site file> && nginx -t && nginx -s reload
"""
import os, re, shutil, subprocess, sys, glob
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

def say(m): print("[018_maint] " + m, flush=True)

def find_site():
    """016's proven lookup verbatim: sites-enabled candidates win outright; other dirs
    only when enabled yields nothing (enabled+available are duplicate REAL files on
    this box, not symlinks — realpath dedup alone refused rc 3 twice on 13 Aug)."""
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
LINES = ("    location ^~ /admin/faults   { proxy_pass http://127.0.0.1:8000; " + HDRS + " }\n"
         "    location = /dashboard/maint { proxy_pass http://127.0.0.1:8000; " + HDRS + " }\n")

FUNCTIONAL_GATE = re.compile(r"location\s*/\s*\{[^}]*auth_request\s+/_review_gate;", re.S)
ANCHOR = re.compile(r"(?m)^([ \t]*)location = /intro/relay[^\n]*\n")

def main():
    if not APPLY:
        say("dry run (no --apply) — nothing changed"); return 0
    sites = find_site()
    if not sites:
        say("FAILED: could not locate the trustsquare.co nginx site file"); return 3
    if len(sites) > 1:
        say("FAILED: multiple candidate site files, refusing to guess: " + ", ".join(p for p, _ in sites)); return 3
    real, shown = sites[0]
    say("site file: " + real)
    text = open(real, encoding="utf-8", errors="replace").read()

    # 1. FUNCTIONAL idempotency — the exempt location itself, not any marker
    if "location ^~ /admin/faults" in text:
        say("maint-lane exemption already FUNCTIONALLY present — nothing to do")
        return 0

    # 2. No armed gate in the conf -> nothing to exempt from; the key lane already answers.
    #    Deliberate exit 0 (recorded done): if a gate is ever re-armed by a NEW migration,
    #    that migration owns its own exempt list; GATE-COOKIE-1 is the standing brace.
    if not FUNCTIONAL_GATE.search(text):
        say("no armed review gate in this conf (no auth_request in the catch-all) — nothing to")
        say("exempt; the maint lane already answers on the key. GATE-COOKIE-1 stays the brace.")
        return 0

    # 3. Collision refusal — any other mention of our paths means a manual/partial variant
    collisions = [f for f in ("/admin/faults", "/dashboard/maint") if f in text]
    if collisions:
        say("REFUSING (fails safe): the conf already mentions " + "; ".join(collisions))
        say("outside our exact block — adding ours risks duplicate-location errors.")
        say("Hand this log to Claude: one manual reconciliation, then re-deploy.")
        return 7

    # 4. Anchor: the intro/relay exempt line 016 wrote — insert directly after it
    matches = ANCHOR.findall(text)
    if len(matches) != 1:
        say("FAILED: expected exactly ONE `location = /intro/relay` exempt line, found %d —"
            % len(matches))
        say("the gate block is a variant this migration does not know. Not editing.")
        return 4
    new = ANCHOR.sub(lambda m: m.group(0) + LINES, text, count=1)
    if "location ^~ /admin/faults" not in new or "location = /dashboard/maint" not in new:
        say("FAILED: substitution did not land both exempt lines"); return 4

    # NGINX-BAK-LOOP-1: write the backup OUTSIDE the globbed directory. Writing it beside
    # the site file planted the exact "multiple candidate site files" condition that made
    # the NEXT run of this class refuse (rc 3) -- 018 was blocked all of 14 Aug by 016's.
    _bakdir = "/root/nginx-site-backups"
    os.makedirs(_bakdir, exist_ok=True)
    backup = os.path.join(_bakdir, os.path.basename(real) + ".bak-maintexempt-" + TS)
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
    say("MAINT LANE EXEMPT — /admin/faults* and /dashboard/maint answer on app auth alone;")
    say("everything else under /admin/ STAYS gated. Verify: keyed GET /admin/faults?limit=1")
    say("answers JSON with no cookie; RG-0065 flips READY TO LOCK.")
    say("Rollback: cp %s %s && nginx -t && nginx -s reload" % (backup, real))
    return 0

if __name__ == "__main__":
    sys.exit(main())
