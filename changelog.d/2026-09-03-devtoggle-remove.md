## 2026-09-03 — DEVTOGGLE-REMOVE-1: dev DEMO/BOTH/LIVE toggle removed from the live app

David saw the dev-only demo/both/live panel on the phone live app. Both "REMOVE BEFORE LAUNCH"
controls (fixed top-right `demo-toggle-panel` and the hero `dev-mode-toggle` pill) are deleted
from marketsquare.html. Cause: the panel's inline style had `display:none` followed by
`display:flex`, so it painted until JS hid it, and stayed painted under `?demo=1`/devSetMode.
JS left in place (null-guarded). Ledger RG-0255 asserts the markup is absent from repo and served index.
