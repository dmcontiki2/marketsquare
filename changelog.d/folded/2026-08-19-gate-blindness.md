## 19 August 2026 — PG-PORTABLE-1 + EMAIL-NOT-A-PAGE-1: the two guards that blocked the nightly for 15 days

David asked why two faults were still red "at this point", and whether they had been
buried in vague requests he'd missed. They had not been requests at all. Both were
correctly detected on **4 August**, then printed into a scrolling pre-deploy scan block
and appended to `deploy_audit.log` — 50 and 46 times. Manual deploys run in `warn` mode,
which logs DANGER and proceeds (35 such runs between 14 and 19 Aug); only the 02:00
`strict` nightly aborted, into a log, at 02:00, with nobody awake. Detection was never
the problem. Escalation was.

**PG-PORTABLE-1** — the pg-readiness ratchet read 54 against a baseline of 53. The growth
was real, not a false positive: `_demand_match_and_compose` carried SQLite-only date
arithmetic in both `UPDATE demand_tickets` statements and in the 90-day cool-down check.
The caller now supplies portable UTC stamps in SQLite's own `'YYYY-MM-DD HH:MM:SS'` shape,
so stored values are unchanged and the statements move to Postgres untouched. Surface
count 53 → **49**; the baseline auto-tightened and was *not* re-baselined upward.

Twice during the fix the ratchet stayed red because the new *comments* quoted the literal
pattern the regex counts — the same trap paid for on 15 Aug. The comments no longer spell
it out, and say why.

**EMAIL-NOT-A-PAGE-1** — `test_widget_is_wired_into_every_tester_page` named 17 files and
was both right and wrong, which is exactly why it sat unfixed. Three were real
tester-reachable pages missing the fault widget (`orchestration_v2/cockpit.html`,
`durability_map.html`, `email_templates.html`) — now wired. Fourteen were outreach **email
bodies**, where `ts_report.js` cannot run and the tag would ship a `<script src=…>` inside
an invitation. Split, not weakened: pages must carry the widget; email bodies must carry
**no script at all** (stricter, RG-0025 aligned). Classification is structural — published
under `templates/`, 600px email wrapper, zero `<script>` — and fails safe, treating anything
ambiguous as a page. `NOT_TESTER_FACING` stays empty; David's 5 Aug ruling is untouched.

**Ledger:** RG-0112, RG-0113 LOCKED. RG-0114 LOCKED is the class fix — it reads
`deploy_audit.log` and turns the ledger red when any guard tag has been red on 8+
consecutive scans, so a chronic warning surfaces in daylight instead of scrolling past.
RG-0112's first draft failed on correct code (it banned a string repo-wide when its scope
was one function); the assertion was corrected in the same session rather than tolerated.

Strict-mode pre-deploy: **exit 0, verdict REVIEW**. Regression ledger: **exit 0, no regressions**.
