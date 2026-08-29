# THIRD-PARTY LAUNCH REGISTER
**Every external account, key, subscription and legal document — and whether it is actually ready.**

*Created 21 Aug 2026 · Soft launch to public **Fri 29 Aug 2026** · Full launch **Mon 1 Sep 2026** (RUL-001)*
*Last ship day was **Wed 27 Aug — PASSED.** Nothing deploys on launch eve or launch day.*
*Maintained by the daily scheduled task `pre-soft-launch-third-party-check`. It rewrites the status column from **evidence**, not from what this file claims.*

**Last swept: 2026-08-29, 08:30–08:50 UTC (10:30–10:50 SAST) · TODAY IS SOFT LAUNCH · verdict GREEN.**

*The RED list is EMPTY for the first time in this register's life. The two REDs that made yesterday
AMBER — "nothing is watching the site and nothing can wake David" — were both closed by David on
28 Aug (watch key re-installed and PROBED 200; watcher deployed, cron */5), and the one piece that
could only be proven this morning has been: **the 06:00 UTC heartbeat email is IN David's inbox**
(received 06:00:22Z, "UP — 200 in 391ms"), so the alert path Worker → Resend → inbox is proven
end-to-end on the exact morning strangers arrive. The site goes public watched, alarmed, and green
on every functional probe.*

Evidence grade on every row: **PROBED** (measured live this run) · **EXECUTED** (the code path ran) ·
**READ** (a file says so) · **UNRECORDED** (nobody has ever written it down).
Only PROBED is reported as fact — the 21 Aug lesson (the register said Google OAuth was dark;
`/auth/providers` said otherwise; the probe won).

---

## MACHINE-READ FIELDS
*The regression ledger reads these lines directly. They stay red until a human fills them in — that is the point.*

```
DOMAIN_REGISTRAR: Cloudflare, Inc. (IANA ID 1910 · whois.registry.co · registrar lock ON, clientTransferProhibited)
DOMAIN_EXPIRY: 2026-12-30
DOMAIN_AUTORENEW: ON (read in the Cloudflare Registrations dashboard 2026-08-28; status Active)
DOMAIN_VERIFIED_ON: 2026-08-28
GOOGLE_CONSENT_SCREEN: PUBLISHED (In production · External · verification NOT required, no sensitive or restricted scopes) verified 2026-08-27
```
*Ledger: **RG-0137** (domain lifeline, LOCKED 28 Aug) · **RG-0139** (consent screen published).*

Domain lifeline verified 28 Aug via `whois.iana.org` → `whois.registry.co` (the method note below).
Expiry **2026-12-30 (123 days out)**, registrar lock ON, auto-renew ON, DNSSEC unsigned (hardening
option, not a launch item). Not re-whoised today — RG-0137 asserts the fields and is green on this
run's ledger.

> **The method note is worth keeping.** Four consecutive sweeps declared these fields permanently
> machine-unanswerable, and the 26 Aug entry hardened that into canon. All four were *guessing RDAP
> hostnames* and reading 404s as proof the data did not exist; none asked the authority which server
> to use. `whois.iana.org:43 ← "co"` returns `refer: whois.registry.co`, and that server answers in
> about a second. **A negative result proves a negative only if the method was right.**

---

## 🔴 RED — WHAT BLOCKS OR THREATENS TODAY

**Nothing.** The RED list is empty on launch morning.

### The two REDs of 27–28 Aug — CLOSED, and the closing evidence is live, not read off a file

1. ~~**External uptime watcher not deployed (day 6)**~~ — ✅ **DEPLOYED by David 28 Aug 11:2x UTC**
   (Worker `trustsquare-uptime`, cron `*/5`, 2-strike DOWN alert, daily heartbeat). **Re-probed this
   run 08:36 UTC:** `ok:true · "200 in 190ms" · kv:true · consecutiveFails:0`. **RG-0138 promoted
   OPEN → LOCKED** (7-day heartbeat staleness tripwire armed). DAVID_QUEUE D4 closed.
2. ~~**RED-alert Resend key dead (day 3)**~~ — ✅ **Re-installed by David 28 Aug** from the live
   systemd drop-in; PROBED from the box `GET https://api.resend.com/domains` → **HTTP 200**. And
   the class is fixed, not just the instance: **RG-0201 LOCKED** — `ROTATE_SECRETS.bat [4b/6]` now
   refreshes the out-of-band watch copy in the same rotation that replaces the key, so a rotation
   can never orphan the alert channel again. DW-076 / D3 closed.

**And the piece neither of those could prove — proven this morning.** `UPTIME_DEPLOYED.md` recorded
the alert half UNPROVEN ("empty `actions` means nothing errored — it does not mean an email
arrived") and named its own test: the first heartbeat fires 06:00 UTC on launch morning. **PROBED
in David's Gmail this run: the heartbeat email arrived 2026-08-29T06:00:22Z** from
`hello@mail.trustsquare.co` — *"UP — 200 in 391ms"*. `LAST_HEARTBEAT` rolled forward to 2026-08-29
in the same run. The site cannot fall over unnoticed this weekend: a DOWN gets 2-strike detection
within ~10 minutes and an email whose delivery path was exercised today.

### DEPLOY DEBT — 13 commits, 37 files, ZERO deployable (checked, not counted)

`git log origin/deploy..HEAD` = **13 commits** this morning. Every changed path was checked against
`ops/autodeploy/deploy_manifest.txt` this run: **none of the 37 files is deployable** — registers,
`DAVID_QUEUE.md`, `DAILY_WATCH/`, `changelog.d/`, `scripts/`, `ops/cloudflare/` (the Worker deploys
via wrangler, not the manifest), `.gitignore`. **The site today serves the 28 Aug 03:08 UTC release
and it already carries everything user-facing** (`post_deploy_status.json` re-probed: `generated_at
2026-08-28T03:08:38Z`, seed ok, ladder_seed ok, migrations "none pending"). No deploy is needed and
none happens on launch day.

**AMBER residue, tracked by machinery, none of it blocking:** RG-0198 (anonymous
`/dashboard/summary` still serves `lastDone` / `nextGoals` / `priorityItems` / `recentChangelog` —
re-probed today, unchanged, deliberately deferred past launch: the fix needs a deploy and touches
the endpoint both operator consoles read) · RG-0180 (`connect-src` still `'self' https:'`;
`script-src` holds the load-bearing half) · RG-0173 (agency journey probe unbuilt) · RG-0132 (no
production golden run on record for the OpenAI BASE lane).

## DAVID-ONLY ACTIONS, IN DATE ORDER
*Mirrors `DAVID_QUEUE.md` — 12 items, **6 open** (`python3 scripts/david_queue.py` prints the next
one with its steps). Nothing on this list blocks today.*

| When | Days left | Action | Why only David |
|---|---|---|---|
| **TODAY (launch flip)** | **0** | **Activate Resend $20/mo 50k tier** — pre-approved (B7), execution not a new decision. The free tier (100/day) will not carry public sign-in volume if today works · D6 | Spend |
| **Before Tue 1 Sep** | **3** | **Cancel the Anthropic subscription in the account** if it auto-renews. The decision is MADE (D8 closed 28 Aug: "works as we have it wired" = DROP, RUL-013's no-renew default; successor wired, `design → gpt-5.6-sol`, Scaleway standby). Only the billing click remains | Spend |
| **Overdue — was ~25 Aug** | — | Buy the budget-capped **Gemini key** ($10/mo cap at the vendor) and run `add_gemini_key.bat`. Until then photo anonymisation stays **reject-only** (RUL-033) — a quality cost that grows with every seller upload, never a blocker · D5 | Money + secret |
| **Once, soon after launch** | — | One smallest-pack **Paystack buy with tab-close mid-flow** → closes the detached-credit E2E. `/payment/test` → `paystack_connected: true` re-probed today · D9 | Real money on the live rail |
| **Once** | — | One real **Didit ID check** → settles free-500-vs-$1.10-from-call-one. Lane re-probed ARMED today (`available:true, price_t:1`); still no real NPR query has ever run. RG-0136 reads `[ ok ]` because it asserts the SAFETY properties; the billing shape is unanswerable without one live check · D10 | Real money |
| **David picks the moment** | — | **Travelpayouts tours resubmit.** Declined twice (latest 24 Aug). RUL-041 bars an unchanged resubmit — **today's public soft launch is the first materially changed face** · D11 | Commercial |
| **When convenient** | — | Delete the two superseded **Cloudflare tokens** (`MarketSquare Media`, `Trustsquare Cache Purge`) · D12 | Rotation residue |
| **Week 1** | — | Re-read the **Google OAuth user cap** (Audience showed 0/100; console says verification not required, so it should not bind — symptom if wrong: sign-ins refuse at exactly 100) and consider consent-screen **branding** | Console login |
| **Month 1** | — | Appoint the **accountant** (R2,000/mo + R500 software — RUL-023, "not optional and not deferrable") | Engagement + spend |
| ~~DONE 28 Aug~~ | — | ✅ ~~Resend watch key~~ (D3, PROBED 200 from box) · ✅ ~~Uptime watcher deployed~~ (D4, RG-0138 LOCKED; heartbeat PROBED in inbox 29 Aug) · ✅ ~~Paystack 2FA~~ (D2, David confirmed) · ✅ ~~Launch special~~ (D7 — **ON by RUL-060**, David's call over the 'off' recommendation; armed + health ok; hard close 1 Sep) · ✅ ~~Anthropic renew-or-drop~~ (D8 — DROP decided; see above) | — |
| ~~DONE 26–28 Aug~~ | — | ✅ Domain lifeline complete (D1, RG-0137 LOCKED) · ✅ Google consent screen In production (27 Aug) · ✅ Hetzner firewall IP + `LAUNCH_API_KEY` + self-heal token (RG-0188 ok) | — |

## PROBED THIS RUN — the live facts (29 Aug 2026, 08:30–08:50 UTC)

| Probe | Result | Grade |
|---|---|---|
| `GET /health` | `ok` · `TrustSquare BEA` · **v1.3.1** · db primary present (2,879,488 B), integrity **ok** | PROBED |
| `GET /auth/providers` | `{"google":true,"apple":false}` | PROBED |
| `GET /auth/oauth/google/start` | **302 → accounts.google.com**, real client_id `869589580243-…`, correct redirect_uri, scope `openid email profile` | PROBED |
| `GET /auth/oauth/apple/start` | **503** — RUL-030 enforcing itself | PROBED |
| `GET /id-verify/status` | `available:true` · `price_t:1` · *"READY — sellers can buy a check"* | PROBED |
| `GET /payment/test` | `{"status":"ok","paystack_connected":true}` | PROBED |
| `GET /terms` | 200, 122,935 B, serving **EULA v1.15** (the v1.13/v1.9 strings in-page are history text) | PROBED |
| `GET /dashboard/bit` | **8/8 PASS**, worst 0, `failing: []` | PROBED |
| `GET /flags` | 200 anonymous (gate deliberately down, RUL-034 — expected on public day). `ai_provider.active: openai` · card `2026-08-26.1` · `data.flights true`, `places/mapbox/ops false` · providers available: anthropic, openai, scaleway (**no gemini — D5**) | PROBED |
| **Uptime Worker** | `ok:true · 200 in 190ms · kv:true · consecutiveFails:0` (08:36 UTC) | PROBED |
| **Heartbeat email** | **IN INBOX** — received `2026-08-29T06:00:22Z`, *"UP — 200 in 391ms"*, from `hello@mail.trustsquare.co` | PROBED (Gmail) |
| `/static/post_deploy_status.json` | `generated_at 2026-08-28T03:08:38Z` · seed ok · ladder_seed ok · migrations **"none pending"** | PROBED |
| `GET /dashboard/summary` | 200 anonymous; still serves the 4 narrative fields verbatim (`redacted: "posture"` holding) → **RG-0198 still open, deliberately** | PROBED |
| TLS certificate | valid to **2026-11-22 02:55 GMT (85 days)**, Google Trust Services WE1 | PROBED |
| `regression_ledger.py` | **exit 0 · every locked fix holding · 0 REGRESSED · 11 open · 0 UNVERIFIED** *(first run had 2 NOT EVALUATED — fastapi absent in the sandbox again; `maint_deps.py` run per RG-0200 and the board re-run clean)* | EXECUTED |
| `rulings_check.py` | **61 rulings, 0 FAIL, 0 WARN** (RUL-060 launch-special ON and RUL-061 now on the board) | EXECUTED |
| `eula_sync.py --check` | **in sync**, 117,749 B across the three copies | EXECUTED |
| `check_canon_pointers.py` | **ALL IN LINE ✓** — docs ↔ `canon.yml` agree, `eula = v1.15` both sides | EXECUTED |
| `david_queue.py` | 12 items, **6 open** (D5, D6, D9, D10, D11, D12) | EXECUTED |
| `git log origin/deploy..HEAD` | **13 commits, 37 files — 0 in `deploy_manifest.txt`.** No app behaviour unpublished | EXECUTED |

### EXECUTED THIS RUN — what Claude did rather than reported

1. **The alert path was PROVEN, not assumed.** `UPTIME_DEPLOYED.md` said the first heartbeat lands
   06:00 UTC on launch morning and "do not assume it works because the deploy succeeded." The inbox
   was probed: **the email is there, 06:00:22Z.** `LAST_HEARTBEAT` rolled forward to 2026-08-29 in
   `UPTIME_DEPLOYED.md` with the evidence written beside it (backup kept).
2. **The ledger's sandbox blind spot was cleared again** (fastapi/httpx absent → RG-0181/0182 NOT
   EVALUATED on the first run). `scripts/maint_deps.py` run per RG-0200's step-0 clause; board
   re-run: **exit 0, both entries evaluated `[ ok ]`, 0 UNVERIFIED.** *Sandbox-local by nature — the
   sandbox is rebuilt between runs, so each sweep must repeat this. Recorded so the next session
   runs `maint_deps.py` before believing an UNVERIFIED count.*
3. **Deploy debt re-read against the manifest rather than counted** — 13 commits looked like debt;
   0 of 37 files deployable. The number alone would have invited a launch-day deploy for nothing.
4. **This register rewritten from today's probes** — RED emptied on evidence, verdict moved
   AMBER → GREEN, David's table cut to the 6 genuinely-open items.

### NOT DONE, DELIBERATELY — RG-0198, unchanged, and the reason still stands

`GET /dashboard/summary` still narrates engineering state to an anonymous caller. The fix needs a
deploy and touches the endpoint both operator consoles read with no credential — **changing it
unwatched on launch day is how a console goes dark over launch weekend.** It stays in the ledger,
asserting, until the first post-launch deploy window. (Same reasoning holds for DW-062's dead
example.com links inside the bulk-import CSV *template strings* — an ms.js change, rides the first
post-launch deploy, not today.)

---

## MONEY

| Service | State | Grade | Cost | Blocks today? |
|---|---|---|---|---|
| **Paystack** (business 1777715) | LIVE + approved, intl + Apple Pay on. `/payment/test` → **`paystack_connected: true`** (re-probed today). Webhook secret armed, RG-0091 LOCKED. ✅ **2FA ON — David confirmed 28 Aug** (D2 closed). Remaining: the one detached-credit E2E buy (D9) | PROBED | 2.9% + R1 | No |
| **FNB business account** | Open | READ | — | No |
| **CIPC** | Company done (2026/340128/07). Provisional patent not filed (~R900, BACKLOG A7) | READ | R900 one-off | No |
| **Accountant** | **Not engaged.** RUL-023: month 1, "not optional and not deferrable" | READ | R2,500/mo | No |
| **Paddle** (MoR, phase 2) | Account not opened; pre-check never done | READ | 5% + $0.50 | No |

## AI PROVIDERS

| Service | State | Grade | Blocks today? |
|---|---|---|---|
| **OpenAI** (BASE lane, 100% of live traffic) | Serving — `ai_provider.active: openai`, card current (`2026-08-26.1`), re-probed. **No production golden run on record** (RG-0132 open): `scripts/golden_seam_v2.py` on the box with the production key, first post-launch window | PROBED | No — tracked by machinery |
| **Anthropic API** (failover) | **No key on the server, by decision** (SPEND-GUARD-1). Failover PROVEN in the decision layer — RG-0128 LOCKED | EXECUTED | No |
| **Anthropic subscription** (Fable, fix agent) | **DROP decided 28 Aug (D8): RUL-013's no-renew default executes — Fable is OUT from 1 Sep.** Successor wired and re-verified on source: `TASK_MODEL design → openai gpt-5.6-sol`, Scaleway `mistral-medium-3.5-128b` standby. **Residue: if the subscription auto-renews in the account, the cancel click before the billing date is David's** | READ (code) + DAVID (decision 28 Aug) | No |
| **Gemini** | 🟠 **Key still ABSENT** (probe: not in `ai_provider.available`). Photo anonymisation stays **reject-only** (RUL-033); RG-0121 OPEN by design. D5 has the exact steps incl. the $10/mo vendor-side spend cap; paid tier chosen deliberately (free tier logs traffic) | PROBED | No — quality cost only |
| **Scaleway** (EU last resort) | Configured, free tier, price unobservable | READ | No |

## IDENTITY · EMAIL · SIGN-IN

| Service | State | Grade | Blocks today? |
|---|---|---|---|
| **Google OAuth** | ✅ **LIVE** — `google:true`; start 302s to Google with the real client_id (re-probed today). RG-0111 LOCKED. **Do not re-raise this lane** | PROBED | No |
| **Google consent screen** | ✅ **PUBLISHED — "In production"**, External, verification not required (27 Aug, console). Week-1 residuals: user cap displayed 0/100; branding not shown | READ (console, 27 Aug) | No |
| **Apple Sign-In** | **OUT by ruling (RUL-030).** start → 503, enforcing (re-probed). Never re-propose | PROBED | — |
| **Didit** (DHA ID check) | **ARMED** — `available:true`, `price_t:1` (re-probed). Still no real NPR query has ever run; billing shape settles on D10's one live check. RG-0136 LOCKED (safety properties) | PROBED | No (never a blocker, RUL-039) |
| **Resend** (app sending) | Sending live, **free tier — the $20/50k flip is D6, due TODAY at the launch flip (pre-approved B7)**. `mail.trustsquare.co` verified. The ~5-min 422 is the HEALTHY answer (INFRA-RESEND-1) — settled, do not re-raise | PROBED (22 Aug send path; delivery re-proven today via the heartbeat, same Resend account) | The flip is today's one operational to-do |
| **Resend** (RED-alert watch key) | ✅ **ALIVE — re-installed 28 Aug, PROBED 200 from the box; delivery re-proven TODAY by the 06:00 heartbeat arriving.** RG-0201 LOCKED (rotation refreshes the watch copy — the orphaning class is dead). *Two different credentials from the app key — do not merge them again* | PROBED | No |
| **Gmail SMTP** (fallback) | Authenticated 22 Aug. Still sends from a personal address | PROBED (22 Aug) | Presentation risk only |
| **support@trustsquare.co** | ✅ RG-0174 LOCKED: inbound routes to the SUPPORT pipeline, ONE reply per inbound | EXECUTED | No |
| **RED-alert channel** | ✅ **PROVEN END-TO-END TODAY.** Worker (edge, no SSH, no box dependency) → Resend → inbox, exercised 06:00 UTC. DW-073's structural complaint (RED path = one SSH command to the very box being monitored) is answered by the watcher's independent transport; the daily-watch row closes on its own check | PROBED | No |
| **n8n** | Self-hosted, running (verified 2 Jun) | READ | No |
| **WhatsApp / Meta** | **Not a dependency.** Open question is AL-8, the SEV-1 wake channel | READ | No |

## INFRASTRUCTURE

| Service | State | Grade | Cost | Blocks today? |
|---|---|---|---|---|
| **Hetzner CPX32** | Live and serving. **Single point of failure** — accepted for launch scale. Firewall self-heal ARMED (RG-0188 ok). Account has **no 2FA** (noted; week-1 candidate for David's console pass). Disk 45% used | PROBED | **EUR 15.49/mo grandfathered — RUL-025: do NOT rescale** | No |
| **Hetzner Object Storage** | Live, daily 3AM backup, 14-day retention | READ | EUR 5.99 | No |
| **Cloudflare** (DNS/CDN/registrar/Workers) | Live. **WAF deliberately open** (RUL-034); `/flags` 200 anonymous — expected on public day. Now also hosts the uptime Worker (free plan) | PROBED | Free | No |
| **SSL** | ✅ valid to **2026-11-22 (85 days)**, Google Trust Services WE1 | PROBED | Free | No |
| **Domain registrar** | ✅ Cloudflare · expires **2026-12-30 (123 days)** · auto-renew ON · lock ON. RG-0137 LOCKED. DNSSEC unsigned (noted, not raised) | PROBED (28 Aug) | Included | No |
| **GitHub** | Live. Deploy debt 13 commits, **none deployable** — see above | EXECUTED | Free | No |
| **External uptime monitor** | ✅ **LIVE — Worker `trustsquare-uptime`, cron */5, 2-strike alert, daily heartbeat; probe half AND alert half both PROVEN as of this morning.** RG-0138 LOCKED (7-day heartbeat staleness tripwire) | PROBED | Free | No |

## DATA FEEDS

**Live:** Travelpayouts flights Data API (partner 758984; `data.flights: true` re-probed; token
UNROTATABLE-ACCEPTED), Numista (RG-0150 polices the boundary), free keyless set (OSM, Scryfall,
Wikidata, Frankfurter — RUL-022, no paid FX ever).
**Tours: DECLINED 24 Aug**, 26 available / 20 blocked (incl. Booking.com, Viator, GetYourGuide).
RUL-041 bars an unchanged resubmit; **David picks the moment — today's public launch is the first
materially changed face** (D11). Aviasales flights unaffected. Drive loader stays OFF (RG-0025
inverted — no third-party script on any app page).
**Affiliate lane:** server-side link-out only (TP-LINKOUT-1), fails closed, dark by flag — RG-0181
re-evaluated `[ ok ]` this run.
**Deliberately dark:** JustTCG, Duffel, AeroDataBox, Mapbox, GeoNames, Places (`false` on /flags).
**Closed:** Google Places (**OUT — silent ~$360 bill, never re-propose**), Amadeus (portal dead 17 Jul), BrickLink.
**Unknown:** eBay keyset ("pending ~1 day" on 7 Jun — no later entry says it arrived).

---

## DOCUMENTS

| Document | State | Grade | Gate? |
|---|---|---|---|
| **EULA** | **v1.15 LIVE** — `/terms` re-probed today (122,935 B page, "EULA v1.15" in the served copy). Three copies byte-in-sync (117,749 B). `canon.yml` ↔ `LEGAL_VERSIONS.md` agree | PROBED | Counsel (A6) is **NOT a gate** (RUL-020) |
| **Privacy Policy** | `privacy.html` live-exempted at origin (migration 021); BACKLOG A1 still open | READ | Bar G7 |
| **Privacy UK/US/AU supplements** | Never drafted; matters because RUL-019 made launch worldwide | READ | Bar G7 · David confirms scope, Claude drafts |
| **IP Brief v6** | DRAFT, counsel-gated, lands with the EULA | READ | Not in the bar |
| **WhitePaper v3.11** | DRAFT (v2 is the published prior-art defence) | READ | No |
| **CC-002 pricing/AI canon** | Deferred to the first post-launch week (from Mon 8 Sep) by David 21 Aug | READ | Deferred by ruling |

---

## WATCH-OUTS — contradictions on disk, stated not resolved

1. **`.env` files prove nothing** — verify at the point of USE (RG-0147, LOCKED).
2. **`AGENT_BRIEFING` v1.9 is stale** on Paystack — treat its other rows with the same caution.
3. **"READY" is not "works"** — the Didit probe is a presence check. No real NPR query has run (D10).
4. **`BACKLOG.md`'s header still reads "Updated S140 · 18 June 2026"**; bodies current, headers rot.
5. **The scheduled task's own prompt is now stale on EIGHT rows** — the six listed 28 Aug (secrets
   rotation "BLOCKING" — done 22 Aug, RG-0146/0147 LOCKED · the Resend-422 misread · "uptime
   monitor not built, no vendor" — **now live and proven** · "domain recorded NOWHERE" — RG-0137
   LOCKED · "nothing says what replaces Fable" — RUL-013 + D8's DROP decision · Google OAuth
   residue) **plus two more:** it says **Paystack 2FA is not set up** (David confirmed ON, 28 Aug)
   and that **RG-0136 "stays OPEN"** (LOCKED 21 Aug; the billing question lives on D10, not in the
   ledger). The task also self-terminates after 1 Sep by its own text, so fixing the prompt is
   optional — but no future sweep should re-raise these eight.
6. **`OPEN_LOOPS.md`'s 🔴 BLOCKING NOW section** still physically carries the discharged B1 row +
   correction notes (additive-edit discipline); its two "genuine threats" (watcher + key) are now
   BOTH closed — moves to CLOSED wording at the next attended reconciliation.
7. **`DAILY_WATCH/OPEN_ITEMS.md` rows DW-073 / DW-076** predate yesterday's fixes; their closes
   belong to the daily watch's own re-run (its file, its rules — not edited by this sweep). Today's
   heartbeat evidence is recorded in `UPTIME_DEPLOYED.md` where RG-0138 reads it.
8. **`david_queue.py` still counts D1 and D4 as hand-marked** (RG-0199's open line) even though both
   verify methods now pass — the queue's method should close them on its next attended run.

### Corrected 22–29 Aug (stands — do not re-raise)

- **Secrets rotation is DONE** (22 Aug; RG-0146/0147 LOCKED). Residue: D12 token deletions;
  FOUNDERS_ID_SALT rotate-or-accept is Claude's pending call.
- **Resend's ~5-min 422 is the HEALTHY answer** (INFRA-RESEND-1); the watch key was the dead one and
  is now alive + class-fixed (RG-0201).
- **"Nothing on disk says what replaces Fable" — wrong.** RUL-013 + `ai_provider.py` + D8 DROP.
- **`bit_flags.auth_fail_closed: false` is a MISREAD** — narrowing switch; real control fail-closed
  (`B-NEG-AUTH` PASS 401).
- **RDAP is the wrong door for `.co`** — `whois.iana.org` → `whois.registry.co`.
- **SSL renews 2026-11-22**, not 24 Sep. **`post_deploy_status.json` serves at `/static/`.**
- **Anonymous PII on `/launch-api/prospects/list` is SHUT** (RG-0176 LOCKED).

---

## VERDICT

**SOFT LAUNCH IS TODAY (Sat 29 Aug) · 3 days to full launch (Mon 1 Sep) · GREEN.**

Every functional probe is green, the ledger holds every locked fix with **0 regressed and 0
unverified**, all 61 rulings are reflected, the EULA is live and in sync, the money rail answers,
strangers can sign in, the launch special is armed (RUL-060), and — the piece that kept yesterday
AMBER — **the site goes public watched and alarmed, with the alert path proven end-to-end by this
morning's heartbeat in David's own inbox.** One operational to-do rides today's flip: D6, the
pre-approved Resend $20 tier, so public sign-in volume never hits the free-tier cap. Then D8's
cancel click before 1 Sep. Everything else is post-launch.
