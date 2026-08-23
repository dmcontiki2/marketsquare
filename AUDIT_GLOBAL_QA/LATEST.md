# Global QA audit — 2026-08-23 (14.2s)

**3 findings** (2 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] 🆕 `MSJS-DRIFT` — live ms.js (v517, 1122109B) != repo ms.js (1139164B) — expected while a deploy is staged; CRITICAL if it persists after deploying
- **INFO** [drift] 🆕 `VERSION-KEY` — repo html pins ms.js v459, live pins v517 AND the bytes differ (see MSJS-DRIFT) — a real deploy is staged
