## 2026-08-14 — maintenance-loop: GATE-CACHE-1 + HOST-CAP-1 (the loop's own two faults)

Queue: 3 new (TS-0031/0032/0033), 0 fix-shipped, 23 verified. No app fault reached
"gates GREEN, patch ready", so no application code was touched. Both fixes this session
are to the maintenance machinery itself — found by the loop failing in its own two ways.

**GATE-CACHE-1 — one session logs in ONCE; a rate-limited credential reads BLIND, not RED.**
`/review/login` allows 8 logins per 10 minutes and every PROCESS minted its own ts_review
token (ledger-before, the agent, each per-fault run). One session exhausted the allowance,
after which every gated body probe read 401 and the ledger printed *"13 previously-fixed
issue(s) HAVE COME BACK. Do not deploy over this."* while the site was healthy — a bare
POST /review/login answered 429 "Too many attempts". False red is the most expensive
failure this board has: it invites the next session to fix what is not broken and blocks a
deploy for nothing. Fixed at both ends in `scripts/regression_ledger.py` and
`scripts/maintenance_agent.py`: the token is cached in `.secrets/review_cookie.json`
(gitignored, 0600, 12h, keyed on BASE) so a session logs in once instead of once per
process; and a 429 is NAMED, so affected entries raise ProbeOffline → UNVERIFIED (exit 2,
blind) instead of REGRESSION (exit 1). A token the origin rejects is expired in place
(FUSE blocks unlink) so a dead credential is never re-presented. RG-0011/DW-024 is
untouched — nothing passes blind. Ledger **RG-0070**.

**HOST-CAP-1 — a killed run still leaves a record.** The sibling of BRAIN-DEPS-2: that
fixed the background half (the sandbox reaps detached processes); this is the foreground
half. The Cowork sandbox hard-caps one bash call at ~178s, and a single PATH_A fault on a
megabyte file (window + brain + worktree on FUSE + the 46s gate ledger, whose own
subprocess timeout is 240s) does not fit. Three runs were killed mid-gate and each wrote
NOTHING — no report, no heartbeat, no trace the queue had been read, which is
indistinguishable from a loop that never ran. Guards untouched; bookkeeping only: the run
report is flushed after every fault and at each early-exit lane, so a kill costs at most
the fault in flight; `--only=REF` drives the queue one fault per invocation on a capped
host; `MAINT_TIME_BUDGET_S` stops cleanly BEFORE starting a fault that cannot finish and
names the remainder DEFERRED rather than dropping it. Ledger **RG-0071**.

Fault dispositions (shadow, nothing shipped): TS-0031 → PATH_B, design backlog (AI-added
vehicle details — left, as the contract requires). TS-0032 → PATH_A, brain declined a
clean patch → escalated for a human. TS-0033 → not completed; every attempt exceeded the
host cap mid-gate. TS-0032/TS-0033 look like one class: selecting a city (Maun, Sydney)
shows the right count, then the adventures page reverts and shows other countries'
adventures. Ledger green before (70/0 regressed) and after (71 entries, 0 regressed,
6 open). Heartbeat posted: /dashboard/maint run 2026-08-14T06:01:28Z.
