## 2026-08-30 — RAMP-1 + CATPRIO-1: outreach volume is earned, not configured

David asked how to send all of South Africa's outreach in one go off the new Resend Pro
sub; the clean answer (reputation warm-up, not blast) was ratified and IMPLEMENTED as
machinery in CityLauncher/emailer:

- RAMP-1: wave_runner.py now computes batch size from measured evidence — ramp_state()
  doubles defaults.batch_size (12) per CONSECUTIVE clean completed wave (bounce ≤ 2%),
  capped at 96; a dirty wave resets the streak; stop-loss gates (5% bounce / 0 complaints)
  untouched. Explicit per-city batch_size still wins (National=30, documented). Policy
  block in waves_policy.json ("ramp"). No manual fast-lane by design.
- CATPRIO-1: a city entry may carry category_priority to reorder/subset categories, so a
  dedicated Stays & Tours wave is targetable when dated. Pretoria default order untouched.
- Verified: py_compile clean; full --plan dry-run on copied tree (Pretoria wave#1 clean →
  streak 1 → batch 24; National override 30 holds; all cities blocked by arm/gates);
  stays-first dry-run composed adventures_accommodation×24 behind 5 gates.
- Locked: regression ledger RG-0213 (LOCKED) asserts ramp present + wired, max_batch ≤ 200,
  stop-loss unweakened, adventures categories in the composer pool. Ledger run exit 0.
- Backups: wave_runner.py.bak-20260830-ramp1, waves_policy.json.bak-20260830-ramp1,
  regression_ledger.py.bak-20260830-ramp1.

Reserved to David: wave dates + arming (LAUNCH_EMAILS.md rules 2–3); Resend Pro activation Monday.
