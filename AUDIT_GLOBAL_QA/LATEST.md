# Global QA audit — 2026-09-18 (18.4s)

**3 findings** (2 new vs previous run)

- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] 🆕 `MSJS-DRIFT` — live ms.js (v685, 1283843B) != repo ms.js (1289998B) — content differs after line-ending normalisation, so this is REAL drift, not CRLF; expected while a deploy is staged, CRITICAL if it persists after deploying
- **INFO** [drift] 🆕 `VERSION-KEY` — repo html pins ms.js v495, live pins v685 AND the bytes differ (see MSJS-DRIFT) — a real deploy is staged
