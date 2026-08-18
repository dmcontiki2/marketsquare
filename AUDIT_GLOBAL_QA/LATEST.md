# Global QA audit — 2026-08-18 (17.3s)

**3 findings** (0 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] `MSJS-DRIFT` — live ms.js (v498, 1074812B) != repo ms.js (1091364B) — expected while a deploy is staged; CRITICAL if it persists after deploying
- **INFO** [drift] `VERSION-KEY` — repo html pins ms.js v448, live pins v498 AND the bytes differ (see MSJS-DRIFT) — a real deploy is staged
