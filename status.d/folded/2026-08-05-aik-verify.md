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
- v2: reconcile runs server-side over SSH (edge gate 403s off-browser HTTP by design).
