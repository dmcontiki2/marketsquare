## 2026-08-24 — SHIPPED: ONE-REPLY-1 + support Reply-To live (release 06:23:42, tag ship-20260824-0623)

- Rode the 06:23:42 release (concurrent-session commit swept the files; origin/deploy = 9bb74cf).
  Smoke: index 200 in 0.43s with sentinels, listings 200, /health ok, post_deploy all-ok
  (seed, ladder_seed, migrations none pending).
- E2E PROBED live: test C raced the restart by 9s and still double-replied (old process);
  test D after post_deploy settled got EXACTLY ONE reply — substantive answer carrying
  fault ref LIST-13. MAINT-B1's ack promise kept inside the one email.
- Still pending for RG-0174 promotion: David's `wrangler deploy` of the dead-letter worker
  (test D's copy still forwarded to the personal inbox — worker unchanged on CF), then one
  clean no-copy E2E. Rollback point: tag ship-20260824-0623.
