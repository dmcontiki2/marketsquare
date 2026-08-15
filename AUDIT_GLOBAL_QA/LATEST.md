# Global QA audit — 2026-08-15 (13.8s)

**3 findings** (0 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] `MSJS-DRIFT` — live ms.js (v474, 1060023B) != repo ms.js (1070419B) — expected while a deploy is staged; CRITICAL if it persists after deploying
- **INFO** [drift] `VERSION-KEY` — repo html pins ms.js v438, live pins v474 AND the bytes differ (see MSJS-DRIFT) — a real deploy is staged
