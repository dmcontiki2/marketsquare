## 2026-09-18 — DEVICE-NOLAPSE-1: David's access no longer lapses on a timer (RUL-141, RG-0393)

- Fault: the dashboard's Quick Listing frame showed nginx "401 Authorization Required". PROBED from the
  server log: David's laptop Chrome had never been enrolled as a device; he had signed in by password on
  17 Sep 04:33 UTC; the 8-hour admin token lapsed and the Orchestrator gate refused the frame.
- Fix (bea_main.py): device passes are minted without an expiry and judged only by revocation; the
  ts_device cookie is re-issued for 400 days on every /admin/device-ok and /admin/device-token call; a
  master-password login also enrols that browser; new middleware `_device_renews_admin_token` swaps an
  expired X-Admin-Token for a fresh one when the device pass is valid and returns X-Admin-Token-Renewed.
- dashboard.server.html: a fetch wrapper stores X-Admin-Token-Renewed in sessionStorage.
- Middleware proven on the server's own venv with TestClient: expired token + no device = 401;
  expired token + device (itself carrying an old exp) = 200 and renewed; junk device = 401.
- Locked: regression ledger RG-0393 (fails against the pre-fix file — tested), rulings_check RUL-141,
  RULINGS.md RUL-141, Projects/CLAUDE.md standing rule.
