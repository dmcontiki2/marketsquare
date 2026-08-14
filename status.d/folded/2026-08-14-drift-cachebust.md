- **DRIFT-CACHEBUST-1 (14 Aug 2026) — the "stalled deploy engine" was never stalled; the drift
  monitor could not go clean BY CONSTRUCTION.** Every release logged
  `DEPLOY DRIFT: 2 file(s) local-ahead of live - run /ship: dashboard.html, marketsquare.html`,
  waited out two server ticks, and reported it again — a scheduled session was booked to diagnose
  a stall that does not exist. Cause: `ops/autodeploy/server_deploy.sh:170-186` rewrites the SERVED
  `index.html` in place (`sed -i`, monotonic `?v=` bump) so browsers actually fetch each new build —
  the served file is DESIGNED to differ from its source. `check_deploy_drift.py` md5'd local against
  served, so the only two manifest files carrying `?v=` references (marketsquare.html→index.html,
  8 refs; dashboard.server.html→dashboard.html, 6) reported drift on every deploy, for ever, and no
  amount of re-deploying could clear it. Fixed at class level: `?v=[0-9]+` → `?v=N` is normalised on
  BOTH sides before hashing — locally in `_md5`, and on the box via `sed` piped to `md5sum` — exactly
  as DRIFT-CRLF-1 normalises line endings. Proven with a two-file stand-in differing ONLY in the bump:
  raw md5 differed, normalised md5 matched. Genuine staleness still reports; only the bump is
  neutralised. Locked as **RG-0072**; full ledger re-run after the change: no regressions.
- **Separately, the missing 18 Kenya listings are NOT a seeder fault.** Release 24f6556 logged
  `0 deploy target(s) changed` (it carried only AI-accountability files, none in the manifest), so the
  engine placed nothing and the `post_deploy` seed hook never ran. All 24 tiers have complete photo
  sets on disk and on the server — a simulation of the seeder's discovery step finds every one. The
  seed lands the moment a deploy actually places a manifest file.
