# Global QA audit — 2026-08-26 (15.9s)

**4 findings** (2 new vs previous run)

- **MEDIUM** [links] `LINKS-DEAD` — 5 hardcoded external links failing (checked 11): ['https://example.com/hilux1.jpg', 'https://example.com/hilux2.jpg', 'https://example.com/house1.jpg', 'https://example.com/house2.jpg', 'https://example.com/kruger1.jpg']
- **INFO** [demo] `DEMO-PLACEHOLDERS` — 3 'coming soon' placeholder listings present (by design; verify they stay out of counts)
- **INFO** [drift] 🆕 `MSJS-DRIFT` — live ms.js (v542, 1156049B) != repo ms.js (1173438B) — expected while a deploy is staged; CRITICAL if it persists after deploying
- **INFO** [drift] 🆕 `VERSION-KEY` — repo html pins ms.js v477, live pins v542 AND the bytes differ (see MSJS-DRIFT) — a real deploy is staged
