- **Evening handoff (morning session, Claude):** DW-023/RG-0029 CLOSED + LOCKED (gate
  live, verified, ledger green at lock time). DW-025: 244/273 images self-hosted;
  /demo-listings fully local; 29 rate-limit stragglers + live demo_sellers.json rewrite
  ride migration 017 run 2 (hardened: 0.5s pacing, backoff, attempt-tracked stand-in
  rung) — ON the deploy ref via the Kenya session's sweep commit 8691602. **Server did
  NOT act on that ref for 10+ min this morning — diagnose the deploy timer/log FIRST
  tonight** (paste in the scheduled task). RG-0063 OPEN, correctly counting 40 sellers
  refs live. **Bat lesson (Claude's error, owned): release.bat does NOT commit — it
  pushes existing HEAD silently; three presses burned. Tonight and henceforth:
  deploy_marketsquare.bat (gates + folds + auto-commits + publishes).** Tonight 17:45:
  scheduled session runs DW-029 rotation (ROTATE_SECRETS.bat + 5 vendor dashboards,
  one-at-a-time install-verify) then finishes DW-025 and locks RG-0063. Also noted for
  the register: /admin/deploy hook now sits behind the reviewer gate (L7 family).
