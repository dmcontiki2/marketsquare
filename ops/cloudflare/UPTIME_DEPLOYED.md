# EXTERNAL UPTIME WATCHER — deploy marker

**UPTIME-EXTERNAL-1 · ledger RG-0138 · closes OPEN_LOOPS L8 · DAVID_QUEUE D4**

```
DEPLOYED_ON: 2026-08-28
LAST_HEARTBEAT: 2026-08-29
```

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

## Keeping this marker honest

RG-0138 fails if `LAST_HEARTBEAT` goes more than **7 days** stale, which catches a Worker that
dies quietly. That check is only as good as this date, so roll it forward when a heartbeat is
actually seen — never on the assumption that one was sent.
