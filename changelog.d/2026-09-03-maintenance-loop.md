## 2026-09-03 — maintenance-loop: DEMO-BANNER-2 (RG-0141 regression cleared at the root)

**Unattended B2b maintenance run, 07:4x SAST.** Fault queue read via `maintenance_agent.py` (SHADOW,
foreground): **0 new / 0 fix-shipped / 26 verified**; heartbeat posted to `/dashboard/maint`
(run 2026-09-03T05:42:02Z). No shadow patches, no PATH_B routes, no escalations (brief: silence).

**Top item — a LOCKED fix had rotted (RG-0141 / DW-091):** LIVE-MAP-1 (2d6bcfd, 06:07 SAST) rebuilt
the 11 generated demo maps from `scripts/journey_template.html`, which never carried the DEMO-BANNER-1
include — the 22 Aug fix had patched the 11 OUTPUT files by hand. The same rebuild also dropped
`ts_fares.js` (TP-FARES-1) and stepped `ts_report.js` back to `?v=5`, and no assertion covered either.
This is the RG-0062 class (13 Aug: ts_report.js dropped by a rebuild, fixed by moving the line INTO
the template) recurring for the two lines that were never moved in.

Fix (DEMO-BANNER-2), class-level:
- `scripts/journey_template.html` now carries `ts_report.js?v=6`, `ts_demo_banner.js?v=1` and the
  TP-FARES-1 comment + `ts_fares.js?v=1` — the one source every rebuild copies.
- `python3 scripts/build_journey.py` rebuilt all 11 maps (au, au_rail, bw, c2c, gb, gb_rail, ke, mz,
  na, us, us_rail). Diff vs. the committed files: exactly the tail script block, +280 B each, nothing else.
- Ledger: **RG-0141** gains a clause asserting the TEMPLATE carries exactly one `ts_demo_banner.js`
  include; **RG-0182** gains a clause asserting the template AND every `adventures_*_map.html` carry
  `ts_fares.js`. Both tripwires proven to bite (negative test with the lines removed → FAIL).
- Evidence (PROBED): targeted run RG-0141 → `15 demo map(s), every one loads ts_demo_banner.js` +
  `live ts_demo_banner.js serves and mounts the DEMO tab`; RG-0182 → no fails (after fastapi bootstrap
  via `maint_deps.py`). Full board via `ledger_resume.py` (sandbox cap ~170 s/call): **248 entries ·
  224 holding · 0 REGRESSED · 20 open · 4 ready to lock · 0 UNVERIFIED · exit 0**.

Not done here, by contract: no push, no deploy — NIGHTLY-SHIP-1 / the autodeploy agent (RG-0252)
ships the commit. Until it does, the 11 live maps still serve WITHOUT the DEMO tab (live
`/static/adventures_au_map.html` has 0 occurrences of `ts_demo_banner`). READY TO LOCK but not
promoted (attended lane's entries, made today): RG-0252, RG-0254, RG-0255; RG-0236 held by design.
