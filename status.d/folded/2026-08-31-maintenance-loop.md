**Maintenance loop, 31 Aug 2026 (T-1 to full launch).** Fault queue empty — 0 new, 0 triaged,
0 fix-shipped, 26 verified, 7 closed — so the session's work was finding out why. Three
defects closed, none of them reported by anyone:

- **RG-0222 / DASH-TRIAGE-REDACT-1 (privacy, launch-critical).** `GET /dashboard/email-triage`
  served sender addresses, subjects and reply bodies to any anonymous caller — the sibling
  RG-0211 tightened on 30 Aug and left behind. Now counts-only for strangers, rows behind the
  admin credential both dashboards already hold. Awaiting deploy; live assertion stays red
  until it lands.
- **RG-0223 / MAINT-INTAKE-2.** The brain read only `app_faults`, the lane RUL-040 shuts at
  soft launch, while customer complaints arrive by email. It now censuses `email_triage` every
  run (15 total, 1 held) so "0 seen" can never again mean "nobody looked".
- **LEDGER-PENDING-BUILD-1.** RG-0221 printed READY TO LOCK daily for a build that has not
  started; promoting it would have locked the weak half. Pre-build harnesses now read OPEN
  with their reason.

Ledger green before and after (deps restored first — the board was exit 2 on missing
`httpx`/`fastapi`). Rulings 76/0/0. No escalations. Committed, not pushed — NIGHTLY-SHIP-1
carries it through the gates.
