- **Maintenance loop 13:24Z — B2b lane restored through the armed gate (GATE-COOKIE-1, RG-0064):**
  the morning's gate arming (016) had silently killed remote maint intake/heartbeat at nginx
  (401 before the app saw X-Maint-Key; 13:17Z run failed safe). Both consumers now carry the
  ts_review credential like the ledger does; gate config untouched (an origin-side exemption
  stays David's call — one line for the 17:45 session if wanted). Proven: clean 13:24Z run,
  heartbeat on the live card 13:24:46Z, RG-0064 locked with an inverse guard (anonymous
  /admin/* stays refused). Heartbeat gap 03:39→13:24 was this. Queue: TS-0031 → PATH_B
  (design backlog, 3rd identical verdict). Ledger green before and after; commit rides
  NIGHTLY-SHIP-1 / the revived engine (DW-042) — client-side scripts only, nothing needs the box.
