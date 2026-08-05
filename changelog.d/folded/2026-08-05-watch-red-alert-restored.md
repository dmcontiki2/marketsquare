## 2026-08-05 — DW-016 CLOSED: watch RED-alert email path restored

- David ran fix_watch_alerts.bat (one-shot, now retired): key copied to /etc/marketsquare/resend.watch.conf, 0640 root:msdeploy.
- Watch task (trustsquare-daily-watch) prompt updated: RED email now sends from the server via the msdeploy-readable copy; broken path re-opens DW-016 loudly.
- Proven live: test email accepted by Resend (id 77de9576), delivered to dmcontiki2@gmail.com.
