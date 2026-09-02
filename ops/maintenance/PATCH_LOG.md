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
