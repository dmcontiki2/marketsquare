## 2026-09-04 — Batch 2 of the 29 Aug listing audit (RUL-065) · built unattended, STAGED not shipped

Scheduled 04:00Z build. Precondition checked first: Batch 1 (SF-AIDESC-1 / A2HS-ASK-1, RG-0205/0209)
was already LIVE — probed on the served ms.js by the 2 Sep run and carried by David's releases.

- **SF-MULTIVISION-1 (RG-0206, ms.js).** `sfRunMultiVision()` — when the seller advances from
  Photos with 2+ photos, main + up to 9 more filled slots (hard cap 10 = the AI_BASELINE vision
  envelope) go up in ONE `/listings/vision-draft` call. Per-photo indices map back to the slot keys
  sent: off-category in slot 2+ drops that photo with a named toast (the WRONG-TYPE-1 rule main
  already had); anonymity flags the slot badge ("✓ checked · will blur" — the upload-time SELLER-ANON
  gate still does the blurring). >5 MB files skipped client-side so server indices stay aligned.
  Photos 11+ upload as before — nothing gated, nothing lost (RUL-066 ladder). Runs in the
  background; re-paints only when the seller is not mid-keystroke; a photo-set signature stops
  re-runs on back-and-forth. Hook: `sfGo('secA')` from `photos` (covers the button and the skip link).
- **INTRO-REMIND-1 (RG-0208, bea_main.py).** Hourly daemon sweep `_intro_reminder_sweep()`
  (INTRO_REMIND_ENABLED=1 default, first pass 3 min after boot, INTRO_REMIND_EMAIL_CAP=100/run):
  ~24h pending → email #1 naming the 48h −5 penalty; ~72h → email #2 naming the 96h removal + web
  push where `users.buyer_token → wearable_devices` has an enabled subscription; B3 danger zone
  (≥2 ignored intros in the rolling 30-day window, `status='expired'`, demo/local-market excluded
  exactly as RESP-1) → explicit paragraph naming the block + 60-day cooling-off on the reminder, or
  ONE standalone warning per window. Idempotent: `intro_requests.reminder_stage` /
  `last_reminder_at` (new columns, conditional UPDATE) + every attempt rowed in new
  `intro_reminder_log`. No Tuppence path touched. `POST /admin/intro-reminder-sweep?dry_run=1`
  for a manual count. Harness-proven on a scratch DB: 2 reminders + 1 B3 first run, 0 on re-run.
- **SF-COACH-ASK-1 (RG-0207, ms.js + bea_main.py) — built AND verified in test, so it ships with
  the batch.** Every sell-flow coach avatar is tappable (+ an "Ask me a question ›" line) → small
  ask box under the bubble → NEW free lane `POST /advert-agent/coach/ask` (Haiku, ≤3 sentences,
  step + category + current fields as context; same identity gate as vision-draft: registered user
  or invited prospect). Server-side cap `SF_COACH_ASK_CAP=10` per listing session in new
  `coach_ask_log`. RUL-066 ceiling behaviour: `warn` from 8 of 10 ("2 questions left"), 429 at the
  cap with the 1T dashboard-coach funnel copy, the typed question kept read-only in the box (never
  lost — also survives re-renders and network failure), every cap-hit rowed with limit/tier/category.
  The paid `/advert-agent/coach` is untouched. Harness: 401 unknown/empty email, 10 answers with
  warn at 8/9/10, 429 on the 11th, cap row logged.
- **Ledger.** RG-0206/0207/0208 promoted OPEN → LOCKED (source-half assertions; RG-0207 strengthened
  to require both halves + the cap constant). RG-0257 assertion FIXED: it read the bat's header
  comment and painted a false REGRESSION ("order wrong"); it now judges code lines only. Run after:
  exit 0, no regressions. rulings_check: 92 checked, 0 FAIL.
- **Schema (applied at startup by run_migrations, no migration file needed):** intro_requests
  +reminder_stage +last_reminder_at; tables intro_reminder_log, coach_ask_log.

Verify: `py_compile bea_main.py` ok · `node --check ms.js` ok · markers present · live site untouched.
Deploy is David's word ("ship") — not run by this session.
