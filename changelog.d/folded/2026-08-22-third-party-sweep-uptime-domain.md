## 2026-08-22 — Pre-soft-launch third-party sweep: an external watcher built, and two unowned facts given machinery

**7 days to soft launch (Fri 29 Aug) · verdict AMBER.** Unattended sweep. All guards green:
ledger **exit 0** (132 entries, 0 regressed), `rulings_check` **39/39, 0 FAIL**, `eula_sync --check`
**in sync** (117,749 B — EULA v1.14 is live). Live probes: `/health` ok/1.3.1, `/auth/providers`
`{google:true,apple:false}`, `/auth/oauth/google/start` **302 → Google with a real client_id**,
`/auth/oauth/apple/start` **503** (RUL-030 enforcing itself), `/id-verify/status` **available:true,
price_t 1**, TLS **32 days** (24 Sep).

### UPTIME-EXTERNAL-1 — the outage watcher, built rather than handed back as a vendor menu

`OPEN_LOOPS` **L8** had sat since 14 Aug with the next action "David names a service". That is a
technical decision wearing a management costume — exactly what **RUL-037** ends. Decided and built
this run: a **Cloudflare Worker on a 5-minute cron trigger**.

- **No new vendor** — Cloudflare already carries DNS, CDN, R2 and the inbound email worker.
- **No new money** — cron triggers and 100k requests/day are on the free plan; 288 invocations/day.
- **The right vantage** — every instrument we own today runs *on the box it watches* (ops sweep, BIT,
  subscription monitor, the 01:30 cron) or *on David's PC* (the 06:30 watch). A dead box or a closed
  laptop is a blind day **by construction**; it already happened on 6 Aug. This one is on the edge.
- Rejected, with reasons: paid uptime SaaS (money + a vendor decision for something we can do free),
  a systemd timer on the box (dies with the thing it watches), GitHub Actions (a 5-min cron exceeds
  the free minutes on a private repo — it would start billing).

Behaviour: `GET /health` expecting **200 *and* `{"status":"ok"}`** (a 200 with a sick body is still
down); **two consecutive failures** alert, at most one repeat per 30 min; recovery alerts once with
the outage duration; and a **daily heartbeat**, because a monitor that died in July is
indistinguishable from a site that is fine. State in Workers KV, degrading honestly to
alert-without-suppression if the binding is missing — it can never fail *silently*.

Files: `ops/cloudflare/uptime_monitor_worker.js` (186 lines, ESM syntax-checked),
`ops/cloudflare/uptime_wrangler.toml`, `ops/cloudflare/UPTIME_MONITOR.md` (runbook + a proof step
that exercises the *alert path*, not just the probe). Deploy is three commands and is sequenced
**after `ROTATE_SECRETS.bat`** so the fresh Resend key goes in, never the burnt one.

### Three new ledger entries — facts that lived only in conversation now have assertions

- **RG-0138** (OPEN) — an outage is noticed by something that is neither the server nor David's
  desktop. Source half passes on inspection; stays red until `UPTIME_DEPLOYED.md` exists and its
  heartbeat is under 7 days old.
- **RG-0137** (OPEN) — *DOMAIN-LIFELINE-1.* The registrar, expiry and auto-renew state for
  trustsquare.co were recorded in **no file in this repo**. Every other dependency has an owner; the
  one that takes the site, the mail domain, the OAuth redirect URIs and the payment webhooks down
  *together* had none. A lapsed domain is not an outage you debug, it is one you learn about from a
  customer. DNS is Cloudflare (`ainsley`/`koa`, probed) which narrows but does **not** prove the
  registrar — a full-zone setup looks identical either way. The entry reads four `DOMAIN_*` fields in
  `THIRD_PARTY_LAUNCH_REGISTER.md` and fails while they are UNKNOWN, while auto-renew is off, within
  60 days of expiry, or if the record goes 180 days unverified.
- **RG-0139** (OPEN) — *ONETAP-PUBLISH-1.* The Google OAuth **consent screen** may still be in
  Testing, where only listed test users can sign in. A Testing-mode app 302s to Google identically to
  a published one, so **no probe we own can tell them apart** — it would present for the first time
  as "sign-in is broken" on soft-launch morning. Live half asserted (`/auth/providers`); record half
  demands a dated `GOOGLE_CONSENT_SCREEN: PUBLISHED (verified YYYY-MM-DD)` line.

### Register corrected where the file disagreed with the code (the 21 Aug rule, applied again)

- **"Resend's health probe 422s every 5 min on a malformed sender."** Not a defect. `_infra_resend()`
  (INFRA-RESEND-1, 22 Jul) posts a deliberately **empty body** and treats **422 as the healthy
  answer** — auth passed, nothing sent — because the send-scoped production key 401s on `/domains`
  while sending perfectly. 401/403 is the failure signal and is mapped to `fail`. No cry-wolf, nothing
  to fix. The register had merged it with the genuine 7 Aug incident (a malformed `from` losing real
  mail), which was class-fixed the same day as RESEND-FROM-1.
- **"Nothing on disk says what replaces Fable when RUL-013 expires on 1 Sep."** Wrong. RUL-013 names
  the successor and `ai_provider.py` already wires it: `TASK_MODEL["design"] = "gpt-5.6-sol"`,
  Scaleway standby. What expires is the *subscription*, which is a spend question, not a gap.
- **"Which AI lane is serving?"** Resolved rather than restated: OpenAI base, no Anthropic server key
  by decision (SPEND-GUARD-1), failover proven in the decision layer 21 Aug (RG-0128). The residue is
  RG-0132, which is tracked machinery.

`OPEN_LOOPS.md` **L8** rewritten to match. Deploy debt unchanged and named: 3 unpublished commits
(`f2da615`, `c2ab57b`, `3838142`) plus uncommitted 21 Aug edits — DW-058, David's Wed 27 Aug action.
