# Global QA audit — 2026-07-27 (14.5s)

**2 findings** (0 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] `MSJS-DRIFT` — live ms.js (v395, 1028907B) != repo ms.js (1028911B) — expected while a deploy is staged; CRITICAL if it persists after deploying
