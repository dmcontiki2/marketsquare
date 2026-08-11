# Global QA audit — 2026-08-11 (12.3s)

**3 findings** (1 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] 🆕 `MSJS-DRIFT` — live ms.js (v458, 1056818B) != repo ms.js (1073228B) — expected while a deploy is staged; CRITICAL if it persists after deploying
- **INFO** [drift] `VERSION-KEY` — repo html pins ms.js v435, live pins v458 (deploy pending)
