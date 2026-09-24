## 2026-09-24 — ADMIN-BIND-1 (RG-0448): five admin routes were open to the public app key

Found while lowering the platform AI ceiling David approved this morning. `POST/GET /admin/users`,
`DELETE /admin/users/{id}`, `GET /admin/ai-spend` and `PUT /admin/ai-spend/config` were guarded by
`auth.require_api_key` alone — and that key ships inside ms.js. PROBED LIVE before the fix: the public key
returned the admin account list (200) and the AI-spend config with the alert e-mail (200); the PUT would have
let anyone raise the per-user and platform AI ceilings. Same class as DELETE-BIND-1 (23 Sep).

Each of the five handlers now calls `_require_admin_or_key(x_admin_token, x_admin_key)` before touching the
database. No page or script called these five with the app key alone (the admin console and the spend gauge
use the admin key / token on `/admin/ai-spend/summary`), so nothing visible changes. Guard: RG-0448, with a
live probe that FAILs on a 200, passes on the app's 401, and reports BLIND on an edge 403.

Then, as approved: `daily_platform_ceiling_usd` 100 → 10 (still ~300× today's spend), set through the
admin route from the box with the admin key.
