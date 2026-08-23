## 2026-08-23 — post-deploy verification (attended)

Deploy ref published by David (74ab420); probed: deploy==HEAD, /health 200, ledger
green 0 REGRESSED. RG-0154 and RG-0158 promoted to LOCKED. DW-058 substance closed
(commits in, deploy live, server runs new code) — formal close on next host-side
deploy_drift clean read. DW-061 will re-alert on this deploy; needs on-box
--update-baseline. 12 ledger entries honestly open.
