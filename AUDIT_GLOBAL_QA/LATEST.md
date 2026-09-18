# Global QA audit — 2026-09-18 (17.9s)

**2 findings** (1 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] 🆕 `VERSION-KEY-BENIGN` — repo html pins ms.js v495, live pins v686, but the served bytes are IDENTICAL to the repo — this is the server's monotonic ?v= bump, not drift. Recorded, not raised (DW-001).
