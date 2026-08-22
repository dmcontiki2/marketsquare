# Independent Peer Review — 2026-08-22-0713

*Peer: gpt-5.6-terra (second vendor, read-only) · Lens: security · Author: Claude · System Engineer: David*

**Scope:**
  - Records/FORENSIC_C1C2_BRIEF.md (26,631 chars)
  - Records/PEER_PACK_BEA_EXTRACT.md (120,000 chars TRUNCATED)

**Usage:** 40521 in / 4422 out tokens · actual cost ≈ $0.1341

---

# Security Peer Review Report

## Findings

### [BLOCKER] Account-binding protection is explicitly disabled by default, leaving paid actions dependent on caller-supplied email

**Evidence:** `Records/PEER_PACK_BEA_EXTRACT.md`, `bea_main.py` lines 941–952 set `account_binding` to `0` by default. The binding helper at lines 5159–5177 deliberately returns the caller-provided `passed_email` when the flag is off:

> “Flag OFF is byte-identical to today's behaviour…”  
> `return passed`

AI endpoints invoke this helper as their principal identity control:

- AI Listing Rewrite: lines 16273–16282
- AI Seller Audit: lines 16362–16371
- AI Batch Cards: lines 17484–17504
- Intro creation: lines 5343–5346

This means that unless the production `launch_switches.account_binding` is affirmatively `1`, a request can name an arbitrary account email for charging and quota purposes. The code comments themselves acknowledge that the old state is caller-asserted identity.

This directly conflicts with the audit’s broad claim in `FORENSIC_AUDIT_CYCLE1` that the app “fails closed” and that “a valid stolen MS_API_KEY walks straight past every check above.” For these routes, the authorization boundary is not robust even before a stolen credential is considered if account binding remains dark.

**Impact:** Unauthorized Tuppence charging, AI-cost abuse charged against other accounts, and potentially unauthorized creation/acceptance-related actions. A public/bundled API key, if that is the key used by frontend clients, would make this especially serious.

**Required discussion:** Is `account_binding=1` enabled in the actual production row now? It must be verified by a production-state query, not inferred from source or `/flags` presentation.

---

### [BLOCKER] Price-check and yield endpoints perform wallet lookup before authenticating/binding the requesting account, creating an account-balance oracle

**Evidence:** `bea_main.py` lines 16935–16978 (`/listings/{listing_id}/price-check`) and lines 17249–17300 (`/listings/{listing_id}/yield-calc`).

In both handlers:

1. The caller provides `email`.
2. `_require_tuppence(email, _charge)` is called.
3. Only afterward does `_bind_charged_email(email, ts_user, ...)` run.

For price check:

```python
_require_tuppence(email, _charge)   # line 16976
email = _bind_charged_email(email, ts_user, "ai3-price")  # line 16977
```

For yield:

```python
_require_tuppence(email, _charge)   # line 17298
email = _bind_charged_email(email, ts_user, "ai4-yield")  # line 17299
```

`_require_tuppence` returns a distinguishable `402` when the supplied account lacks sufficient balance (lines 16261–16268). If the named victim account has sufficient balance, execution reaches binding and returns a different result—typically `401`/`403` when account binding is enabled. This reveals whether a target account has at least the requested balance without authenticating as that account.

Additionally, successful free-result paths disclose `tuppence_remaining`:

- Price check: lines 17090–17112.
- Yield calculator: lines 17344–17359.

**Impact:** Account/balance enumeration remains possible despite the audit’s claim that IL-01’s protected balance endpoint eliminated the existence/oracle concern. Securing one direct balance route does not secure other balance-dependent paths.

**Recommendation:** Bind and authenticate identity before *any* wallet read, preflight, cost-ceiling lookup, listing access dependent on user identity, or response construction. Return a uniform authentication failure before checking any caller-selected account.

---

### [BLOCKER] Introduction acceptance is non-idempotent and has no balance enforcement; retries can charge a buyer repeatedly

**Evidence:** `bea_main.py` lines 5717–5787.

`accept_intro`:

- Loads an intro by ID.
- Unconditionally sets `status = 'accepted', tuppence_charged = 1` (lines 5740–5742).
- Unconditionally inserts a `-1` buyer transaction (lines 5744–5748).
- Does not require that the prior status is pending.
- Does not check `tuppence_charged`.
- Does not call `_require_tuppence` or `_deduct_tuppence`.
- Does not use an atomic conditional update, a transaction-level idempotency guard, or a unique debit constraint.

Repeated requests for the same intro can therefore insert repeated charges and repeat webhook/relay side effects. With `account_binding` off, the conditional owner check is also absent (lines 5727–5739), leaving the API-key dependency as the only stated access control.

**Impact:** A seller, attacker with the relevant API key, proxy retry, or client double-submit can drive a buyer’s balance negative and produce duplicate accepted-intro side effects. This is a direct integrity and financial-loss issue.

**Recommendation:** Make acceptance an atomic state transition, e.g. `UPDATE ... WHERE id=? AND status='pending' AND tuppence_charged=0`, verify exactly one affected row, then debit through one atomic balance-safe mechanism. Treat subsequent requests as idempotent, with no further charge or notification.

---

### [MAJOR] The AI Batch Cards endpoint permits unbounded image payloads and forwards arbitrary caller-provided base64 to an external AI provider

**Evidence:** `bea_main.py` lines 17484–17607.

The endpoint caps **count** at ten images (lines 17500–17502), but does not cap:

- JSON request-body size,
- decoded byte size per image,
- aggregate decoded size,
- image dimensions/pixel count,
- valid base64 encoding,
- declared MIME type against detected file content.

At lines 17536–17555, the handler accepts a data URI header or defaults to JPEG, then passes the raw base64 string to `ai_provider.complete`. A malformed or enormous body can consume application memory and CPU before the upstream call; valid but oversized images can amplify vendor payload/cost exposure. The configured call timeout is 60 seconds (lines 17561–17564), which does not constrain body ingestion or memory allocation.

This materially qualifies Cycle 1’s categorical statement that “Every probed attack vector held” and “Resource exhaustion” is controlled. The cited test only covered `/listings?limit=99999999`; it does not cover upload/body amplification or AI-vendor cost exhaustion.

**Impact:** Application resource exhaustion, upstream AI bill abuse, and denial of service. This is especially concerning while the external gate/WAF posture is reported down.

**Recommendation:** Enforce request `Content-Length` and streaming limits at the proxy and application layers; decode and validate images server-side; impose per-image and aggregate byte/pixel limits; reject unsupported MIME signatures; rate-limit by authenticated account and IP; and reserve the *worst-case vision cost* before upload/provider dispatch.

---

### [MAJOR] Authorization of paid AI endpoints is inconsistent and cannot be treated as established from the supplied evidence

**Evidence:**

- `/listings/{listing_id}/ai-rewrite` has no `Depends(auth.require_api_key)` or other route-level auth dependency: lines 16273–16282.
- `/listings/{listing_id}/ai-audit` likewise: lines 16362–16371.
- `/listings/batch-cards` likewise: lines 17484–17498.
- `/listings/{listing_id}/price-check` and `/yield-calc` likewise: lines 16935–16978 and 17249–17300.
- In contrast, `/tuppence/history` explicitly declares `_key: str = Depends(auth.require_api_key)` at line 17612.
- Intro acceptance explicitly declares the API-key dependency at lines 5717–5720.

The absence of a dependency does not necessarily prove these AI routes are unauthenticated—there could be unprovided middleware—but the supplied code does not demonstrate a consistent global AuthN/AuthZ policy. The audit documents do not identify middleware coverage, nor do they report authenticated/unauthenticated probes of these chargeable routes.

**Impact:** The claim that application authorization “fails closed” is not justified for all financially consequential endpoints. If no global middleware exists, these endpoints are callable anonymously when account binding is off and remain balance-oracle-prone when it is on.

**Required discussion:** Provide the FastAPI middleware/router configuration and live probes for each paid endpoint: no credentials, public app API key only, valid user session for self, valid session for another user, expired session, and malformed cookie.

---

### [MAJOR] Secret exposure is broader than the audit frames, and plaintext email/operational data are unnecessarily logged

**Evidence:**

- `FORENSIC_AUDIT_CYCLE1` states the production secret set was “printed into a transcript TWICE” and remains unrotated, including `MS_API_KEY`, `PAYSTACK_WEBHOOK_SECRET`, `RESEND_API_KEY`, `CF_CACHE_TOKEN`, `MS_DEPLOY_TOKEN`, `FOUNDERS_ID_SALT`, and supplier tokens.
- `bea_main.py` logs customer email addresses in ordinary operational logs:
  - AI rewrite: line 16352.
  - AI audit: line 16460.
  - Batch Cards: lines 17601–17602.
  - Account-binding shadow logs include passed and session emails: lines 5165–5170.
- `/dashboard/summary` reportedly anonymously exposes WAF/gate state and infrastructure sizing (`FORENSIC_AUDIT_CYCLE2_PEER`).

The audit correctly calls rotation a blocker, but calls this “one focused piece of work” and says that rotating the secret set and ruling gate posture clears both REDs. I disagree with that closure criterion. Rotation alone does not establish that the leaked transcripts, logs, CI artifacts, shell history, document copies, access controls, backups, and third-party destinations were contained or that the secret set was fully inventoried. The repeated email logging also enlarges the impact of a future log/transcript exposure.

**Impact:** Credential compromise remains a total-bypass risk; customer email data may be exposed in operational records beyond the minimum necessary.

**Recommendation:** Treat this as an incident response exercise, not simply rotation: identify every transcript/artifact and reader; revoke/replace tokens; inspect use and vendor audit logs; invalidate sessions/JWTs where applicable; rotate dependent salts with a migration plan; set credential-scanning and redaction controls; and define log retention/access controls. Avoid logging raw email unless there is an explicit operational need; use account IDs or a keyed pseudonym.

---

### [MAJOR] KYC documents and identity data can be routed to whichever active AI provider an administrator selects; privacy and data-boundary controls are unproven

**Evidence:** `_sonnet_verify_identity` in `bea_main.py` lines 11112–11197 sends document image bytes plus claimed name and ID/passport number to:

```python
ai_provider.complete(... provider=_ts_active_provider(), allow_fallback=False, ...)
```

at lines 11166–11177. Meanwhile, the active provider is database-switchable without restart (lines 1644–1680), and the public `/flags` representation lists OpenAI, Anthropic, and Scaleway as available provider lanes (lines 15021–15047).

`allow_fallback=False` is good because it avoids uncontrolled fan-out of ID documents. However, it does not pin KYC to a privacy-approved provider or jurisdiction. The function name and comments call it “Sonnet” verification, but runtime routing uses the generic active provider. The extract does not show consent, a processor agreement/data-residency assessment, retention/deletion policy, redaction, or an administrative authorization distinction between changing normal AI traffic and changing KYC routing.

**Impact:** A routine AI traffic switch can redirect highly sensitive identity documents and ID numbers to a different external processor. This is materially different from routing marketplace copywriting.

**Recommendation:** Pin KYC to a specific approved provider/model and explicit region, separate from the normal active-provider switch. Require a distinct privileged control and audit event for any KYC routing change. Establish and document user consent, retention, vendor processing terms, and deletion/error handling before launch.

---

### [MINOR] Relay authorization secret comparison is not constant-time, and alias capability entropy/rate controls are not evidenced

**Evidence:** `bea_main.py` lines 5304–5339.

The relay endpoint checks:

```python
if not RELAY_INBOUND_SECRET or x_relay_secret != RELAY_INBOUND_SECRET:
```

at lines 5311–5314. Use `hmac.compare_digest` for secret verification. More importantly, aliases use `token_hex(6)`—48 bits of entropy—at lines 5210–5217. That is not inherently unsafe for a 30-day, server-authenticated relay, but the evidence does not show Cloudflare Worker authentication, replay protection, inbound rate limiting, or per-alias abuse controls.

The endpoint is protected by the relay secret, so the alias itself is not the sole authorization control. Nevertheless, after the documented secret-transcript incident, all secret-authenticated internal endpoints warrant careful review.

---

### [QUESTION] The audit’s “hard auth surface” conclusion overstates the coverage actually demonstrated

**Evidence:** `FORENSIC_AUDIT_CYCLE1` says:

> “Every probed attack vector held.”  
> “the app’s own auth surface is genuinely hard … fails closed”

Cycle 2 adds a useful rate-limit probe of `/admin/login`, but neither cycle presents probes for:

- all paid AI routes discussed above,
- introduction accept/decline replay and ownership behavior,
- account-binding enabled versus disabled states,
- balance-oracle behavior,
- batch-image limits,
- deploy-hook authentication,
- KYC document-fetch allowlist implementation,
- webhook signature validation,
- global middleware coverage.

The claim is directionally encouraging for the endpoints that were actually tested (especially IL-01 and admin login rate limiting), but it should be narrowed to those tested endpoints. It is not evidence that every security-critical endpoint is fail-closed.

---

### [PRAISE] The audit correctly identified the credential exposure and anonymous operational disclosure as launch-blocking

`FORENSIC_AUDIT_CYCLE1` and `FORENSIC_AUDIT_CYCLE2_PEER` are right to retain HOLD while exposed production credentials remain unrotated and the public gate/WAF posture is unresolved. Cycle 2’s discovery that `/dashboard/summary` discloses the disabled-defense state and server sizing is a concrete improvement over Cycle 1. The KYC path’s `allow_fallback=False` at `bea_main.py` line 11177 is also a sound privacy safeguard against accidental multi-vendor propagation of ID documents.

## Three findings the System Engineer should discuss first

1. **Account-binding is default-off and paid endpoint authentication is inconsistent** — confirm the live production state of `account_binding`, route middleware coverage, and whether a frontend-distributed API key is relied upon for authorization.
2. **Pre-auth wallet/balance oracle and repeated intro charging** — fix the order of binding versus balance lookup, and make intro acceptance atomic/idempotent before launch.
3. **Unbounded Batch Cards image ingestion under a known gate/WAF exposure condition** — add hard body/image limits, cost reservation, and authenticated rate limiting before allowing the endpoint to be publicly reachable.

## What I could not verify from the material provided

I could not verify the live values of `launch_switches.account_binding`, `intro_relay`, or AI spend ceilings; the implementation of `auth.require_api_key`, `_require_admin`, `_check_cost_ceiling`, `_fetch_kyc_document`, or any global FastAPI middleware; whether API keys are public frontend credentials or private server credentials; Cloudflare/edge rate and body-size limits; actual vendor-token rotation and incident containment; KYC consent and processor agreements; webhook signature validation; database transaction/isolation behavior under concurrency; or live exploitability of the identified routes.
