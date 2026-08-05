# Independent Peer Review — 2026-08-05-1255

*Peer: gpt-5.6-terra (second vendor, read-only) · Lens: full · Author: Claude · System Engineer: David*

**Scope:**
  - Records\AI_SERVICES_AUDIT_2026-08-05.md (7,306 chars)
  - Records\PEER_PACK_BEA_EXTRACT.md (103,792 chars)
  - ai_provider.py (14,315 chars)
  - ai_breaker.py (13,316 chars)
  - ai_service_tiers.py (15,900 chars)
  - ai_scoreboard.py (17,186 chars)
  - test_ai_breaker.py (7,904 chars)
  - ai_price_card.json (15,890 chars)
  - ai_funnel_snapshot.json (969 chars)
  - AI_AUTO_FAILOVER_P2_DESIGN.md (14,443 chars)
  - privacy.html (8,059 chars)
  - Records\DRILL_T0_SEAM_2026-08-01.md (1,194 chars)
  - Records\GOLDEN_SET_OPENAI_2026-08-01.md (3,157 chars)

**Usage:** 60536 in / 8699 out tokens · actual cost ≈ $0.2255

---

# Independent Peer Review — Internal AI Services, Round 2

## Overall assessment

The post-fix packet materially improves the original position:

- The single-vendor endpoint gates have been replaced in the supplied endpoints.
- The three prepaid AI services now use a pre-flight Tuppence check and charge after the model response.
- User-facing service copy is vendor-neutral.
- The heartbeat calls `claim_probe()` before issuing direct probes.

However, I do **not** consider the cost-control or deliver-then-charge claims complete. The main remaining defects are:

1. AI services are callable using caller-supplied email addresses without visible user authentication, enabling Tuppence theft/cost consumption.
2. The “hard” cost ceiling is a post-spend ledger check with no reservation, and is bypassable under concurrency; input sizes are also unbounded.
3. The scoreboard sends direct, unclaimed probes that can alter breaker recovery state outside the heartbeat’s atomic lease mechanism.
4. Spend attribution records the configured active provider rather than the provider that actually served a fallback request.
5. KYC documents can be routed to any provider via normal failover, with no demonstrated task-specific processor pinning or upstream URL protection.

---

## Re-judgment of Phase-1 findings F1–F5

| Finding | Verdict | Review result |
|---|---|---|
| **F1 — Anthropic-only gates** | **CONFIRMED, with totality qualification** | The shown service endpoints now use `ai_provider.any_lane_configured()` and the helper correctly tests all configured lanes. I cannot independently validate all 15 claimed replacements because the full `bea_main.py` ranges were not supplied. |
| **F2 — Charge before service delivery** | **PARTIALLY CONFIRMED / NOT COMPLETE** | AI1, AI2, AI3, AI4, and AI5 now perform Tuppence deduction after the model/computation path. But AI1/AI2/AI5 can charge after syntactically valid yet empty/useless model output, and the lack of an atomic balance reservation creates service/cost races. |
| **F3 — “Claude” in customer copy** | **CONFIRMED** | The supplied help-card copy is vendor-neutral (“Our AI”), resolving the stated branding/routing contradiction. |
| **F4 — dashboard Sonnet reference** | **REFUTED as an inference/cost finding on supplied evidence** | The supplied dashboard content merely labels abstract task tiers in a visual map; it is not an inference call, model selection, or metered AdvertAgent call. The claimed original reference at `dashboard.server.html:906` is not supplied. |
| **F5 — P2b/P2c residue** | **PARTIALLY CONFIRMED AS FIXED** | The heartbeat is now implemented and correctly calls `claim_probe()`. The current report’s statement that heartbeat is absent is stale. Dashboard Restore UI evidence remains absent, while the backend restore endpoint and `/flags` breaker payload are shown. |

---

# Findings

## [BLOCKER] Caller-controlled `email` / `seller_email` permits Tuppence charging and AI spending against another account

**Lens:** Security, cost, privacy, integrity  
**Evidence:** `bea_main.py:13743–13762`, `13830–13861`, `14401–14442`, `14942–14961`; `bea_main.py:13697–13714`

The five paid endpoints accept account identity directly from request parameters or body fields:

- AI1: `async def ai_listing_rewrite(listing_id: int, email: str)` at `bea_main.py:13743–13744`
- AI2: `async def ai_seller_audit(listing_id: int, email: str)` at `bea_main.py:13830–13831`
- AI3: `async def ai_price_check(listing_id: int, email: str, ...)` at `bea_main.py:14401–14402`
- AI4: `async def ai_yield_calc(listing_id: int, email: str, ...)` at `bea_main.py:14712–14716`
- AI5: `req.seller_email` is used for both cost ceiling and charge at `bea_main.py:14955`, `14961`, `15053`.

The supplied endpoint bodies show no authentication dependency or binding of the submitted email to an authenticated principal. `_deduct_tuppence()` then debits exactly the supplied address at `bea_main.py:13700–13713`.

For AI3 and AI4, no listing ownership validation is shown at all. An attacker who knows or can guess a target email can submit requests using that email, spend the target’s Tuppence, and consume the platform AI budget. AI1/AI2 add a seller-email comparison, but that comparison still trusts the caller-supplied `email`; it is not authentication.

This is more serious after F2’s deliver-then-charge change because the service may now execute an expensive call before the eventual debit attempt.

**Required discussion:** Every paid endpoint should derive the account identity from authenticated server-side session/API-key/JWT claims, not from query/body data. Ownership checks should compare the authenticated identity to the listing owner. The charge and the AI-cost attribution should use that same identity.

---

## [MAJOR] “Hard” daily cost ceilings are not hard under concurrent requests; no pre-dispatch currency reservation exists

**Lens:** Cost, concurrency, operability  
**Evidence:** `bea_main.py:1596–1650`; AI calls after checks at `13749–13796`, `13836–13898`, `14441–14442` and `14580–14584`, `14760–14761` and `14862–14866`, `14955–15021`; `AI_AUTO_FAILOVER_P2_DESIGN.md:v1.2` “currency budget reservation” remains open

`_check_cost_ceiling()` calculates spend from already-written `ai_spend_log` rows and rejects only when that historical sum is already at or above the cap:

```python
SELECT COALESCE(SUM(est_cost_usd),0) ...
...
if total >= cap: raise HTTPException(429)
```

at `bea_main.py:1617–1644`.

No reservation is written before dispatch. Therefore, N concurrent requests can all observe remaining budget, all pass `_check_cost_ceiling()`, and all dispatch provider calls. Logging occurs only after the call, e.g.:

- AI1: call at `13793–13796`, log at `13800`
- AI2: call at `13895–13898`, log at `13902`
- AI3: call at `14580–14584`, log at `14617`
- AI4: call at `14862–14866`, log at `14899`
- AI5: call at `15018–15021`, log at `15025`.

Thus the ceiling cannot bound actual expenditure under burst traffic. The design itself acknowledges the missing “currency budget reservation,” but the Phase-1 report’s claim that ceilings are “hard” overstates what the code provides.

The guard also explicitly fails open on database/internal errors at `bea_main.py:1600–1602` and `1649–1650`. That may be an availability choice, but it is incompatible with a strict platform-spend guarantee.

**Required discussion:** Decide whether spend containment or availability is senior during DB/ledger failure. If spend containment is required, atomically reserve a computed worst-case charge before dispatch, reconcile the reservation against actual tokens/provider price afterward, and expire/release failed or abandoned reservations.

---

## [MAJOR] Output caps do not bound provider cost because request/input size is unbounded, especially for AI5 images

**Lens:** Cost, performance, denial of service  
**Evidence:** `ai_provider.py:complete()` docstring; `bea_main.py:14957–15021`; `bea_main.py:14993–15012`

The claimed Correction-2 rails cap fallback attempts and pass `max_tokens`, which constrains output tokens. They do **not** bound input tokens or image bytes.

AI5 limits only count:

```python
images = req.images[:10]
```

at `bea_main.py:14957–14959`.

Each image is then accepted as an arbitrary base64 string and inserted into provider-bound message content at `bea_main.py:14993–15012`. There is no demonstrated:

- base64 decoded-byte limit,
- aggregate request-body limit,
- image dimension/pixel limit,
- content-type validation beyond a filename-style data-URI header check,
- image decompression-bomb protection,
- per-request input-token/currency reservation.

A request containing ten very large encoded images can create large server memory use, long request latency, and provider input charges. The fixed `max_tokens=2000` at `bea_main.py:15019–15021` does not control that input-side exposure. It also defeats the design/card claim that the “maximum possible charge” is computable pre-dispatch.

The same general concern applies to unbounded listing text passed to AI1/AI2, although AI5 is the clearest high-impact route.

**Required discussion:** Impose decoded-byte, image-dimension, total-pixel, aggregate-payload, and prompt-character/token budgets before provider dispatch. These bounds need to participate in the reservation calculation.

---

## [MAJOR] Scoreboard nightly probes bypass `claim_probe()` and can interfere with breaker state and recovery

**Lens:** Design correctness, operability, cost  
**Evidence:** `ai_scoreboard.py:probe_once()` and `run_probe_round()`; `ai_provider.py:complete()`; `ai_breaker.py:claim_probe()` and `record()`; `bea_main.py:16846–16864`

The new heartbeat correctly implements the intended ownership protocol:

1. Select eligible breaker rows.
2. Call `_hb_brk.claim_probe(_p, _t)` at `bea_main.py:16856–16859`.
3. Only then issue `complete(..., probe=True)` at `16860–16862`.

That portion is **correct**.

However, the scoreboard independently calls:

```python
complete(... provider=provider, ..., probe=True)
```

in `ai_scoreboard.py:probe_once()` without calling `ai_breaker.claim_probe()`.

Because `ai_provider.complete()` records every probe via `_brk.record(..., probe=True)`, scoreboard probes mutate the same breaker state as heartbeat probes. They can:

- issue direct probes while a heartbeat or traffic probe holds the half-open lease;
- add recovery-success streaks without an atomic claim;
- cause a T1/T2 lane to close after scoreboard probe successes;
- exercise T3-banned lanes and influence their progress toward `ready`;
- add avoidable probe spend outside the advertised “one per heartbeat tick total” control.

The design says direct probes must be atomically claimed before use; this is not merely a dashboard/statistics issue. The scoreboard currently has no equivalent claim or a “do not update breaker” mode.

**Required discussion:** Either:
1. have scoreboard probe only normal/closed lanes and use a non-breaker-recording health measurement path, or
2. require scoreboard to atomically claim an eligible breaker probe before calling `complete(probe=True)`, or
3. centralize all breaker-affecting probes in one scheduler.

---

## [MAJOR] Provider attribution and probably cost accounting are wrong after fallback

**Lens:** Cost, observability, maintainability  
**Evidence:** `bea_main.py:1493–1521`; AI1 `13793–13800`; AI2 `13895–13902`; AI3 `14580–14586`, `14616–14617`; AI4 `14862–14868`, `14898–14899`; AI5 `15018–15025`

The seam returns the actual serving provider and model in `AIResult`, and may fall back from the requested active lane to another provider. But `_log_ai_spend()` derives `provider` from the current configured active provider:

```python
_prov = _ts_active_provider()
...
INSERT ... (email, endpoint, model, ..., provider)
```

at `bea_main.py:1511–1521`.

The shown call sites do not pass `_sr.provider` or `_sr.model` to logging. For example, AI1:

- invokes the seam with `provider=_ts_active_provider()` at `13793–13796`;
- receives `_sr`;
- logs only logical model key `"haiku"` at `13800`.

If Anthropic is configured active but the request falls back successfully to Scaleway or OpenAI, the ledger records Anthropic as the provider. Equivalent patterns appear in all supplied paid endpoints.

This contradicts the Phase-1 claim that provider attribution is complete. It also undermines per-provider spend reconciliation, vendor cost comparison, breaker/cost incident diagnosis, and any future currency-specific rails. If `_token_cost()` prices by logical tier rather than actual provider/model—its implementation was not supplied—the monetary amount may also be materially wrong after fallback.

**Required discussion:** Change logging to record `AIResult.provider` and `AIResult.model`, and price exact provider-model token usage. A fallback chain needs per-attempt cost accounting if failed provider calls can incur billable input charges.

---

## [MAJOR] F2 “deliver then charge” fix charges for empty or unusable successful JSON

**Lens:** Correctness, customer fairness, product integrity  
**Evidence:** `bea_main.py:13805–13824`, `13906–13929`, `15029–15062`; user promise at `marketsquare.html:1417–1419`

The change from deduct-before-call to deduct-after-call is real. However, AI1/AI2/AI5 define success too weakly:

- **AI1** accepts parsed JSON even if both `new_title` and `new_description` are empty at `bea_main.py:13805–13807`, then charges at `13814–13817`.
- **AI2** accepts an empty/malformed `actions` array, resulting in `clean_actions = []`, then charges at `13907–13915` and `13920–13923`.
- **AI5** accepts no drafts, fewer drafts than submitted images, or drafts with empty title/description fields, then charges the full 2T at `15029–15045` and `15051–15054`. It still reports `cards_processed: card_count` at `15059–15062`, even if no usable draft was generated.

The help card promises no deduction if the AI call fails due to server error (`marketsquare.html:1417–1419`). A syntactically successful but semantically empty response may not throw an error, but it has still failed to deliver the represented service. The code comments call these “good result[s]” without validating that claim.

**Required discussion:** Establish endpoint-specific delivery acceptance criteria before deduction: non-empty rewritten fields for AI1, exactly three valid actionable items for AI2, and one valid draft per accepted image—or an explicitly stated partial-result/partial-charge policy—for AI5.

---

## [MAJOR] KYC is not pinned to an approved processor, so normal active-lane selection and fallback can send identity documents to all providers

**Lens:** Privacy, security, governance  
**Evidence:** `bea_main.py:9646–9737`; `ai_provider.py:complete()`; `privacy.html:§5`

The privacy policy now gives a substantially better disclosure. It expressly identifies:

- AI feature categories, including identity-document verification;
- Anthropic (US), OpenAI (US), and Scaleway (France/EU);
- the fact that automatic failover may send a request to any of them;
- a data-minimization statement.

This resolves the prior lack of multi-processor disclosure at a transparency level.

But the KYC code calls the general seam with:

```python
task="sonnet",
provider=_ts_active_provider(),
```

at `bea_main.py:9702–9713`. `ai_provider.complete()` then constructs an active-plus-fallback chain across all adapters. There is no KYC-specific allowed-provider list, geographic policy, consent/notice gate, or fallback prohibition shown.

That means a sensitive identity document, full legal name, and ID/passport number can move from an EU-selected or Anthropic-selected lane to a different processor during automatic failover. The privacy page discloses this possibility, but disclosure is not a substitute for a documented processor-selection decision and applicable agreements/transfer safeguards.

I disagree with treating KYC fallback pinning as a minor deferred decision. It is a live architecture/privacy decision because the current code already permits multi-processor fallback.

**Required discussion:** Decide and enforce one of the following explicitly:

- KYC only through a pinned approved provider/region, with no automatic fallback;
- a restricted KYC fallback allowlist, backed by processor-specific agreements and transfer assessment;
- a non-LLM OCR/verification path as the default, with an approved exception route.

---

## [MAJOR] KYC document fetch is an apparent SSRF and unbounded-download surface unless an omitted upstream route validates `doc_url`

**Lens:** Security, privacy, performance  
**Evidence:** `bea_main.py:9646–9665`, `9740–9753`; missing route evidence below supplied range

`_sonnet_verify_identity()` accepts a `doc_url` and performs server-side fetching:

```python
req = urllib.request.Request(doc_url, ...)
with urllib.request.urlopen(req, timeout=10) as resp:
    img_bytes = resp.read()
```

at `bea_main.py:9661–9665`.

The shown `IdentityVerifyIn` schema accepts arbitrary `doc_url: str` at `bea_main.py:9740–9745`. There is no visible restriction to a trusted R2 hostname, HTTPS, a fixed bucket/key format, redirect validation, private-address blocking, response-size limit, or content validation.

If the omitted route does not enforce those controls, an authenticated caller can direct the server toward internal services or cloud metadata addresses and cause the response to be base64 encoded and sent to an external AI processor. `resp.read()` is also unbounded.

**Absent evidence:** the identity-verification route handler and all `doc_url` validation logic are not supplied after `bea_main.py:9753`. This must be supplied to close the finding; the helper itself is unsafe absent upstream enforcement.

---

## [MINOR] T3 “hourly” heartbeat scheduling does not survive a successful probe

**Lens:** Correctness, cost, operability  
**Evidence:** `bea_main.py:16828–16833`; `ai_breaker.py:_record_ok()`

The heartbeat comment says T3 rows “probe hourly” at `bea_main.py:16828–16833`. Initially, a T3 trip uses the hourly interval (`PROBE_AFTER_T3_S`).

But after a claimed successful T3 probe, `_record_ok()` updates the next `probe_after` using `PROBE_AFTER_S`, which is five minutes:

```python
probe_after = now + timedelta(seconds=PROBE_AFTER_S)
```

in the non-recovery branch of `ai_breaker.py:_record_ok()`.

For a T3 row, this creates additional probes at approximately five-minute intervals until it reaches `ready`, rather than hourly. This is a small direct cost but more importantly contradicts the documented ban-probe policy. It also means a revoked/temporarily restored account can receive multiple probes before an operator evaluates the situation.

**Required discussion:** Preserve `PROBE_AFTER_T3_S` for all rows whose `trip_reason == "T3_account"` until manual restore, including after successful probes.

---

## [MINOR] Help-card descriptions still overpromise price and yield capabilities

**Lens:** Customer communication, maintainability  
**Evidence:** `marketsquare.html:1401–1412`; `bea_main.py:14553–14578`, `14717–14726`, `14791–14820`

F3’s vendor-neutral copy fix is good, but two capability descriptions are broader than the implemented service:

- The Fair Price card says the AI “compares the asking price to current SA market rates” and returns “a suggested fair range” (`marketsquare.html:1401–1403`). Yet when no verified feed exists, AI3 returns `cannot_verify`, no suggested range, and no charge at `bea_main.py:14553–14578`.
- The Yield card says it estimates returns “using current SA market data” (`marketsquare.html:1410–1412`). The implementation often requires the user to provide the missing rent or purchase price and returns `needs_input` without a result at `bea_main.py:14717–14726` and `14791–14820`.

These descriptions should present verified-feed and user-input contingencies honestly, especially given the product’s stated “don’t guess” doctrine.

---

## [QUESTION] F1 endpoint-gate totality is claimed but cannot be independently verified from this extract

**Lens:** Assurance, maintainability  
**Evidence:** computed claim in `Records/PEER_PACK_BEA_EXTRACT.md`; spot checks at `bea_main.py:13749`, `13836`, `14418`, `14728`, `14950`, `9655`

The supplied endpoint samples consistently use `ai_provider.any_lane_configured()`, and `ai_provider.py:any_lane_configured()` correctly tests configured provider keys against supported task mappings. This is the appropriate architectural fix for F1.

However, the assertion that all fifteen listed gates were replaced is Author-derived grep output. The actual source excerpts are absent for the remaining claimed locations, notably `bea_main.py:3319`, `4962`, `5082`, `5158`, `5234`, `8901`, `9117`, `13749`, `15208`, and `16094`.

**Absent evidence:** `bea_main.py:3319–5234`, `8901–9117`, `15208`, and `16094` are not present in the packet. The full-file grep claim is plausible but not independently auditable from the provided material.

---

## [QUESTION] Scoreboard enable-flag migration is not demonstrated

**Lens:** Operability, deployment correctness  
**Evidence:** `ai_scoreboard.py:is_enabled()`; `bea_main.py:716–768`

`ai_scoreboard.py:is_enabled()` requires `launch_switches.scoreboard_enabled`. The supplied `launch_switches` schema and shown idempotent `ALTER TABLE` migration list at `bea_main.py:716–768` do not create this column.

The scoreboard intentionally fails closed if the column is missing, so a fresh or incompletely migrated deployment will silently never run scoreboard probes. There may be a migration elsewhere or an external enable script, but it is not included.

**Absent evidence:** any `scoreboard_enabled` schema migration or the named `enable_scoreboard.bat` implementation is absent from the packet.

---

## [QUESTION] The claimed dashboard Restore button is not evidenced

**Lens:** Operability, security  
**Evidence:** backend route `bea_main.py:12502–12516`; `/flags` payload `12579–12607`; dashboard extract only `dashboard.server.html:976–1020`

The backend endpoint exists:

```python
POST /admin/ai-restore
```

at `bea_main.py:12502–12516`, and `/flags` exposes breaker state at `bea_main.py:12579–12607`.

But the supplied dashboard excerpt is only the AI provider visualization and contains no Restore control or authenticated call to `/admin/ai-restore`. The Phase-1 F5 statement that dashboard Restore remained queued is therefore not demonstrably resolved by this packet.

**Absent evidence:** dashboard code rendering a Restore action and invoking `/admin/ai-restore` is not supplied. The relevant UI source range is absent.

---

## [PRAISE] F1’s conceptual fix is correctly located at the seam boundary

**Lens:** Design, maintainability  
**Evidence:** `ai_provider.py:configured_lanes()`, `any_lane_configured()`; supplied endpoint checks

Replacing endpoint-level `ANTHROPIC_API_KEY` guards with a provider-neutral availability check is the correct abstraction boundary. The helper uses the same `envkey()` mechanism as adapters, including `.env` fallback, and does not confuse lane configuration with health. Health remains a breaker/seam concern.

This is materially better than repeating vendor-specific boolean logic at fifteen endpoints.

---

## [PRAISE] The heartbeat itself correctly claims the probe lease before direct probing

**Lens:** Concurrency, resilience  
**Evidence:** `bea_main.py:16846–16864`; `ai_breaker.py:claim_probe()`

The requested round-1 correction is implemented correctly in the heartbeat:

- eligible rows are selected by state and `probe_after`;
- a single row is selected round-robin;
- `claim_probe()` is called before provider dispatch;
- `probe=True` suppresses fallback;
- only one heartbeat probe is attempted per tick;
- probe spend is logged.

That is a sound implementation of the atomic-probe ownership rule. The separate scoreboard path, not this heartbeat path, is the remaining concern.

---

# F1–F5 and Round-1 Headline Conclusions

## F1 — Vendor independence

**Conclusion:** **Confirmed for supplied endpoints; full-class totality remains a claim.**

The core defect is fixed in the visible endpoints and in `ai_provider.py`. The new helper is appropriate. I cannot independently certify all fifteen locations from only Author-generated grep results.

## F2 — Charge order

**Conclusion:** **Improved but not complete.**

The code correctly moved debits after model/computation paths, which resolves the specific “server throws before completion but user was charged” defect. It does not ensure that a useful service was delivered before charge, and it does not atomically reserve either user balance or budget before costly dispatch.

## F3 — Vendor-specific customer copy

**Conclusion:** **Confirmed.**

The supplied market page says “Our AI” rather than “Claude.” This is the correct positioning choice for a failover-capable multi-provider system.

## F4 — Dashboard Sonnet reference

**Conclusion:** **Refuted/reclassified on supplied evidence.**

The shown `dashboard.server.html:976–1020` treats “sonnet” as a task-tier display label. It is not proof of an unmetered inference call or a model-routing defect. The originally cited location and alleged AdvertAgent registry relation were not included.

## F5 — P2b/P2c residue

**Conclusion:** **Heartbeat fixed; UI completion unverified.**

The heartbeat is now present and uses the correct claim mechanism. The original report is stale in saying heartbeat is absent. The backend restore route and flags data exist, but the actual dashboard Restore UI is not evidenced.

## Round-1 headline: probe claiming

**Conclusion:** **Heartbeat corrected; scoreboard remains non-compliant.**

`HEARTBEAT-1` correctly calls `claim_probe()`. The scoreboard’s nightly `complete(probe=True)` calls are unclaimed and write into breaker state, so the overall probing architecture still has a concurrency/state-integrity gap.

## Round-1 headline: cost bounding

**Conclusion:** **Partially implemented, not safely bounded.**

Correction-2 limits retries and output tokens, which is a useful improvement. It does not bound input/image size, concurrent spending, pre-dispatch currency exposure, or fallback-attempt costs accurately. The remaining pre-dispatch reservation work is not a cosmetic P2b item; it is necessary for the stated hard-ceiling guarantee.

## Round-1 headline: multi-processor privacy

**Conclusion:** **Disclosure improved substantially; KYC processor routing remains an unresolved high-risk design choice.**

`privacy.html:§5` is materially clearer: it names all processors, jurisdictions, AI functions, automatic failover, and KYC documents. That is a strong disclosure improvement.

However, the KYC code still uses the ordinary multi-provider seam and can fall back across processors. The policy says this can happen, but no task-specific processor control or evidence of processor-specific KYC safeguards is shown. The KYC fallback-pinning decision should be made before production KYC traffic.

---

# Three findings the System Engineer should discuss first

1. **[BLOCKER] Authentication/account binding for paid AI services.**  
   Caller-provided `email` and `seller_email` fields should not be allowed to select the account charged or the account whose balance/cost quota is consumed.

2. **[MAJOR] Real pre-dispatch cost and input controls.**  
   Implement atomic worst-case spend reservations, provider/model-accurate attribution, and strict input/image limits. Current rails are monitoring/refusal checks, not hard expenditure bounds under concurrency.

3. **[MAJOR] KYC routing and document-fetch security.**  
   Decide whether KYC is pinned or restricted to approved processors, and verify the omitted route prevents SSRF, private-network fetches, arbitrary redirects, and unbounded document downloads.

---

# What I could not verify from the supplied material

I could not verify:

- The full `bea_main.py` source and therefore the claimed totality of all fifteen F1 gate replacements or all AI call-site/cost-wrapper claims.
- The identity-verification endpoint handler following the supplied `IdentityVerifyIn` model, including authentication, ownership checks, R2 host allowlisting, SSRF defenses, redirect handling, and file-size validation.
- The implementation of `_require_admin`, which is used by `/admin/ai-restore` but not supplied, nor the authentication model for the paid user-facing endpoints.
- The implementation of `_token_cost`, `_MODEL_PRICE`, `ai_spend_log` schema, and whether spend amounts are priced by exact returned provider/model versus logical task tier.
- The schema migration or enable script for `launch_switches.scoreboard_enabled`.
- The dashboard UI code for a Restore button or its invocation of `/admin/ai-restore`.
- Whether the stated written AI-processor agreements, no-training commitments, POPIA transfer safeguards, and KYC processor agreements actually exist and cover the described processing.
- Live deployment behavior, real credentials, actual OpenAI/Scaleway provisioning, live database migration state, load/concurrency behavior, or results of the promised full application-level T0 drill.
