# Production box — patch & reboot log (PATCH-CADENCE-1)

One line per maintenance window. Asserted by regression ledger **RG-0246**: the newest
`REBOOT` row must be < 45 days old, and its `reboot_required` column must read `absent`.
A window that upgrades packages but leaves the reboot-required flag standing does NOT
count — record it as `PATCH` and the assertion keeps reading the last `REBOOT`.

Method (root over SSH, David present — RUL-027 lockout class):
1. `sqlite3 marketsquare.db ".backup /var/backups/marketsquare/<db>.pre-reboot-<ts>"` + integrity_check
2. `apt-get update && apt-get -y upgrade` (confold), confirm services active + local /health
3. Capture credential fingerprints from `/proc/<MainPID>/environ` (RG-0147 method)
4. `systemctl reboot`; poll https://trustsquare.co/health until 200
5. Re-read fingerprints (must be IDENTICAL — DW-084 class), BIT, /payment/test, smoke, subscription monitor
6. Append the row below.

| date (SAST) | kind | kernel before -> after | pkgs upgraded | downtime | reboot_required after | fingerprints pre==post | verified how | ref |
|---|---|---|---|---|---|---|---|---|
| 2026-09-02 18:47 | REBOOT | 6.8.0-117 -> 6.8.0-138 | 37 | 34 s (521 at t+26s, 200 at t+34s) | absent | yes (6/6: ANTHROPIC, MS_API, MS_DEPLOY_TOKEN, CF_CACHE, PAYSTACK, RESEND) | root SSH: uname -r, no /var/run/reboot-required, 0 upgradable; public: /health ok 1.3.1, /payment/test ok+paystack_connected, BIT 8/8, root 200 in 0.29s; smoke ALL PASS; subs 35 UP/15 HELD/1 PLANNED, 0 issues. DB backup marketsquare.db.pre-reboot-20260902-164548 integrity ok. Uptime before: 97 d. | DW-085 |
| 2026-10-18 15:55 | REBOOT | 6.8.0-139 -> 6.8.0-147 | 22 | ~33 s (000/521/502 until 200 at t+33s) | absent | yes (7/7: ANTHROPIC, MS_DEPLOY_TOKEN, CF_CACHE, PAYSTACK secret+webhook, RESEND, MS_ADMIN) | root SSH: uname -r 6.8.0-147, no /var/run/reboot-required, 0 upgradable, no failed units, every pre-reboot service back (polkit is on-demand), ports 8000/8001/8002/5001 listening, docker overpass-sa healthy + n8n up; DB integrity ok, 146 live listings pre and post; public /health 200; rendered Home in David's Chrome: app started, 151 listings, category counts correct. DB backup marketsquare.db.pre-reboot-20261018-135137 integrity ok. ssh.socket enabled (lock-out check). Uptime before: 23 d -- an unlogged reboot on 25 Sep 01:30 (kernel -139) sat between the two rows. | David, 18 Oct 2026: 'Please do the restart Claude' (RG-0246 red at 46 days) |
