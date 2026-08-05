## 2026-08-05 — AIK-VERIFY-1: people report, machines verify (David's ruling)

- **Doctrine amended** (MAINTENANCE_AGENT.md + FAULT_REGISTER.md): the month's evidence
  answered the design question early — testers report but do not retest (retest chip 0
  while 21 fixed-or-open majors sat amber). David's ruling: after a fix the AI TESTS it
  and declares it verified (green) on NAMED machine evidence (reproduced-clean, tripwire,
  or live probe in fix_note); the tester retest letter becomes an optional courtesy; a
  tester's "still broken" always reopens. The who of verification changed, never the
  whether.
- **RECONCILE_FAULTS.bat + scripts/fault_reconcile.py:** one click on David's machine —
  reads the queue, marks the 16 substantiated fixed faults VERIFIED with evidence
  (TS-0002/3 via RG-0031; TS-0004 brand-label; TS-0005/7/8/9/10/11/12/19/20 fixback
  9166b30; TS-0014..17 OPS-MAP-2 b0182af), prints the honest still-open triage table,
  writes Records/FAULT_RECONCILE_<date>.md. One y/n before any write.
- No BEA change needed — the PUT /admin/faults ladder already supports verified (+
  verified_at); the Ops Map already counts verified as green.
- v2 same day (found live by David's first click): the edge gate 403s any off-browser
  HTTP call before the maint key is examined — by design. RECONCILE_FAULTS.bat v2 now
  ships the script over SSH and runs it ON the server against localhost (key read from
  the server's own .env; nothing secret travels); report scp'd back to Records/.
  MAINTENANCE_KEY_SETUP.md's verify-curl carries the same gate note now.
- ENVKEY-1 strike again (found live: the rail light stayed off after a PROVEN secret
  install): RELAY_DOMAIN/RELAY_INBOUND_SECRET were read via bare os.getenv, which the
  systemd unit never populates. Both now use ai_provider.envkey() (env -> server .env
  fallback). RG-0038 gained an assertion so the class cannot rot back.
