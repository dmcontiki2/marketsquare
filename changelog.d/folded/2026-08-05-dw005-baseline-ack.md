## 2026-08-05 — DW-005 CLOSED: fea-integrity baseline acked and refreshed

- David confirmed the 3-5 Aug deploys explain the index/ms.js/ms.css byte drift (independently proven: live index == repo modulo ?v= + CF email-obfuscation).
- `fea_integrity_check.py --update-baseline` run as msdeploy; recheck: status ok, zero alerts. Nightly cron re-alerts end.
