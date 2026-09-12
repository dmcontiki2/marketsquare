## 2026-09-12 — Maintenance loop: both reds were the instrument, not the app

Opening ledger: 341 entries, 317 holding, **2 REGRESSED**, 22 open, 0 UNVERIFIED. Fault queue:
**0 new app faults** (`/admin/faults?status=new`), so the session's work was the two reds. Both
turned out to be assertions that were wrong, not fixes that had rotted — and both were wrong in
the same direction: they turned something the system did CORRECTLY into an accusation.

### RG-0257 — a sleeping PC was being reported as a broken lane (AGENT-ASLEEP-1)

The board said *"the host agent last ticked 654 min ago … so this is the agent itself, not an idle
queue"*. It was not the agent. Every other host writer on the disk — nightly TSL, the checkpoint
task, the self-heal log, the deploy audit, DAILY_WATCH — also stopped within ten minutes of the
last heartbeat, at 06:41 SAST. The machine was asleep. A 20-minute Windows scheduled task cannot
tick through sleep and Task Scheduler does not backfill the missed ticks, so silence alone can
never separate a dead lane from a closed lid. By the time the fix was proven, the agent had ticked
again unaided, 1 minute earlier.

This is the **third** false alarm from this one leg (AGENT-HEARTBEAT-1, 5 Sep, was the second), and
it breaks the contract RG-0187 exists to hold: an instrument limit reads NOT EVALUATED, never RED.

Fixed by giving the stale-heartbeat path a **second fact** before it accuses anything: the newest
independent host witness. If a host writer is dated more than a tick plus grace AFTER the last beat,
the host outlived the agent and the lane really is dead → FAIL, naming the witness and the gap. If
nothing is, the host itself was down → NOT EVALUATED → UNVERIFIED (exit 2, loudly not a pass).
Proven by running the real check against a faked stale beat in both directions.

New entry **RG-0355** locks the discriminator in place, as the class: every liveness check that
reads a stamp written by a Windows scheduled task inherits the same limit.

### RG-0295 — the assertion demanded an act reserved to David (JURIS-SUPPLY-SPLIT-1)

The red read *"'Northern California' is in the policy but not armed/gates_green"*. What had actually
happened is in this same changelog, five hours earlier: the RG-0215 jurisdiction gate disarmed every
armed entry in a jurisdiction the outreach-law notes do not cover at heading level — 72 entries,
11 US cities, this register bucket among them. That is RUL-071 executed (*sending is what waits for
law*), and re-arming the US is a legal-positioning call reserved to David.

So the entry was demanding, to go green, exactly the act Claude may not take. The assertion was
wrong, not the code. Amended per the standing rule (fix the assertion, say so in the ref, never
weaken it): a disarm **stamped** with `disarmed_by` now reads INFO — the lane is wired and
deliberately dark — while an **unstamped** unarm still reads RED, which is the silent drift the
entry was built to catch. The supply CLASS is untouched: it asserts the lane is WIRED end to end
(reader → CSV → importer → policy → country map), never that a wave is armed. Live leg re-probed
over SSH the same run: the server pool holds **88** 'Northern California' rows with country='US'.

### Also this run

- Shadow maintenance agent ran clean: 0 faults seen, 0 acted, brain keyed, heartbeat posted to
  `/dashboard/maint` at 15:33:52Z (probed back, matches this run).
- Email lane census: 24 total, 6 held in 30 days (7 support, 5 other, 1 legal, 1 spam) — counts only.
- Escalation brief: nothing in 24h, no brief written.
- `rulings_check.py`: 107 rulings, **0 FAIL**, 15 WARN (rulings with no reflection assertions yet).
- Ledger shards no longer fit a sandbox bash call (two of three exceeded ~180s), so the closing run
  was taken host-side through the permitted queue instead.
