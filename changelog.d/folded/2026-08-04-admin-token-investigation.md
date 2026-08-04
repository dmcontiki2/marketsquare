## 2026-08-04 — Admin-token path investigated; weak-fallback trap removed (JWT-HARDEN-1)

**Trigger:** the GPT-5.6 Peer review asked (correctly) whether rotating `MS_JWT_SECRET` would
actually revoke the admin token exposed during the 2-3 Aug breach window, and whether `ms_admin_token`
was really the same thing as the server-side `MS_ADMIN_KEY` / `ADMIN_KEY`.

**Findings (read-only investigation of `bea_main.py`):**

1. `ms_admin_token` is a **signed HS256 JWT** minted by `_make_token()` from `MS_JWT_SECRET`,
   8-hour expiry — NOT a static key. Therefore rotating `MS_JWT_SECRET` **does** invalidate it.
   The Peer's worry that rotation might be a no-op (opaque token) is resolved: rotation is effective.

2. `ms_admin_token` is **not** `MS_ADMIN_KEY` or `ADMIN_KEY`. Those are a separate static header
   key checked on a different path (`x_admin_key == MS_ADMIN_KEY`). The browser only ever held the
   JWT, so the static admin key was **never browser-exposed** and needs no breach-driven rotation.

3. **Latent trap found (unrelated to Travelpayouts):**
   `_JWT_SECRET = os.environ.get("MS_JWT_SECRET", "ms_jwt_secret_change_me")` carried a hardcoded
   fallback. If any environment ever failed to set the variable, the app would silently sign admin
   tokens with a **publicly-known string**, making all 14 admin-guarded endpoints forgeable — with
   no warning.

4. **Live is safe right now.** Verified on the box by reading the running process environment
   (`/proc/<pid>/environ`): `MS_JWT_SECRET` is SET, 64 chars, strong. The fallback is not in effect.
   (The `.env` file does not contain it — it is injected via systemd / start script — which is why a
   file grep said "NOT PRESENT" while the live process has it.)

**Fix shipped (repo, live on next deploy):**
- Removed the weak fallback: default is now `""`.
- `_make_token()` raises 503 if `MS_JWT_SECRET` is unset (never signs with an empty/known key).
- `_require_admin_or_key()` ignores `X-Admin-Token` when the secret is empty (no empty-key verify).
- Net effect: admin auth now **fails closed** instead of silently trusting a known string.

**Rotation — DONE 4 Aug 2026.** `MS_JWT_SECRET` rotated to a fresh `openssl rand -hex 32` value on
the live box and the service restarted; verified by reading `/proc/<pid>/environ` that the running
process uses the new secret (MATCH). Any admin token captured during the breach window is now
rejected. `MS_REVIEW_SECRET` is derived from `MS_JWT_SECRET` in code (not set explicitly), so it
rotated automatically. `MS_ADMIN_KEY` / `ADMIN_KEY` were NOT rotated (never browser-exposed).
Config hygiene fixed in the same pass: the secret was defined in BOTH the systemd unit
(`Environment=`, the original source) and — after rotation — `/etc/environment`. The stale old value
was removed from the unit file, leaving `/etc/environment` as the single source. Backups:
`/etc/environment.bak-jwt-*` and `/etc/systemd/system/marketsquare.service.bak-jwt-*` (the unit
backup contains the now-dead old secret — delete once confident).

**Low-priority note:** the static-key check `x_admin_key == MS_ADMIN_KEY` is a plain `==`, not
constant-time — a theoretical timing side-channel, worth a `hmac.compare_digest` at some point.


## Follow-ups surfaced during rotation (non-urgent)

- `MS_JWT_SECRET` now lives in `/etc/environment`, which is world-readable and system-wide (every
  local process/login sees it). Move app secrets to a dedicated `EnvironmentFile=` with `chmod 600`.
- `marketsquare.service` runs uvicorn with `--host 0.0.0.0` (all interfaces) — the reason the
  direct-origin hit worked before the firewall. Bind `127.0.0.1` since nginx is the only intended
  client; the Hetzner firewall (RG-0028) already mitigates, so this is defence-in-depth.
- Old-secret backups (`*.bak-jwt-*`) can be deleted once the new secret is trusted in production.
