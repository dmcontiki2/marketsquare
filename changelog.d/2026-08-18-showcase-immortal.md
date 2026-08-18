## 2026-08-18 — SHOWCASE-IMMORTAL-1: supers exempt from fade-out; admin-only delete (RUL-023)

David: fade warnings were reaching the super demos — "they should stay live and only be
deleted by admin users." Root cause: supers are real listings (showcase=1, is_demo=0), so
FADE-1's lifecycle sweep treated them as user listings. Class fix:
- _lifecycle_sweep: candidate query + archive step both exclude showcase listings.
- Deletes: keyed /listings/{id} DELETE now demands real admin credentials (X-Admin-Token /
  X-Admin-Key) for showcase — the ms.js-public app key alone is refused; the seller-email
  delete path 403s showcase outright. "Showcase adverts are admin-managed."
- migrations/024_showcase_immortal.py revives any already-faded/archived showcase and
  clears stale fade-nudge stamps on the next deploy.
- Records: RUL-023 · RG-0106 (LOCKED, repo-asserted; live from next deploy) · reflections.
