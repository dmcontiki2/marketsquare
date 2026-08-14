## 2026-08-13 — Maroushka login "connection error" diagnosed + fixed (GATE-TRUTH-1, RG-0066)

Cause: GATE-ENFORCE-2's catch-all turned the gate screen's /admin/login fallthrough into
nginx HTML 401 → every wrong/stale reviewer code showed a fake "Connection error". BEA was
up throughout — not the old June crash class. Fix built (truthful gate messages), ledger
RG-0066 OPEN, rides the deploy-engine revival (DW-042). Her immediate unblock: re-send the
current reviewer code (lane verified live-healthy); 10-min wait if rate-limited (8/10min).
