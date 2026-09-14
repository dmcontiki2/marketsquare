## 2026-09-13 — Quick Listing: items 1, 3 and 5 closed

Against the three items opened on 12 Sep:

1. **Card-building fix — VERIFIED** in a rendered browser, not just on disk. A duplicate-title fault
   found in the same pass and fixed without touching the RS → TS → LS order.
2. **Embedded photos — still open**, and now has a design: three photo types, none of them
   hardcoded stock (David, 13 Sep). Next job on the harness.
3. **Seller's three scores with coaching — DONE** (RUL-121), mirroring `_import_quality_score()`.
5. **Hand-over to real listings — BUILT, verified, and PROVEN LIVE.** David authorised one draft
   on trustsquare.co under Dave Junior's tester account; it came back as listing **383**, status
   draft, and reads back correctly. Visible at Dashboard → Listings for that account.

Still outstanding towards a final app: the photo refactor, the `/quick/` sub-path and its own
manifest and coloured tile (RUL-125(a)), push registration (no service worker is registered yet,
RUL-122), the six baseline-readiness checks written into the regression ledger (RUL-125(c)), the
name for the wider worker category, and the hirer's side of the communication link.
