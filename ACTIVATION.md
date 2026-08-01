# Phase 3 — Automated Deploy · ACTIVATION

**What this gives you:** the Hetzner box deploys MarketSquare *itself*, from git,
with a health check and automatic rollback. No one runs `deploy_marketsquare.bat`
anymore. "Go live" becomes one push instead of an 8-step console you have to watch.

**Built:** 26 Jul 2026 (Phase 3 of the Launch-Hardening program). Files live in
`ops/autodeploy/` plus `activate_autodeploy.bat`, `release.bat`, `deploy_web.py`.

---

## The single manual step (do this once)

> **Double-click `activate_autodeploy.bat`.**

That's it. It commits + pushes your project, copies the installer to the server,
and runs it. The installer clones the source to `/opt/marketsquare-src`, installs a
systemd timer that polls the mirror every 2 minutes, and enables it. It uses the SSH
key already on your PC — no secret ever leaves your machine.

It deploys nothing on its own. It just arms the mechanism.

*(If you prefer to do it by hand: `scp ops/autodeploy/install_autodeploy.sh
root@178.104.73.239:/tmp/` then `ssh root@178.104.73.239 "bash /tmp/install_autodeploy.sh"`.)*

---

## How you deploy from now on

**From your PC — double-click `release.bat`.** It publishes your current commit to
the `deploy` ref; the server deploys it within ~2 minutes, health-checks it, and
rolls back automatically if the app doesn't come up. This replaces the whole
`deploy_marketsquare.bat` run.

**From any Claude/Cowork session — `python deploy_web.py`.** It triggers the deploy
over the web and verifies the live site. (See "Can a cloud session deploy on its
own?" below — there's one honest caveat.)

Ordinary commits to `main` do **not** auto-ship. A deploy is the deliberate act of
publishing the `deploy` ref. That's the safe default, chosen on purpose given the
history of breakage — you decide when something goes live.

> **Want zero-touch instead?** If you'd rather have *every* push to `main` deploy
> automatically (full GitOps), edit `/etc/systemd/system/marketsquare-deploy.service`,
> set `Environment=MS_DEPLOY_REF=main`, then `systemctl daemon-reload`. More
> convenient, less of a safety gate — your call.

---

## Test it end-to-end (5 minutes, safe)

1. **Arm it:** double-click `activate_autodeploy.bat`. Expect it to end with
   "AUTO-DEPLOY INSTALLED".
2. **Confirm the timer is live:**
   ```
   ssh root@178.104.73.239 "systemctl list-timers marketsquare-deploy.timer"
   ```
   You should see it scheduled to fire in <2 min.
3. **Make a tiny, visible change** (e.g. bump a comment in `marketsquare.html`),
   commit it, then double-click `release.bat`.
4. **Watch the deploy happen by itself:**
   ```
   ssh root@178.104.73.239 "tail -f /var/log/marketsquare-deploy.log"
   ```
   Expect: `DEPLOY start …` → `placed N file(s)` → `restarted service: marketsquare`
   → `DEPLOY OK · now live at <sha> · health ok`.
5. **Verify live:** open <https://trustsquare.co/health> (should be `{"status":"ok"…}`)
   and hard-refresh <https://trustsquare.co> to see your change.

**Prove the safety net (optional):** publish a commit you know is broken (e.g. a
syntax error in `bea_main.py`). The log will show `deploy UNHEALTHY … rolling back`
→ `ROLLBACK OK`, and the site stays on the previous good release. Then fix and
`release.bat` again.

---

## Rollback

You rarely need to do this by hand — a failed health check rolls back automatically.
If you ever want to force it:

- **Re-publish the last good commit:** `git push origin <good-sha>:deploy --force`
  (or check out the last good commit and run `release.bat`). The server redeploys it.
- **Restore files directly on the box** from the snapshot taken before each deploy:
  ```
  ssh root@178.104.73.239
  ls /var/www/marketsquare/.deploy-backups/            # timestamped snapshots
  cp -a /var/www/marketsquare/.deploy-backups/<ts>/<file> /var/www/marketsquare/<file>
  systemctl restart marketsquare
  ```
- **Turn the whole thing off:**
  `ssh root@178.104.73.239 "systemctl disable --now marketsquare-deploy.timer"`.
  You're back to running `deploy_marketsquare.bat` by hand; nothing else changes.

---

## Can a cloud session deploy *on its own*, unattended? (the honest caveat)

Partly — and here's exactly where the line is, so you can decide.

- A cloud/Cowork session **can read** the mirror and **can reach the server over
  HTTPS**. It **cannot** SSH to the box (port 22 blocked, no key) and — verified in
  this build — a scheduled cloud session **cannot push to the GitHub mirror** (the
  sandbox git proxy returns 403 on push; read/clone work fine).
- So a scheduled, unattended session has no way to *trigger* a deploy **unless you
  grant it one channel.** Two clean options, either one is a one-time setup:
  1. **Enable the HTTPS hook.** Add the 2 include lines to `bea_main.py` (see
     `ops/autodeploy/deploy_router.py`), set a `MS_DEPLOY_TOKEN` on the server, and
     make that token available to the sessions that should deploy. Then
     `deploy_web.py` deploys instantly over 443. *(A token is unavoidable for a safe
     internet-facing trigger; per your own rule it stays only on the server and in
     the session env — never in the repo or chat.)*
  2. **Grant the session push access** to the mirror's `deploy` ref. Then
     `deploy_web.py` just pushes and the poller does the rest — no token needed.
- **Without either**, the mechanism is still fully working and hands-free for *you*:
  `release.bat` (one double-click) publishes, and the server deploys itself. What's
  not yet possible is a *scheduled, human-absent* session deploying with zero prior
  grant — and that's a deliberate safety boundary, not a bug. Pick option 1 or 2
  when you want to cross it.

---

## What it does and doesn't cover

**Covers** the code + core-asset deploy: the buyer app, admin, BEA (`main.py`),
backend modules, `ms.js`/`ms.css`, service worker, the adventures maps, legal pages,
the dashboard docs, and the demo/wonders JSON — the same file map the `.bat` uses
(`ops/autodeploy/deploy_manifest.txt`). It bumps the cache-buster, restarts the app,
reloads nginx, purges the CDN, and health-checks.

**Does not** replicate the `.bat`'s one-shot DB fixes, seed scripts
(`seed_super_global.py`, etc.) or the heavy media-tree syncs (super photos, videos,
brand photos, legal-card PNGs). Those remain the `.bat`'s job for first-time seeding.
Add a file to `deploy_manifest.txt` any time you want the auto-deploy to ship it too.

**Left untouched on purpose:** `deploy_marketsquare.bat` still works exactly as
before as your full/first-time deploy and asset-seeder. This adds a second, safer,
git-driven path — it doesn't remove the old one. (The `.bat`'s known
false-`[OK]`-on-failure quirk, noted in the hardening doc, is *not* changed here;
best fixed in an attended session since it can't be tested from the cloud.)
