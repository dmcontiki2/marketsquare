## 2026-08-24 — RUL-054 / SUPPRESS-1 / LAUNCH-API-LOCK-1: the POPIA suppression invariant built

- David's rule audited against the machinery (probed): opt-out core existed and was sound
  (permanent status, clear-safe, UNIQUE email blocks re-scrape); emailer lanes filter. Gaps
  closed same session: separate canonical `suppression` register written by /optout; the
  register verified at TWO gates incl. inside send_email itself (fail-safe: unreadable
  register = no send; offline proof executed); launch-api PII endpoints key-gated
  (X-Launch-Key; found serving full prospect PII anonymously — Claude read 3,241 rows
  without auth this morning; /database/clear was publicly callable, now disabled without a
  key). Ops dashboard prompts/stores the key; fill_wave_gaps sends it.
- RG-0176 OPEN: n8n lane reads the orchestration store — one-click-both-stores proof +
  live 401 await the CityLauncher deploy + LAUNCH_API_KEY provisioning (David's acts).
