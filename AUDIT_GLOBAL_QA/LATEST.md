# Global QA audit — 2026-08-21 (13.1s)

**3 findings** (2 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] 🆕 `MSJS-DRIFT` — live ms.js (v510, 1084619B) != repo ms.js (1096659B) — expected while a deploy is staged; CRITICAL if it persists after deploying
- **INFO** [drift] 🆕 `VERSION-KEY` — repo html pins ms.js v454, live pins v510 AND the bytes differ (see MSJS-DRIFT) — a real deploy is staged
