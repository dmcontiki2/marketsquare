## 8 Sep 2026 — Onboarding goal, run 7 (Fable 5.1, 01:03–02:20 SAST): the wave counter never advanced; register letter; letters filed

**The number: 0** (probe A 0, probe B 0; raw 2 = the two e2e_test seeds, barred by §3). 5,838 on the
list · 1,076 emailed · 5 registered. Tonight's 00:10 wave: **254 real sends, 0 crashes** — all 17
remaining US states got wave #1, Cape Town + 7 states wave #2, cap reached at 254, 47 letters dry-ran.

### WAVE-COUNTER-1 — every wave since day one was stamped "wave 1" (CityLauncher, RG-0339 LOCKED)
- PROBED: `email_events.wave_number` was added by `migrate_db.py` with `DEFAULT 1`, so every 'sent'
  row is born wave 1 and the runner's stamp (`WHERE wave_number IS NULL`) matched nothing, ever.
  1,486 sent events, ALL wave 1. Cape Town had sent on nine days and printed "wave #2" every night
  since 2 Sep.
- Consequences, all measured on the real local DB: the ramp could never see a second clean wave
  (structurally capped at 24 — Massachusetts, Florida, Illinois, Michigan were due 48 and sent 24 or
  12); the stop-loss judged the CUMULATIVE bounce rate instead of the last wave's; and a
  STOP-LOSS-RELEASE-1 stamp for "wave 1" matched for ever, so Cape Town (6.9% cumulative, 6 bounces)
  sent nightly with its stop-loss permanently released.
- Fix: a wave is one city's sends on one send-timezone calendar day — exactly what MIN-GAP-1 already
  enforces — derived from `created_at` in `wave_history()`; `city_stats()` takes the last wave from it;
  the post-send stamp drops the IS NULL guard; `clean_city_list.last_wave()` uses the same counter.
  History is right for every send already made with NO database write. Tomorrow's wave: Massachusetts
  / Florida / Michigan / Illinois earn 48 where their days were clean; Pretoria (last wave 12/3 = 25%)
  is correctly held by its own stop-loss until cleaned; Rhode Island (4/12) and Vermont (3/12) hold.

### REGISTER-LETTER-1 — the outfitter lane is drawn (RG-0317 → LOCKED, RG-0267 still green)
- New `adventures_outfitter_outreach.html` in the club letter's approved structure (RUL-099):
  source line ("your state association's own published member directory"), unsubscribe, support
  route, NO money ask (arm-b finding), US price on the example card, live badges only.
- `emailer.template_key_for()` routes any `register:*` row to `TEMPLATES['<category>:register']`
  for both the letter and the subject ("A free listing for your outfit in Montana"). Scraped ZA
  adventures rows keep their old letter. Rendered from a real Montana row: no placeholder, no rand,
  US compliance footer. Montana `category_priority` += adventures_experiences → composes 12 tonight.
- RG-0317's assertion corrected to the path the code actually takes (it checked the old template).

### LETTER-FILE-1 — RUL-099(e) had never been implemented (RG-0340 LOCKED)
- `visuals/letters/` held only its README after ~1,000 club letters. `_file_letter()` now writes one
  file per letter shape × country per send day from the real-send branch; never on a dry run; can
  never break a send. A dry-rendered PREVIEW of the outfitter letter is filed there now.

### RUL-104 reflected at last
- The club letter said "a South African marketplace" to ~1,000 US readers for four days after the
  ruling. Now "a global marketplace, founded in South Africa". `rulings_check.py` RUL-104 asserts it
  in both letters and the YouTube boilerplate.

### Supply, measured on the server
- `register:usatf-new-england` is DEAD supply: 25 sent, 7 bounced (28%) — personal mailboxes on live
  domains (cox.net, aol, yahoo), so an MX clean cannot rescue it; SOURCE-QUALITY-1 holds the whole
  source from tomorrow, which parks the 213 Massachusetts rows. Correct, no release path wanted.
- Domain since the 6 Sep clean: 505 sent, 22 bounced = 4.36% (gate 5%). rrca runs 2.1%.
- US club lane left: rrca 292 + usatf-pacific 40 ≈ 330 → dry ~9–10 Sep. Outfitters: Montana 199
  (drawn from tonight) + Wyoming ~95 (WYOGA-1 adapter written, parser proven on a fixture,
  `run_us_registers.bat` queued 02:06; wyoga.org is not reachable from the sandbox, host-side only).
- Funnel, graded (`/onboard/funnel?days=2`): 21 sessions, **1 human** (no src — organic), 0 humans
  from any letter; the 10 "photos" hits are the scanner pattern. n=1 — no rate yet. Email side, 4
  days: 914 sent · 13.2% human opens · **2 human clicks (0.23%)** · 0 signed.

Ledger before: 327 · 0 regressed · 22 open · RG-0326 READY TO LOCK (promoted). After: see run 7 tail
in GOAL_STATE.md. rulings_check: 102 checked, 0 FAIL.
