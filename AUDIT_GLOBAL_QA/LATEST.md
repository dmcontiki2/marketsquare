# Global QA audit — 2026-08-30 (13.6s)

**3 findings** (2 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] 🆕 `MSJS-DRIFT` — live ms.js (v552, 1156049B) != repo ms.js (1156147B) — content differs after line-ending normalisation, so this is REAL drift, not CRLF; expected while a deploy is staged, CRITICAL if it persists after deploying
- **INFO** [drift] 🆕 `VERSION-KEY` — repo html pins ms.js v477, live pins v552 AND the bytes differ (see MSJS-DRIFT) — a real deploy is staged
