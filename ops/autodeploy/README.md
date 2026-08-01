# MarketSquare auto-deploy (Phase 3)

Server-side, git-driven deploy that removes "a human runs `deploy_marketsquare.bat`"
as the bottleneck. The box pulls the latest source from the GitHub mirror and
deploys it — with a health check and automatic rollback — on its own.

## The pieces

| File | Runs on | What it does |
|------|---------|--------------|
| `server_deploy.sh` | server | The engine. Pulls the tracked ref, places files (allowlist, never deletes), bumps the cache-buster, restarts the app, reloads nginx, purges the CDN, health-checks, and **auto-rolls-back** on failure. |
| `deploy_manifest.txt` | server | The repo→server file map (same renames the `.bat` does: `marketsquare.html`→`index.html`, `bea_main.py`→`main.py`, `ms.js`→`static/ms.js`, …). Kept as data so it stays in step with the `.bat`. |
| `marketsquare-deploy.service` / `.timer` | server | systemd oneshot + a 2-minute poll timer. Each tick is a no-op unless the tracked ref advanced. |
| `install_autodeploy.sh` | server | One-time installer. Clones the source, installs the units, enables the timer. Idempotent. |
| `deploy_router.py` | server (optional) | An authenticated `POST /admin/deploy` HTTPS trigger for sessions that can only reach the box over 443. **Off unless `MS_DEPLOY_TOKEN` is set.** |
| `../../activate_autodeploy.bat` | David's PC | The single activation double-click (pushes the project, runs the installer). |
| `../../release.bat` | David's PC | "Go live": publishes the current commit to the deploy ref. |
| `../../deploy_web.py` | any session | Triggers a deploy over the web (hook → git-push → honest failure) and verifies it. |

## How a deploy happens

1. Someone publishes the **deploy ref** (default: the `deploy` branch) on the mirror
   — `release.bat`, `git push origin HEAD:deploy`, or `deploy_web.py`.
2. Within ≤2 minutes the timer fires `server_deploy.sh`, which sees `origin/deploy`
   advanced and deploys that exact commit.
3. If the app fails its health check, the previous release is restored automatically
   and the bad commit is **not** recorded as deployed.

Nothing auto-ships on ordinary commits to `main` — deploys are the explicit act of
publishing the deploy ref. To make *every* push to `main` deploy (full GitOps), set
`MS_DEPLOY_REF=main` in `marketsquare-deploy.service` and `daemon-reload`. Trade-off
in `ACTIVATION.md`.

## Config (env in `marketsquare-deploy.service`)

All optional; defaults shown. `MS_DEPLOY_REF` (deploy) · `MS_SRC`
(/opt/marketsquare-src) · `MS_LIVE` (/var/www/marketsquare) · `MS_SERVICES`
(marketsquare) · `MS_HEALTH_URL` (http://localhost:8000/health) · `MS_PURGE_URL`
(http://localhost:8000/admin/purge-cache) · `MS_ADMIN_KEY` (unset) · `MS_KEEP_BACKUPS`
(10).

## Operate

```bash
# is it armed?
systemctl list-timers marketsquare-deploy.timer
# what happened on the last deploys?
tail -n 50 /var/log/marketsquare-deploy.log
# force a check now (bypasses the "unchanged ref" short-circuit)
/opt/marketsquare-src/ops/autodeploy/server_deploy.sh --force
# turn it off
systemctl disable --now marketsquare-deploy.timer
```

## Rollback snapshots

Every changed deploy first copies the files it is about to overwrite into
`/var/www/marketsquare/.deploy-backups/<timestamp>/`. The last `MS_KEEP_BACKUPS`
(default 10) are kept. Manual restore:

```bash
cp -a /var/www/marketsquare/.deploy-backups/<ts>/<file> /var/www/marketsquare/<file>
systemctl restart marketsquare
```

## Safety notes

- Placement is an **allowlist copy** — only files in the manifest are written. The
  live SQLite DB, `.env`, `demo_sellers.json`, uploads and anything else on the box
  are never touched, and nothing is ever deleted.
- A `flock` means two deploys can never overlap.
- No secret lives in these files or in the repo. The optional deploy token lives
  only on the server. The SSH key stays on David's PC.
- Redis is a standalone cache/rate-limit service and is intentionally **not**
  restarted on a code deploy (that would flush the cache for no reason); the BEA's
  background jobs are in-process threads, so restarting `marketsquare` restarts them.
