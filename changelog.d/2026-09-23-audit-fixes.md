## 2026-09-23 — Bug audit of the day's work: fixes, ZA-only languages, --chunk ledger, app pictures (RUL-165)

- AUDIT-Q1: one-tap publish never acts for an EXISTING account typed by a stranger — it gets a draft and a sign-in letter; a new address still publishes in one tap; per-connection limit (5/day).
- AUDIT-Q2: the browser can no longer set trust score, image paths, specs or status on a Quick advert.
- AUDIT-Q3: when publishing is refused (e.g. plan full) the way-back letter is really sent and the arrival button opens the draft.
- AUDIT-AUTH-1: PUT /listings/{id}/publish, PUT /listings/{id} and GET /listings/mine act as the proven session (RUL-135), not ?email=.
- AUDIT-L1: GET /listings/{id} hides the seller's email from everyone but the seller, and never returns language working data; the seller's panel reads GET /listings/{id}/lang (owner-only).
- AUDIT-L2/L3: editing the original words (only after the owner check) clears the old translation, its back-translation and the English search layer.
- AUDIT-L4/L5/L6/L7/Q4/S1/S2/S4: photo marker never translated; Back and view counts unaffected by a language re-render; translate lane only for offered languages; spend counted after success; quality preview never 500s; shorter AI timeouts; live letter lands on the hub card; AI text escaped.
- AUDIT-XSS-1: titles/descriptions are stored as plain text (older stored-XSS class).
- RUL-165: ZA languages live on Claude's drafts; the other eight countries' local languages "prepared", not offered.
- LEDGER-CHUNK-1: `regression_ledger.py --chunk` — time-budgeted, resumable board; the full board ran in-session: 427 entries, 0 regressed.
- APP-PICS-1: six street pictures for Quick's "Where do you work?" step (scripts/gen_app_pictures.py; app imagery only, never users' photos); pushed by the media lane; used only once each picture has loaded.
