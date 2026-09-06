## 2026-09-06 — Goal run 5, part 2: a render test wrote the prospect database, the club card re-probed, session counter (RENDER-TEST-NOWRITE-1)

**Tooling fault (02:00):** the ledger's first run of the new send-path test
(`CityLauncher/tests/test_render_intl.py`, RG-0298) inherited `LAUNCH_SPECIAL_ENABLED=1` from its
environment, so `render()` → `_apply_launch_special()` → `launch_codes.get_or_create_code()`
COMMITTED to the local `prospects.db` from the sandbox and left a hot rollback journal — the 31 Aug
class; the DB was unreadable from the sandbox until a host-side open rolled it back (queued:
`run_py CityLauncher\scripts\club_import.py`, allowlisted, opens read-write, imports nothing new).
Fix at the class: the test forces the launch special OFF before importing `emailer` and refuses to
run if it is somehow on; RG-0298 asserts that line stays; the ledger runs the test through
`_harness()` (RG-0187 had flagged the bare `subprocess.run`). Re-run: RG-0298 green with 34
assertions, and its observed leg reads the post-fix wave log clean.

**Wave outcome, read off `logs/launchday_06Sun09_2026131.log`:** 203 US club letters sent across
22 states (Northern California → Maryland), 0 crashes; DAILY-CAP-1 then held the day at 257 and the
remaining 29 states dry-ran — they go at Monday's 00:10 wave. USATF New England imported host-side
at 01:55: +266, 'Sports Clubs' 1,834 rows / 1,550 distinct (US 1,257, ZA 577), 239 emailed.
Dashboard club card re-probed to those numbers (RG-0287). `session_counter.py` recomputed to 190
after the new fragments; RG-0154 reads DEPLOY DEBT until this ship carries it.
