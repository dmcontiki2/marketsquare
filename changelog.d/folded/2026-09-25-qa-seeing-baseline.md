## 2026-09-25 — The deploy gate's first seeing run met a blind baseline; every deploy was being rolled back (QA-BASELINE-SEEING-1)

QA-GATE-BLIND-1 (0ae338b) taught the QA Bot to prove it can see the app, and to fall back to the app's loopback when
the front door refuses it. Its first seeing run was compared with a baseline written by the blind runs (every route
"PASS" because nginx answered 403 before the app), so 15 routes that have answered strangers for a long time were
reported as "OPENED by this deploy" and two releases were rolled back at 20:58Z (d004d98, INSPECT-FIX-1) and 21:02Z
(dc6425b, QUICK-LINK-1). Nothing in either release opened a route.

- **Proof the 15 were already open:** `qa_bot.py probe` from the same loopback vantage against the running release
  (1bfd487, before either rolled-back deploy) returned the identical 15 FAIL + 1 CRASH (report
  /var/lib/trustsquare-qabot/reports/20260925-210447-probe.html).
- **Re-baselined, not weakened:** that measured run was accepted as the baseline (`probe --accept`, the seeing bot from
  origin/main); the blind baseline is kept beside it as last.json.bak-blindbase-20260925-210310. The 15 FAIL and 1 CRASH
  stay FAIL/CRASH in every report and keep the nightly RED until they are fixed; the gate again rolls back only a release
  that opens a NEW route.
- **The 15, now open work (OPEN_LOOPS L19):** admin/ops reads answering strangers at the app layer (/dashboard/cost,
  /dashboard/email-triage, /dashboard/scan, /dashboard/summary, /health/resources, /listings-coverage, /onboard/funnel,
  /ops/selfcheck with the public key, /optout/status), POST /admin/purge-cache, POST /agencies/wave-prep crashing on the
  public key, and five routes the app serves signed-out by design (/quick/me, POST /quick-invite, POST /search/interpret,
  POST /users, POST /presence/ping) whose rulings need an appeal rather than a lock.
