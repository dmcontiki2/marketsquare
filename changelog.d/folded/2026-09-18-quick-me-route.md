## 2026-09-18 — QUICK-ME-ROUTE-1: /quick/me handed back to the app (migration 043)

- Found by the post-fix ledger run: RG-0386 red — the live /quick/me answered the Quick HTML page, not JSON.
  Cause: migration 042's `location /quick/` prefix (17 Sep) swallowed the app's GET /quick/me, so a
  stranger arriving by e-mail link never got the identity/key the Quick page needs.
- migrations/043_quick_me_route.py adds an exact `location = /quick/me` proxy to the app ahead of the
  page door; nginx -t, reload, and proves JSON on the origin over TLS loopback, else restores.
