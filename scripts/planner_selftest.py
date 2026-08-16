#!/usr/bin/env python3
"""planner_selftest.py — Phase A offline proof (no AI call, no flag, no server).

Proves the pure pipeline end-to-end: wonders dataset -> canned plan -> validate ->
assemble -> render (media=url) -> a real HTML under 300 KB with zero unfilled tokens.
Run:  python3 scripts/planner_selftest.py     (exit 0 = green)
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
import journey_render as jr

def main():
    wonders = json.load(open(os.path.join(REPO, "wonders.json"), encoding="utf-8"))
    if isinstance(wonders, dict):
        wonders = wonders.get("wonders", [])
    za = [w for w in wonders if "south africa" in (w.get("country") or "").lower()][:9]
    assert len(za) >= 9, "need 9 ZA wonders for the canned plan"
    wmap = {w["id"]: w for w in za}
    ids = list(wmap.keys())
    plan = {"title": "Selftest — three days of stone and story",
            "sub": "A canned plan proving the pipeline",
            "days": [{"title": "Day one", "summary": "s1", "stop_ids": ids[0:3]},
                     {"title": "Day two", "summary": "s2", "stop_ids": ids[3:6]},
                     {"title": "Day three", "summary": "s3", "stop_ids": ids[6:9]}]}
    plan = jr.validate_heritage_plan(plan, ids, 3)
    spec = jr.assemble_heritage_spec("South Africa", plan, wmap)
    template = open(os.path.join(HERE, "journey_template.html"), encoding="utf-8").read()
    html, found, missing = jr.render_spec(spec, template, media="url")
    kb = len(html.encode("utf-8")) // 1024
    ok_size = kb < 300
    ok_tokens = "{{" not in html
    ok_pins = "PIN-SPREAD-1" in html
    print(f"selftest: {kb} KB · photos url={found} placeholder={missing} · "
          f"size<300KB={ok_size} · tokens-clean={ok_tokens} · pin-spread={ok_pins}")
    # negative checks: validator must refuse garbage
    bads = 0
    for bad in ({"days": []},
                {"days": [{"title": "x", "stop_ids": ids[0:1]}] * 3},
                {"days": [{"title": "x", "stop_ids": [ids[0]] * 3}] * 3},
                {"days": [{"title": "x", "stop_ids": ["nope", "nah"]}] * 3}):
        try:
            jr.validate_heritage_plan(bad, ids, 3)
        except ValueError:
            bads += 1
    print(f"validator refusals: {bads}/4")
    return 0 if (ok_size and ok_tokens and ok_pins and bads == 4) else 1

if __name__ == "__main__":
    sys.exit(main())
