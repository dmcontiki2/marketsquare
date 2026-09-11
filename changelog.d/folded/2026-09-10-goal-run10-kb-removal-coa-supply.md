## 2026-09-10 — Goal run 10: the sandbox fault escalated to a decision, COA supply wired, number lane restored

Run 10 of the onboarding goal, ~05:30–06:30 SAST. Model: **Opus 5, not Fable 5.1** — the app's
model selector still governs scheduled runs (RUL-096h), and the drift is reported to David rather
than worked around. Third consecutive run without a Linux shell.

**The sandbox fault is now David's decision, not an open defect.** SANDBOX-REPAIR-1's diagnosis
held up on re-probe: the mount fails identically (2 retries, then stop), the 9 Sep host diagnostic
confirms KB5124008 installed 8 Sep on build 26200.9445, and a web search of the upstream issue
(anthropics/claude-code#92984) confirms there is still no vendor fix and that uninstalling the KB
is the only known remedy — plus a second instance of the same class on ARM64 (#92958, KB5124012).
David asked plainly why a thing that worked cannot be fixed; the answer given to him in plain
language was that the broken part is in Windows, not in anything reachable from inside the
sandbox. **He then ruled: remove the update until Anthropic fixes it.**

`MarketSquare\remove_kb5124008.bat` was written for that purpose (self-elevating `wusa /uninstall
/kb:5124008 /norestart`, with the Settings path documented in the header as the fallback).
**Claude did not execute it**: removing a Windows *security* update is a system/security change
barred to the agent even when the user asks for it, and the host queue's agent has no admin token
(`admin token=False`, 9 Sep diagnostic), so no queued lane could have carried it either. The one
action left to David is named once, in one sentence, and it is genuinely his.

**RULING TO RECORD (not yet in RULINGS.md).** David, 10 Sep 2026: *"please proceed and remove that
update until Anthropic has fixed the issue."* RULINGS.md has no fragment compiler and is too large
to rewrite safely with the truncating Write tool, so this entry is the ruling's only home until a
run with a shell appends it. **Next run with a working sandbox must append it and add the
reflection assertion to `rulings_check.py`.** Recorded here so the decision cannot go quiet, per
the rulings-register rule.

**Supply — COA-1 shipped, without touching the 486-line reader.** The 9 Sep draft adapter was to be
spliced into `us_register_reader.py`; splicing needs a heredoc, and there is no shell. Instead the
Colorado Outfitters Association harvester runs as its own file, `CityLauncher/us_register_coa.py`
(self-contained fetch/strip/clean, resumable off its own CSV), writing the same
`us_registers/coa.club.csv` that `club_import.py` already globs — so the pipe is reused and no
existing file was rewritten. `run_us_registers.bat` gained one line calling it. Both files
re-read after writing and confirmed complete. Not yet executed: queued, result unread at
write time.

**Sending — gates, never calendars.** The host DailyWave fired on time at 00:10 (the 9 Sep sleep
miss did not repeat) and sent **86 real emails** across seven states at wave #3 (Montana 24,
Texas 24, New York 12, Wyoming 12, Virginia 10, Pennsylvania 3, Tennessee 1) — the ramp's first
doubling holding at 24. California dry-ran on the stop-loss gate (last wave 12.5% bounce). Queued
today, in order: the scorer, `clean_stoploss_cities.bat` (the defined release for a stop-loss
hold), a second `launch_day_wave.bat`, and `run_us_registers.bat`.

**The pool is drying up, as expected.** The 00:10 wave visited **8 cities; yesterday's visited 18**.
Ten states produced no sendable prospect at all. Under RUL-103 that is an expected outcome and not
a reason to throttle — it is a reason for supply. Leads probed and recorded for the next adapter:
IOGA's public Adventure Finder (~250 Idaho outfitters; the members.ioga.org directory is
login-gated), and Oregon OOGA's member list (script-rendered, Cloudflare-obfuscated mailboxes —
not a quick win, do not re-probe blind).

**Measurement lane restored.** `run_py MarketSquare\scripts\onboarding_number.py` was added to the
host queue allowlist (GOAL-NUMBER-HOST-1). Runs 8 and 9 could not measure the goal at all and had
to record it as unknown; the scorer reads two databases over SSH and one public page and writes
nothing. The allowlist was rebuilt with all 33 prior rows verified present before the write —
the 10 Sep 05:00 near-miss (a stale snapshot that would have deleted a night's rows) is the
reason that check is now done every time.

**Fact board at 05:11–05:14 (host-side, sandbox dead):** 336 entries · 311 holding · 2 regressed ·
22 open. Both reds are dashboard-truth, not goal-funnel: the session badge on the live server says
192 while the evidence on disk says 194, and the provenance auditor reds on the live page. Both
local remedies pass clean (`session_counter --check` OK, `dashboard_provenance --check` 0 defects),
which places the fault in the gap between disk and server — a deploy, not a code fix. Not deployed
this run: the ledger's own rule is not to deploy over a red board.
