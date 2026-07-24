# Global QA audit — 2026-07-24 (14.6s)

**3 findings** (2 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] 🆕 `MSJS-DRIFT` — live ms.js (v370, 1015602B) != repo ms.js (1018086B) — expected while a deploy is staged; CRITICAL if it persists after deploying
- **INFO** [drift] 🆕 `VERSION-KEY` — repo html pins ms.js v372, live pins v370 (deploy pending)
