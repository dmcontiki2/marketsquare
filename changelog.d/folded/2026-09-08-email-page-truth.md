## 2026-09-08 — EMAIL-PAGE-TRUTH-1: the Ops Dashboard Email Templates view now shows the letters that SEND; SPECIAL-CLOSE-1: the expired launch special is closed

David: *"please ensure that these email templates are the latest ones, in the Ops Dashboard. If not
please update them."* They were not.

- **What was wrong.** The page (orchestration_v2/email_templates.html, deployed at /orchestrator/v2/)
  was hand-built on 23 Aug from a snapshot folder (orchestration_v2/templates/) that NOTHING sends
  from, while saying "exactly as the wave machinery sends them". The wave runner (launch_day_wave.bat
  on David's PC → wave_runner → emailer.py) sends from CityLauncher/emailer/templates/, and those
  copies moved on 28 Aug (international pass), 4 Sep (support route + browse link, RUL-100), 5 Sep
  (inline TrustSquare mark), 6 Sep (Tutors A/B arm) and 8 Sep (register letter). Four letters that
  joined the lane were not on the page at all (sports_club, adventures_outfitter, tutors arm B, the
  federation permission letter) nor were the two resend letters (human_followup, relink_apology).
- **Fix, mechanical.** NEW `scripts/build_email_templates_page.py` — the ONE writer. It reads the
  emailer's own TEMPLATES map, subject lines, sender/reply-to and waves_policy.json, mirrors every
  letter in the send lane into orchestration_v2/templates/ in its AS-SENT form (launch-special block
  stripped exactly when launch_codes.enabled() would strip it), and rebuilds the page with every badge
  computed from the sending file (unsubscribe · special state · magic-link CTA · support route ·
  personal-channel scan · browse link · wave tag · inline mark · source line). `--check` exits 1 on
  drift. 20 letters in the lane (7 organisations, 2 clubs/registers, 7 individuals, 4 other), plus
  the placement lane (David's reserved send, unchanged) and the three 23 Aug agency-lane design
  drafts, relocated to orchestration_v2/templates/agency_lane_design/ and shown in their own section
  marked NOT what sends today. Nine deploy-manifest rows added. RG-0344 LOCKED.
- **Found on the way — SPECIAL-CLOSE-1.** CityLauncher/.env was still LAUNCH_SPECIAL_ENABLED=1 with
  LAUNCH_SPECIAL_DEADLINE=2026-09-01, and `launch_codes.enabled()` had no date check, so the window
  RUL-060 closed on 1 Sep never closed: prospects.db shows 645 launch numbers issued 2–7 Sep with
  expires_at 2026-09-01, and the 2–5 Sep sends in block-carrying categories (Tutors 131, Services 127,
  us_university_tutors 138, teachers_trainers 79, adventures 26) went out saying "valid until
  1 September 2026". Fixed at class level: `window_open()` date gate inside `enabled()` (deadline
  day inside, day after out, SAST clock), `issue_for_send()` no-ops when off, .env un-armed with a
  dated note. Proven both ways in a subprocess against a throwaway DB path. RG-0345 LOCKED.
- **Found on the way — the agency letters that SEND still tell the solo-seller story.** AGENCY-WAVE-1
  (23 Aug) put the three-lane block into the preview folder only; RG-0165 asserted it there and read
  green for 16 days. CityLauncher's agency/travel_agency/cars_dealer letters carry the four-step solo
  flow, their CTA is the solo magic link (no wave-prep call in the lane), and the n8n lane reads
  /var/www/marketsquare/n8n/email_templates/ on the server — seven letters dated 10 May 2026, no
  agency letter. Nothing wrong went out (agency sends are David's act, RUL-053(f)); the letter he would
  send today is the solo one. RG-0165's path corrected with a dated note; RG-0346 OPEN carries the gap
  and prints READY TO LOCK when the sending copies carry the agency story with a console link.
- **Own-goal, recovered.** The first draft of RG-0345's executed leg called issue_for_send() in the
  window-open case, which wrote prospects.db from the sandbox — the 31 Aug / RG-0330 hazard — and
  stranded a hot journal. Recovered the same minute by the documented method (rolled back on a
  sandbox-local copy, integrity ok, 5,928 rows / 1,460 emailed / 812 codes, no probe row, journal
  moved aside as `prospects.db-journal.aside-20260908-054001`, backup
  `prospects.db.bak-hotjournal-20260908-054001`). The leg now repoints `_DB` at a temp file BEFORE any
  call and only calls issue_for_send when enabled() is False.
- Ledger: 3 shards + combine green (every locked fix holding; 22 open). rulings_check 0 FAIL.
  Files: scripts/build_email_templates_page.py (new), orchestration_v2/email_templates.html (rebuilt,
  backup .bak-truth-20260908), orchestration_v2/templates/* (20 mirrored + agency_lane_design/),
  ops/autodeploy/deploy_manifest.txt (+9 rows), scripts/regression_ledger.py (+RG-0344/0345/0346,
  RG-0165 ref), CityLauncher/emailer/launch_codes.py (+window_open, backup
  .bak-special-close-20260908-053237), CityLauncher/.env (flag 1→0, backup kept).
