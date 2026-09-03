# Global QA audit — 2026-09-03 (18.7s)

**2 findings** (0 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] `VERSION-KEY-BENIGN` — repo html pins ms.js v481, live pins v581, but the served bytes are IDENTICAL to the repo — this is the server's monotonic ?v= bump, not drift. Recorded, not raised (DW-001).
