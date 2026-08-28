## 2026-08-28 — UPTIME-EXTERNAL-1 DEPLOYED: the site is watched from outside itself (RG-0138 LOCKED)

**Both of the day's REDs are closed on the eve of soft-public.** David's queue: 8 open, down from 11
this morning. D2 (Paystack 2FA), D3 (RED-alert key) and D4 (this) all closed today.

Worker **`trustsquare-uptime`** is live on Cloudflare's edge — built 22 Aug, undeployed for six days,
shipped the day before launch. Cron `*/5`, version `896f82f8`, KV `UPTIME_STATE` bound,
`https://trustsquare-uptime.dmcontiki2.workers.dev`. It probes `/health` and requires **200 AND
`{"status":"ok"}`** — a 200 with a sick body still counts as down.

**PROBED 11:31:54 UTC:** `{"ok": true, "reason": "200 in 191ms", "consecutiveFails": 0, "kv": true,
"actions": []}`. This is the first instrument watching trustsquare.co that runs neither on the box
nor on David's desktop — the blind-day-by-construction gap OPEN_LOOPS L8 was opened for on 14 Aug.

**RG-0138 promoted OPEN → LOCKED in the same session it started passing**, per the standing rule: an
entry that prints READY TO LOCK and is left open cannot trip red when it rots.

### The alert half is recorded as UNPROVEN, deliberately

The first deploy left the Worker unable to send: `wrangler secret put` created a placeholder Worker
which `wrangler deploy` then replaced, taking the secret with it. The manual check caught it —
`"actions": ["heartbeat mail FAILED: RESEND_API_KEY not bound"]` — and the deploy output's binding
table (KV + 7 vars, **no secret**) confirmed the cause. Re-running `secret put` against the real
Worker cleared it.

**But an empty `actions` list means nothing errored; it does not mean an email arrived.** No
successful send has been observed from this Worker, and that is written into
`ops/cloudflare/UPTIME_DEPLOYED.md` as UNPROVEN rather than smoothed into a green tick — a monitor
believed to be working while silently unable to deliver is worse than none, which is precisely the
fault that left this site unwatched 22–28 Aug (DW-076 / RG-0201). **The free proof arrives on its
own: the daily heartbeat fires 06:00 UTC / 08:00 SAST, so the first one lands on soft-launch
morning. In the inbox = proven end-to-end; nothing by ~08:30 SAST = the alert path is still dead.**

A new Resend key scoped to **Sending access** was minted for the Worker rather than reusing the
Full-access production key — an edge Worker that sends one email should not be able to administer
the Resend account, and a shared credential dying silently is the fault this morning was spent on.

### Runbook corrected

`UPTIME_MONITOR.md` said bare `wrangler`; it is not installed globally on David's machine and the
project's own `cloudflare_email_worker/README.md` already used `npx wrangler`. Fixed, along with an
explicit note that the three commands run in PowerShell on the PC, **not** on the server — a wrong
`cd` and a wrong shell each cost a round trip on launch eve.

**Board:** ledger **exit 0 · 181 holding · 0 REGRESSED · 11 open**. RG-0138 `[ ok ]`, RG-0201 `[ ok ]`.
