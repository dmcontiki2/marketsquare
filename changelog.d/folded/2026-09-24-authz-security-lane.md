## 2026-09-24 — Security lane + email-identity write routes closed (AUTHZ-PROBE-1, IDENTITY-BIND-3, ADMIN-LOCALGUARD-1)

David asked why the daily watch never caught the bug-audit vulnerabilities. Because every
check it ran was a regression check — it re-proved known fixes; nothing tried the front door
with the wrong key. Built the missing lane and closed the class it exposed.

- **AUTHZ-PROBE-1** — `scripts/authz_probe.py`: calls the live site against every admin route
  and every identity-bound write route with (a) the public app key shipped in ms.js and (b) no
  credential, and asserts each REFUSES. Safe by construction (bogus/nonexistent targets, so no
  real data is touched). stdlib-only, runs from any vantage. It found a real pre-existing hole
  on its first run: `POST /admin/purge-cache` answered anonymous callers 200.
- **ADMIN-LOCALGUARD-1** — `/admin/purge-cache` and `/admin/refresh-pois` failed OPEN when the
  env key was unset. Now fail-closed via `_admin_local_or_key`: a valid admin key OR a request
  with no `X-Forwarded-For` (only a local process — the deploy's own purge — can reach uvicorn
  without nginx stamping that header). External callers always carry it, so the public door is shut;
  the deploy's non-fatal auto-purge keeps working with no config change.
- **IDENTITY-BIND-3** — eight write routes trusted an email in the request instead of the proven
  session (the class AUDIT-AUTH-1 fixed for publish/edit/mine): keep-live, listing cities
  add/remove, listing wonders, profile photo, self-declared experience (trust score), and saved
  searches save/delete. All now bound to the signed-in session via `_actor`; admin key preserved;
  BUZZ_BIND=0 escape hatch unchanged. The session rides a same-origin cookie, so no frontend change.
