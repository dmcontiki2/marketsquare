## 2026-08-18 — Migration 023: relink wonders rides the deploy (HERITAGE-RAIL-1 follow-through)

- Found while answering "where is relink_wonders.py": the root script is NOT in the
  deploy manifest, so "run relink on the server post-deploy" would have needed a manual
  SSH round-trip — exactly the class ONE_DEPLOY retired. migrations/023_relink_wonders_railexp.py
  embeds the same seller-set-preserving relink logic and runs once, automatically, after
  the expanded wonders.json lands (refuses + retries if the catalog is still 332).
  The manual "run relink_wonders.py on the server" step from this morning's fragment is
  hereby superseded — nothing manual remains post-deploy except promoting RG-0101.
