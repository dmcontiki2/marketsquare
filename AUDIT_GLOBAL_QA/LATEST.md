# Global QA audit — 2026-07-17 (13.1s)

**3 findings** (1 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] `MSJS-DRIFT` — live ms.js (v294, 901984B) != repo ms.js (906850B) — expected while a deploy is staged; CRITICAL if it persists after deploying
- **INFO** [drift] 🆕 `VERSION-KEY` — repo html pins ms.js v295, live pins v294 (deploy pending)
