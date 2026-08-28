# EXTERNAL UPTIME WATCHER — runbook

**UPTIME-EXTERNAL-1 · written 22 Aug 2026 · ledger RG-0138 · closes OPEN_LOOPS L8**

## Why this exists

Every instrument watching trustsquare.co today runs **on the box it is watching** (ops sweep,
BIT, subscription monitor, the 01:30 cron) or **on David's PC** (the 06:30 daily watch). So a
dead server or a closed laptop is a blind day *by construction* — it already happened on 6 Aug.
This watcher sits on Cloudflare's edge and owes nothing to either.

## Why a Cloudflare Worker and not a monitoring vendor

Technical decision, taken under RUL-037 rather than handed over as a vendor menu:

| | |
|---|---|
| **No new vendor** | Cloudflare already carries DNS, CDN, R2 and the inbound email worker |
| **No new money** | Cron triggers + 100k req/day are on the free plan; 5-min cron = 288/day |
| **Right vantage** | Edge-hosted, independent of the Hetzner box *and* of any desktop |
| **No lock-in** | ~180 lines of plain JS; the probe is a `fetch` of `/health` |

Rejected: paid uptime SaaS (money + a vendor decision for a thing we can do free), a systemd
timer on the box (self-referential — it dies with the thing it watches), and GitHub Actions
(a 5-min cron exceeds the free minutes on a private repo, so it would start billing).

## What it does

- **Every 5 minutes** — `GET https://trustsquare.co/health`, expects `200` **and**
  `{"status":"ok"}`. A 200 with a sick body still counts as down; that distinction is the
  whole reason it reads the JSON.
- **Two consecutive failures** — emails **TrustSquare is DOWN** with the reason. At most one
  repeat every 30 minutes, so an outage does not become a pager storm.
- **Recovery** — emails **BACK UP** once, with how long it was down.
- **Daily at 06:00 UTC** — emails a **heartbeat**. This is the part people leave out: without
  it, "no email" means either *all is well* or *the monitor died in July*.

## Deploy — three commands, once

Do this **after** the secret rotation (`ROTATE_SECRETS.bat`) so the fresh Resend key goes in,
never the burnt one.

**Run these in PowerShell on David's PC, not on the server.** Use `npx wrangler`, never bare
`wrangler` — it is not installed globally on this machine, and the bare form cost a round trip
on launch eve, 28 Aug 2026. `cloudflare_email_worker/README.md` already had it right.

```powershell
cd C:\Users\David\Projects\MarketSquare

# 1. state store (free tier). Copy the printed id into uptime_wrangler.toml.
npx wrangler kv namespace create UPTIME_STATE

# 2. the alert credential — prompts, never echoes, never touches git
npx wrangler secret put RESEND_API_KEY --config ops/cloudflare/uptime_wrangler.toml

# 3. ship it
npx wrangler deploy --config ops/cloudflare/uptime_wrangler.toml
```

## Prove it works (do not skip — an unproven monitor is not a monitor)

```bash
# runs one check immediately and prints the state
curl https://trustsquare-uptime.<your-subdomain>.workers.dev/
```
Expect `"ok": true` and `"kv": true`. Then, to prove the **alert path** rather than just the
probe, temporarily set `TARGET_URL` to `https://trustsquare.co/definitely-not-a-page`,
redeploy, wait two cron ticks, confirm the DOWN email arrives, then set it back.

## Record the proof

Write `ops/cloudflare/UPTIME_DEPLOYED.md` with these two lines (RG-0138 reads them; the
entry stays red until they exist and stays red if the heartbeat goes more than 7 days stale):

```
DEPLOYED_ON: YYYY-MM-DD
LAST_HEARTBEAT: YYYY-MM-DD
```

## Known limits, stated rather than discovered later

- It watches `/health` only — the app can be up while a *feature* is broken. That is what
  the BIT board and the regression ledger are for; this answers "is the platform reachable".
- Cloudflare cron is best-effort: a tick can be a minute or two late. It is an outage alarm,
  not a latency SLA.
- Alerts ride Resend, which is also one of the things that can break. The heartbeat is what
  catches that: if Resend dies, the heartbeat stops too, and silence past 24 h is the signal.
