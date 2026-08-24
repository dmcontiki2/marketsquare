## 2026-08-24 — agency funnel walked end-to-end; one real trap found and fixed (AGENCY-INVITE-MAIL-1)

- Funnel probe (recipient view, clean client): all 10 outreach-email links/images answer 200
  anonymously — the gate is DOWN for reads today. Email CTA → console landing was E2E-proven
  23 Aug (Kronberg). CSV paste parser honours quoted commas. Bulk ADVERT import asserted live
  (RG-0166).
- Trap: bulk agent roster never sent the promised sign-in links; invite email was the code
  template with an empty code box. Fixed on disk (bea_main.py, estate_agents.py, ms.js),
  56/56 tests, ledger RG-0171 OPEN pending deploy. AWAITING: David's ship.
