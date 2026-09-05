## 2026-09-05 — ALERT-OFFORIGIN-1: the RED alarm no longer rides the machine it watches (DW-097)

**The fault.** The daily watch's RED-alert path was one SSH command to the origin: parse
`RESEND_API_KEY` out of `/etc/marketsquare/resend.watch.conf`, then curl Resend *from the box*.
So the alarm shared a transport with the entire class of failure it exists to report. Observed
in anger twice — **26 Aug (DW-073)** and **5 Sep (DW-097)** — where the verdict was RED *because*
the origin was unreachable, and therefore no alert could be sent. David learned of both only by
reading a report hours later. A fire alarm wired through the burning room is not an alarm.

**What did not save us:** the independent Cloudflare watcher (RG-0138) probes `/health`, which was
green on both days. An origin that serves the public fine while refusing SSH is invisible to it by
design. A second vantage existing was never the same thing as the alarm being reachable.

**The fix.**
- `ops/cloudflare/uptime_monitor_worker.js` gains **`POST /alert`** — bearer-keyed
  (`ALERT_INGEST_KEY`), using the Resend key already bound to the Worker (delivery proven
  end-to-end 29 Aug). Cloudflare egress, no dependency on the origin.
- **The recipient is never taken from the request** (fixed `ALERT_TO`), subject/lines escaped and
  capped, `level` clamped, KV rate limit 12/hour that **fails open** — a limiter able to silence an
  outage alarm is worse than the abuse it prevents.
- **`dry:true`** authenticates and validates without sending, so the path is probed on every
  ledger run instead of only during an emergency.
- `scripts/watch_alert.py` is the watch's single entry point: **Worker lane first**, the old ssh
  lane kept as a **fallback only** (two independent lanes beat one; a Cloudflare-side failure is
  real if rarer). Exit 1 = no lane delivered, which is itself a HIGH finding.
- `deploy_uptime_worker.bat` publishes it via the host queue — **deploy first, `secret put`
  second**, the 28 Aug placeholder-Worker lesson.
- Daily-watch task prompt updated to call `watch_alert.py` instead of hand-rolling ssh+curl.

**Locked.** Ledger **RG-0279** — three legs: the Worker has a key-gated `/alert` whose recipient
comes from config; `watch_alert.py` tries the Worker lane *before* the ssh lane; and a LIVE dry
probe proves the endpoint is deployed, our key accepted and Resend bound. Stated limit: the
daily-watch task text lives outside the repo, so the entry asserts the LANE the task calls, not the
task's wording — which is exactly why the alert logic moved into the repo rather than the prompt.

**Also today, for the record:** DW-096 (the third SSH lockout) was healed and class-fixed by the
maintenance loop earlier — `hetzner_fw_selfheal.py` now runs on every 20-minute host tick
(**RG-0274**), so an ISP IP move self-corrects instead of waiting for a human to notice.
