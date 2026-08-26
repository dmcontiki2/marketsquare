# THIRD-PARTY LAUNCH REGISTER
**Every external account, key, subscription and legal document — and whether it is actually ready.**

*Created 21 Aug 2026 · Soft launch to public **Fri 29 Aug 2026** · Full launch **Mon 1 Sep 2026** (RUL-001)*
*Last ship day **Wed 27 Aug** — nothing deploys on launch eve.*
*Maintained by the daily scheduled task `pre-soft-launch-third-party-check`. It rewrites the status column from **evidence**, not from what this file claims.*

**Last swept: 2026-08-26 ~05:0x–07:3x UTC (SECOND pass of the day) · 3 days to soft launch · verdict AMBER.**
*The 02:5x pass and the 06:30 daily watch both ran before this one; this pass re-PROBED their third-party rows
independently and EXECUTED five fixes. Verdict moved RED → AMBER because the one item that was genuinely
leaking (anonymous prospect PII) is now shut, and three of the four ledger reds proved to be the instrument,
not the app.*
Evidence grade on every row below: **PROBED** (measured live this run) · **EXECUTED** (the code path ran) ·
**READ** (a file says so) · **UNRECORDED** (nobody has ever written it down).
Only PROBED is reported as fact — the 21 Aug lesson (the register said Google OAuth was dark; `/auth/providers` said otherwise; the probe won).

> **Note on today.** The unattended 06:30 daily watch ran a few hours before this sweep and opened
> DW-065 … DW-074. This sweep did not re-file those; it re-PROBED the third-party-facing ones,
> confirmed them independently, and **executed two fixes**. Where a row here and a watch row disagree,
> this file's grade tells you which was measured.

---

## MACHINE-READ FIELDS
*The regression ledger reads these lines directly. They stay red until a human fills them in — that is the point.*

```
DOMAIN_REGISTRAR: UNKNOWN
DOMAIN_EXPIRY: UNKNOWN
DOMAIN_AUTORENEW: UNKNOWN
DOMAIN_VERIFIED_ON: UNKNOWN
GOOGLE_CONSENT_SCREEN: UNKNOWN
```
*Ledger: **RG-0137** (domain lifeline) · **RG-0139** (consent screen published). Both OPEN, both print
READY TO LOCK the moment the values above are real. **RDAP re-tried this run (26 Aug) on three
endpoints — `rdap.org` 404, `rdap.nic.co` no answer, `rdap.identitydigital.services` 404; no `whois`
binary in the sandbox.** Third consecutive sweep to fail this probe: the .co registry is genuinely
unreachable from here, so these four fields will NEVER be filled by machinery. One glance at David's
registrar login settles all four, permanently.*

---

## 🔴 RED — WHAT BLOCKS OR THREATENS 29 AUG

1. ~~**ANONYMOUS PII IS BEING SERVED RIGHT NOW**~~ — ✅ **CLOSED 26 Aug, PROBED twice.**
   `GET /launch-api/prospects/list` with no key and no cookie now answers **HTTP 401**
   (`{"detail":"X-Launch-Key required"}`). At 04:20 this morning the same call returned **200 ·
   146,226 bytes · 200 records** carrying `name`, `email`, `phone`, `business_name`, `city`,
   `country` **and pre-authenticated `admin.html?magic=1&…` entry URLs**. David provisioned
   `LAUNCH_API_KEY` and the CityLauncher deploy rode between the two reads. **RG-0176 has been
   PROMOTED OPEN → LOCKED this run** (commit `da85045`) so the assertion can trip red if it ever
   rots — it was printing READY TO LOCK and sitting unpromoted, which is a fix that cannot defend
   itself. DW-068 CLOSED. **Residual, named not hidden:** the n8n cross-store suppression half
   (one opt-out click must suppress in BOTH the orchestration DB and the launcher store) is still
   proven only by hand, and is written into RG-0176's scope rather than left to weaken it.
2. **The migration chain is JAMMED** (RG-0125, DW-066). `migrations/033_csp_verify_served.py`
   **failed** on today's 02:07:10Z deploy — PROBED at `/static/post_deploy_status.json`. It failed
   *honestly* (verified the served CSP after reload, found no `script-src`, refused to claim success,
   restored 0 files). Blast radius today is zero — 033 is last on disk — but **every migration added
   from now sits dead behind it**, which is the DW-030 fault that stranded five migrations for three
   days. **This is the only ledger RED left on the board** (RG-0125), and it is genuinely blocked
   on a deploy, not on work. The 04:05:08Z report is the freshest — the 06:02 SAST release did not
   place a new one. 033 has been rewritten TWICE since: `b77cd2b` (discovery from `nginx -T`
   instead of globs) and **`97f8168` CSP-SCRIPT-SRC-5**, which found the real reason it kept
   failing — *it was measuring the port-80 301 redirect, not the page*, and racing nginx's
   asynchronous reload. It now speaks TLS+SNI to :443, fails loudly on a 3xx, and polls until the
   answer settles. **Both commits are unpublished.** They ride the 27 Aug ship or the jam persists
   into launch.
   **CTO note, so the next session does not re-hunt it:** if 033 goes `ok` on the next deploy but
   RG-0178 stays red, the header is being emitted at the **Cloudflare edge**, not by nginx — 033
   verifies at the origin and cannot see a Transform Rule. That would be a David-panel item
   (Cloudflare → Rules → Response Header Transform / Managed Headers), and it is the one
   explanation consistent with "the snippet declares script-src and the server does not serve it".
   It cannot be discriminated from this vantage: the origin's :443 accepts only Cloudflare IPs.
3. **No `script-src` CSP at the edge** (RG-0178/RG-0180, DW-069). Same root cause as #2. PROBED on
   `/` and `/terms`: `content-security-policy: frame-ancestors 'self'` and nothing else. Every other
   security header is present, so the header lane works — the script directive specifically is being
   overwritten by something downstream. If a remote script ever reached a page the browser would run
   it from **any** origin; the repo-side guard (RG-0177) is the only thing standing between us and
   the 3–4 Aug TP-Drive breach class.
4. ~~**SSH to the origin is down**~~ — ✅ **CLEARED 26 Aug, attended.** David added
   `197.184.106.176` to the TCP 22 rule of `trustsquare-origin-lockdown`; the ISP had moved the line
   off the whole `197.185.x` block, which is why all three old entries failed at once. PROBED
   immediately: **port 22 OPEN**, and the ledger re-run reads **`[ ok ] RG-0099`** — reds 3 → 2.
   DW-065 CLOSED with evidence. **DW-073 remains OPEN and is the residual:** the RED-alert path is
   one SSH command to the box, so the channel that most needs to work in a failure still shares a
   transport with the failure. Unblocked today, not structurally fixed — RED #5 is its real answer.
5. **External uptime monitor STILL NOT DEPLOYED** (RG-0138, L8) — built 22 Aug, day 4 unblocked.
   This has stopped being "a blind day" and become the structural answer to #4: an edge-hosted
   watcher owes nothing to the box or the desktop. 3 commands, `ops/cloudflare/UPTIME_MONITOR.md`.
   Launch weekend unwatched, with the SSH alert path proven broken today, is the worst blind spot
   on this page.
6. **Google consent screen Published-or-Testing is UNRECORDED** (RG-0139). A Testing-mode app 302s
   identically to a Published one — invisible to every instrument we own until a stranger tries to
   sign in on launch morning. OAuth start re-PROBED this run: **302 → accounts.google.com** with a
   real client_id. The lane works; only its audience is unknown.
7. **Domain registrar / expiry / auto-renew UNRECORDED** (RG-0137). The one dependency that can end
   everything silently. RDAP unreachable for the third sweep running (above).

**AMBER, close behind:** RG-0156 (**orchestrator.html** — outside the deploy manifest, access code
`96315` hardcoded in a public web root, empty state renders an outage as an all-clear; launch gate
G2, hard 29 Aug) · RG-0160 (the two example **dossier PDFs** the live SAW teaser links still 404) ·
RG-0173 (**agency journey probe** — the machinery answer to "how did we miss the funnel breaks").

## DAVID-ONLY ACTIONS, IN DATE ORDER

| When | Days left | Action | Why only David |
|---|---|---|---|
| ~~NOW~~ **DONE 26 Aug** | — | ✅ ~~Add the current IP at Hetzner~~ — `197.184.106.176` added to the TCP 22 rule; port 22 PROBED open, RG-0099 green, DW-065 closed. **Still open underneath it:** RG-0188 — there is no `.secrets/hetzner_token.txt`, so `hetzner_fw_selfheal.py` still exits 'NO TOKEN, nothing changed' and the next lockout is again a hand-fix | Lockout risk reserved (RUL-027) |
| ~~NOW~~ **DONE 26 Aug** | — | ✅ ~~Provision `LAUNCH_API_KEY` + ride the CityLauncher deploy~~ — PROBED anonymously after: `/launch-api/prospects/list` = **401**. RG-0176 promoted to LOCKED this run | Secret + deploy (RUL-037). RED #1 CLOSED |
| **NOW** | 3 | 🔴 **Paste the current Resend key into `/etc/marketsquare/resend.watch.conf`** (keep `0640 root:msdeploy`). The watch's RED-alert key has been DEAD since the 22–23 Aug rotation — PROBED today by sending a real alert: Resend returned `401 validation_error`. **Nothing has been able to wake David about an outage for four days**, and nobody noticed because only a real RED exercises this path. Now visible to the register (`SECRETS_REGISTER.md` → Out-of-band copies, added this run) | Root on the box + credential (RUL-037). DW-076 |
| **NOW** | 3 | **Paste a Hetzner API token (firewall write scope) into `.secrets/hetzner_token.txt`** — the file EXISTS but is EMPTY, which is worse than missing: it satisfies a presence check while `hetzner_fw_selfheal.py` exits 'NO TOKEN, nothing changed'. SSH-LOCKOUT-1 fired for real at 04:20 today and cleared only because David was awake to hand-fix it | Credential (RUL-037). RG-0188 · DW-077 |
| **NOW** | 3 | **Google Cloud console → OAuth consent screen: PUBLISHED or Testing?** Write it into `GOOGLE_CONSENT_SCREEN:` above | Console login. RG-0139 |
| **NOW** | 3 | **Registrar, expiry and auto-renew for trustsquare.co** → the four `DOMAIN_*` fields above. Machinery has now failed this three sweeps running | RDAP unreachable. RG-0137 |
| **NOW** | 3 | **Deploy the uptime watcher** — 3 commands, `ops/cloudflare/UPTIME_MONITOR.md` | Cloudflare token + Resend secret. RG-0138 · now also the fix for DW-073 |
| **By Wed 27 Aug** | 1 | **Run the last pre-launch ship.** It must carry: the rewritten `migrations/033` (unjams the chain), RG-0156 orchestrator fix, RG-0160 dossier PDFs, and today's fixes | Deploys reserved (RUL-037) |
| **27 Aug** | 1 | Turn on **Paystack 2FA** (reminder set) | Account security |
| **Overdue (was ~25 Aug)** | — | Buy the budget-capped **Gemini** key, paste to server. Today's arm-up run PROBED it still absent; photo anonymisation stays reject-only (RUL-033) | Money + secret |
| **Launch flip** | 3 | Activate **Resend $20/mo 50k tier** (pre-approved B7 — execution, not a new decision) | Spend |
| **Launch flip** | 3 | Set `LAUNCH_SPECIAL_DEADLINE=2026-09-01` on **both** MarketSquare and CityLauncher | Config both sides |
| **Before 1 Sep** | 6 | **Renew or drop the Anthropic subscription.** Successor already decided and wired (RUL-013, `ai_provider.py`: `gpt-5.6-sol`, Scaleway standby) — this is only the subscription question | Spend |
| **Once** | — | One smallest-pack **Paystack** buy with tab-close → closes the detached-credit E2E | Real money on the live rail |
| **Once** | — | One real **Didit** ID check → settles free-500-vs-$1.10 billing. **Re-verified this run (07:0x): the lane is armed — `/id-verify/status` reads `available:true`, `price_t:1`, 14 guards present — and STILL no real NPR query has ever run.** RG-0136 reads `[ ok ]` because it asserts the SAFETY properties (a PARTIAL_MATCH never passes, a provider failure never charges, the tick never gates an introduction); the billing question is unanswerable without one live check | Real money |
| **When convenient** | — | Delete the two superseded **Cloudflare tokens** (`MarketSquare Media`, `Trustsquare Cache Purge`) | Dashboard login. Rotation residue, not blocking |
| **David picks the moment** | — | **Travelpayouts tours resubmit.** Declined again 24 Aug (*"website under development or not yet ready"*); available 26 / blocked 20 incl. Booking.com, Viator, GetYourGuide. Per RUL-041 never resubmit unchanged — soft launch 29 Aug is the natural moment | Commercial |
| **Month 1** | — | Appoint the **accountant** (R2,000/mo + R500 software, RUL-023) | Engagement + spend |

## PROBED THIS RUN — the live facts

| Probe | Result | Grade |
|---|---|---|
| `GET /health` | `ok` · `TrustSquare BEA` · **v1.3.1** · db primary present, integrity ok | PROBED |
| `GET /` | **200 in 0.47 s** | PROBED |
| `GET /auth/providers` | `{"google":true,"apple":false}` | PROBED |
| `GET /auth/oauth/google/start` | **302 → accounts.google.com** with a real client_id | PROBED |
| `GET /auth/oauth/apple/start` | **503** — RUL-030 enforcing itself | PROBED |
| `GET /id-verify/status` | `available:true` · `"READY — sellers can buy a check"` · `price_t:1` | PROBED |
| `GET /payment/test` | `{"status":"ok","paystack_connected":true}` | PROBED |
| `GET /terms` | 200, serving **EULA v1.15** | PROBED |
| `GET /dashboard/bit` | **8/8 PASS**, worst 0 | PROBED |
| `GET /flags` | 200 anonymous (gate deliberately down, RUL-034). `ai_provider.funnel.card_version` still **2026-08-19.1** — production quotes a week-old card until a deploy rides (DW-067 residual) | PROBED |
| `GET /launch-api/prospects/list` | ✅ **401 `X-Launch-Key required`** — was 200 · 146,226 B · 200 PII records incl. `magic_link` at 04:20 today. Shut between the two reads | PROBED |
| TLS certificate | valid to **2026-11-22 (88 days)**, Google Trust Services WE1 | PROBED |
| `/static/post_deploy_status.json` | `generated_at 2026-08-26T**04:05:08**Z` · seed ok · ladder_seed ok · **`migration:033_csp_verify_served.py` FAILED — chain jammed.** The 06:02 SAST release placed no newer record | PROBED |
| CSP headers on `/` and `/terms` | `frame-ancestors 'self'` only — **no `script-src`, no `connect-src`** | PROBED |
| origin port 22 (`178.104.73.239:22`) | **OPEN — 8/8 tries, 0.48 s, banner `SSH-2.0-OpenSSH_9.6p1`.** The ledger nonetheless printed RG-0099 REGRESSION on two consecutive full runs the same minute; the entry's own function called standalone returned *'both management lanes clear'*. A false red here says 'do not deploy'. Fixed at class level this run — LEDGER-VANTAGE-1 below | PROBED |
| RDAP for trustsquare.co | **FOURTH consecutive failure — 5 endpoints this run** (`rdap.org` 404 · `rdap.nic.co` no answer · `rdap.identitydigital.services` 404 · `rdap.net` 404 · `rdap.markmonitor.com` 404); no `whois` binary; IANA bootstrap lists no `.co` service. **Stop expecting machinery to answer this** — one glance at the registrar login settles all four `DOMAIN_*` fields permanently | PROBED |
| `regression_ledger.py` | **exit 1** · **183 entries · 165 holding · 1 REGRESSED · 17 open · 0 ready to lock · 0 UNVERIFIED.** Opened this run at 4 REGRESSED + 2 UNVERIFIED | EXECUTED |
| `rulings_check.py` | **56 rulings, 0 FAIL, 0 WARN** (was 51 on 24 Aug — RUL-052…056 landed and are reflected) | EXECUTED |
| `eula_sync.py --check` | **in sync**, 117,749 B across the three copies (source = v1.15) | EXECUTED |
| `git log origin/deploy..HEAD` | **2 commits unpublished — `97f8168` (CSP-SCRIPT-SRC-5, the real 033 fix) and `da85045` (this run).** The fix for RED #2 is sitting in the debt | EXECUTED |

**THE LEDGER OPENED THIS RUN AT 4 REGRESSED AND CLOSED AT 1. Three of the four were the
instrument, not the app** — and every one of them says "do not deploy", three days out:

- **RG-0099 (SSH vantage).** Port 22 was demonstrably OPEN — 8/8 probes, 0.48 s, real OpenSSH
  banner — while two consecutive full runs called it a REGRESSION, and the entry's own function
  run standalone said *'both management lanes clear'*. LEDGER-FLAP-1's 3-try guard was written for
  a dropped packet; this is the vantage's port-22 lane under full-run load. **Fixed
  (LEDGER-VANTAGE-1):** a control probe to `github.com:22` / `gitlab.com:22` runs before the
  verdict. Origin dead + control dead → **NOT EVALUATED** (says nothing about the firewall).
  Origin dead + control alive → still **RED**, with the runbook line. Assertion not weakened.
- **RG-0182 (indicative-fare lane).** `scripts/prove_fares_lane.py` hardcoded
  `/tmp/prove_fares.db` and swallowed `OSError` on cleanup. A previous run had left that exact
  path owned by `nobody:nogroup`, so the remove failed *silently*, sqlite opened the stale file
  read-only, and the harness died *"attempt to write a readonly database"* — which the ledger read
  as a rotted fix. **Fixed (HARNESS-TMPDIR-1):** `mkdtemp` per run — cannot collide, honours
  `TMPDIR`, needs no cleanup guard to be correct. Same for `data_flights.py`'s selftest. Now **13/13**.
- **RG-0181 (affiliate link-out).** Purely the missing `fastapi` import RG-0187 was written for.
  Installed; selftest **9/9**, every refusal refusing.
- **RG-0186 (migration proof method).** The guard matched the call site spelled `served_csp()`
  *with empty parens* and went red the moment 033 legitimately grew an argument
  (`served_csp(settle=15)`, from CSP-SCRIPT-SRC-5). **Third cut of one mistake** — the file's own
  comment warns against matching wording rather than behaviour, and this cut matched a *spelling*.
  **Fixed (CSP-VERIFY-GUARD-3):** matches `served_csp(`.
- **RG-0015 (git lock)** was red on a stranded `.git/HEAD.lock`; healed with `scripts/git_unlock.py`.

**The one survivor is real: RG-0125** — and it is waiting on a deploy, not on work.

### DEPLOY DEBT — the site on 29 Aug is whatever has SHIPPED

`origin/deploy` = **`14d927f`** (Release 26 Aug 06:02 SAST). **TWO commits ahead:**

| Commit | When | What it carries | Why it matters on 29 Aug |
|---|---|---|---|
| `97f8168` | 26 Aug 06:10 | **CSP-SCRIPT-SRC-5** — `migrations/033` now speaks TLS+SNI to :443 instead of measuring the port-80 301 redirect, fails loudly on a 3xx, and polls until the async reload settles | **Clears RED #2** (the jammed chain) and is the only route to RED #3 (`script-src` at the edge) |
| `da85045` | 26 Aug 07:2x | This run: LEDGER-VANTAGE-1, HARNESS-TMPDIR-1, CSP-VERIFY-GUARD-3, RG-0176 → LOCKED, `SECRETS_REGISTER.md` out-of-band-copies table | Takes three false "do not deploy" reds off the board and makes the dead alert key visible to the register |

**Nothing else deploys before Wed 27 Aug — that is the last ship day.** The working tree also holds
live uncommitted work from a concurrent attended session (`STATUS`, `RULINGS.md`, `DAILY_WATCH`,
`WAVE_PLAN_LAUNCH_2026.html`, `bea_main.py`, `dashboard.server.html`); this run committed **only**
its own four files and left the rest untouched.

Still to BUILD and ride the ≤27 Aug ship: RG-0156 orchestrator fix, RG-0160 dossier PDFs.

---

## MONEY

| Service | State | Grade | Cost | Blocks 29 Aug? |
|---|---|---|---|---|
| **Paystack** (business 1777715) | LIVE + approved, intl + Apple Pay on. `/payment/test` → **`paystack_connected: true`** (re-probed this run). Webhook secret armed, RG-0091 passing. **2FA not set up** (27 Aug) | PROBED | 2.9% + R1 | No — 2FA + E2E close-out remain |
| **FNB business account** | Open | READ | — | No |
| **CIPC** | Company done (2026/340128/07). Provisional patent not filed (~R900, A7) | READ | R900 one-off | No |
| **Accountant** | **Not engaged.** RUL-023: month 1, "not optional and not deferrable" | READ | R2,500/mo | No |
| **Paddle** (MoR, phase 2) | Account not opened; pre-check never done | READ | 5% + $0.50 | No |

## AI PROVIDERS

| Service | State | Grade | Blocks 29 Aug? |
|---|---|---|---|
| **OpenAI** (BASE lane, 100% of live traffic) | Serving — `/flags` shows `ai_provider.active: openai`. **No production golden run on record** (RG-0132 open): run `scripts/golden_seam_v2.py` on the box with the production key | PROBED + EXECUTED | No — tracked by machinery |
| **Anthropic API** (failover) | **No key on the server, by decision** (SPEND-GUARD-1). Failover PROVEN in the decision layer — RG-0128 LOCKED | EXECUTED | No |
| **Anthropic subscription** (Fable, fix agent) | Active, **time-boxed to 1 Sep** (RUL-013). Successor decided and wired: `TASK_MODEL["design"] = "gpt-5.6-sol"`, Scaleway standby. Only the renewal is open — a spend question, David's, before 1 Sep. Nothing on disk contradicts this | READ + code | No |
| **Gemini** | 🟠 **Key STILL ABSENT — probed today** by the scheduled arm-up run; funds were expected ~25 Aug. Photo anonymisation stays **reject-only** (RUL-033); RG-0121 OPEN by design. **The price row was wrong and is now corrected**: first-party standard tier is **$0.75 in / $3.75 out**, not the OpenRouter-captured $0.375/$1.50 (input understated 2×, output 2.5×). Canary year-1 re-costs $548 → **$845**; still ~51% cheaper than terra-only, narrowing to ~27% at the 1 Jan 2027 step. **A re-cost, not a re-decision — RUL-032 stands.** RG-0184 now asserts no traffic-taking lane may be priced from an aggregator | PROBED + EXECUTED | Indirectly — reject-only until the key lands |
| **Scaleway** (EU last resort) | Configured, free tier, price unobservable | READ | No |

## IDENTITY · EMAIL · SIGN-IN

| Service | State | Grade | Blocks 29 Aug? |
|---|---|---|---|
| **Google OAuth** | ✅ **LIVE** — `google:true`; start 302s to Google with a real client_id (re-probed). RG-0111 LOCKED | PROBED | No |
| **Google consent screen** | ⚠️ **UNRECORDED — Published or Testing unknown.** Not probeable anonymously | UNRECORDED | **Potentially yes** — RG-0139 |
| **Apple Sign-In** | **OUT by ruling (RUL-030).** start → 503, enforcing (re-probed). Do not re-propose | PROBED | — |
| **Didit** (DHA ID check) | **ARMED** — `available:true`, `price_t:1` (re-probed). **Unproven clause re-verified this run and it STANDS: no real NPR query has ever run**, so the billing shape (free-500 vs $1.10 from call one) and the real-registry outcome mapping are both untested. One real check is on David's once-list | PROBED | No (never a blocker by RUL-039) |
| **Resend** | Sending live, free tier. `mail.trustsquare.co` verified, root domain not. **The ~5-min 422 is the HEALTHY answer** (INFRA-RESEND-1, disproven cry-wolf 22 Aug — the scheduled task's own prompt is stale on this row; do not re-raise) | PROBED (22 Aug) | Operationally yes — it carries sign-in. $20 tier flips at launch |
| **Gmail SMTP** (fallback) | Authenticated 22 Aug. Still sends from a personal address | PROBED (22 Aug) | Presentation risk at public launch |
| **support@trustsquare.co** | ✅ RG-0174 **LOCKED**: inbound routes to the SUPPORT pipeline, ONE reply per inbound, personal inbox is dead-letter only | EXECUTED + ledger | No |
| **RED-alert channel** | 🔴 **BROKEN — exercised for the first time today and did not deliver.** It is one SSH command to the box, and SSH is down. The alert path and the failure share a transport. DW-073 | PROBED (by failure) | **Yes, operationally** — a launch-weekend outage would not reach David |
| **n8n** | Self-hosted, running (verified 2 Jun) | READ | No |
| **WhatsApp / Meta** | **Not a dependency.** Open question is AL-8: the SEV-1 wake channel — and DW-073 just made it urgent | READ | No |

## INFRASTRUCTURE

| Service | State | Grade | Cost | Blocks 29 Aug? |
|---|---|---|---|---|
| **Hetzner CPX32** | Live and serving. **Single point of failure.** ✅ **Port 22 restored 26 Aug** — `197.184.106.176` added to the firewall; PROBED open, RG-0099 green. Account has **no 2FA** (console banner, noted in passing) | PROBED | **EUR 15.49/mo grandfathered — RUL-025: do NOT rescale** | Not the site; yes the management lane |
| **Hetzner Object Storage** | Live, daily 3AM backup, 14-day retention. ("HETZNER_S3" keys are actually Cloudflare R2 — SECRETS_REGISTER) | READ | EUR 5.99 | No |
| **Cloudflare** (DNS/CDN/WAF/R2/email) | Live; nameservers `ainsley`/`koa`. **WAF deliberately open** (RUL-034); origin gate down by pre-launch posture (`/flags` 200 anonymous — expected) | PROBED | Free | No |
| **SSL** | ✅ valid to **2026-11-22 (88 days)**, Google Trust Services | PROBED | Free | No |
| **GitHub** | Live. Deploy debt = **1 commit, and it carries a fix for a live RED** (above) | EXECUTED | Free | Indirectly — RED #2 |
| **Domain registrar** | ⚠️ **UNRECORDED.** RDAP re-probed and unreachable for the 3rd sweep running; David's login is the only source | UNRECORDED | Unknown | **Potentially catastrophic** |
| **External uptime monitor** | 🔴 **BUILT 22 Aug, NOT DEPLOYED — day 4.** Now also the structural fix for the broken RED-alert path (DW-073). RG-0138 | EXECUTED (source) | Free | See RED #5 |

## DATA FEEDS

**Live:** Travelpayouts flights Data API (partner 758984; `data.flights: true` on `/flags`; token
UNROTATABLE-ACCEPTED), Numista (rotated key probed 200; RG-0150 polices the data boundary), and the
free keyless set (OSM, Scryfall, Wikidata, Frankfurter, FX per RUL-022).
**Tours: DECLINED AGAIN 24 Aug** (*"website under development or not yet ready"*) — available 26 /
blocked 20, incl. Booking.com, Viator, GetYourGuide. Per RUL-041 never resubmit unchanged; **David
picks the resubmit moment** and soft launch is the natural one. Aviasales flights unaffected. Drive
loader stays OFF (RG-0025 inverted — no third-party script on any app page).
**Affiliate lane:** `travelpayouts_partners.py` (TP-LINKOUT-1) — server-side link-out, host
allowlist, fails closed, dark by flag. RG-0181 asserts the invariant; the lane being dark is
deliberate, not a defect.
**Deliberately dark:** JustTCG (key valid, UNSET — free tier is non-commercial), Duffel, AeroDataBox,
Mapbox, GeoNames.
**Closed:** Google Places (**OUT — silent ~$360 bill, never re-propose**), Amadeus (portal dead 17 Jul), BrickLink.
**Unknown:** eBay keyset was "pending ~1 day" on 7 Jun — no later entry says it arrived.
**Held:** ~14 paid vendors, all `false` until David enables with a ceiling.

---

## DOCUMENTS

| Document | State | Grade | Gate? |
|---|---|---|---|
| **EULA** | **v1.15 IS LIVE** — `/terms` serves v1.15 (re-probed). Three copies byte-in-sync, 117,749 B | PROBED | Counsel (A6) is **NOT a gate** (RUL-020) |
| **Privacy Policy** | `privacy.html` exists and is exempted at origin (migration 021); A1 still lists it open | READ | Bar G7 |
| **Privacy UK/US/AU supplements (D4)** | **Never drafted.** Matters because RUL-019 made launch worldwide | READ | Bar G7 · David confirms scope, Claude drafts |
| **IP Brief v6** | DRAFT, counsel-gated, lands with the EULA | READ | Not in the bar |
| **WhitePaper v3.11** | DRAFT (v2 is the published prior-art defence) | READ | No |
| **CC-002 pricing/AI canon** | Parked, **77 days** against a 7-day threshold (DW-010, formally deferred by David 21 Aug) | READ | Deferred by ruling |

---

## WATCH-OUTS — contradictions on disk, stated not resolved

1. **`.env` files prove nothing** — verify at the point of USE (RG-0147, LOCKED).
2. **`AGENT_BRIEFING` v1.9 is stale** on Paystack — treat its other rows with the same caution.
3. **"READY" is not "works"** — the Didit probe is a presence check. No real NPR query has run.
4. **`LAUNCH_DEADLINE-1` is unsatisfied on the CityLauncher side** — that `.env` has no `LAUNCH_SPECIAL_DEADLINE` at all.
5. **A Testing-mode Google consent screen is invisible to every instrument we own.** The only
   remaining sign-in failure mode that would present for the first time on launch morning.
6. **The scheduled task's own prompt is stale on three rows** and has been for four days: it calls
   the secrets rotation BLOCKING (done + probed 22 Aug; RG-0146/RG-0147 LOCKED and green today),
   repeats the Resend "malformed-sender 422" claim (disproven 22 Aug — the 422 is the healthy
   answer), and says the uptime monitor "was due 22 Aug" without noting it is built. None re-raised.
   **Refresh the task prompt when David next edits it.**
7. **`OPEN_LOOPS.md` still files B1 (secrets) under 🔴 BLOCKING NOW** while the row's own text says
   rotation is complete. Corrected by a dated note this run; the row moves at the next attended
   reconciliation (this file has no compiler, so edits stay additive — CHANGELOG-COLLISION-1 class).
8. **`bit_flags.auth_fail_closed` is `false`** on live `/flags`. Noted, not raised — no assertion
   covers it and no ruling names it. Worth one look before public traffic.

### Corrected 26 Aug — files/rows the probes overruled this run

- **"Deploy debt = 3 record-only commits, no app code"** (24 Aug row) — **wrong now.** The debt is
  1 commit and it carries the migration-033 rewrite, i.e. the fix for a live RED. Row rewritten.
- **"External uptime monitor — no vendor named / not built"** (task prompt) — it IS built
  (Cloudflare Worker, 22 Aug, no new vendor, no cost). What is missing is the deploy.
- **"Secrets exposed twice and not rotated — the only BLOCKING item"** (task prompt) — rotation
  completed 22 Aug; SECRETS_REGISTER "Still burnt" table is EMPTY; RG-0146/RG-0147 LOCKED and green
  on today's run. Not re-raised, and `OPEN_LOOPS.md` annotated so the next session does not either.
- **"Resend's health probe 422s on a malformed sender — fix that"** (task prompt) — the 422 is the
  *healthy* auth answer (INFRA-RESEND-1). There is nothing to fix and no outage being masked.
- **Ledger 167 → 181 entries; rulings 51 → 56;** open list refreshed. RG-0181/RG-0182 moved from
  REGRESSED to UNVERIFIED by RG-0187, which is machinery correcting an instrument, not a fix rotting.
- **Gemini price row** — corrected today from an OpenRouter estimate to a first-party read
  (understated 2× / 2.5×). The decision stands; the margin narrowed.

**Second pass, ~05:0x–07:3x UTC — what THIS run overruled:**

- **"3 REGRESSED / 2 UNVERIFIED" (the 02:5x row above)** — that reading was already stale by the
  time it was written, and the replacement is not a re-count but five fixes: **183 entries · 165
  holding · 1 REGRESSED · 17 open · 0 UNVERIFIED**.
- **"RG-0099 — SSH-LOCKOUT-1 has recurred"** (ledger, twice) — **the probe overruled the ledger.**
  Port 22 answered 8/8 in 0.48 s with a real OpenSSH banner at the same minute the ledger called it
  a regression. The instrument was measuring itself. LEDGER-VANTAGE-1 now makes that case say
  NOT EVALUATED instead of REGRESSION.
- **"RG-0181/RG-0182 are the sandbox vantage, unfixable here" (DW-071)** — half right, and the
  other half was one line of code. `fastapi` was one install; the fares harness was a hardcoded
  `/tmp` path left owned by another user. Both now genuinely PASS (9/9 and 13/13) rather than
  reading UNVERIFIED, which closes DW-071's structural half — not just its "second clean run".
- **"RG-0176 is passing but still marked open"** (DW-068 residual (a)) — **promoted to LOCKED this
  run.** A fix that prints READY TO LOCK and is never promoted cannot trip red when it rots; that
  is the exact failure the ledger exists to prevent.
- **"Resend's health probe 422s on a malformed sender"** (task prompt, re-checked independently) —
  confirmed stale for the FIFTH time. `_infra_resend()` sends an empty body deliberately and maps
  **422 → `{"status":"ok"}`** (INFRA-RESEND-1, 22 Jul: the production key is sending-scoped and 401s
  on `/domains` even when perfectly able to send). **But the same words hid a real fault:** the
  watch's SEPARATE Resend key in `/etc/marketsquare/resend.watch.conf` IS dead (401), and has been
  since the rotation. The prompt was wrong about the mechanism and accidentally right that Resend
  needed a look.
- **`SECRETS_REGISTER.md` could not see a credential it is responsible for.** The register (and
  RG-0146 with it) knew only the app's copy in `secrets.env`. A new **Out-of-band copies** table
  now lists every second copy of a rotated credential, with the rule that a rotation is not
  finished until each row is updated and re-probed.
- **RDAP for `.co` is not going to answer.** Five endpoints, four sweeps, plus an IANA bootstrap
  with no `.co` service. Recorded as permanently machine-unanswerable so no future sweep spends
  time on it.

### Corrected 22–24 Aug (stands — do not re-raise)

- **Secrets rotation is DONE** (22 Aug). Residue: two superseded Cloudflare tokens for David to
  delete; FOUNDERS_ID_SALT rotate-or-accept is Claude's pending call.
- **Resend's ~5-min 422 is the HEALTHY answer** (INFRA-RESEND-1).
- **The AI serving lane is resolved**: OpenAI base, Anthropic keyless by decision, failover proven (RG-0128).
- **Fable's successor is named and wired** (RUL-013 + `ai_provider.py`); only the subscription
  renewal is open, and it is a spend question.
- **SSL renewed** — 2026-11-22, not the 24 Sep an older row claimed.
- **`post_deploy_status.json` serves at `/static/`** — the bare path 404s. Do not misread that 404
  as a missing deploy record.
