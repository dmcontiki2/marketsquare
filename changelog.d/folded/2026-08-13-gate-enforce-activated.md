## 2026-08-13 — Origin token gate ACTIVATED: migration 007 unblocked (GATE-ENFORCE-2)

David's ruling (13 Aug, morning): close DW-023 / RG-0029 now. Actions, all prepared
this session, publish rides David's next release click:

- **migrations/DEFERRED.txt**: the 007_review_gate_enforce.py line REMOVED (DEFER-1
  mechanism) — nginx auth_request gate on the API catch-all runs on the next deploy.
  Exempt by design: /review/login, /review/verify, /health, /payment/webhook,
  /email/inbound, /intro/relay, /.well-known/. Documents and /static/ untouched.
  **005 stays deferred deliberately** — Basic Auth on documents is a separate posture
  decision (and refuses to run without a provisioned password anyway).
- **scripts/regression_ledger.py**: `_get()` taught to read bodies THROUGH the gate —
  one /review/login per run (code from MS_REVIEW_CODE or gitignored
  .secrets/review_code.txt, provisioned this session, chmod 600), ts_review cookie
  retry on 401/403. Body probes keep asserting payload truths (RG-0045 stays strong,
  fails loudly if it can read nothing); gate POSTURE stays measured anonymously via
  _status() (RG-0029's job). Pre-deploy proof: full run exit 0, zero behavior change.
- **Tester impact: none expected** — ts_review cookies are 365-day since 5 Aug
  (David's ruling); testers who entered the code once stay in.
- **Named tail (queued, NOT silent):** on-box/edge tooling that reads data endpoints
  anonymously (maintenance-loop intake, server smoke's data probes) will see 401 after
  the gate rises — same family as UA-EDGE-1/BIT-AIM-1. Queued as OPEN_LOOPS L7 for the
  next attended loop: point on-box tools at 127.0.0.1:8000 or give them the cookie.
- This publish also carries everything queued on "next deploy": migration 015 (Tier-2
  re-verdict for D12), RG-0050 dashboard, NO-RETEST-1 routes, SHOWCASE-BANNER-1 /
  migration 014.
- After the deploy: verify anon /wonders|/flags|/demo-sellers = 401, /health = 200,
  documents/static = 200 → promote RG-0029 OPEN→LOCKED → full ledger green run.

Backups: migrations/DEFERRED.txt.bak-20260813-025750,
scripts/regression_ledger.py.bak-20260813-025750. Restore = cp back.
