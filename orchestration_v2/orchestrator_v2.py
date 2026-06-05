#!/usr/bin/env python3
"""
orchestrator_v2.py - Orchestration v2 . Phase 5 (Automate). The deterministic nightly
conductor of the whole arc. It runs Detect(sense) + Prevent, triages the result, and writes
ONE "since last night" report. Zero-token.

SHADOW by default: writes v2/ shadow files, DEPLOYS NOTHING, and never touches the old loop's
section-9 state files. It runs beside the old loop, so the two can be compared for parity before
any cutover - exactly the controlled switch-over the Phase-0 design calls for.

The surgical Fix edit is a Sonnet checkpoint (a separate Fixer task), surfaced here as a green
WORK ORDER - this conductor never edits or ships code itself. Amber/red are staged for David.

Cutover (after shadow parity): turn on a v2 Fixer (Sonnet checkpoint) that consumes the green
work order under the lane gates, and retire the 3 old Claude loop tasks. Until then: shadow.

Usage: orchestrator_v2.py [--live] [--ms PATH] [--demo-listings URL] [--img-limit N]
                          [--root DIR] [--orch DIR] [--out DIR]
"""
import argparse, datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prevent
import triage


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(p, default=None):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return default


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="authoritative run (default = shadow)")
    ap.add_argument("--ms", default="/var/www/marketsquare/static/ms.js")
    ap.add_argument("--demo-listings", default="http://localhost:8000/demo-listings")
    ap.add_argument("--img-limit", type=int, default=15)
    ap.add_argument("--root", default="/var/www/marketsquare")          # BACKLOG/CHANGELOG
    ap.add_argument("--orch", default="/var/www/marketsquare/orchestrator")  # sensor findings.cron.json
    ap.add_argument("--out", default=here)
    a = ap.parse_args()
    mode = "live" if a.live else "shadow"

    # ---- 1. PREVENT (guards + gentle monitor) ----
    try:
        ms = open(a.ms, encoding="utf-8", errors="replace").read()
    except Exception:
        ms = ""
    gds = prevent.guards(ms) if ms else []
    mon = prevent.monitor_images(prevent.load_demo(a.demo_listings), a.img_limit)

    # ---- 2. DETECT (sense): read the deterministic sensor's latest output ----
    sense = _load(os.path.join(a.orch, "findings.cron.json"), {}) or {}
    smoke = (sense.get("smoke") or {}).get("result", "n/a")
    smoke_green = (sense.get("smoke") or {}).get("all_green")
    health = (sense.get("health") or {}).get("status", "n/a")
    anomalies = sense.get("anomalies", []) or []

    # ---- 3. assemble Detect-schema findings (guard FAILs + monitor ALERT + sense anomalies) ----
    findings = []
    for g in gds:
        if g["status"] == "FAIL":
            findings.append({"id": g["id"], "sev": "HIGH", "slice": "regression",
                             "symptom": g["desc"] + " regressed", "root_cause": g["detail"],
                             "file": "ms.js", "area": "fea", "root_token": g["id"].lower(),
                             "match_terms": [g["protects"]], "proposed_lane": "green", "confidence": "confirmed"})
    if mon.get("status") == "ALERT":
        findings.append({"id": "M-IMG", "sev": "LOW", "slice": "demo image link-health",
                         "symptom": "%d dead demo gallery URLs (gentle, 0 false positives)" % mon.get("dead", 0),
                         "root_cause": "external Unsplash link-rot in demo_listings.json galleries",
                         "file": "demo_listings.json", "area": "demo", "root_token": "gallery-dead-urls",
                         "match_terms": ["dead", "gallery"], "proposed_lane": "green", "confidence": "confirmed"})
    for an in anomalies:
        t = an.get("type", "anomaly")
        findings.append({"id": "SENSE-" + t, "sev": an.get("sev", "MED"), "slice": "sense:" + t,
                         "symptom": an.get("summary", ""), "root_cause": an.get("summary", ""),
                         "file": "", "area": "ops", "root_token": "sense-" + t,
                         "match_terms": [t], "proposed_lane": "amber", "confidence": "confirmed"})

    findings_doc = {"detect_run": "orchv2-" + now()[:10], "session": sense.get("current_session"),
                    "scope": "nightly sense + prevent", "generated_at": now(),
                    "engine": "Orchestrator v2 (Phase 5, %s)" % mode, "findings": findings}

    # ---- 4. TRIAGE (dedupe + lane + priority) ----
    ignore = (_load(os.path.join(here, "ignore.json"), {}) or {}).get("ignored", [])
    backlog = triage.load_backlog(os.path.join(a.root, "BACKLOG.md"))
    changelog = triage.load_changelog_sections(os.path.join(a.root, "CHANGELOG.md"))
    tri = triage.triage(findings_doc, ignore, backlog, changelog)
    s = tri["summary"]
    green = [x for x in tri["items"] if x["status"] == "queued" and x["lane"] == "green"]
    staged = [x for x in tri["items"] if x["status"] == "staged"]

    # ---- 5. "since last night" report ----
    gp = sum(1 for g in gds if g["status"] == "PASS")
    report = {
        "schema": "orchestrator-v2", "generated_at": now(), "loop_date": now()[:10], "mode": mode,
        "since_last_night": {
            "smoke": smoke, "smoke_green": smoke_green, "health": health,
            "guards": "%d/%d pass" % (gp, len(gds)),
            "guards_fail": len(gds) - gp,
            "monitor": mon.get("detail", ""),
            "monitor_dead": mon.get("dead", 0), "monitor_checked": mon.get("checked", 0),
            "to_fix_green": len(green), "review_amber": s["review_amber"],
            "need_you_red": s["need_you_red"], "dismissed": s["dismissed"], "known_filed": s["known_filed"],
        },
        "green_work_order": [{"id": x["id"], "ref": x.get("ref"), "title": x["title"], "file": x["file"]} for x in green],
        "staged_for_you": [{"id": x["id"], "ref": x.get("ref"), "title": x["title"], "lane": x["lane"]} for x in staged],
        "guards": gds, "monitor": mon,
        "cost_tokens": 0,
        "note": ("SHADOW - deployed nothing; the old loop and its section-9 files are untouched. "
                 "The green work order is for the Sonnet-checkpoint Fixer; this conductor never edits code."
                 if mode == "shadow" else "LIVE conductor run."),
    }

    rep_path = os.path.join(a.out, "orchestrator_v2_report.json")
    json.dump(report, open(rep_path, "w", encoding="utf-8"), indent=2)
    open(rep_path, "a", encoding="utf-8").write("\n")
    json.dump(tri, open(os.path.join(a.out, "orchestrator_v2_triaged.json"), "w", encoding="utf-8"), indent=2)

    sl = report["since_last_night"]
    line = ("%s orchestrator_v2(%s): smoke %s, health %s, guards %s, monitor %d dead/%d, "
            "triage -> %d green to-fix, %d amber, %d red, %d dismissed; cost $0 (0 tokens).\n"
            % (report["generated_at"], mode, sl["smoke"], sl["health"], sl["guards"],
               sl["monitor_dead"], sl["monitor_checked"], sl["to_fix_green"], sl["review_amber"],
               sl["need_you_red"], sl["dismissed"]))
    open(os.path.join(a.out, "orchestrator_v2_log.md"), "a", encoding="utf-8").write(line)
    print(line.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
