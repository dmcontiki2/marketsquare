#!/usr/bin/env python3
"""015_maint_b4_tier2_rerun.py -- RE-RUN Tier 2 after MAINT-B4-6 (rewrite fallback).

MAINT-B4 (MAINTENANCE_AGENT.md): Tier 1 (offline spine) signed READY 9 Aug 2026.
Tier 2 -- the real brain's PATCH QUALITY -- needs the server's ai_provider key and
was re-queued after MAINT-B4-3 gave the brain the real file bytes. This migration
runs it exactly once, on the box, SANDBOXED and SHADOW: the rehearsal builds its
own throwaway repo, the stub/live brain cannot commit, and MAINTENANCE_AGENT_ENABLED
is explicitly stripped from the env here (belt + braces on top of the agent's own
default-off construction). Nothing in this file can ship code or touch the DB.

Verdict goes where a gated session can read it without SSH:
  $MS_LIVE/static/maint/b4_tier2.json   (behind GATE-ENFORCE-1's reviewer gate)
and the full table prints into the deploy log.

Exit 0 whether the verdict is READY or NOT READY -- the verdict is DATA, not a
migration failure; a nonzero exit would jam the migration chain (DW-030's lesson).
Exit 1 only if the rehearsal could not run at all (then it retries next deploy).
"""
import json, os, subprocess, sys
from datetime import datetime, timezone

def main():
    if "--apply" not in sys.argv:
        print("dry-run: would run maint_b4_rehearsal.py --live-brain (sandboxed, shadow)")
        return 0
    src  = os.environ.get("MS_SRC", "/opt/marketsquare-src")
    live = os.environ.get("MS_LIVE", "/var/www/marketsquare")
    reh  = os.path.join(src, "scripts", "maint_b4_rehearsal.py")
    if not os.path.exists(reh):
        print("011: rehearsal script missing at %s -- cannot run" % reh)
        return 1
    env = dict(os.environ)
    # ai_provider.py lives at the repo root; the agent imports it by name.
    env["PYTHONPATH"] = src + ((":" + env["PYTHONPATH"]) if env.get("PYTHONPATH") else "")
    # B4 rehearses the LAUNCH posture: strict guard, DESIGN batches to Path B.
    # (Under MAINT_PHASE=prelaunch, SYN-DESIGN would route PATH_A and false-fail
    #  the expect table -- the rehearsal's expectations are the postlaunch canon.)
    env["MAINT_PHASE"] = "postlaunch"
    env.pop("MAINTENANCE_AGENT_ENABLED", None)   # rehearsal is shadow, always
    p = None
    try:
        p = subprocess.run([sys.executable, reh, "--live-brain"], env=env, cwd=src,
                           capture_output=True, text=True, timeout=540)
    except subprocess.TimeoutExpired:
        print("011: Tier-2 rehearsal TIMED OUT (540s) -- treat as NOT READY")
    out = ""
    if p is not None:
        out = (p.stdout or "")
        if (p.stderr or "").strip():
            out += "\n[stderr]\n" + p.stderr
    print(out)
    ready = (p is not None) and p.returncode == 0
    verdict = {
        "run": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tier": 2,
        "ready": ready,
        "verdict": ("READY -- real brain's patch gated green end-to-end; "
                    "arming stays David's one act (MAINTENANCE_AGENT_ENABLED=1)") if ready
                   else "NOT READY -- see table in this file / the deploy log; do not arm",
        "table": out[-3000:],
    }
    dst = os.path.join(live, "static", "maint")
    try:
        os.makedirs(dst, exist_ok=True)
        with open(os.path.join(dst, "b4_tier2.json"), "w", encoding="utf-8") as f:
            json.dump(verdict, f, indent=2)
        print("011: verdict written -> static/maint/b4_tier2.json (reviewer-gated)")
    except OSError as e:
        print("011: could not write verdict file (%s) -- verdict remains in this log" % e)
    print("011: TIER-2 VERDICT: %s" % verdict["verdict"])
    return 0 if p is not None else 1

if __name__ == "__main__":
    sys.exit(main())
