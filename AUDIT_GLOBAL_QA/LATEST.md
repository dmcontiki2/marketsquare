# Global QA audit — 2026-08-04 (12.4s)

**3 findings** (0 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] `MSJS-DRIFT` — live ms.js (v428, 1033905B) != repo ms.js (1048751B) — expected while a deploy is staged; CRITICAL if it persists after deploying
- **INFO** [drift] `VERSION-KEY` — repo html pins ms.js v423, live pins v428 (deploy pending)
