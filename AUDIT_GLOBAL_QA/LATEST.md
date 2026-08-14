# Global QA audit — 2026-08-14 (13.6s)

**3 findings** (1 new vs previous run)

- **INFO** [demo] 🆕 `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] `MSJS-DRIFT` — live ms.js (v470, 1060023B) != repo ms.js (1076474B) — expected while a deploy is staged; CRITICAL if it persists after deploying
- **INFO** [drift] `VERSION-KEY` — repo html pins ms.js v438, live pins v470 AND the bytes differ (see MSJS-DRIFT) — a real deploy is staged
