#!/usr/bin/env python3
# run_daily_checks.py - TrustSquare daily read-only check RUNNER (added 17 Jul 2026)
# -----------------------------------------------------------------------------
# WHY THIS EXISTS: the daily-loop SKILL.md is a read-only Cowork guardrail file
# (agents must not silently rewrite their own overnight automation). This runner
# is the ONE stable line the SKILL.md calls; the *mutable* list of checks lives in
# ops/daily_checks.json, which IS agent-writable. So future automation extends the
# morning brief by editing that JSON allow-list - never the protected skill.
#
# SAFETY: executes ONLY entries tagged type=="read-only"; it never deploys, scps,
# restarts, or pushes. Non-fatal by design (always exits 0) so it can never break
# a loop run. Each registered check must accept --json and print {status, line, ...}.
import os, sys, json, subprocess
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "ops", "daily_checks.json")

def main():
    as_json = "--json" in sys.argv
    try:
        man = json.load(open(MANIFEST, encoding="utf-8"))
    except Exception as e:
        out = {"status": "runner_error", "error": f"cannot read manifest: {e}", "checks": {}, "brief_lines": []}
        print(json.dumps(out) if as_json else f"DAILY CHECKS: runner error - {e}")
        return 0

    results, folds, brief_lines = {}, {}, []
    for c in man.get("checks", []):
        cid = c.get("id", "?")
        if not c.get("enabled", False):
            results[cid] = {"status": "disabled"}; continue
        if c.get("type") != "read-only":
            results[cid] = {"status": "skipped", "reason": "not tagged read-only"}; continue
        cmd = c.get("cmd") or []
        try:
            r = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, timeout=90)
            blob = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {}
        except Exception as e:
            results[cid] = {"status": "error", "error": str(e)}
            brief_lines.append({"section": c.get("brief_section", ""), "severity": "SEV-4",
                                "text": f"{cid}: check failed to run ({e})"})
            continue
        status = blob.get("status", "unknown")
        results[cid] = {"status": status, "line": blob.get("line", "")}
        if c.get("fold_key"):
            folds[c["fold_key"]] = blob
        if status in (c.get("flag_statuses") or []):
            brief_lines.append({"section": c.get("brief_section", ""),
                                "severity": c.get("severity_when_flagged", "SEV-3"),
                                "text": blob.get("line", f"{cid}: {status}")})

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ran": [k for k, v in results.items() if v.get("status") not in ("disabled", "skipped")],
        "flagged": [b["text"] for b in brief_lines],
        "checks": results, "deploy_drift": folds.get("deploy_drift"),
        "findings_fold": folds, "brief_lines": brief_lines,
    }
    if as_json:
        print(json.dumps(summary))
    else:
        if brief_lines:
            print("DAILY CHECKS - needs attention:")
            for b in brief_lines: print(f"  [{b['severity']}] {b['text']}")
        else:
            print(f"DAILY CHECKS: all {len(summary['ran'])} clean")
    return 0

if __name__ == "__main__":
    sys.exit(main())
