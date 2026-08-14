## 2026-08-14 — DRIFT-CACHEBUST-1: the deploy engine was never stalled

`check_deploy_drift.py` compared the md5 of each local manifest file against the copy served on the
box. But `server_deploy.sh` rewrites the served `index.html` in place, bumping `?v=N` monotonically so
browsers fetch each new build. The served file therefore differs from its source by design, and the two
files carrying those references — `marketsquare.html` → `index.html` and `dashboard.server.html` →
`dashboard.html` — reported permanent phantom drift that no deploy could ever clear.

Fixed by normalising `?v=[0-9]+` → `?v=N` on both sides before hashing (locally in `_md5`, remotely via
`sed` before `md5sum`), the same class of fix as DRIFT-CRLF-1. Real staleness still reports.

Locked as **RG-0072**. Ledger re-run after the change: no regressions.
