# Independent Peer Review — 2026-08-22-0712

*Peer: gpt-5.6-terra (second vendor, read-only) · Lens: full · Author: Claude · System Engineer: David*

**Scope:**
  - Records/FORENSIC_C1C2_BRIEF.md (26,631 chars)
  - Records/PEER_PACK_BEA_EXTRACT.md (120,000 chars TRUNCATED)

**Usage:** 40569 in / 6067 out tokens · actual cost ≈ $0.1539

---

# Independent Peer Review — HALT Launch Readiness

**Scope:** Read-only review of the supplied Cycle 1 / Cycle 2 audits and truncated code extract.  
**Overall conclusion:** **HOLD remains correct.** The exposed/unrotated credential set is independently sufficient for a hard launch hold. In addition, I found a likely **customer-wallet integrity blocker** in the supplied code that neither audit identifies, and several launch-critical controls are asserted without sufficient production evidence.

## Findings

### [BLOCKER] Repeated or retried “accept intro” requests can charge the buyer repeatedly, including after acceptance

**Lens:** Code correctness, security, financial integrity, consumer protection

**Evidence:** `PEER_PACK_BEA_EXTRACT.md`, `accept_intro`, lines **5717–5787**.

The endpoint:

- Reads an intro by ID (lines 5721–5725).
- Performs only conditional seller ownership validation, controlled by `account_binding` (lines 5727–5739).
- Unconditionally runs:

```python
UPDATE intro_requests SET status = 'accepted', tuppence_charged = 1 WHERE id = ?
```

(lines 5740–5742), followed by:

```python
INSERT INTO transactions (user_email, type, amount, description)
VALUES (?, 'intro_deduct', -1, ?)
```

(lines 5744–5748).

There is no check that:

1. the intro was previously in a pending/chargeable state;
2. `tuppence_charged` was previously false;
3. the buyer has sufficient Tuppence at acceptance time;
4. the request is idempotent; or
5. the transaction has a unique business reference such as `intro_id`.

The supplied `transactions` schema likewise has no `intro_id`, idempotency key, uniqueness constraint, or balance constraint: `database.py`, lines **57–64**.

**Failure mode:** A normal browser retry, seller double-click, network retry, or deliberate repeated `PUT /intros/{id}/accept` can insert another `-1` transaction on every successful call. A buyer can therefore be charged multiple times for one introduction and potentially driven negative. This is not merely accounting cleanliness: it is a direct customer-billing defect and dispute/refund exposure.

The endpoint may require an API key and, if enabled, a seller session; neither protection makes repeated calls safe for an authorized seller.

**Launch impact:** This is a **hard blocker for any launch scope where paid introductions are enabled.** The audits treat Tuppence charging and auth as strong, but neither Cycle 1 nor Cycle 2 appears to have tested repeat acceptance, replay, concurrent acceptance, negative-wallet behavior, or transaction idempotency.

---

### [BLOCKER] Known-exposed production credentials remain active while publicly accessible operational intelligence advertises the weakened posture

**Lens:** Security, incident response, operability

**Evidence:**

- `FORENSIC_AUDIT_CYCLE1 — nice.docx`, “**The blocker — confirmed, not cleared**”:
  - the production secret set was printed into transcripts twice and remains unrotated;
  - public anonymous responses from app shell, `/listings`, and `/dashboard/summary`;
  - WAF allowlist rule disabled.
- `FORENSIC_AUDIT_CYCLE2_PEER — nice.docx`, “**New finding Cycle 1 missed — anonymous information disclosure**”:
  - `/dashboard/summary` anonymously discloses:
    - `"Hetzner CPX32 (8GB RAM) + 100GB volume"`
    - `"WAF allowlist DISABLED"`
    - `"origin gate GATE-ENFORCE-1 the only guard"`.

I agree with both audit cycles: this is unequivocally a launch hold. The secret exposure is not neutralized by strong endpoint authentication; a valid exposed credential is expressly described as bypassing it.

I disagree, however, with Cycle 1’s simplified clearance claim that rotating the secret set and “ruling the gate posture” automatically clears both RED dimensions. **Rotation is necessary but not sufficient** unless the team verifies all of the following in production:

- every exposed credential has been revoked at its issuer, not merely replaced locally;
- old credentials fail;
- service reload/restart actually picked up each replacement;
- no deployment transcript, shell history, `.env`, repository artifact, backup, CI variable, dashboard, or log still contains the old credential;
- `/dashboard/summary` no longer discloses defensive posture and infrastructure intelligence;
- Cloudflare configuration and origin reachability match the intended public-launch threat model.

The material does not show this verification plan or acceptance evidence.

---

### [MAJOR] Account-binding authorization is feature-flagged OFF by schema default; launch state is not demonstrated

**Lens:** Security, authorization, launch configuration

**Evidence:**

- `PEER_PACK_BEA_EXTRACT.md`, schema lines **928–947**: `account_binding` is not shown in the initial table definition excerpt, but the related `auth_fail_closed` flag defaults to `0`; the account-binding implementation itself is explicitly a dark-launch flag.
- `ACCOUNT-BIND-1`, lines **5122–5127**: charged identity is session-proven only when `launch_switches.account_binding = 1`.
- `_account_binding_enabled`, lines **5129–5140`: returns `False` on DB/flag read failure (“fail-closed” in implementation terminology, but operationally it disables the stronger account-binding check).
- `_bind_charged_email`, lines **5163–5177**:
  - when the flag is off, it returns caller-supplied `passed_email`;
  - it merely shadow-logs missing sessions or session/email mismatches.
- `accept_intro`, lines **5727–5739**: seller-owner authorization is also conditional on this same flag.

Thus, if the flag is off—or the flag read fails—important paid actions revert to caller-asserted identity despite the audit’s repeated description of authentication and charging as “hard.”

Examples from supplied code:

- AI rewrite/audit bind caller email only if the flag is on (`16281`, `16370`).
- Intro creation binds buyer email only if the flag is on (`5343–5346`).
- Intro acceptance owner authorization occurs only if the flag is on (`5727–5739`).

**Launch impact:** The audited security conclusion cannot be accepted without a live production proof that `account_binding=true`, the authenticated user-flow works, and failure of the flag/database read does not silently fall back to caller-supplied identity for monetary actions.

**Required discussion point:** Is the flag live for soft launch, and is this state independently asserted in a release gate? The supplied audits do not answer that.

---

### [MAJOR] The review has no immutable production-release provenance; “predeploy ok” and local regression results do not prove the server is running the reviewed code

**Lens:** Operability, maintainability, change management, incident recovery

**Evidence:** `FORENSIC_AUDIT_CYCLE1 — nice.docx`, scorecard dimension 7:

> “`bea_main.py` is a 1.0 MB single file with **12 files uncommitted on disk**.”

The same document reports live probes, local/repo script execution, and “predeploy verdict ok,” but supplies no:

- deployed Git commit/SHA;
- build artifact digest;
- server-side commit match;
- deployment timestamp tied to the audit;
- release tag;
- rollback artifact/version;
- post-deploy smoke-test record tied to that artifact.

This is especially material because the audit’s asserted protections are feature flags and deployment/environment-sensitive behavior. A local working tree with 12 uncommitted files means the reviewed code, the committed code, and the deployed code may be three different states.

**Launch impact:** Not necessarily a standalone code blocker, but it is a **major release-control weakness** at D-7. Do not count a local regression ledger as evidence of the live release until the team can identify and validate the exact deployed revision.

---

### [MAJOR] AI Batch Cards permits up to ten unbounded base64 images; the stated cap controls count, not request size, memory, vendor spend, or abuse

**Lens:** Security, performance, cost control, availability

**Evidence:** `PEER_PACK_BEA_EXTRACT.md`, `AI5 Batch Cards`, lines **17483–17607**.

The endpoint:

- accepts `req.images` with no shown request-byte or decoded-image-byte limit;
- only caps count: `images = req.images[:10]` (lines **17500–17502**);
- accepts arbitrary base64 payloads and forwards each to the model as an image block (lines **17536–17556**);
- allows up to 2,000 output tokens (lines **17561–17564**);
- charges a flat 2T regardless of image count/size (lines **17486–17490**, **17504**).

No shown controls validate:

- maximum HTTP body size;
- maximum base64 length;
- decoded image byte size;
- image dimensions/pixel count;
- actual image format/content;
- per-user request rate/concurrency;
- vendor image-input cost before dispatch.

The code’s “media type detection” is just string inspection of a data URI header and otherwise defaults to JPEG. It is not validation.

**Failure mode:** A legitimate or malicious authenticated client can submit ten very large base64 values, tying up request parsing, memory, worker capacity, and upstream vendor cost. The monetary ceiling mechanism may help only if it is correctly configured and atomically enforced, neither of which is established in the material.

**Launch impact:** Major if this feature is visible at launch. The simplest safe launch alternative is to keep Batch Cards dark until strict byte/pixel/rate limits and one production golden run exist.

---

### [MAJOR] AI spend “hard rail” is not proven active, while code explicitly identifies the unset-ceiling state as uncapped

**Lens:** Cost, operability

**Evidence:** `PEER_PACK_BEA_EXTRACT.md`, `/admin/ai-spend/summary`, lines **6168–6199**:

```python
"ceiling_warning": (None if cfg and (cfg["daily_platform_ceiling_usd"] or 0) > 0
                    else "platform ceiling is 0/unset — AI spend is UNCAPPED")
```

(lines **6192–6195**).

Yet the supplied `ai_spend_config` initialization excerpt, lines **885–895**, creates only:

- `monthly_income_usd`
- `alert_threshold_pct`
- `alert_email`
- `last_alerted_at`

It does not show daily user/platform ceiling columns or their initialization. They may be added by omitted migrations, but that cannot be verified from this truncated material.

Cycle 1 claims “capped AI COGS”; Cycle 2 discusses costs and failover, but neither supplies the production value of `daily_platform_ceiling_usd`, proof that it is nonzero, or a live test that the ceiling rejects work while preserving correct customer behavior.

**Launch impact:** This becomes a hard blocker if public AI features are enabled and the daily platform ceiling is zero/unset or untested. The code itself says that state is uncapped.

---

### [MAJOR] Privacy review is incomplete: KYC identity documents and extracted identity data are sent to the dynamically active AI vendor without demonstrated consent, processor controls, retention controls, or jurisdictional approval

**Lens:** Privacy, legal/compliance, security

**Evidence:** `PEER_PACK_BEA_EXTRACT.md`, KYC code lines **11112–11197**.

The code takes an identity-document image and sends it through the generic AI provider seam:

```python
_sr = ai_provider.complete(...,
    task="sonnet", ...,
    provider=_ts_active_provider(), allow_fallback=False, timeout=120)
```

(lines **11166–11177**).

It explicitly asks the provider to extract full name and ID/passport number (lines **11139–11164**) and returns the extracted name and ID (lines **11190–11196**).

The provider list labels OpenAI and Anthropic as US-jurisdiction vendors, while Scaleway is EU (lines **15038–15047**). Cycle 2 says OpenAI serves “100% of live AI traffic” and has no production golden run. `allow_fallback=False` prevents failover but does **not** pin KYC to a privacy-approved vendor; it follows whatever `_ts_active_provider()` returns.

The audits’ privacy review focuses on anonymous listings and summary endpoints, which is useful but insufficient for KYC. It does not demonstrate:

- explicit, informed KYC consent for external AI processing;
- a lawful basis and POPIA assessment;
- vendor DPA/processor terms;
- cross-border transfer safeguards;
- document retention/deletion period;
- access controls and audit trail for source documents and extracted IDs;
- whether KYC is disabled at launch.

**Launch impact:** If KYC/verified-tier is exposed in launch scope, this is a substantial privacy/compliance gate. If it is dark, document and assert that state rather than treating it as an unexamined feature.

---

### [MAJOR] The anonymous operational-information disclosure must be fixed independently of any “gate posture” decision

**Lens:** Security, attack-surface management

**Evidence:** `FORENSIC_AUDIT_CYCLE2_PEER — nice.docx`, new finding section:

> `/dashboard/summary`, cookieless, returns 200 and leaks exact server sizing, “WAF allowlist DISABLED,” and that the origin gate is the only guard.

I agree with Cycle 2 that this materially worsens hardening. I further note that this is not logically solved by deciding that listings and the app shell may be public on 29 August. A public marketplace can intentionally expose listings; it should not need to expose:

- host capacity/sizing;
- defensive controls currently disabled;
- origin access/gate architecture;
- other internal operational state.

The material does not demonstrate that `/dashboard/summary` is authenticated, reduced to safe public information, or removed before launch.

---

### [QUESTION] Is the “gate down” finding actually a blocker, or does the audit conflate intended public-marketplace access with unauthorized origin exposure?

**Lens:** Design, security architecture, launch governance

**Evidence:** Cycle 1 states that anonymous `/listings`, app shell, and `/dashboard/summary` returning 200 means the origin gate is “effectively down.” Cycle 2 confirms that `/`, `/listings`, `/demo-listings`, `/dashboard/summary`, `/dashboard/bit`, `/auth/providers`, `/id-verify/status`, and `/flags` are anonymous.

The conclusion is clearly valid for `/dashboard/summary` and likely several operational endpoints. However, a marketplace full launch necessarily requires public app-shell and listings access. The supplied documents do not define:

- which endpoints are deliberately public at soft launch and full launch;
- whether Cloudflare-origin-only network access is enforced;
- whether “WAF allowlist disabled” means a protective allow rule is absent or a bypass rule is disabled;
- whether public `/flags`, `/auth/providers`, `/dashboard/bit`, and `/id-verify/status` have been threat-modeled and minimized;
- what the formal approved gate configuration is for each launch phase.

Without that endpoint-by-endpoint policy, “gate down” is too imprecise to use as a closure criterion. The correct criterion should be: **only explicitly public, minimized endpoints are reachable; operations/admin/origin details are not.**

---

### [QUESTION] Why does the secret-rotation plan itself require hand-editing a systemd unit after the audit already records environment-loading inconsistency?

**Lens:** Operability, security, incident response

**Evidence:**

- Cycle 1’s clearance plan says:
  > “Run `ROTATE_SECRETS.bat`, then hand-edit the systemd unit for `MS_API_KEY` / `MS_DEPLOY_TOKEN` / `FOUNDERS_ID_SALT`...”
- `PEER_PACK_BEA_EXTRACT.md`, lines **5186–5189**, says:
  > “the systemd unit does NOT export the server `.env` to this process.”

This indicates configuration is split between systemd environment and a code-level fallback to `/var/www/marketsquare/.env`. That is a high-risk secret-rotation arrangement: partial rotation can create inconsistent processes, failed integrations, unexpected fallback to old disk values, or an operator lockout.

**Question:** What is the single source of truth after rotation, how is it protected, and how will the team prove every service process has loaded the new value and rejects the old one? The documents say the action is “ready,” but do not show a safe, reversible, verified runbook.

---

### [QUESTION] The Cycle 1 “Cloudflare blocked load testing” explanation was overturned. Why was the bounded origin-reaching load test not scheduled immediately after that correction?

**Lens:** Performance, reliability, capacity planning

**Evidence:** Cycle 2 explicitly disproves the stated reason: default curl, `python-requests`, and browser user agents all return 200. It correctly retains “not measured” because the team chose not to load-test production seven days before launch.

I agree that destructive production testing at D-7 may be unwise. But the revised evidence means a **small, pre-approved, rate-bounded** test or staging-clone test is feasible. Current claims—SQLite is only 2.88 MB, roughly 120 ms reads, 104 listings—say almost nothing about simultaneous authenticated actions, writes, image uploads, AI calls, payment webhooks, or database locks.

**Question:** What concurrency level defines the 29 August soft-launch operating limit, and what exact non-production or approved-production measurement will establish it before launch?

---

### [MINOR] Launch calendar dates and weekdays are internally wrong

**Lens:** Operability, release governance

**Evidence:** Both audits state:

> “Soft launch Fri 29 Aug · Full launch Mon 1 Sep 2026.”

In 2026, **29 August is Saturday** and **1 September is Tuesday**. The stated D-7 date, Saturday 22 August, is consistent.

This may seem cosmetic, but incorrect weekdays in a launch plan can cause staffing, vendor-support, communications, monitoring, and rollback coverage errors. Correct the authoritative launch calendar before approvals.

---

### [MINOR] User-facing AI-price and yield claims exceed the implemented evidence model

**Lens:** Product integrity, legal/compliance, maintainability

**Evidence:**

- `marketsquare.html`, lines **1584–1586**, advertises:
  > “Our AI compares the asking price to current SA market rates and gives a verdict … plus a suggested fair range.”
- But `ai_price_check`, lines **17089–17113**, returns `cannot_verify`, charges nothing, and advises comparison with similar listings when no verified feed exists.
- `marketsquare.html`, lines **1593–1595**, advertises yield estimation using “current SA market data.”
- The yield implementation uses hard-coded benchmark text and a versioned cost-band resolver, while often requiring user-entered rent/purchase price (`17255–17377`).

The product may behave honestly in many cases, but the help copy is broader than the code’s actual verified-data coverage. At launch, soften claims or make verification/feed coverage explicit, particularly for financial guidance.

---

### [PRAISE] Cycle 2 performed meaningful adversarial correction rather than merely endorsing Cycle 1

**Lens:** Review quality, maintainability, security governance

Cycle 2 correctly overturned Cycle 1’s unjustified GREEN ratings for profitability and reliability, checked the anonymous summary body rather than only its HTTP status, tested rate limiting, and corrected the false “Cloudflare blocks non-browser load” explanation. This is the type of independent evidence challenge the process needs.

---

### [PRAISE] The supplied code shows several sound defensive patterns

**Lens:** Security, privacy, cost correctness

Examples include:

- parameterized SQL in the shown Tuppence operations;
- account-binding logic when enabled, including scope checking of the user JWT (`5120–5177`);
- explicit KYC SSRF commentary and `allow_fallback=False` for identity documents (`11125–11177`);
- delivery-then-charge intent in AI endpoints;
- relay subject newline sanitization (`5231–5233`);
- relay sender enrollment checks (`5304–5339`);
- a documented attempt to reserve AI spend before dispatch (`897–909`).

These controls are useful foundations. They do not offset the blocking acceptance-idempotency defect or the unresolved credential incident.

---

## The Three Findings the System Engineer Should Discuss First

1. **Repeated intro acceptance can repeatedly debit a buyer** (`accept_intro`, lines 5740–5748), with no idempotency, prior-state check, or balance enforcement.  
   **Decision:** paid introductions should not launch until this path is proven exactly-once and retry-safe.

2. **Exposed production credentials are still active, while public endpoints disclose weakened defenses and infrastructure details.**  
   **Decision:** retain HOLD until issuer-side revocation, deployment reload, old-secret rejection, disclosure removal, and endpoint/gate posture are independently verified.

3. **The account-binding control is flag-dependent and its live state is unproven** (`5122–5177`, `5727–5739`).  
   **Decision:** prove in production that account binding is enabled and enforce it as a launch invariant for all paid and seller-owner actions.

## What I Could Not Verify From the Material Given

I could not verify:

- the actual live value of `account_binding`, `intro_relay`, verified-tier, AI feature, and cost-ceiling flags;
- the deployed commit/artifact, its match to the supplied source excerpts, or the state of the 12 uncommitted files;
- whether the daily AI user/platform ceiling columns exist in the production schema and have nonzero values;
- the real implementation of `auth.require_api_key`, `_check_cost_ceiling`, spend-hold settlement, Paystack webhook validation, rate limits, and Cloudflare/origin configuration;
- whether the exposed credentials were actually exposed outside the cited transcripts, revoked at providers, or rotated successfully;
- production backup restoration, payment/intro retry behavior, AI golden-run output quality, vendor-failure behavior, or launch-scale capacity;
- KYC feature enablement, KYC user consent, retention/deletion controls, vendor data-processing agreements, or POPIA transfer assessment;
- the exact intended public endpoint policy for soft launch versus full launch.
