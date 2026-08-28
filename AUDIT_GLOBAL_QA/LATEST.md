# Global QA audit — 2026-08-28 (17.1s)

**3 findings** (0 new vs previous run)

- **MEDIUM** [links] `LINKS-DEAD` — 5 hardcoded external links failing (checked 11): ['https://example.com/hilux1.jpg', 'https://example.com/hilux2.jpg', 'https://example.com/house1.jpg', 'https://example.com/house2.jpg', 'https://example.com/kruger1.jpg']
- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] `VERSION-KEY-BENIGN` — repo html pins ms.js v477, live pins v549, but the served bytes are IDENTICAL to the repo — this is the server's monotonic ?v= bump, not drift. Recorded, not raised (DW-001).
