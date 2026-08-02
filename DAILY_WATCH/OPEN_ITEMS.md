# DAILY WATCH — Open Items Register

One register, one daily probe (Cowork task `trustsquare-daily-watch`, 06:30).
Rules (David, 2 Aug 2026):
- EVERY finding from every check becomes an item here. Severity is recorded but NEVER used to hide or dismiss an item.
- An item leaves this list ONLY by being CLOSED with evidence (its originating check re-run and passing), or explicitly REJECTED by David with a reason.
- No status limbo: each item is OPEN (needs David's review), SCHEDULED (David set a target), FIXED-UNVERIFIED (change made, check not yet re-passed), or CLOSED.
- The daily report lists ALL non-closed items, every day, plus open loops from OPEN_LOOPS.md.

| ID | First seen | Sev | Source | Summary | Status | Next action |
|----|-----------|-----|--------|---------|--------|-------------|
| DW-001 | 2026-08-02 | INFO | audit VERSION-KEY | Repo html pins ms.js v419, live pins v421. Root cause found 2 Aug: server_deploy.sh bumps ?v= monotonically on the live index and cannot write it back to the repo; ms.js CONTENT is byte-identical (MSJS-DRIFT silent). Proposed permanent fix: make VERSION-KEY fire only when content also differs + regression-ledger lock. | OPEN | David: approve the check refinement or schedule it |
| DW-002 | 2026-08-02 | INFO | audit DEMO-PLACEHOLDERS | 3 'coming soon' placeholder listings live (by design); verify they stay out of listing counts. | OPEN | Verify count exclusion once, then close with evidence |
| DW-003 | 2026-08-02 | MEDIUM | consolidation | Monitoring consolidated 7 tasks -> 1 (06:30). Intraday outage detection (old 13:00/19:00 pulse + phone email) is GONE: a daytime outage is now seen next morning. Server-side 01:30 cron shadow still runs but does not alert David's phone. | OPEN | David: accept 24h latency, or schedule re-adding a pulse-only intraday tick |
| DW-004 | 2026-08-02 | MEDIUM | consolidation | Daily-loop's autonomous Fixer/deploy phase paused with the old task. Queue/staged items (orchestrator/queue.json, staged.json) now only surface in the daily list; nothing ships unattended. | OPEN | David: keep fixes manual (per 2 Aug instruction) or schedule a supervised fixer revival |
| DW-005 | 2026-08-02 | MEDIUM | cron-sensor fea-integrity | 01:30 cron shadow flagged HIGH: origin index.html shrank 405089 -> 400810 bytes (-4279B) overnight. Live fea_integrity_check re-run 09:58 UTC: alerts empty, 400810B stable (baseline has absorbed it). Unexplained shrink; likely tied to the 1 Aug TP-FLIGHTS-1 server work — needs David to confirm intended. | OPEN | David: confirm the 1-2 Aug index change was intended, then close |
| DW-006 | 2026-08-02 | INFO | run_daily_checks deploy_drift | 2 files local-ahead of live: dashboard.html, marketsquare.html — deploy pending (same thread as open loop L1 and DW-001 v419/v421). Watch observes only; nothing ships unattended. | OPEN | David: say "ship" (/tsl) or hold |

## Closed / Rejected (evidence required)

(none yet)
