# Independent Peer Review — 2026-08-05-1151

*Peer: gpt-5.6-terra (second vendor, read-only) · Lens: full · Author: Claude · System Engineer: David*

**Scope:**
  - Records\AI_SERVICES_AUDIT_2026-08-05.md (7,306 chars)
  - ai_provider.py (13,480 chars)
  - ai_breaker.py (13,316 chars)
  - ai_service_tiers.py (15,900 chars)
  - ai_scoreboard.py (17,186 chars)
  - AI_AUTO_FAILOVER_P2_DESIGN.md (14,443 chars)

**Usage:** 21437 in / 5845 out tokens · actual cost ≈ $0.1130

---

# Independent Peer Review — Internal AI Services

## Scope and review basis

I reviewed only the supplied materials:

- `Records\AI_SERVICES_AUDIT_2026-08-05.md`
- `ai_provider.py`
- `ai_breaker.py`
- `ai_service_tiers.py`
- `ai_scoreboard.py`
- `AI_AUTO_FAILOVER_P2_DESIGN.md`

The critical application file cited by the Author, `bea_main.py`, was **not supplied**, nor were the dashboard/card files, database schema/migrations, spend/charge helpers, test suite, price card, or live configuration. Therefore, several claimed application-level findings cannot be independently confirmed from this packet.

---

## Phase-1 finding disposition (F1–F5)

### F1 — 15 endpoint hard-gate on `ANTHROPIC_API_KEY`

**Disposition: REFUTE as independently evidenced / application claim unverified.**  
**Lens: Design, vendor independence, operability**

The claimed 15 guards are all in `bea_main.py`, which is not included. I cannot verify the cited lines or count.

The supplied seam code does support the underlying concern:

- `ai_provider.py`, `_anthropic()` returns `error_kind="unconfigured"` if Anthropic has no key.
- `complete()` builds a fallback chain across `ADAPTERS`, so, absent an application-level Anthropic guard, it can attempt OpenAI and Scaleway:
  ```python
  chain = [prov] + ([p for p in ADAPTERS if p != prov] if allow_fallback else [])
  ```
- Thus the seam itself is not Anthropic-only.

However, this does **not** prove the claimed 15 endpoint gates exist. The reported issue may be real, but it is not auditable from the supplied code.

---

### F2 — charge order contradicts published refund policy for 3 services

**Disposition: REFUTE as independently evidenced / charge-integrity claim unverified.**  
**Lens: Financial integrity, customer trust, maintainability**

The cited `_deduct_tuppence`, `_require_tuppence`, endpoint handlers, failure paths, and help-card copy are all stated to be in `bea_main.py` or UI files that were not provided.

I therefore cannot independently confirm:

- which services charge before invocation;
- whether transactions, compensating refunds, idempotency keys, or exception handlers exist;
- whether user-facing copy promises “no Tuppence is deducted”;
- whether a fallback success after an initial provider failure counts as a delivered result.

The supplied seam creates an additional reason this requires a full end-to-end audit: one user request may invoke more than one provider (`ai_provider.py`, `complete()`), while charge behavior appears to be service-level. Without the caller code, there is no way to establish whether the charge is correctly tied to final delivery rather than merely dispatch.

---

### F3 — help copy names “Claude” despite live failover

**Disposition: REFUTE as independently evidenced / decision claim unverified.**  
**Lens: User trust, vendor independence, privacy disclosure**

The service-card/help-copy source was not supplied. I cannot confirm the quoted “Claude rewrites/reviews/estimates” statements.

The technical premise is valid: `ai_provider.py` can return a result from `"openai"` or `"scaleway"` after the active lane fails. Therefore, static Claude-only branding would be inaccurate whenever fallback is exercised.

I disagree with the Author’s classification of this as merely “not a code bug.” It is also a **customer disclosure and privacy-routing issue** if user text or images can be sent to a different processor than the one named in the UI. Whether that is legally material depends on the privacy notice, consent model, jurisdictions, and vendor DPAs, none of which were supplied.

---

### F4 — dashboard references Sonnet outside metered AdvertAgent registry

**Disposition: REFUTE as independently evidenced / unverified.**  
**Lens: Cost governance, maintainability**

`dashboard.server.html` was not supplied. I cannot verify line 906, whether the reference dispatches a model call, or whether it bypasses metering.

---

### F5 — P2b/P2c residue, including no heartbeat

**Disposition: CONFIRM in material part.**  
**Lens: Operability, resilience, cost**

The supplied implementation does not contain the P2c heartbeat described in `AI_AUTO_FAILOVER_P2_DESIGN.md` §6:

> “every 60 s, if any row is eligible … claim and send ONE probe”

There is no periodic scheduler in `ai_breaker.py`, and `ai_provider.complete()` does not call `claim_probe()` at all.

`ai_scoreboard.py` has a `run_nightly()` function, but that is a periodic all-lane scoreboard probe round, not the specified one-per-tick breaker heartbeat. Its execution is also conditional on `launch_switches.scoreboard_enabled`:

```python
if not is_enabled(conn):
    ... return None
```

I cannot verify the dashboard-light and Restore-button portions of F5 because their application/UI code is absent.

---

# New findings

## BLOCKER — Circuit breaker probe-claim mechanism is not wired into serving or scoreboard probes

**Lens: Resilience, correctness, performance, cost**  
**Evidence: `ai_provider.py: complete()`, `ai_breaker.py: claim_probe()`, `ai_scoreboard.py: probe_once()`**

The design’s central probe-safety claim is not implemented in the supplied execution path.

`ai_breaker.py` provides an atomic claim function:

```python
def claim_probe(provider, task):
    ...
    UPDATE ai_breaker SET state='half_open' ...
```

But no supplied file calls `claim_probe()`.

Instead:

1. Normal routing excludes any non-`closed` breaker state:
   ```python
   # ai_breaker.py, allows()
   return (row is None) or (row["state"] == "closed")
   ```

2. A probe explicitly bypasses state gating:
   ```python
   # ai_provider.py, complete()
   if probe and p == prov:
       return p not in _brk.drill_banned()
   ```

3. `ai_scoreboard.py` sends direct probes without claiming:
   ```python
   # ai_scoreboard.py, probe_once()
   r = complete(... provider=provider, ..., probe=True)
   ```

Consequences:

- A tripped lane may receive every scoreboard probe round regardless of `probe_after`.
- Concurrent workers can send duplicate probes to the same tripped lane; the advertised atomic “one trial call in flight” protection is unused.
- The 90-second half-open lease is functionally dead code in the supplied flow.
- The documented recovery behavior is driven by any direct scoreboard probe, rather than by an atomic scheduled/realtime probe policy.
- If scoreboard probing is disabled—as the report says it currently is—there is no shown mechanism to recover an idle tripped lane.

This directly contradicts `AI_AUTO_FAILOVER_P2_DESIGN.md` §5, which says:

> “Probe claiming is ATOMIC … rowcount 1 claims the probe; anything else does not probe.”

**Required discussion/fix direction:** make `complete(probe=True)` require a successful `claim_probe()` for non-closed rows, or have the heartbeat/scoreboard claim before dispatch and pass an explicit claimed-probe token. Do not bypass the breaker state merely because a caller labels a request as a probe.

---

## MAJOR — Failover can silently multiply vendor spend and latency; no seam-level budget reservation exists

**Lens: Cost, performance, charge/refund integrity**  
**Evidence: `ai_provider.py: complete()`, `AI_AUTO_FAILOVER_P2_DESIGN.md` v1.2**

`ai_provider.complete()` attempts each eligible provider serially:

```python
for p in open_chain:
    r = ADAPTERS[p](...)
    ...
    if r.ok:
        return r
```

Each adapter has a default 30-second timeout. With three lanes, one user request can consume up to approximately three timeout windows and invoke up to three billable vendor requests.

The design acknowledges this gap in its v1.2 residue:

> “The CURRENCY budget reservation (pre-dispatch $ ceiling) lands with P2b”

That reservation is not in the supplied code. Nor does `complete()` receive a per-request cost reservation, cost ceiling, or caller budget token.

The Author’s Phase-1 report claims:

> “17/17 wrapped call sites ceiling-checked and spend-logged”

Even if true for initial dispatch, a check made once before calling `complete()` is not enough to bound cumulative cost of fallback attempts unless it reserves the **worst-case chain cost**, adjusts balances per provider attempt, or disables fallback when the remaining budget cannot cover it.

This is particularly important for charge integrity:

- A first provider may time out after receiving and processing the request; the client can still be charged by that provider.
- The seam then sends the same request to the next provider.
- The user may receive one result, while platform vendor cost has been incurred multiple times.
- In a user-paid service, a flat 1T/2T charge may become systematically unprofitable during partial outages without showing as an application-level failure.

**Required discussion/fix direction:** reserve a bounded amount before dispatch for the selected eligible chain, or explicitly authorize only one fallback based on remaining platform/user budget. Log every adapter invocation—not only final success—with provider, model, token use, timeout/unknown outcome, request correlation ID, and reservation reconciliation.

---

## MAJOR — “At most one attempt per configured lane” is false; unconfigured lanes remain in the attempted chain

**Lens: Correctness, performance, operability**  
**Evidence: `ai_provider.py: complete()`**

The v1.2 design claims:

> “at most ONE attempt per configured lane”

But `complete()` does not know whether a lane is configured before dispatch. It includes every adapter whose task model exists:

```python
chain = [prov] + ([p for p in ADAPTERS if p != prov] if allow_fallback else [])
chain = [p for p in chain if ADAPTERS.get(p) and TASK_MODEL.get(p, {}).get(task)]
```

Configuration is discovered only after invoking each adapter:

```python
if not key:
    return AIResult(... ok=False, error_kind="unconfigured")
```

This means an unkeyed OpenAI or Scaleway lane is still “attempted” on every fallback traversal. It likely does not create vendor cost, but it:

- contradicts the stated rail;
- adds avoidable work and breaker bookkeeping;
- means “configured lane” metrics and actual attempted-chain behavior differ;
- increases the likelihood that application-level telemetry records failures that are merely absent keys.

A preflight capability/configuration helper is needed—not just for F1’s endpoint gating, but also to construct an accurate chain.

---

## MAJOR — Breaker’s “consecutive T1 failures” logic does not reset on intervening non-T1 failures

**Lens: Correctness, resilience**  
**Evidence: `ai_breaker.py: _record_fail()`**

The design says T1 is:

> “3 consecutive T1-class failures within 120 s”

But `_record_fail()` only modifies `consec_fails` for T1 kinds:

```python
if kind in T1_KINDS:
    ...
    sets["consec_fails"] = consec
```

For `rate_limited`, `invalid_request`, `unknown`, `unauthorized`, and `unconfigured`, it does not reset the prior T1 streak. Only `_record_ok()` resets it.

Example:

1. timeout;
2. timeout;
3. `invalid_request` caused by an application deployment bug;
4. timeout.

The third timeout can trip T1 because the stale count remains 2, despite the failures not being consecutive T1 failures.

This can incorrectly remove a healthy lane from routing after a mixture of unrelated errors. The result is more fallback traffic, more cost, and potentially an unnecessary all-lanes-down condition.

**Required discussion/fix direction:** explicitly reset `consec_fails` and `first_fail_at` for every non-T1 outcome that semantically breaks consecutiveness, while preserving the separate T2 accounting policy.

---

## MAJOR — Scoreboard probes bypass spend rails and can generate unmetered vendor cost

**Lens: Cost governance, operability, maintainability**  
**Evidence: `ai_scoreboard.py: run_probe_round()`, `probe_once()`**

`ai_scoreboard.py` directly invokes vendor calls through the seam:

```python
r = complete(... probe=True)
```

It estimates cost locally after the call:

```python
cost = ((r.in_tokens or 0) * pin + (r.out_tokens or 0) * pout) / 1e6
```

But the supplied code has no:

- platform spend-ceiling check before the probe;
- budget reservation;
- call to the application’s asserted `_log_ai_spend`;
- durable, authoritative vendor cost ledger;
- provider-specific cost cap;
- protection against a manually invoked `--force` probe round.

The design says heartbeat spend is logged through `_log_ai_spend`, but `ai_scoreboard.py` has no such integration. Its own `est_cost_usd` is an estimate based on response token reporting and a locally loaded/fallback price table, not a spend rail.

This is a silent-cost-drift risk because probes can be enabled or forced outside the normal user-service wrappers that the Author says are ceiling checked.

**Required discussion/fix direction:** route scheduled and attended probes through the same cost reservation and spend-log interface as user calls, with a separately budgeted “operational probes” category. A probe should be skipped—not dispatched—when its operational budget is exhausted.

---

## MAJOR — Fallback resends potentially sensitive prompts/images to multiple vendors without a shown routing/privacy control

**Lens: Privacy, security, vendor independence**  
**Evidence: `ai_provider.py: complete()`, `_to_openai_messages()`**

The seam reuses the same `messages` and `system` payload for every fallback adapter:

```python
r = ADAPTERS[p](messages, TASK_MODEL[p][task], max_tokens, system, timeout)
```

For vision, `_to_openai_messages()` embeds image data in a `data:` URL and forwards it to OpenAI-compatible services:

```python
"url": f"data:{src.get('media_type','image/jpeg')};base64,{src.get('data','')}"
```

This means an Anthropic timeout or connection failure can cause the same user content—including images—to be disclosed to OpenAI and Scaleway. A timeout is ambiguous: the original provider may have received, retained, processed, and billed the request before the client timed out.

I cannot determine whether this is permitted because no privacy notice, consent record, processor inventory, DPA, country-routing policy, or data-classification policy was supplied. But the implementation does establish multi-vendor onward transmission as a technical fact.

This is not solved merely by branding the service “AI.” Vendor-independent routing requires vendor-independent privacy and data-processing governance.

**Required discussion:** determine whether every task payload is approved for every fallback vendor and region; add task/data-class routing restrictions where necessary; ensure user-facing disclosure and internal records reflect actual provider invocation(s), not only the final successful provider.

---

## MAJOR — Tier resolver treats an explicit empty provider map as “use all defaults”

**Lens: Correctness, cost, maintainability**  
**Evidence: `ai_service_tiers.py: available_tiers()`**

The resolver uses:

```python
prov = providers or DEFAULT_PROVIDERS
```

An explicitly supplied empty dictionary, `{}`, is falsy, so it silently becomes `DEFAULT_PROVIDERS`.

That defeats the ordinary meaning of an injected provider-state map. A caller that intentionally passes `{}` to represent “no providers are available” will instead enable every default live provider, including services backed by external feeds such as `ebay_browse`, `bricklink`, or `scryfall`.

This can violate the stated “hide where we can’t deliver” behavior and can cause unwanted external calls or misleading UI availability during a provider-state outage.

**Required discussion/fix direction:** use an explicit `None` check:

```python
prov = DEFAULT_PROVIDERS if providers is None else providers
```

Add tests for `providers={}` and for intentionally disabled individual providers.

---

## MINOR — Scoreboard’s sanity check does not affect availability/ranking

**Lens: Operability, quality assurance**  
**Evidence: `ai_scoreboard.py: ranking()`**

The code records whether a response passes the probe sanity check, but a response with `ok=1` and `sane=0` still counts as available:

```python
oks = [r for r in configured if r[0] == 1]
avail = 100.0 * len(oks) / len(configured)
```

`sanity_fails` is reported but does not make the lane unavailable, degraded, or ineligible:

```python
sane_fails = sum(1 for r in oks if r[1] == 0)
```

A provider that consistently returns irrelevant but non-empty text can therefore rank as highly available. The stated design correctly says a golden set is the quality gate, but the probe sanity predicate is specifically intended as a non-degenerate liveness signal. If it is meaningful enough to collect, repeated failures should at least affect status or trigger an alert.

---

## MINOR — Scoreboard documentation says “configured lane,” implementation probes all defined lanes

**Lens: Maintainability, cost, operability**  
**Evidence: `ai_scoreboard.py` module docstring; `run_probe_round()`**

The module description says it:

> “probes EVERY configured lane x task tier”

But `run_probe_round()` loops every provider in `ADAPTERS` and every task in `TASKS`, irrespective of configuration:

```python
for provider in ADAPTERS:
    for task in TASKS:
```

Unconfigured attempts are intentionally recorded, so this may be a deliberate diagnostic choice. However, it conflicts with the documentation and with the cost statement based on configured lanes. In particular, enabling the scoreboard calls into every adapter every night, even where keys are absent.

This should be described accurately, or changed to use an explicit configured-lane inventory.

---

## QUESTION — What is the authoritative active-provider source?

**Lens: Vendor independence, operability, maintainability**  
**Evidence: `ai_provider.py`; `AI_AUTO_FAILOVER_P2_DESIGN.md` §0**

`ai_provider.py` resolves the active provider once at import:

```python
AI_ACTIVE = os.getenv("AI_ACTIVE", "anthropic")
```

The design instead states the live application uses a DB-backed `launch_switches.ai_active`, with a roughly ten-second cache, and passes it per call from `bea_main.py`.

That may be correct, but it is not visible in the supplied application code. The System Engineer should require a single demonstrated request path showing:

1. DB switch update;
2. cache refresh;
3. provider argument reaching `complete()`;
4. fallback behavior;
5. provider attribution in spend logs and user/audit records.

Without that, the asserted “one place to swap” claim is misleading: there appear to be at least two provider-selection mechanisms.

---

## QUESTION — How are failed/ambiguous provider attempts represented in the financial ledger?

**Lens: Cost, charge/refund integrity, auditability**  
**Evidence: `ai_provider.py: complete()`**

The seam returns only one final `AIResult`. If Anthropic times out and Scaleway succeeds, the final return reports Scaleway. The failed Anthropic invocation exists only transiently inside the loop unless the missing caller-side logging captures it per adapter attempt.

The design claims attribution “per adapter invocation,” but no spend logger was provided. The System Engineer should require proof that the ledger captures:

- each provider attempt;
- request/service correlation;
- initial dispatch and fallback sequence;
- token counts where available;
- estimated versus invoiced cost;
- ambiguous timeout outcomes;
- user charge, refund, and delivery status.

Without this, platform cost can drift while final-result metrics falsely imply that only the successful provider was used.

---

## PRAISE — The provider seam is materially real at the supplied-module level

**Lens: Maintainability, vendor independence**

`ai_provider.py` has a reasonable adapter boundary:

- abstract task tiers;
- provider-specific model registry in one module;
- translation of Anthropic content blocks for OpenAI-compatible endpoints;
- normalized `AIResult`;
- provider/model attribution;
- bounded per-attempt output token parameter.

This is substantially better than model/vendor strings scattered through endpoint code. It provides a credible basis for vendor substitution—provided the application-level Anthropic guards claimed in F1 are removed and routing/privacy/cost controls are completed.

---

## PRAISE — Failure taxonomy distinguishes configuration and application errors from provider health

**Lens: Resilience, operability**

The separation of `unconfigured`, `invalid_request`, T1, T2, and T3 classes in `ai_provider.py` and `ai_breaker.py` is sound in principle. In particular:

- missing keys do not trip a breaker;
- `400/422` are treated as likely application errors rather than provider outages;
- account/credit errors are separated from transient transport failures.

The issue is not the taxonomy itself; it is the incomplete probe-claim wiring and the consecutive-T1 implementation defect described above.

---

# Three findings the System Engineer should discuss first

1. **BLOCKER: breaker probes are not atomically claimed and bypass breaker state**  
   `ai_breaker.claim_probe()` is unused. This invalidates the stated half-open/one-probe recovery design and can create uncontrolled probe behavior.

2. **MAJOR: fallback cost and financial accounting are not bounded at the seam**  
   One user request can make multiple vendor calls, while no supplied code reserves cumulative budget or proves per-attempt spend/charge/refund accounting.

3. **MAJOR: vendor fallback is a multi-processor data-routing decision, not only a reliability feature**  
   The same prompts and images can be retransmitted to multiple vendors after ambiguous failure. Verify privacy disclosure, processor approvals, regional routing, and audit logs before describing the platform as vendor-independent.

# What I could not verify from the material given

I could not verify:

- any `bea_main.py` endpoint guards, line references, call-site totality, charges, refunds, cost ceilings, spend logging, provider-selection forwarding, or admin authentication;
- the claimed F1 count of 15 Anthropic-key gates;
- the claimed F2 charge-before/deliver-then-charge behavior for any user service;
- user-facing Claude branding or dashboard Sonnet reference;
- UI/dashboard breaker lights, restore endpoint wiring, n8n alert wiring, or actual heartbeat scheduler;
- database migrations, schema compatibility, transaction boundaries, ledger contents, or idempotency;
- the stated test results, drill artifacts, golden-set results, live key configuration, live provider capabilities, actual model pricing, or live-site behavior;
- privacy notices, consent flows, DPAs, data residency constraints, or vendor contracts.
