## 2026-08-16 — Planner Lane Phase A BUILT (flag-dark)
David: "Build phase A". Shipped dark behind planners.heritage (p_heritage, OFF):
journey_render.py extracted from build_journey.py — ONE renderer, embed mode (CLI
showcases, 5/5 rebuilt BYTE-IDENTICAL through the module) + media-as-URL mode
(personal maps; selftest renders 190 KB vs 2.4 MB showcases, PIN-SPREAD inherited).
Migration 022 planner_specs. POST /planner/heritage/compose (FREE class, app key,
5/day velocity cap; AI picks wonder IDs + words at the everyday task tier via the
seam — coordinates and photos come ONLY from wonders.json, geography cannot be
hallucinated; failed compose returns 502, charges nothing, stores nothing) and
GET /planner/map/{id} (owner-only, renders on demand). scripts/planner_selftest.py
green: pipeline + 4/4 validator refusals. Manifest: journey_render.py +
journey_template.html now deploy. RG-0097 LOCKED (dark + whole: flag-off answers
404 never 500; source pieces present). Activation = David flips planners.heritage.
Cost model impact: none while dark; lit = everyday-tier tokens only (~$0.01/compose,
capped 5/user/day), zero feeds.
