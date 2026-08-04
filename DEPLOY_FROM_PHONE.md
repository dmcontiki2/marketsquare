# Deploying from your phone

**David's ask, 5 Aug 2026:** *"If a tester tells me there are fixes reported which they want
to verify as fixed, and I am at work, I want to deploy from my phone and they can verify 10
minutes later."*

This works today. It needed no new infrastructure, because the server already pulls the
`deploy` ref on a timer — **publishing that ref IS the deploy** (ONE_DEPLOY.md). Your phone
only has to move a pointer, and GitHub can do that from a browser.

---

## The two steps

### 1. At the keyboard, before you leave — arm it

```powershell
.\arm_phone_deploy.bat
```

The `.\` is required — PowerShell will not run a script from the current folder without it.
The message argument is **optional**; leave it off and it stamps the date and time. If you
want your own, quote it: `.\arm_phone_deploy.bat "dead-click fixes + wishlist badge"`.

Runs autobump, folds the changelog and status fragments, then **every gate in strict mode**
— the pre-deploy scan plus the tripwire suites. If anything is red it stops and commits
nothing. If everything is green it commits and pushes **`main` only**.

`main` is a mirror. Pushing it deploys nothing. Nothing is live yet.

### 2. From your phone — publish

Open this (bookmark it / add to home screen):

**`https://github.com/dmcontiki2/marketsquare/compare/deploy...main?expand=1`**

Then: **Create pull request** → **Merge pull request** → **Confirm**. Three taps.

That moves the `deploy` ref. The server's timer picks it up within about two minutes.

---

## What happens without you

The server does the rest, and this is why it is safe to do blind:

1. Pulls the new `deploy` commit
2. Snapshots the current live files to `.deploy-backups/<timestamp>/`
3. Copies only what the manifest allows — never touches the database, `.env` or uploads
4. Bumps the cache-buster so browsers actually get the new build
5. Restarts and **health-checks**
6. **If the health check fails it restores the snapshot and restarts again** — the site
   comes back on the old build by itself, without you
7. Purges the CDN, runs any one-time migration

**Timeline:** tap at 10:00, live by ~10:02, testers verifying by ~10:05.

## Why the gates moved

`deploy_marketsquare.bat` runs the gates in *warn* mode — a red tripwire prints `!!` and the
deploy continues, which is fine when you are sitting there reading it. You will not be
reading it from a train. So `arm_phone_deploy.bat` sets `PREDEPLOY_MODE=strict` and refuses
to commit at all if a gate is red. **The check moves to the moment you can still do something
about it.**

## Checking it landed, from the phone

- `https://trustsquare.co/health` → `{"status":"ok",...}`
- Your dashboard's session badge updates after the deploy carries `STATUS.md`

## If something is wrong

You do not need to do anything — the server rolls itself back on a failed health check. If
the site is up but the fix is wrong, the safest phone action is nothing: leave it, and let
it be fixed properly at a keyboard. Never try to hand-edit from a phone.

## What this does NOT do

It does not commit for you. If the fixes are only on your disk, uncommitted, the phone has
nothing to publish — so `arm_phone_deploy.bat` has to run before you leave. Making that
automatic (a scheduled arm) is possible but deliberately not built: an unattended commit of
whatever happens to be in the working tree is how you ship half-finished work by accident.
