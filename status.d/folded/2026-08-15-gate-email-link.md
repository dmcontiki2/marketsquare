- **GATE-EMAIL-1 BUILT, awaiting deploy (15 Aug):** gate entry is now email-linked (one-time
  30-min single-use link -> same ts_review cookie, 365d); reviewer code demoted to break-glass;
  GATE-COOKIE-2 ends the sessionStorage re-challenge lockout class at the root. Migration 019
  exempts /review/request-link + /review/enter at the origin and seeds the 5-email allowlist.
  RG-0081 OPEN (live half flips it READY TO LOCK post-deploy); RUL-014 registered. NEXT: /tsl
  on David's word, then send each tester their first link and promote RG-0081.
