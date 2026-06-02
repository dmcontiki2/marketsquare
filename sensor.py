#!/usr/bin/env python3
"""
sensor.py - deterministic, zero-token TrustSquare Orchestrator SENSOR (server cron).

RM-4 (AI-independence) Phase 1. Reproduces the Claude-Sensor's findings.json WITHOUT
a model: runs smoke_test.py --local, curls /health + /dashboard/cost + /dashboard/summary,
runs fea_integrity_check.py, parses AUDIT_PROGRESS.md open markers, Monday-guards the scan.

SHADOW MODE (default): writes findings.cron.json + log.cron.md ALONGSIDE the live files,
so the running loop is completely undisturbed during the parity window. Pass --live to
write the real findings.json + log.md (only after 7-day parity is proven, when the Claude
Sensor scheduled task is paused).

Read-only re product code: never edits app code, never deploys, never restarts the BEA.
Always exits 0 (a sensor must never fail the box); problems surface as anomalies/notes.
"""
import datetime
import json
import os
import re
import subprocess
import sys

ROOT = "/var/www/marketsquare"
ORCH = os.path.join(ROOT, "orchestrator")
BASE = "http://localhost:8000"
LIVE = "--live" in sys.argv
FINDINGS = os.path.join(ORCH, "findings.json" if LIVE else "findings.cron.json")
LOGMD = os.path.join(ORCH, "log.md" if LIVE else "log.cron.md")
SENSOR_VERSION = "cron-sensor v1.0 (RM-4 P1, deterministic, zero-token)"


def _curl_json(path, timeout=8):
    try:
        out = subprocess.run(["curl", "-s", "--max-time", str(timeout), BASE + path],
                             capture_output=True, timeout=timeout + 5)
        return json.loads(out.stdout.decode("utf-8", "replace"))
    except Exception:
        return None


def run_smoke():
    """Run the canonical smoke test in --local mode on the box. Returns (passed, total, all_green)."""
    try:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "smoke_test.py"), "--local"],
                           capture_output=True, timeout=200, cwd=ROOT)
        out = r.stdout.decode("utf-8", "replace")
        lines = out.splitlines()
        ok = sum(1 for l in lines if l.strip().startswith("[OK]") and "All checks passed" not in l)
        fail = sum(1 for l in lines if l.strip().startswith("[FAIL]") and "check(s) failed" not in l)
        return ok, ok + fail, (r.returncode == 0 and fail == 0)
    except Exception:
        return 0, 0, False


def run_fea_integrity():
    """Read-only FEA fingerprint vs fea_baseline.json. Returns the parsed --json dict or None."""
    try:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "fea_integrity_check.py"), "--json"],
                           capture_output=True, timeout=120, cwd=ROOT)
        return json.loads(r.stdout.decode("utf-8", "replace"))
    except Exception:
        return None


def parse_open_items():
    """Deterministic open-item parse from AUDIT_PROGRESS.md '[ID . SEV . OPEN]' markers.
    NOTE (parity): this is only as accurate as the doc's markers. Items fixed but not flipped
    to DONE will show stale-OPEN, and items recorded without the marker won't appear - both are
    tuned during the parity window (and they argue for keeping AUDIT_PROGRESS.md markers honest)."""
    items = []
    try:
        txt = open(os.path.join(ROOT, "AUDIT_PROGRESS.md"), encoding="utf-8").read()
    except Exception:
        return items
    for m in re.finditer(r"\[([A-Za-z0-9-]+)\s*[·.]\s*([A-Z/]+)\s*[·.]\s*OPEN\]\s*`?([^\n]*)", txt):
        iid, sev, rest = m.group(1), m.group(2), m.group(3).strip()
        fm = re.search(r"([\w./-]+\.(?:py|js|css|html))(:\d+)?", rest)
        f = (fm.group(1) + (fm.group(2) or "")) if fm else ""
        items.append({"id": iid, "sev": sev, "file": f, "summary": rest[:240]})
    return items


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    weekday = now.strftime("%A")
    dow = int(now.strftime("%u"))  # 1=Mon

    health = _curl_json("/health") or {}
    cost = _curl_json("/dashboard/cost") or {}
    summ = _curl_json("/dashboard/summary") or {}
    ceil = cost.get("ceilings") or {}

    passed, total, green = run_smoke()

    anomalies = []
    if total and not green:
        anomalies.append({"sev": "HIGH", "type": "smoke",
                          "summary": f"smoke {passed}/{total} not all-green - recorded, not fixed (Fixer's job)."})
    if health.get("status") != "ok":
        anomalies.append({"sev": "HIGH", "type": "health",
                          "summary": f"/health status={health.get('status')!r} (expected 'ok')."})
    pct = ceil.get("platform_pct_of_ceiling")
    if isinstance(pct, (int, float)) and pct >= 80:
        anomalies.append({"sev": "HIGH", "type": "spend",
                          "summary": f"platform AI spend at {pct}% of daily ceiling (>=80% threshold)."})
    hv, sv = health.get("version"), summ.get("bea_version")
    if hv and sv and hv != sv:
        anomalies.append({"sev": "LOW", "type": "config-inconsistency",
                          "summary": f"/dashboard/summary bea_version {sv!r} != /health version {hv!r} "
                                     f"- stale hardcoded version field in the summary endpoint. Cosmetic, non-blocking."})

    fea = run_fea_integrity()
    fea_status = (fea or {}).get("status")
    if fea and fea_status == "alert":
        for a in fea.get("alerts", []):
            anomalies.append({"sev": "HIGH", "type": "fea-integrity", "summary": a})
    elif fea is None:
        anomalies.append({"sev": "LOW", "type": "fea-integrity",
                          "summary": "FEA integrity check could not run/measure (network/edge) - no tamper conclusion drawn."})

    open_items = parse_open_items()

    scan_note = (f"Deep static scan runs Mondays only; today is {weekday} (DOW={dow}) - skipped."
                 if dow != 1 else
                 "Monday: deterministic ruff/vulture/pylint scan not yet wired into the cron sensor "
                 "(linters absent on the box) - see RM-4 P1 flag; static-scan still owned by the Monday Claude pass until then.")

    findings = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "loop_date": now.strftime("%Y-%m-%d"),
        "weekday": weekday,
        "sensor_version": SENSOR_VERSION,
        "mode": "live" if LIVE else "shadow",
        "smoke": {"passed": passed, "total": total, "result": f"{passed}/{total}", "all_green": green},
        "health": {"status": health.get("status"), "version": health.get("version"),
                   "endpoint_checked": "https://trustsquare.co/health"},
        "current_session": summ.get("currentSession"),
        "spend": {
            "today_usd": ceil.get("today_spend_usd"),
            "platform_ceiling_usd": ceil.get("daily_platform_ceiling_usd"),
            "platform_pct_of_ceiling": ceil.get("platform_pct_of_ceiling"),
            "platform_breached": ceil.get("platform_breached"),
            "daily_user_ceiling_usd": ceil.get("daily_user_ceiling_usd"),
            "margin_pct": cost.get("margin_pct"),
            "real_token_pct": cost.get("real_token_pct"),
            "month_cost_usd": cost.get("month_cost_usd"),
            "calls_this_month": cost.get("calls_this_month"),
        },
        "anomalies": anomalies,
        "scan_delta": None,
        "scan_note": scan_note,
        "fea_integrity": fea_status,
        "open_items": open_items,
        "open_item_count": len(open_items),
        "cost_tokens": 0,
        "notes": ("Deterministic cron sensor (zero token). SHADOW run - written alongside the live "
                  "findings.json for parity comparison; the live loop is untouched."
                  if not LIVE else
                  "Deterministic cron sensor (zero token), LIVE - this is the authoritative findings.json."),
    }

    os.makedirs(ORCH, exist_ok=True)
    with open(FINDINGS, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)
        f.write("\n")

    line = (f"{findings['generated_at']} sensor(cron,{findings['mode']}): smoke {passed}/{total}, "
            f"health {health.get('status')}, {len(anomalies)} anomalies, {len(open_items)} open items, "
            f"scan delta n/a, FEA {fea_status}, cost $0 (0 tokens).\n")
    with open(LOGMD, "a", encoding="utf-8") as f:
        f.write(line)

    print(line.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
