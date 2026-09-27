## 2026-09-24 — Maintenance loop: three board reds cleared, four READY TO LOCK settled, two silent-pass instruments fixed

**24 Sep 2026 · 07:40–08:20Z · maintenance loop (B2b brain, SHADOW) · RG-0351 · RG-0413 · RG-0431 · RG-0331 · RG-0429 · RG-0437 · RG-0447 · RG-0451 (new)**

Board at start: 437 entries · 409 holding · **3 REGRESSED** · 21 open · 4 ready to lock · 0 unverified.
Fault queue empty (0 new, 0 fix-shipped, 26 verified, 12 closed); heartbeat 20260924T075001Z read
back from `/dashboard/maint`; backup lane skipped (newest archive 14.8 h old); no escalation brief.

**One real regression, fixed in the product.**
- **RG-0351 / pg ratchet (PG-PORTABLE-3).** PHONE-KEY-1 (commit 4300824, `phone_codes` +
  `/auth/phone/start|verify`) put back three plain SQLite-clock calls and two modifier forms;
  `test_pg_readiness.py` read 20 against a baseline of 15. `bea_main.py`: `CURRENT_TIMESTAMP` for the
  three, `_sql_since(hours=1)` and `_sql_since(hours=-10/60)` as bound stamps for the two. Values proven
  byte-identical in `:memory:` (expiry, created_at, the one-hour window and the used_at stamp).
  `test_pg_readiness` PASS at 15; py_compile clean. RG-0351 now also FAILS on the modifier count, so the
  next one is caught by the board and not only by the pre-deploy scan. Ships with the nightly TSL.

**Two false reds -- assertions that checked a spelling, fixed to check the property (refs amended).**
- **RG-0413** (door funnel): LINK-KEY-1 legitimately widened the publish beacon to `q_handover_link` /
  `q_handover_phone`. Now a pattern: `q_published` when live, plain `q_handover` otherwise.
- **RG-0431** (language layer): AUDIT-L3 rewrote the edit-reset as a CASE that also clears the stale
  translation -- a stronger fix the literal needle read as REGRESSION. Now asserts the UPDATE drops
  `extra_status` back to 'draft' in either form.
Both proven to still convict: removing the beacon / the reset turns each red.

**Four READY TO LOCK prints, settled one by one -- not promoted blind.**
- **RG-0331** promoted LOCKED: LISTING-COUNTRY-1 (RG-0430) fixed it on the existing `listings.country`
  column. Its column test was vacuous (a DOTALL regex matching any `listings(` followed anywhere by
  `country_iso2`); now asserts the create INSERT names `country`, proven to fail when it does not.
- **RG-0429, RG-0447** carried the DATE `"2026-09-24"` in the state slot; the judge reads any non-LOCKED
  state as OPEN, so both shipped fixes could have rotted as "open". Set LOCKED, fixed_on 2026-09-24.
  Class fix **LEDGER-STATE-1 (RG-0451, new)**: `entry()` refuses any state but LOCKED/OPEN at import.
- **RG-0437** printed READY TO LOCK because its open case returned INFO (scored as a pass) -- the fix was
  NOT built. Built it: `rulings_check._read` now goes through `safe_read.settled_read` (cached, one read
  per file -- uncached it took the check from 2 s to 2 min; now ~37 s); an unsettled read prints NOT
  CHECKED / UNSETTLED, never FAIL; an unsettled RULINGS.md exits 2. Harness now FAILS on the plain read.
  Then promoted LOCKED.

Board at end: **438 entries · 417 holding · 0 REGRESSED · 21 open · 0 ready to lock · 0 unverified.**
rulings_check: 142 rulings, 0 FAIL, 25 WARN (unasserted rulings, pre-existing), 0 NOT CHECKED.
Backups beside each edited file: `*.bak-maint-20260924-*`. Work lock taken for the three files and
released at commit.
