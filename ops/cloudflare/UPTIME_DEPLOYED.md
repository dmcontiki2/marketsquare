# EXTERNAL UPTIME WATCHER — deploy marker

**UPTIME-EXTERNAL-1 · ledger RG-0138 · closes OPEN_LOOPS L8 · DAVID_QUEUE D4**

```
DEPLOYED_ON: 2026-08-28
LAST_HEARTBEAT: 2026-09-05
```

*Rolled forward 5 Sep 2026 on witnessed mail, not assumption: heartbeats read back out of Gmail for
3, 4 and 5 Sep (today's at 06:00:26Z, "UP — 200 in 39ms"). It had sat at 2026-08-29 for seven days
while the mail was arriving daily — nobody was rolling it, which is exactly the hand-maintained-marker
weakness DW-098 fixed on the liveness side. This half stays hand-recorded by design (only a witnessed
INBOX read proves the alert half), so it will drift again unless a session looks.*

## What is deployed

- Worker **`trustsquare-uptime`**, Cloudflare Workers free plan, deployed by David
  **28 Aug 2026 11:2x UTC** — the day before soft-public, after six days undeployed.
- URL: `https://trustsquare-uptime.dmcontiki2.workers.dev`
- Version ID at first deploy: `896f82f8-aa0d-4b65-a6ed-62ce843704b7`
- Cron: `*/5 * * * *` · KV `UPTIME_STATE` = `d8a9733e29ca47c290208855cbbef690`
- Probes `https://trustsquare.co/health`, requires **200 AND `{"status":"ok"}`**
- Alerts `dmcontiki2@gmail.com` from `hello@mail.trustsquare.co` (the VERIFIED domain —
  the root domain is refused, the RESEND-FROM-1 lesson of 7 Aug 2026)

## PROBED 28 Aug 2026 11:31:54 UTC

```json
{ "ok": true, "reason": "200 in 191ms", "ms": 191,
  "consecutiveFails": 0, "down": false, "actions": [], "kv": true }
```

Probe half: **PROVEN.** It reaches the site from Cloudflare's edge, reads the JSON body rather
than trusting the status code, and its KV state store binds.

## The alert half is NOT yet proven — and the distinction is the point

An earlier probe at **11:26:33 UTC** returned
`"actions": ["heartbeat mail FAILED: RESEND_API_KEY not bound"]`. The first `wrangler secret put`
had created a placeholder Worker which `wrangler deploy` then replaced, taking the secret with it;
the deploy output's binding table showed KV and seven variables and **no secret**, which is what
gave it away. Re-running `secret put` against the real Worker fixed it, and `actions` is now empty.

**Empty `actions` means nothing errored — it does not mean an email arrived.** No successful send
has been observed from this Worker. Recorded as UNPROVEN rather than green, because a monitor
believed to be working and silently unable to deliver is worse than no monitor: that is exactly
the fault that left this site unwatched from 22–28 Aug (DW-076 / RG-0201).

**What settles it, at no further cost:** the daily heartbeat fires at **06:00 UTC (08:00 SAST)**,
so the first one lands on **soft-launch morning, Sat 29 Aug**. If a heartbeat email is in David's
inbox that morning, the alert path is proven end-to-end and this file's LAST_HEARTBEAT should be
rolled forward. **If nothing arrives by ~08:30 SAST, the alert path is still dead and must be
treated as such** — do not assume it works because the deploy succeeded.

## PROVEN 29 Aug 2026 — the heartbeat ARRIVED

**The alert half is no longer unproven.** PROBED in David's Gmail inbox by the 29 Aug third-party
sweep: message from `hello@mail.trustsquare.co`, subject *"TrustSquare uptime watcher — daily
heartbeat"*, received **2026-08-29T06:00:22Z**, body reading *"UP — 200 in 391ms"*. The Worker was
re-probed the same run at 08:36 UTC: `ok:true, 200 in 190ms, kv:true, consecutiveFails:0`. The
path Worker → Resend → inbox is proven end-to-end on soft-launch morning, exactly as this file
said it would or would not be. LAST_HEARTBEAT rolled forward on that evidence, not on assumption.

## 5 Sep 2026 — the Worker gained an EAR: `POST /alert` (ALERT-OFFORIGIN-1, DW-097)

Until today this Worker could only speak when *it* noticed something. The daily watch had no
way to ask it for anything, so the watch's own RED alert was one SSH command to the origin —
and on **26 Aug and again 5 Sep** the origin was unreachable, which is *why* the verdict was
RED, so no alarm could be raised at all. The alarm shared a transport with the fault it reports.

Worth being clear about what did NOT cover this: **this Worker probes `/health`, which was green
on both days.** An origin that serves the public perfectly while refusing SSH is invisible to it
by design. Having a second vantage was never the same thing as having a reachable alarm.

```
POST https://trustsquare-uptime.dmcontiki2.workers.dev/alert
Authorization: Bearer <ALERT_INGEST_KEY>        # Worker secret; local copy .secrets/watch_alert_key.txt
{"level":"RED","reason":"...","lines":["..."],"dry":false}
```

- **The recipient is NEVER taken from the request** — it is `ALERT_TO` in the config. A leaked
  ingest key can wake David; it can never mail anybody else.
- Subject and lines are HTML-escaped and length-capped; `level` is clamped to RED/AMBER/TEST.
- KV rate limit **12/hour**, and it **fails open** on purpose: a limiter that can silence an
  outage alarm is worse than the abuse it prevents.
- **`dry:true`** authenticates and validates and sends nothing — which is how ledger **RG-0279**
  probes this path on *every run*, for free. An alert path exercised only by a real emergency is
  an alert path nobody knows is broken until the emergency.
- Callers use `scripts/watch_alert.py` (Worker lane first, the old ssh lane as fallback only).
**PROVEN 5 Sep 2026 07:52 UTC — an alert reached the inbox without the origin.** Deployed via the
host queue (rc=0, 09:52:08 SAST). Dry probe: `would_send:true, resend_key_bound:true, kv:true`. Then a
real send with `--no-fallback`, so the ssh lane was not even available to it: Resend id
`e83298f3-2b98-4673-8cad-080dfb0e883f`, and the message was read back out of Gmail at **07:52:27Z**,
one second later, from `hello@mail.trustsquare.co`. Resend *accepting* is not delivery — the inbox read
is the evidence, which is this file's own 28-29 Aug lesson applied again.

- Redeploy: `deploy_uptime_worker.bat` — **deploy FIRST, `secret put` SECOND**, the 28 Aug lesson
  recorded above.

## Keeping this marker honest

**Superseded 5 Sep 2026 (WATCHER-LIVE-PROBE-1, DW-098) — read this before trusting the date below.**
RG-0138 used to FAIL when `LAST_HEARTBEAT` went more than 7 days stale. It no longer reads this
date for liveness at all: it now GETs the Worker's public endpoint, requires a real check result
with KV bound and a timestamp under 15 minutes old, and reports UNVERIFIED (never RED) if the
machine running it cannot reach the net. The old check was a READ wearing a PROBE's colour — it
answered "did somebody type a date recently", not "is the watcher running" — and it was one day
from going red by arithmetic alone.

`LAST_HEARTBEAT` survives as **INFO only**: it records the day a heartbeat *mail* was witnessed,
which is the ALERT half (see `/alert` above), not liveness. Roll it forward only when a heartbeat
email is actually seen — never on the assumption that one was sent.
