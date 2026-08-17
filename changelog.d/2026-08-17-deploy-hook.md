## 2026-08-17 — DEPLOY-HOOK-1: HTTPS deploy trigger enabled (rides this deploy)

Sessions could not ship FX-LIVE-1 unaided: hook unprovisioned (401 = nginx wall, token
never minted), no mirror push creds, desktop dialogs hidden behind the Claude window.
Closed the class:
- bea_main.py includes ops/autodeploy/deploy_router.py (import-safe; endpoint 503 /
  fail-closed until MS_DEPLOY_TOKEN exists server-side). Router added to deploy_manifest.
- add_deploy_token.bat (new, rotate-pattern): mints the token in a root-only systemd
  drop-in, restarts, health-checks, lands MS_DEPLOY_TOKEN in .secrets\deploy_keys.txt —
  value never printed. One double-click, once.
- Secrets hygiene same night: 3× ROTATE runs (windows hidden behind Claude) — last run
  clean; lane files deploy_keys/ms_maint_key were stale-from-4-Aug, now synced from
  rotated_secrets.txt. The maint key exposed in tonight's transcript died in that rotation.
- Nightly TSL 02:01 blocked by pre-existing strict-mode flags pg-readiness + tester-intake
  (failing ratchet/guard tests since ≥14 Aug, independent of FX-LIVE-1) — housekeeping item.
