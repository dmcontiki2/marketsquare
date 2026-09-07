## 2026-09-07 — Seven stale secret backups deleted from the server (David's permission, same day)

David, after RG-0308 closed: "Please delete any of the files you asked permission for to delete."
Deleted over ssh, each name pattern-checked as a stamped `.bak-YYYYMMDD-HHMMSS` before `rm`:
`/etc/marketsquare/secrets.env.bak-20260822-062621`, five `/var/www/marketsquare/.env.bak-*`
(22 Aug ×4, 2 Sep ×1), `/usr/local/bin/backup_dbs_to_r2.py.bak-20260906-084230`.
Verified after: all seven gone; the three live files they backed up untouched (sizes and modes
unchanged); `/health` 200; `secret_consumers.py --check` OK with no STALE line.
Not in the permission and still on the box: two July `.env.bak-*` files (600, two credential lines
each) and `resend.watch.conf.bak-20260828` — named in SECRETS_REGISTER.md.
