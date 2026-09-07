## 2026-09-07 — The last three stale secret backups deleted from the server ("Yes please")

Second permission, same day. Deleted: `/var/www/marketsquare/.env.bak-20260718-onemodel`,
`/var/www/marketsquare/.env.bak-cf-20260722-174900`, `/etc/marketsquare/resend.watch.conf.bak-20260828`.
Guard: each was removed only if its live twin existed under the un-stamped name; twins verified
unchanged afterwards (`.env` 1620 B, `resend.watch.conf` 74 B — the RED-alert key copy, intact).
`/health` 200. No `.bak` remains in `/etc/marketsquare/` or beside the app `.env`.
`secret_consumers.py --check` OK. Register carries the rule going forward: a rotation's `.bak` is
deleted by the next session once the new value is proven.
