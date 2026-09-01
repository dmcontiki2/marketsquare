# Global QA audit — 2026-09-01 (13.8s)

**2 findings** (0 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] `VERSION-KEY-BENIGN` — repo html pins ms.js v479, live pins v564, but the served bytes are IDENTICAL to the repo — this is the server's monotonic ?v= bump, not drift. Recorded, not raised (DW-001).
