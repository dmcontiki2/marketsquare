## Watch reds + ambers fixed — trust-plan false red, SQL ratchet, git-lock host lane, sensor catch-up, transport-blind (25 Sep 2026)

Attended CTO pass on David's "fix the two new reds, and also the 4 ambers" after the 25 Sep daily watch.

- **COACH-EARNABLE-2 (RG-0373 amended, DW-155).** The red was the ASSERTION, not the app. RG-0373's
  referral leg said "referrals are not tracked" -- true on 15 Sep, false since RUL-142 was built on
  24 Sep (a client of an accepted intro taps "I hired them", POST /intros/{id}/hired, and the ladder
  counts distinct confirmed clients). The live plan's referral step is correct: `do: wait`, points at
  that button. The leg now asserts the property -- offered only while the ladder can earn it, and it
  must point at the real tap. Proven able to say no (stripped source -> not earnable).
- **PG-PORTABLE-4 (RG-0351, DW-146).** Four SQLite-only calls from the 24 Sep evening commits made
  portable in bea_main.py: LM no-show age computed in Python (was julianday), the LM my-accepted window
  and the EULA 14.5 B3 30-day window use a bound `_sql_since()` stamp (were datetime('now', ...)), and
  used_signin_links uses `ON CONFLICT(link_hash) DO NOTHING` (was INSERT OR IGNORE). test_pg_readiness
  back to the 15/15/2/12 baseline.
- **GIT-LOCK-6 (RG-0467, DW-154).** nightly_checkpoint.bat exited on a clean tree BEFORE calling
  git_unlock.bat, and the 20-min agent only swept when it had work -- so a HEAD.lock a sandbox commit
  left at 02:01 stood 278 min. The checkpoint now sweeps first; the agent runs `git_unlock.bat /aged`
  every tick (locks older than 15 min only -- a sandbox commit is invisible to tasklist).
- **SENSOR-CATCHUP-1 (RG-0468, DW-157).** The once-a-day 01:30 UTC cron sensor was skipped by the
  security assessment's one-time kernel reboot at 01:30:06Z. `sensor.py --catch-up` (no-op once today's
  run exists) runs after every boot and hourly via /etc/cron.d/marketsquare-sensor-catchup
  (migration 052). sensor.py now rides the deploy manifest.
- **TRANSPORT-BLIND-1 (RG-0466, DW-144/145 residual).** _judge() now moves FAIL lines that carry a
  transport signature (gaierror, name resolution, read timeout, urlopen error, dropped connection,
  re-emitted ProbeOffline) to NOT EVALUATED, individually; real faults -- including RG-0099's SSH
  lockout -- still convict. Behavioural self-test inside the entry.
- **DW-156 (RG-0450).** genie/HARNESS.html re-synced to quick.html (byte-identical).
