## 2026-09-11 — Maintenance loop: two freshness guards given producers (RG-0353, RG-0354)

Ledger started the run at **2 REGRESSED** (339 entries, 315 holding, 22 open). Both reds
were the same class, one day after the first instance of it was named: **a guard without a
producer**. Nothing was broken in either case — the things being asserted were still true.
What had stopped was the thing that keeps the evidence current.

- **RG-0175 — wave-hygiene witness stale (>14 days).** Both proof suites still passed that
  morning (`CityLauncher/tests/test_wave_hygiene.py`, `tests/test_intl_templates.py`, all
  assertions PASS). `wave_hygiene_status.json` had been written **by hand on 28 Aug** and
  nothing on disk ever wrote it again. Fixed with `scripts/wave_hygiene_witness.py`
  (WAVE-WITNESS-1): it re-runs both suites, attributes their real PASS/FAIL lines to the
  three witness items, and writes those verdicts. It never bumps a timestamp — a failing
  suite writes `not_ok` and exits non-zero, so RG-0175 goes red on the fact, not the clock.
  Proven by a sabotage run that forced both suites to fail and confirmed no `ok` could be
  written. Wired into step 2b of every maintenance run. **New entry RG-0353.**

- **RG-0127 — the dashboard read a section 22 days old.** `GET /dashboard/summary` matches
  the FIRST `## Last Completed` heading in a 300 KB append-only file; `status_compile.py`
  folds every fragment under `## Current Session`. So sessions wrote diligently for 22 days
  and the dashboard faithfully rendered 2026-08-20. Two halves, same shape: **seven status
  fragments were also sitting unfolded**, because the compiler only ran from a deploy and
  none had run since 8 Sep. Fixed by making the fold maintain a marker-delimited
  `DASH-FEED-1` block placed above the first unmanaged heading and rewritten wholesale each
  run, so it can never accumulate and the reader's anchor is the one the writer maintains.
  Seven fragments folded; winning section now 1 day old. **New entry RG-0354.**

- **Fault queue empty** — 0 new, 0 acted. Shadow agent ran clean; heartbeat posted and read
  back live at `06:32:40Z`. Email lane census: 24 total, 6 held over 30 days.
- **Backup produced**: `backups/2026-09-11_0633.zip`, restores clean, users=71, listings=113.
- **No escalations** in the last 24h — no brief written. Rulings check: 106 checked, 0 FAIL.

The general rule, now paid for three times in two days: **any assertion of the form "X must
be fresh" needs the thing that MAKES X running unattended in this loop, or the red is
decoration and the only cure is a human remembering.** Before locking the next freshness
guard, name its producer.
