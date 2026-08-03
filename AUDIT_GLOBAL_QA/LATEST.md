# Global QA audit — 2026-08-03 (11.5s)

**3 findings** (1 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] 🆕 `MSJS-DRIFT` — live ms.js (v426, 1033905B) != repo ms.js (1049997B) — expected while a deploy is staged; CRITICAL if it persists after deploying
- **INFO** [drift] `VERSION-KEY` — repo html pins ms.js v422, live pins v426 (deploy pending)
