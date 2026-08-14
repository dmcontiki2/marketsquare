- **GATE-EXEMPT-MAINT-1 + BRAIN-DEPS-2 (13 Aug, David's "fix both"):** migration 018
  committed — exempts /admin/faults* + /dashboard/maint (and nothing wider) from the
  origin gate per 007's M2M doctrine, after auditing that every route fails closed on
  _require_maint; runs on the next successful deploy (engine stalled, DW-042 — tonight's
  17:45 session or NIGHTLY-SHIP-1). RG-0065 OPEN watches for it landing (keyed-no-cookie
  intake 401 = expected until then; GATE-COOKIE-1 keeps the loop alive). Maintenance-loop
  scheduled task rewritten to the foreground agent-run method (sandbox reaps detached
  processes at the call boundary). Note for tonight's DW-029 rotation: GATE-COOKIE-1
  re-reads .secrets/review_code.txt every run — rotating the review code is compatible,
  no code change needed.
