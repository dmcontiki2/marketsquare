- **GATE-EMAIL-1 LIVE (15 Aug ~08:05 UTC, /tsl):** email-linked gate entry shipped and proven
  live end-to-end; RG-0081 LOCKED. Allowlist seeded (David x2 + 3 testers) at
  /var/www/marketsquare/review_emails.txt — edit live, no restart. Rollback tag
  pre-tsl-gateemail-20260815. NEW OPEN: RG-0082 — CF edge cache hands the gated HTML shell to
  anonymous visitors after a cookie-holder primes it (pre-existing since 13 Aug; data sealed;
  fix = CF html-bypass rule [David console] OR origin no-store migration; reversible by 29 Aug).
