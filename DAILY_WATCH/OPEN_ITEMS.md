# DAILY WATCH — Open Items Register

One register, one daily probe (Cowork task `trustsquare-daily-watch`, 06:30).
Rules (David, 2 Aug 2026):
- EVERY finding from every check becomes an item here. Severity is recorded but NEVER used to hide or dismiss an item.
- An item leaves this list ONLY by being CLOSED with evidence (its originating check re-run and passing), or explicitly REJECTED by David with a reason.
- No status limbo: each item is OPEN (needs David's review), SCHEDULED (David set a target), FIXED-UNVERIFIED (change made, check not yet re-passed), or CLOSED.
- The daily report lists ALL non-closed items, every day, plus open loops from OPEN_LOOPS.md.

| ID | First seen | Last seen | Sev | Source | Summary | Status | Next action |
|----|-----------|-----------|-----|--------|---------|--------|-------------|
| DW-001 | 2026-08-02 | 2026-08-05 | INFO | audit VERSION-KEY | Repo html pins ms.js v431, live pins v440 (was 423/428 on 4 Aug — the 4-5 Aug deploys moved both). Root cause unchanged: server_deploy.sh bumps ?v= monotonically on the live index and cannot write it back to the repo. Proposed permanent fix stands: VERSION-KEY fires only when content also differs + regression-ledger lock. | OPEN | David: approve the check refinement or schedule it |
| DW-002 | 2026-08-02 | 2026-08-05 | INFO | audit DEMO-PLACEHOLDERS | 3 'coming soon' placeholder listings live (by design); audit re-confirmed today; ledger RG-0007 (placeholders stay unpriced/inert) holds. | OPEN | Verify count exclusion once, then close with evidence |
| DW-003 | 2026-08-02 | 2026-08-05 | MEDIUM | consolidation | Monitoring consolidated 7 tasks -> 1 (06:30). Intraday outage detection (old 13:00/19:00 pulse + phone email) is GONE: a daytime outage is now seen next morning. Server-side 01:30 cron shadow still runs but does not alert David's phone. Unchanged today. | OPEN | David: accept 24h latency, or schedule re-adding a pulse-only intraday tick |
| DW-004 | 2026-08-02 | 2026-08-05 | MEDIUM | consolidation | Daily-loop's autonomous Fixer/deploy phase paused with the old task. Re-verified today: orchestrator/queue.json = [] and staged.json = [] (nothing waiting). | OPEN | David: keep fixes manual (per 2 Aug instruction) or schedule a supervised fixer revival |

| DW-006 | 2026-08-02 | 2026-08-05 | LOW | run_daily_checks deploy_drift | IMPROVED today: bea_main.py and ms.js are NO LONGER local-ahead — JWT-HARDEN-1 (admin auth fails closed) is now LIVE, removing the security weight (sev MEDIUM -> LOW). Remaining 2 files local-ahead: dashboard.html, marketsquare.html (the latter likely the VERSION-KEY ?v= class, see DW-001). | OPEN | David: ship the 2 remaining files (/tsl) or confirm marketsquare.html drift is the version-key artifact |
| DW-008 | 2026-08-03 | 2026-08-05 | MEDIUM | audit MSJS-DRIFT | Check passing since 2026-08-05 — awaiting David's close. Today's audit raises NO MSJS-DRIFT finding (ms.js shipped 5 Aug, so repo and live bytes align again). CAVEAT: this pass does not prove the raw-byte CRLF-compare bug in audit_global_qa.py is fixed — it simply had nothing to mis-compare; the harness fix (compare content like RG-0026's check_deploy_drift.py) is still worth landing. | OPEN | David: close (accept it will re-cry after the next CRLF divergence) or schedule the audit-harness content-compare fix |
| DW-009 | 2026-08-03 | 2026-08-05 | LOW | cost sweep | Same single WARN as 3-4 Aug (line moved 902 -> 906 by edits): dashboard.server.html uses Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku. Totals today 0 critical / 1 warning / 24 ok / 37 info (info growth is DW-018, benign). Spend: platform $100/day ceiling, $0.00 today, month-to-date $0.65 over 102 calls. | OPEN | David/attended: justify the Sonnet call or downgrade it to Haiku |
| DW-010 | 2026-08-03 | 2026-08-03 | MEDIUM | cc_age_check (Monday lane) | Change-control CC-002 open 54+ days against a 7-day ageing threshold: '4/5 STAGED (Fable run 10 Jun) — baseline ok, term map evidence-based'. CC-001/003/004 resolved; CC-002 is the last one. NOT re-checked today (Monday-only lane; today Wednesday). Carried forward unchanged. | OPEN | David: land or formally defer CC-002 |
| DW-012 | 2026-08-03 | 2026-08-03 | INFO | Monday deep scan coverage | Monday deep scan cannot run fully unattended: pylint and eslint not installed in sandbox or server; ruff/vulture pip-installed per run. Same gap the 01:30 cron sensor reports (RM-4 P1 scan_note). NOT re-checked today (Monday-only lane). | OPEN | David: accept the node --check proxy, or schedule wiring the linters into the sandbox image once |
| DW-013 | 2026-08-04 | 2026-08-05 | MEDIUM | smoke_test parity + RG-0027 side-effect | Re-confirmed today: smoke 30/39 from BOTH instruments (sandbox run and 01:30 cron — parity OK, no MISMATCH). Same 9 failures, all the Cloudflare-gate artifact class (HTML shell size, ms-data x2, CSS/JS external links, ms.css/ms.js 200 + cache-immutable): smoke_test curls the public edge from a non-allowlisted path. App independently verified fine (health ok v1.3.1, index 200 in 0.81s from the allowlisted sandbox). Risk unchanged: a real breakage in those 9 is indistinguishable from the artifact. | OPEN | Attended session: point smoke_test's public-surface fetch at localhost origin (as its API checks do) or allowlist the box, then re-run to 39/39 |



## Ledger OPEN entries (tracked in scripts/regression_ledger.py, not duplicated here)

- **RG-0003** — 240 non-Adventures listings carry no country field; currency inferred from the price string, defaulting to Rand. Still failing 2026-08-05. Not READY TO LOCK.
- **RG-0004** — demo_stay_4 city='Pretoria' but country='MZ'; demo_stay_9 city='Pretoria' but country='NA'. Still failing 2026-08-05. Not READY TO LOCK.
- **RG-0030** — LOCKED 2026-08-05 (was READY TO LOCK; promoted same day, see closed DW-017).

## Closed / Rejected (evidence required)

- **DW-018** CLOSED 2026-08-05 (attended) — David purged `_to_delete/` (dir now empty). EVIDENCE: cost sweep re-run same day — info-count back to 28 (was 37; all 9 stray-stage-copy Sonnet INFOs gone), totals 0 critical / 1 warning / 24 ok / 28 info; regression ledger exit 0 after the purge. Residual: two inert `.bat.retired` files at repo root for David to delete by hand (FUSE blocks sandbox unlink).

- **DW-005** CLOSED 2026-08-05 (attended, David's nod) — the byte drift was the 3-5 Aug deploys, confirmed independently: post-deploy index verified content-identical to repo after ?v=/Cloudflare-rewrite normalisation (0 real diff lines, this session). Baseline refreshed via `fea_integrity_check.py --update-baseline` (now index 400834B, ms.js v441, ms.css v305, BEA 1.3.1). EVIDENCE: re-run returns status ok, alerts [], notes [] — the nightly cron stops re-alerting.

- **DW-016** CLOSED 2026-08-05 (attended) — RED-alert email path RESTORED. David created /etc/marketsquare/resend.watch.conf (0640 root:msdeploy) via one-shot fix_watch_alerts.bat; watch task prompt updated to send from the server via that copy. EVIDENCE: msdeploy read verified (ls -l + cat READ-OK) AND a live test email accepted by Resend (id 77de9576-aac0-4659-9ed1-0142945962c1) to dmcontiki2@gmail.com. Residual: DW-003 (no INTRADAY tick) still open — this fix restores RED push at 06:30, not daytime coverage.

- **DW-007** CLOSED 2026-08-05 (attended, David's "what can you fix" go-ahead) — fix_support_public.bat retired to `_to_delete/retired-deploy-bats-20260802/` (copy verified byte-identical, root-level file renamed aside; support.html already rides the deploy manifest, line 32, so nothing lost). EVIDENCE: regression ledger re-run exit 0 — "RG-0023 ok / every locked fix is holding".
- **DW-011** CLOSED 2026-08-05 — dead `base_score = 40` assignment dropped from bea_main.py (only 3 refs: 2 comments + the assignment; PEN-CAP-1 comment block kept). EVIDENCE: py_compile green + ruff F841 clean on bea_main.py. NOTE: rides the next deploy; SCAN-29 (B904 x2) intentionally left for the Monday lane.
- **DW-014** CLOSED 2026-08-05 — CLAUDE.md TP-DRIVE-1/RG-0025/compliance-gate paragraphs rewritten to the post-breach truth (loader REMOVED, RG-0025 inverted, Drive disabled, explicit DO-NOT-REINTRODUCE warning). EVIDENCE: asserts passed — 'stays on all 10 live pages' and 'full capacity' no longer present; ledger RG-0025 passing.
- **DW-015** CLOSED 2026-08-05 — run_daily_checks.py now seeds the host key itself (`_seed_transport()`, idempotent, silent-fail to an honest report). EVIDENCE: py_compile green; fresh run returned real drift data (2 files ahead), no transport error.
- **DW-017** CLOSED 2026-08-05 — RG-0030 flipped OPEN -> LOCKED in scripts/regression_ledger.py (anchor-asserted one-line change). EVIDENCE: ledger re-run exit 0, RG-0030 reports ok under LOCKED.
