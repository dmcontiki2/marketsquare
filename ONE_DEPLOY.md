# ONE DEPLOY — the only way MarketSquare code goes live (2 Aug 2026)

**Deploying = publishing a commit to the `deploy` ref.** Nothing else ships code.
Locked by regression-ledger **RG-0023**; the media lane by **RG-0021**.

## The one deploy (any of these buttons — same engine underneath)

| You are…                | Do this                                             |
|-------------------------|-----------------------------------------------------|
| David at the PC         | double-click **deploy_marketsquare.bat** (now a thin gated wrapper) or **release.bat** |
| /ship, /TSL, /start     | they run deploy_marketsquare.bat → same wrapper     |
| Any session w/ push auth| `git push origin HEAD:deploy` (or `python deploy_web.py`) — **gated by the `pre-push` hook**, see below |
| HTTPS-only agent        | `POST /admin/deploy` with `X-Deploy-Token` (enable per ops/autodeploy/deploy_router.py) |

The wrapper: git_unlock → autobump (child ?v= refs) → predeploy_check + CM/DB
gate + deploy lock → commit → push `main` (backup) → push `deploy` (THE deploy)
→ waits, then md5-verifies local vs live (check_deploy_drift.py).

**Every lane is gated, including the raw push (DEPLOY-GATE-ALL-1, 20 Sep 2026).**
A `pre-push` hook fires on `refs/heads/deploy` and only that ref, runs
`predeploy_check.py` with `PREDEPLOY_MODE=strict` set *before* the scan, and
**refuses the push on a DANGER verdict**. Pushing `main` is untouched — it
deploys nothing. Install or repair it with:

    python3 scripts/install_git_hooks.py          # idempotent
    python3 scripts/install_git_hooks.py --check  # exit 1 if not armed

Deliberate override, when you mean it (both are visible in shell history):

    PREDEPLOY_MODE=warn git push origin HEAD:deploy
    git push --no-verify origin HEAD:deploy

Why it exists: on **18 Sep 2026 a deploy rode while the regression board read
REGRESSION**, because this lane ran no gate — RG-0381 had fixed only the lane a
human double-clicks. Git hooks are **local to a clone and never carried by git**,
so re-run the installer after a fresh clone; `RG-0422` goes red if it is missing.

The engine (ops/autodeploy/server_deploy.sh, on the server, every ~2 min):
manifest allowlist copy (never deletes; never touches DB/.env/uploads/
demo_sellers.json) → **monotonic** cache-buster (an older number can never land
on live) → restart → nginx reload → health check → **auto-rollback on failure**
→ CDN purge → post_deploy hook (idempotent seed + one-time `migrations/*.py`).

- Add a deployable file → one line in `ops/autodeploy/deploy_manifest.txt`.
- One-time server change → drop `migrations/NNN_name.py` (see migrations/README.md).
- Watch a deploy: `ssh root@178.104.73.239 "tail -f /var/log/marketsquare-deploy.log"`

## The media lane (not a second engine)

Git ignores binaries, so photos/videos/PDF/n8n templates can't ride the mirror.
**media_push.bat** ships them, hash-gated (only changed files upload). It never
carries code — RG-0023 trips red if code appears in any other .bat's scp.

## Rollback — one story

Bad deploy that fails health → **server rolls itself back automatically**.
Bad deploy that is healthy-but-wrong → `git revert <commit>` then release again.
By hand (break-glass): snapshots live in `/var/www/marketsquare/.deploy-backups/<ts>/`
→ `cp -a <snapshot>/<file> /var/www/marketsquare/<file> && systemctl restart marketsquare`.

## Break-glass: GitHub or the timer is down

This is a RECOVERY PROCEDURE, not a second deploy path:
1. `systemctl status marketsquare-deploy.timer` — restart it if stopped.
2. Timer fine but no pull? `ssh` in and run
   `/opt/marketsquare-src/ops/autodeploy/server_deploy.sh --force`.
3. GitHub itself down and the fix cannot wait: copy the changed file(s) by hand
   (scp), then — the moment GitHub returns — commit + release the SAME change so
   the ref catches up and the ledger stays truthful.
The old 44KB copy engine is preserved at
`deploy_marketsquare.bat.bak-onedeploy-20260802` for archaeology only.

## After launch: how an agent deploys fixes

1. Agent fixes in the repo (heredoc writes, py_compile, .bak first).
2. Runs the gates as machinery: predeploy_check, tsl_gate, regression ledger
   (green before AND after — no entry, not done).
3. Auto-ship class only (LOW, behaviour-neutral, no Gate 1/2: payments, Tuppence
   ledger, EULA, KYC, compliance-gated flags). Anything gated → queue for David's
   one-word "ship".
4. Publishes via push (deploy-scoped token) or `POST /admin/deploy` (token) —
   the server does the deploying; the agent never needs ssh.
5. Verifies off the live site (/health, smoke, ledger live checks), writes
   CHANGELOG + ledger entry, notifies David flat: done / failed / rolled back.
Safety net under all of it: the engine's health-check auto-rollback.

## Retired 2 Aug 2026 (DEPLOY-CONSOLIDATION-1)

10 scp paths → `_to_delete/retired-deploy-bats-20260802/` (README inside maps
each to its replacement). Restore any = ledger RG-0023 goes red.
