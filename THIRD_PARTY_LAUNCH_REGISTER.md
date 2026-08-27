# THIRD-PARTY LAUNCH REGISTER
**Every external account, key, subscription and legal document — and whether it is actually ready.**

*Created 21 Aug 2026 · Soft launch to public **Fri 29 Aug 2026** · Full launch **Mon 1 Sep 2026** (RUL-001)*
*Last ship day **Wed 27 Aug — TODAY.** Nothing deploys on launch eve.*
*Maintained by the daily scheduled task `pre-soft-launch-third-party-check`. It rewrites the status column from **evidence**, not from what this file claims.*

**Last swept: 2026-08-27 ~05:0x–07:2x UTC · 2 days to soft launch · verdict AMBER.**
*Verdict held at AMBER, but the composition changed completely: **three of yesterday's seven REDs
are CLOSED on live probes** — the migration chain is unjammed, a full `script-src` CSP is enforced
at the edge, and deploy debt is **ZERO for the first time in this register's life**. What remains
red is no longer code. It is four things only David can do, and one of them (the external uptime
watcher) has now been sitting built-and-undeployed for five days with launch weekend approaching.*

Evidence grade on every row: **PROBED** (measured live this run) · **EXECUTED** (the code path ran) ·
**READ** (a file says so) · **UNRECORDED** (nobody has ever written it down).
Only PROBED is reported as fact — the 21 Aug lesson (the register said Google OAuth was dark;
`/auth/providers` said otherwise; the probe won).

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
READY TO LOCK the moment the values above are real. **RDAP was NOT re-attempted this run.** Five
endpoints over four consecutive sweeps have failed and the IANA bootstrap lists no `.co` service —
that is a settled negative, recorded 26 Aug, and re-running it is the sweep spending time to
re-learn something it already knows. **These four fields will never be filled by machinery.** One
glance at David's registrar login settles all four, permanently.*

---

## 🔴 RED — WHAT BLOCKS OR THREATENS 29 AUG

**Two days out, nothing on this list is code. Every remaining item is a click, a key or a login.**

1. **External uptime monitor STILL NOT DEPLOYED** (RG-0138, L8) — **built 22 Aug, day 5 unblocked.**
   This is now the single worst blind spot on the page and the only RED that gets worse by waiting.
   Launch weekend is the exact window in which nobody is watching a console: the daily watch is
   desktop-bound and runs once at 06:30, and the RED-alert path is one SSH command to the same box
   that would be down. An edge-hosted watcher owes nothing to the box or the desktop. **3 commands,
   `ops/cloudflare/UPTIME_MONITOR.md`** — Cloudflare Worker, 5-min cron, 2-strike DOWN alert,
   recovery notice, daily heartbeat so a dead monitor cannot read as a healthy site. No new vendor,
   no cost. It must go in **after** the Resend watch key (#2), so the fresh key goes in with it.
2. **The RED-alert key is DEAD — day 3** (DW-076). The watch's separate Resend key in
   `/etc/marketsquare/resend.watch.conf` has been returning `401 validation_error` since the 22–23
   Aug rotation. It was found only because a real RED was exercised on 26 Aug and did not deliver.
   **Nothing has been able to wake David about an outage for five days.** Root on the box +
   credential, so David's (RUL-037). Not fixable from this vantage: this sandbox holds no SSH key.
3. **Google consent screen Published-or-Testing is UNRECORDED** (RG-0139). A Testing-mode app 302s
   identically to a Published one — invisible to every instrument we own until a stranger tries to
   sign in on launch morning. OAuth start re-PROBED this run: **302 → accounts.google.com** with a
   real client_id and the correct `redirect_uri`. The lane works; only its audience is unknown.
   **This is the last sign-in failure mode that would present for the first time to real users.**
4. **Domain registrar / expiry / auto-renew UNRECORDED** (RG-0137). The one dependency that can end
   everything silently, and the only one with no instrument at all.

### CLOSED SINCE YESTERDAY — all three on live probes, not on a file

- ~~**The migration chain is JAMMED** (RG-0125, DW-066)~~ — ✅ **CLOSED.**
  `/static/post_deploy_status.json` now reads `generated_at 2026-08-27T03:46:59Z` ·
  `seed ok` · `ladder_seed ok` · **`migrations ok — "none pending"`.** 033 is through; nothing sits
  dead behind it. RG-0125 reads `[ ok ]`.
- ~~**No `script-src` CSP at the edge** (RG-0178/DW-069)~~ — ✅ **CLOSED.** PROBED on both `/` and
  `/terms`: `default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com
  https://cdnjs.cloudflare.com; …; object-src 'none'; base-uri 'self'; form-action 'self';
  frame-ancestors 'self'`. **Yesterday's CTO note hypothesised a Cloudflare-edge emitter and it is
  now DISPROVEN** — the emitter was nginx all along and 033 had been measuring the port-80 301
  redirect. Recorded here because a hypothesis that outlives the probe that killed it is the next
  session's wrong turn. RG-0178 promoted to LOCKED 27 Aug.
- ~~**Deploy debt**~~ — ✅ **ZERO.** `git log origin/deploy..HEAD` = **0 commits**.
  `origin/deploy` = `2341ab6`, released **27 Aug 05:45 SAST**. Both of yesterday's unpublished
  commits (`97f8168` CSP-SCRIPT-SRC-5, `da85045`) have ridden.
- Also closed since yesterday's AMBER shortlist: **RG-0156** (orchestrator.html — through the
  manifest, no hardcoded access code) and **RG-0160** (both example dossier PDFs serve live and the
  teaser links them) both read `[ ok ]`.

**AMBER, close behind:** RG-0173 (agency journey probe — the machinery answer to "how did we miss
the funnel breaks", still open) · RG-0180 (`connect-src` still `'self' https:`, so a script that
somehow executed could still exfiltrate — but `script-src` now stops it executing, which was the
load-bearing half) · **RG-0198, opened this run** (below).

## DAVID-ONLY ACTIONS, IN DATE ORDER

| When | Days left | Action | Why only David |
|---|---|---|---|
| ~~NOW~~ **DONE 26 Aug** | — | ✅ Hetzner firewall IP · ✅ `LAUNCH_API_KEY` — both re-PROBED holding this run (port 22 open 3/3; `/launch-api/prospects/list` = **401**) | — |
| ~~NOW~~ **DONE (found this run)** | — | ✅ **`.secrets/hetzner_token.txt` is now populated** (64 B). `hetzner_fw_selfheal.py` is armed and **RG-0188 reads `[ ok ]`** — yesterday it exited "NO TOKEN, nothing changed". The next lockout is no longer a hand-fix. *Residual, low stakes: no `.secrets/cf_waf_token.txt`, so the Cloudflare half is unarmed; that half retires with the pre-launch gate* | Was a credential (RUL-037) |
| **NOW** | 2 | 🔴 **Paste the current Resend key into `/etc/marketsquare/resend.watch.conf`** (keep `0640 root:msdeploy`). Dead since the 22–23 Aug rotation — day 3. RED #2 | Root on the box + credential. DW-076 |
| **NOW** | 2 | 🔴 **Deploy the uptime watcher** — 3 commands, `ops/cloudflare/UPTIME_MONITOR.md`. Do it *after* the line above. RED #1 | Cloudflare token + Resend secret. RG-0138 |
| **NOW** | 2 | **Google Cloud console → OAuth consent screen: PUBLISHED or Testing?** Write it into `GOOGLE_CONSENT_SCREEN:` above | Console login. RG-0139 |
| **NOW** | 2 | **Registrar, expiry and auto-renew for trustsquare.co** → the four `DOMAIN_*` fields above. Machinery has permanently failed this; it will not be asked again | RDAP dead for `.co`. RG-0137 |
| **TODAY, Wed 27 Aug** | 0 | **The last pre-launch ship, IF one is still wanted.** The 05:45 release already carried everything that was outstanding; the only thing added since is this run's four ledger/instrument commits, which change no app behaviour. **A further deploy today is optional, not required** | Deploys reserved (RUL-037) |
| **27 Aug — today** | 0 | Turn on **Paystack 2FA** (reminder set for today) | Account security |
| **Overdue (was ~25 Aug)** | — | Buy the budget-capped **Gemini** key, paste to server. Still absent; photo anonymisation stays reject-only (RUL-033) | Money + secret |
| **Launch flip** | 2 | Activate **Resend $20/mo 50k tier** (pre-approved B7 — execution, not a new decision) | Spend |
| **Launch flip** | 2 | Set `LAUNCH_SPECIAL_DEADLINE=2026-09-01` on **both** MarketSquare and CityLauncher (CityLauncher's `.env` still has no such key at all) | Config both sides |
| **Before 1 Sep** | 5 | **Renew or drop the Anthropic subscription.** Successor is decided AND wired — re-verified on disk this run: RULINGS RUL-013 plus `ai_provider.py` `TASK_MODEL["openai"]["design"] = "gpt-5.6-sol"`, Scaleway standby. **Nothing is unbuilt here** — this is purely the subscription question | Spend |
| **Once** | — | One smallest-pack **Paystack** buy with tab-close → closes the detached-credit E2E. `/payment/test` → `paystack_connected: true` re-probed today | Real money on the live rail |
| **Once** | — | One real **Didit** ID check → settles free-500-vs-$1.10 billing. **Re-verified this run: lane ARMED** (`available:true`, `price_t:1`, *"READY — sellers can buy a check"*) and **still no real NPR query has ever run.** RG-0136 reads `[ ok ]` because it asserts the SAFETY properties (a PARTIAL_MATCH never passes, a provider failure never charges, the tick never gates an introduction); the billing shape is unanswerable without one live check | Real money |
| **When convenient** | — | Delete the two superseded **Cloudflare tokens** (`MarketSquare Media`, `Trustsquare Cache Purge`) | Rotation residue, not blocking |
| **David picks the moment** | — | **Travelpayouts tours resubmit.** Declined again 24 Aug; 26 available / 20 blocked incl. Booking.com, Viator, GetYourGuide. Per RUL-041 never resubmit unchanged — **soft launch on Friday is the natural moment** | Commercial |
| **Month 1** | — | Appoint the **accountant** (R2,000/mo + R500 software, RUL-023) | Engagement + spend |

## PROBED THIS RUN — the live facts

| Probe | Result | Grade |
|---|---|---|
| `GET /health` | `ok` · `TrustSquare BEA` · **v1.3.1** · db primary present (2,879,488 B), integrity ok | PROBED |
| `GET /auth/providers` | `{"google":true,"apple":false}` | PROBED |
| `GET /auth/oauth/google/start` | **302 → accounts.google.com**, real client_id, `redirect_uri=https://trustsquare.co/auth/oauth/google/callback` | PROBED |
| `GET /auth/oauth/apple/start` | **503** — RUL-030 enforcing itself | PROBED |
| `GET /id-verify/status` | `available:true` · `"READY — sellers can buy a check"` · `price_t:1` | PROBED |
| `GET /payment/test` | `{"status":"ok","paystack_connected":true}` | PROBED |
| `GET /terms` | 200, serving **EULA v1.15** | PROBED |
| `GET /dashboard/bit` | **8/8 PASS**, worst 0, ran 2026-08-27T05:08:58Z. Includes `B-NEG-AUTH` (S1) = PASS, `HTTP 401` | PROBED |
| `GET /flags` | 200 anonymous (gate deliberately down, RUL-034). `ai_provider.active: openai`. **`funnel.card_version` is now `2026-08-26.1`** — was a week-stale `2026-08-19.1` yesterday; DW-067's residual has cleared | PROBED |
| `GET /launch-api/prospects/list` | **401 `X-Launch-Key required`** — holding | PROBED |
| **CSP on `/` and `/terms`** | ✅ **Full policy served on BOTH** — `default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com https://cdnjs.cloudflare.com; … object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'`. Plus HSTS 31536000, `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff` | PROBED |
| `/static/post_deploy_status.json` | `generated_at 2026-08-27T**03:46:59**Z` · seed ok · ladder_seed ok · **migrations ok, "none pending"** — the chain is UNJAMMED | PROBED |
| `GET /dashboard/summary` | 200 anonymous, 1,360 B. `redacted: "posture"` — **POSTURE-REDACT-1 is working.** But it still serves `recentChangelog`, `lastDone`, `nextGoals`, `priorityItems` verbatim → **new ledger entry RG-0198** | PROBED |
| origin port 22 (`178.104.73.239:22`) | **OPEN — 3/3**, banner `SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.1` | PROBED |
| TLS certificate | valid to **2026-11-22 (87 days)**, Google Trust Services WE1 | PROBED |
| `git log origin/deploy..HEAD` | ✅ **0 commits. Deploy debt is ZERO.** `origin/deploy` = `2341ab6`, 27 Aug 05:45 SAST | EXECUTED |
| `regression_ledger.py` | **exit 0** · **191 entries · 177 holding · 0 REGRESSED · 14 open · 0 READY TO LOCK · 0 UNVERIFIED** (opened the run at 190/176/0/13 + 1 ready-to-lock) | EXECUTED |
| `rulings_check.py` | **58 rulings, 0 FAIL, 0 WARN** (was 56 on 26 Aug — RUL-057/058 landed and are reflected) | EXECUTED |
| `eula_sync.py --check` | **in sync**, 117,749 B across the three copies | EXECUTED |
| RDAP for trustsquare.co | **Not attempted — settled negative.** 5 endpoints × 4 sweeps, no `whois` binary, no `.co` service in the IANA bootstrap | (recorded 26 Aug) |

### EXECUTED THIS RUN — four fixes, all in-repo, none needing a deploy

1. **RG-0144 promoted OPEN → LOCKED** (DW-079). It was printing `READY TO LOCK` on the first run
   after POSTURE-REDACT-1 shipped. A fix that prints READY TO LOCK and is never promoted cannot
   trip red when it rots — that is the exact failure the ledger exists to prevent, so it was
   promoted in the same session it started passing.
2. **RG-0192 stopped lying about its own state** (DW-080). A LOCKED entry was still printing
   `READY TO LOCK -- google_maps.py no longer reads the remaining-count as an absolute cap`. An
   instrument that tells a session something untrue about itself is the same class of fault as a
   stale doc. Now reads `holding -- …`.
3. **LEDGER-UNVER-CAUSE-1 — the ledger stopped blaming the network for a missing library.**
   *Found by being bitten by it, first thing this run.* The `NOT EVALUATED` summary asserted,
   unconditionally, *"this machine cannot reach https://trustsquare.co"* — and printed exactly
   that on a run whose two UNVERIFIED entries were **`fastapi` dependency demotions**, on a machine
   that was curling the site fine in the same minute. RG-0187 demoted them honestly; the summary
   then named the wrong cause, which sends the next session to fix the wrong thing (the RG-0117
   mistake one layer up). The summary now reads the recorded reason back off each entry, lists the
   entry ids, and states the network verdict from the **measured** `_NET` preflight, never from
   assumption. **Proven both ways this run:** with `fastapi` blocked it prints the real cause plus
   *"This machine CAN reach https://trustsquare.co, so the site is not the cause"*; with it present
   the board is clean. Asserted by an extension to **RG-0187**'s scope — a fix without an assertion
   is half a fix.
4. **RG-0198 opened** — see below. Filed as machinery per RUL-037, not as a sentence to David.

### NEW THIS RUN — RG-0198, the other half of the dashboard leak

`GET /dashboard/summary` answers an anonymous stranger with `redacted: "posture"` — RG-0144's
security half is genuinely fixed and holding. Beside it, the same 1,360-byte payload still carries
**today's internal engineering changelog verbatim, headline included**, the session number and
basis, live counts (listings / sellers / introductions / Tuppence top-ups), and a `priorityItems`
list whose first entry literally begins *"**DAVID — DEPLOY the 22 Aug work.**"*

Rated deliberately **below** the posture leak: it names no control to attack, so it is
confidentiality and presentation, not a way in. It is **split into its own entry rather than folded
into RG-0144** precisely so it cannot ride on RG-0144's coat-tails — one assertion covering both
halves would go green the moment either half passed.

**Not fixed this run, and the reason is on the record rather than in someone's head.**
POSTURE-REDACT-1's own comment states that *both operator dashboards fetch this endpoint with no
credential*, and that "a fix that breaks the console will be reverted under pressure". The honest
fix is two-sided — the consoles start sending the admin key, and the anonymous payload keeps its
operational fields while the narrative fields return withheld — and the second side cannot be
verified from this vantage without being able to load the consoles. **Quietly changing a live
endpoint the operator console reads, on the last ship day before soft-public, is how a console goes
dark unwatched over a launch weekend.** It is in the ledger, where it will keep asserting until it
is done.

---

## MONEY

| Service | State | Grade | Cost | Blocks 29 Aug? |
|---|---|---|---|---|
| **Paystack** (business 1777715) | LIVE + approved, intl + Apple Pay on. `/payment/test` → **`paystack_connected: true`** (re-probed). Webhook secret armed, RG-0091 passing. **2FA not set up — the reminder is for TODAY** | PROBED | 2.9% + R1 | No — 2FA + E2E close-out remain |
| **FNB business account** | Open | READ | — | No |
| **CIPC** | Company done (2026/340128/07). Provisional patent not filed (~R900, A7) | READ | R900 one-off | No |
| **Accountant** | **Not engaged.** RUL-023: month 1, "not optional and not deferrable" | READ | R2,500/mo | No |
| **Paddle** (MoR, phase 2) | Account not opened; pre-check never done | READ | 5% + $0.50 | No |

## AI PROVIDERS

| Service | State | Grade | Blocks 29 Aug? |
|---|---|---|---|
| **OpenAI** (BASE lane, 100% of live traffic) | Serving — `/flags` shows `ai_provider.active: openai`, card version now current (`2026-08-26.1`). **No production golden run on record** (RG-0132 open): run `scripts/golden_seam_v2.py` on the box with the production key | PROBED | No — tracked by machinery |
| **Anthropic API** (failover) | **No key on the server, by decision** (SPEND-GUARD-1). Failover PROVEN in the decision layer — RG-0128 LOCKED | EXECUTED | No |
| **Anthropic subscription** (Fable, fix agent) | Active, **time-boxed to 1 Sep** (RUL-013 — "ENDS 1 Sep 2026 and does not renew by default"). Successor decided AND wired, **re-verified on disk this run**: `ai_provider.py` `TASK_MODEL["openai"]["design"] = "gpt-5.6-sol"`, Scaleway standby. Only the renewal is open — a spend question | PROBED (code) + READ | No |
| **Gemini** | 🟠 **Key still ABSENT.** Funds were expected ~25 Aug. Photo anonymisation stays **reject-only** (RUL-033); RG-0121 OPEN by design. Price row corrected 26 Aug to first-party ($0.75 in / $3.75 out); canary year-1 $845, still ~51% cheaper than terra-only. **A re-cost, not a re-decision — RUL-032 stands** | PROBED | Indirectly — reject-only until the key lands |
| **Scaleway** (EU last resort) | Configured, free tier, price unobservable | READ | No |

## IDENTITY · EMAIL · SIGN-IN

| Service | State | Grade | Blocks 29 Aug? |
|---|---|---|---|
| **Google OAuth** | ✅ **LIVE** — `google:true`; start 302s to Google with a real client_id (re-probed). RG-0111 LOCKED | PROBED | No |
| **Google consent screen** | ⚠️ **UNRECORDED — Published or Testing unknown.** Not probeable anonymously | UNRECORDED | **Potentially yes** — RED #3, RG-0139 |
| **Apple Sign-In** | **OUT by ruling (RUL-030).** start → 503, enforcing (re-probed). Do not re-propose | PROBED | — |
| **Didit** (DHA ID check) | **ARMED** — `available:true`, `price_t:1` (re-probed). **Still no real NPR query has ever run**, so the billing shape and the real-registry outcome mapping are both untested. One real check is on David's once-list | PROBED | No (never a blocker by RUL-039) |
| **Resend** (app sending) | Sending live, free tier. `mail.trustsquare.co` verified, root domain not. **The ~5-min 422 is the HEALTHY answer** (INFRA-RESEND-1) — do not re-raise | PROBED (22 Aug) | Operationally yes — it carries sign-in. $20 tier flips at launch |
| **Resend** (RED-alert watch key) | 🔴 **DEAD — day 3.** Separate key in `/etc/marketsquare/resend.watch.conf`, `401 validation_error` since the 22–23 Aug rotation. **RED #2** | PROBED (26 Aug) | **Yes, operationally** |
| **Gmail SMTP** (fallback) | Authenticated 22 Aug. Still sends from a personal address | PROBED (22 Aug) | Presentation risk at public launch |
| **support@trustsquare.co** | ✅ RG-0174 LOCKED: inbound routes to the SUPPORT pipeline, ONE reply per inbound, personal inbox is dead-letter only | EXECUTED | No |
| **RED-alert channel** | 🟠 **Transport restored, key still dead.** SSH is back (port 22 probed open 3/3), so the channel is no longer sharing a failure with its own transport — but the key it sends with is dead, so it still cannot deliver. DW-073 + DW-076. The uptime watcher (RED #1) is the structural answer to both | PROBED | **Yes, operationally** |
| **n8n** | Self-hosted, running (verified 2 Jun) | READ | No |
| **WhatsApp / Meta** | **Not a dependency.** Open question is AL-8, the SEV-1 wake channel | READ | No |

## INFRASTRUCTURE

| Service | State | Grade | Cost | Blocks 29 Aug? |
|---|---|---|---|---|
| **Hetzner CPX32** | Live and serving. **Single point of failure.** Port 22 open (3/3, re-probed). ✅ **Firewall self-heal now ARMED** — `.secrets/hetzner_token.txt` populated, RG-0188 `[ ok ]`. Account has **no 2FA** (noted in passing) | PROBED | **EUR 15.49/mo grandfathered — RUL-025: do NOT rescale** | No |
| **Hetzner Object Storage** | Live, daily 3AM backup, 14-day retention. ("HETZNER_S3" keys are actually Cloudflare R2 — SECRETS_REGISTER) | READ | EUR 5.99 | No |
| **Cloudflare** (DNS/CDN/WAF/R2/email) | Live; nameservers `ainsley`/`koa`. **WAF deliberately open** (RUL-034); origin gate down by pre-launch posture (`/flags` 200 anonymous — expected) | PROBED | Free | No |
| **SSL** | ✅ valid to **2026-11-22 (87 days)**, Google Trust Services WE1 | PROBED | Free | No |
| **GitHub** | Live. ✅ **Deploy debt = 0** — everything committed is live | EXECUTED | Free | No |
| **Domain registrar** | ⚠️ **UNRECORDED.** RDAP permanently unanswerable for `.co`; David's login is the only source | UNRECORDED | Unknown | **Potentially catastrophic** — RED #4 |
| **External uptime monitor** | 🔴 **BUILT 22 Aug, NOT DEPLOYED — day 5.** RG-0138. **RED #1** | EXECUTED (source) | Free | See RED #1 |

## DATA FEEDS

**Live:** Travelpayouts flights Data API (partner 758984; `data.flights: true` on `/flags`, re-probed;
token UNROTATABLE-ACCEPTED), Numista (rotated key; RG-0150 polices the data boundary), and the
free keyless set (OSM, Scryfall, Wikidata, Frankfurter, FX per RUL-022).
**Tours: DECLINED 24 Aug** (*"website under development or not yet ready"*) — 26 available / 20
blocked, incl. Booking.com, Viator, GetYourGuide. Per RUL-041 never resubmit unchanged; **David
picks the resubmit moment and Friday's soft launch is the natural one.** Aviasales flights
unaffected. Drive loader stays OFF (RG-0025 inverted — no third-party script on any app page).
**Affiliate lane:** `travelpayouts_partners.py` (TP-LINKOUT-1) — server-side link-out, host
allowlist, fails closed, dark by flag. RG-0181 asserts the invariant; the lane being dark is
deliberate, not a defect.
**Deliberately dark:** JustTCG (key valid, UNSET — free tier is non-commercial), Duffel, AeroDataBox,
Mapbox (`data.mapbox: false`), GeoNames, Places (`data.places: false` — and Google Places is OUT).
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
| **CC-002 pricing/AI canon** | Parked, **78 days** against a 7-day threshold (DW-010, formally deferred by David 21 Aug) | READ | Deferred by ruling |

---

## WATCH-OUTS — contradictions on disk, stated not resolved

1. **`.env` files prove nothing** — verify at the point of USE (RG-0147, LOCKED).
2. **`AGENT_BRIEFING` v1.9 is stale** on Paystack — treat its other rows with the same caution.
3. **"READY" is not "works"** — the Didit probe is a presence check. No real NPR query has run.
4. **`LAUNCH_DEADLINE-1` is unsatisfied on the CityLauncher side** — that `.env` has no
   `LAUNCH_SPECIAL_DEADLINE` at all.
5. **A Testing-mode Google consent screen is invisible to every instrument we own.** The only
   remaining sign-in failure mode that would present for the first time on launch morning.
6. **The scheduled task's own prompt is stale on five rows** and has been for five days. Listed
   once here so no future sweep re-raises them: it calls the **secrets rotation** BLOCKING (done +
   probed 22 Aug; RG-0146/RG-0147 LOCKED and green today), repeats the **Resend malformed-sender
   422** claim (disproven — the 422 is the healthy answer), says the **uptime monitor** has "no
   vendor named" and was "due 22 Aug" without noting it is BUILT and needs only 3 commands, says
   nothing on disk names **Fable's successor** (RUL-013 + `ai_provider.py` both name it), and still
   lists **Google OAuth** residue as though the lane were in doubt. **Refresh the task prompt when
   David next edits it.**
7. **`OPEN_LOOPS.md` still files B1 (secrets) under 🔴 BLOCKING NOW** while the row's own text says
   rotation is complete. Annotated 26 Aug; the row moves at the next attended reconciliation (that
   file has no compiler, so edits stay additive — CHANGELOG-COLLISION-1 class). **Its 🔴 BLOCKING
   NOW section is also now stale in the other direction**: the four items it points at as "what
   genuinely blocks 29 Aug" are three-quarters closed.

### Corrected 27 Aug — files/rows the probes overruled this run

- **`bit_flags.auth_fail_closed: false` was flagged 26 Aug as "worth one look before public
  traffic". The probe says it is a MISREAD, and the correction goes here so it is not raised a
  third time.** `auth_fail_closed` is a **narrowing switch**, not the base auth control:
  `bea_main.py:155` — *"when auth_fail_closed is ON the admin surface narrows to…"* — and
  `ops/bit/bit_mitigator.py` lists it as a SAFE mitigator flag bound to `B-NEG-AUTH`. The actual
  control is already fail-closed and PROVEN live: today's `/dashboard/bit` reports
  **`B-NEG-AUTH` (S1) = PASS, `HTTP 401 (want [401, 403])`**. Nothing to do.
- **"The migration chain is JAMMED" / "no `script-src` CSP at the edge" / "deploy debt = 2
  commits"** (all three, 26 Aug REDs) — **all three overruled by probes this morning.** Rewritten
  above.
- **"If 033 goes ok but RG-0178 stays red, the header is being emitted at the Cloudflare edge"**
  (26 Aug CTO note) — **DISPROVEN.** nginx was the emitter all along; 033 was measuring the port-80
  301 redirect. The note is retired here rather than left to mislead.
- **The ledger's own `NOT EVALUATED` summary** claimed the site was unreachable when the real cause
  was a missing `fastapi`. Fixed and asserted this run (LEDGER-UNVER-CAUSE-1, under RG-0187).
- **"Nothing on disk says what replaces Fable"** (task prompt) — **wrong.** RUL-013 names the
  successor and `ai_provider.py` line 63 wires it. Only the spend decision is open.
- **RDAP** — recorded 26 Aug as permanently machine-unanswerable; **not re-attempted this run**, by
  decision, so the sweep stops paying for a settled negative.

### Corrected 22–26 Aug (stands — do not re-raise)

- **Secrets rotation is DONE** (22 Aug). Residue: two superseded Cloudflare tokens for David to
  delete; FOUNDERS_ID_SALT rotate-or-accept is Claude's pending call.
- **Resend's ~5-min 422 is the HEALTHY answer** (INFRA-RESEND-1) — but the *separate watch key* is
  genuinely dead (DW-076). Two different credentials; do not merge them again.
- **The AI serving lane is resolved**: OpenAI base, Anthropic keyless by decision, failover proven (RG-0128).
- **SSL renewed** — 2026-11-22, not the 24 Sep an older row claimed.
- **`post_deploy_status.json` serves at `/static/`** — the bare path 404s. Do not misread that 404
  as a missing deploy record.
- **Anonymous PII on `/launch-api/prospects/list` is SHUT** (401, re-probed twice since). RG-0176 LOCKED.
