# Daily watch 2026-09-11 — findings fragment (fold into OPEN_ITEMS.md/.json)

Written as a NEW file, not an edit, because the Cowork Linux sandbox is dead and the
register is far too large to rewrite with the app's file tools without truncating it
(the standing Edit/Write ban on this mount). Fold this in from the next session that
has a working shell. next_id was 117 when this was written.

VERDICT: AMBER. The site is green on every probe that could be made. The two fact
boards (regression ledger, rulings check) DID NOT RUN AT ALL today — neither lane was
available — so "nothing rotted" is NOT EVALUATED today, not asserted.

## What PROBED green (live, this run)

- `GET /health` -> `{"status":"ok","service":"TrustSquare BEA","version":"1.3.1"}`,
  db primary present 2,969,600 B, integrity ok.
- `GET /` -> served, 115,260 characters of index HTML.
- `GET /payment/test` -> `{"status":"ok","paystack_connected":true}`.
- `GET /dashboard/bit` -> `state:"pass", pass 8, total 8, failing []`,
  ran_at 2026-09-11T05:03:31Z (fresh against the 10-minute server heartbeat).
  Notable detail inside it: `B-NEG-DEMOBLEED` clean (65 live listings),
  `B-BEA-DEMODATA` count=303, `B-BEA-WONDERS` count=319.
- `GET /flags` -> mode live, active AI provider `openai`, all three providers
  available (anthropic/scaleway/openai), funnel card_version 2026-08-26.1.
- `GET /static/post_deploy_status.json` -> generated 2026-09-08T15:01:39Z, ref deploy,
  all FIVE steps ok, including `fea_baseline: refreshed after clean deploy
  (3/3 files match source)` — RG-0281 still doing its job. Last deploy is 3 days old;
  that is deploy debt, not a fault.
- Self-heartbeat CLEAN: register last_run 2026-09-10, today 2026-09-11, gap exactly 1 day.

## NEW — DW-117 (HIGH) — the sandbox is dead again; SANDBOX-REPAIR-1 has RECURRED

first_seen 2026-09-11 · sev HIGH · source: the watch's own first command
refs: DW-116, RG-0348, claude-code #92984

Every sandbox command fails identically, three times this run:
`failed to mount ... is under Plan9 share "c" which is not mounted; create: RPC error -1:
ensure user: user vigilant-laughing-hamilton already exists unexpectedly`.

This is the class the 10 Sep note on disk recorded as RESOLVED at ~06:20 SAST after
David removed KB5124008, and PROBED working at 06:44 and 15:45 that day. That same note
predicted this: "Windows Update will reinstall this KB unless it is paused, so there will
probably be a next time." Today is the next time — 1 day later. The likely cause is
KB5124008 (or a successor) reinstalled overnight, but that is INFERRED, not probed: the
diagnosis is queued (see DW-118 for why it has not run).

Blast radius — TEN of the thirteen checks could not run:
instrument bootstrap, `audit_global_qa.py`, `regression_ledger.py`,
`cost_compliance_sweep.py`, `run_daily_checks.py`, all server-side SSH sensors
(`fea_integrity_check`, `subscription_monitor`, orchestrator queue/staged/cron-parity),
`smoke_test.py`, the Monday-lane scripts, and both register writes.

NEXT ACTION: read the result of the queued `sandbox_repair.bat` once the host agent
ticks. If a KB from the #92984 family is installed, the remedy is David's (remove the KB,
or pause Windows Update so it stops coming back). Pausing updates is the part that
turns this from a recurring outage into a closed one.

## NEW — DW-118 (HIGH) — the host-queue agent has not ticked for ~15 hours

first_seen 2026-09-11 · sev HIGH · source: autodeploy_agent_log.txt + 3 pending .req files
refs: DW-117, RUL-095, RG-0257

`autodeploy_agent_log.txt` ends at **2026-09-10 16:11:12 SAST**. Nothing since.
Three requests written by this run at 05:15Z sat unprocessed across at least two
20-minute tick windows (checked four times):
`20260911-051500-000_run_bat_marketsquare-sandbox-repair.req`,
`...-051501-000_run_bat_marketsquare-ledger-host.req`,
`...-051502-000_run_bat_marketsquare-rulings-host.req`.

WHY THIS ONE MATTERS MORE THAN IT LOOKS: the host queue is the designated FALLBACK for
a dead sandbox (SANDBOX-REPAIR-1 step 4 — "the run is NOT idle while the sandbox is
dead"). With the sandbox dead AND the queue not ticking, there is no lane at all to run
the fact boards, and no lane to run the diagnosis that would explain the first fault.
The recovery path shares its failure mode with the thing it is meant to recover — the
same shape as ALERT-OFFORIGIN-1 (DW-097), where the alarm rode the transport it existed
to report on.

Contributing context, already on record: `power_check.bat` (10 Sep) proved the machine
has Modern Standby only, sleep idle timeouts are 0 on both AC and DC, "what is allowed
to wake this machine: NONE", and it suspended 06:45:53–15:43:57 SAST on 10 Sep when the
lid was closed. A sleeping laptop explains the overnight gap. It does NOT explain the
ticks missed after this session started, because the machine must be awake to run it.

NEXT ACTION: CTO lane. (a) Confirm whether the `autodeploy_agent` scheduled task is
still ENABLED and whether it is set to run missed tasks on wake — the DW-104 class
(a scheduled task silently switched off) has bitten once already. (b) Nothing in the
ledger asserts the queue agent is alive; a stranded-request tripwire exists (RG-0257)
but it only fires from a board that itself needs a lane to run. An external liveness
check — the Cloudflare uptime Worker already has its own egress — is the durable answer.

## Items re-checked and NOT closed (no check, no close)

- DW-087 (LOW, deep scan): Monday-only lane; today is Friday. Not re-run. Stays OPEN.
- DW-111 (MEDIUM, repeating Resend 422): needs SSH to the box; no shell, no SSH. Not
  re-run. Stays OPEN.
- DW-115 (LOW, predeploy_check DANGER since 5 Sep): needs the shell. Not re-run. Stays OPEN.

Nothing was closed today. No originating check passed, so nothing may leave the list.

## AI-watch — clear

Searched the last ~48h for provider bans, export controls, outages, rate limits and
pricing changes touching Anthropic, OpenAI and the open-weight/GPU shortlist, with
attention to South African access. No Critical or Watch finding; no register item.
The known-stale "Sonnet 5 reverts to $3/$15 on 1 Sep" claim surfaced again in aggregator
content and is REFUSED on sight per standing instruction ($2/$10 permanent since
11 Aug, RG-0184; the app pins claude-sonnet-4-6 regardless). The June 2026 US export
restriction on Anthropic was lifted 30 June 2026 — history, not news.

## Coverage map — NOT updated today

Yesterday's board stands: 71 green · 1 blue · 2 amber · 0 red · 10 grey (84 cards),
snapshot dated 10 Sep. It could not be rewritten this run for the same reason the
register could not: the file is large and the only safe writer on this mount is a bash
heredoc. Two cards would have moved on today's evidence — the BLUE watch-liveness card
(DW-112/DW-104) and a new card for DW-118 — and neither move has been made, so the map
is one day stale and says so here rather than silently.

## Phase D — no self-commit

`commit.bat` runs through the host queue, which is the very thing that is not ticking.
Today's only new artifact is this file. Nothing was staged and nothing was committed.

---

# ADDENDUM — written 06:20Z / 08:20 SAST, after the sandbox came back

The shell returned mid-session. Everything below was PROBED with it, and it
corrects two things written earlier in this same file.

## DW-117 — RESOLVED this session (was: sandbox dead)

`echo alive; ls -d /sessions/*/mnt/Projects` ran clean at 06:13:47Z and the
Projects mount is readable and writable. Remedy, done by David in this session:
`kb_fix.ps1` removed KB5124008 (wusa exit 3010 = accepted-reboot-required; DISM
removed Package_for_RollupFix~...~26100.9445.1.26 as well), then a restart.

WHAT MADE THIS ATTEMPT STICK, and it is the durable half: Windows Update is now
PAUSED until 2026-10-16 (`PauseUpdatesExpiryTime`, read back from the registry
in the run's own output). The package list proved the loop that beat the two
earlier attempts — KB5124008 was REINSTALLED at 21:40 on 10 Sep, hours after
David removed it that morning. Removal without pausing buys about one day.

STILL OPEN AS A CLASS: the pause is 5 weeks, the maximum Windows 11 Home allows.
Around 16 Oct it lifts itself and the update can return. If Anthropic has not
shipped a fix by then this recurs. That is a diary item, not a mystery.

THREE OF MY OWN SCRIPTS FAILED BEFORE ONE WORKED, and the pattern is worth
keeping: (1) `fix_sandbox_windows.bat` used `wusa /quiet`, which suppressed the
error and then printed DONE over a silent failure; (2) `remove_kb_properly.bat`
crashed before its first write, so the window vanished and the report held only
its header line; (3) `kb_fix.ps1` worked because Start-Transcript records the
whole run to a file even on a crash. LESSON: a diagnostic script must write its
findings incrementally to disk, never only to a console the user may lose, and
must never report success from an exit code it has not inspected.

## DW-118 — WITHDRAWN. It was a FALSE ALARM, and a documented one.

Earlier in this file I recorded the host-queue agent as dead since 10 Sep 16:11
because `autodeploy_agent_log.txt` had gone silent. That reasoning is WRONG and
the ledger already says so in RG-0257's own scope note: the agent only calls the
worker when a .req exists, so an idle agent logs NOTHING, and log silence is the
normal state of a healthy agent with an empty queue. That note exists because
the identical mistake was made on 5 Sep and "a wrong sentence had gone to David
in a report". I made it again.

PROBED, and it clears the agent completely:
- `host_queue/agent_heartbeat.txt` = Fri 09/11/2026 7:51:02 — fresh.
- My three requests, written 05:15Z (07:15 SAST), were picked up at 07:31:02 —
  the very next tick, ~16 minutes, exactly as designed.

The real cause of my wrong call: I checked for results four times between 07:20
and 07:35 SAST, mostly BEFORE the :31 tick, and read the absence as death rather
than as "not yet". The instrument to consult was the heartbeat file, which was
one command away and which RG-0257 names as the correct source. NOT filed as a
register item against the agent — nothing is wrong with the agent. Filed here as
an OPERATOR error against this watch.

## NEW — three REGRESSIONS on the restored board (ledger exit 1)

Board: 339 entries · 314 holding · 3 REGRESSED · 22 open · 0 ready to lock ·
0 UNVERIFIED. This is the first full board since 10 Sep.

1. DASH-FEED-1 — the section `/dashboard/summary` reads is 22 days old
   (2026-08-20). Sessions are writing where the dashboard does not read. The
   entry names the remedy: move a fresh '## Last Completed' block ABOVE it in
   STATUS.md. NOT done in this session.
2. Wave-hygiene witness stale (>14 days). NOT done in this session.
3. `check_bat_crlf.py` — LF-only line endings. FIXED IN THIS SESSION, and the
   first of the three was MY OWN doing: kb_fix.bat, written with the app's file
   tools an hour earlier, landed LF-only. Also converted: fix_sandbox_windows.bat,
   remove_kb_properly.bat, kb_fix.ps1, and maint_host.bat (another session's).
   Guard re-run reads `0 fail, 1 warn` — the warn is the pre-existing
   ROTATE_SECRETS.bat caret-continuation note, which is fine while it stays CRLF.
   LESSON, and it generalises: the app's Write tool produces LF. Any .bat or .ps1
   written that way on this mount must be converted before it is called done.

Items 1 and 2 are real regressions and are NOT closed. They belong to the next
attended/CTO pass.
