# Independent Peer Review — 2026-07-31-0645

*Peer: gpt-5.6-terra (second vendor, read-only) · Lens: full · Author: Claude · System Engineer: David*

**Scope:**
  - AI_AUTO_FAILOVER_P2_DESIGN.md (11,795 chars)
  - AI_SWAP_ARCHITECTURE.md (13,764 chars)
  - ai_provider.py (9,805 chars)
  - AI_VENDOR_STRATEGY_DECISION_2026-07-11.md (14,056 chars)

**Usage:** 13057 in / 6071 out tokens · actual cost ≈ $0.0990

---

# Independent Peer Review Report

## Overall assessment

The revised P2 design resolves several important issues called out in its own revision notes, especially direct probe attribution, T2 denominators, and separation of health from routing for T3. However, there are still material implementation gaps and cross-document contradictions that can cause either incorrect trips, prolonged user latency, or a false belief that the system is safe under multiple workers.

---

## Findings

### [BLOCKER] T1 cannot be implemented from the proposed schema

**Lens:** Design / correctness / operability  
**Files:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §2, §3, §4

The T1 rule is:

> “3 consecutive T1-class failures within 120 s per provider·task” (§4)

and §3 says:

> “A success resets the T1 consecutive counter.”

But `ai_breaker` contains no field for a consecutive T1 failure count or for the timestamp of the first/current failure in that consecutive sequence. `ai_breaker_stats` only has minute buckets with aggregate `attempts` and `failures`; it cannot represent order, failure class, or whether a success occurred between failures.

Therefore, the proposed tables cannot distinguish:

- timeout → timeout → timeout, from
- timeout → success → timeout → timeout,

even though only the first sequence should trip T1.

**Required design correction:** add authoritative per-provider/task T1 state, for example `t1_consecutive_failures`, `t1_first_failure_at`, and optionally `last_t1_failure_at`; update and evaluate it in the same transaction that records the invocation result. Alternatively, use an event table with enough resolution and ordering to compute consecutive failure sequences, but the current aggregate minute buckets are insufficient.

---

### [MAJOR] The claimed multi-worker safety is not true for routing decisions

**Lens:** Correctness / operability / distributed systems  
**File:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §2, §5

The design says:

> “Hot-path reads go through a ~10 s in-process cache” (§2)

and:

> “every transition busts the cache” (§2)

It then says probe claiming is:

> “Safe even if BEA ever runs multiple workers” (§5)

The atomic `UPDATE ... WHERE ...` probe claim is safe against duplicate **probe claims**, but it does not make normal routing safe across workers. Cache invalidation in one Python process does not invalidate another process’s in-memory cache. If one worker trips Anthropic, other workers can continue routing traffic to Anthropic for up to their local cache TTL, likely causing more avoidable 30-second timeouts.

This is especially significant because the design presents multi-worker survival as a property rather than a current single-worker limitation.

**Required design correction:** either:

1. explicitly scope P2 to one process and state that multi-worker deployment is unsupported until shared invalidation exists, or  
2. use a shared cache/version/epoch or authoritative DB read for breaker-exclusion decisions, or  
3. accept and document a bounded stale-routing window, with monitoring and a much shorter breaker-state TTL.

The cache-busting claim must be narrowed to “local process cache” unless a cross-process mechanism is actually specified.

---

### [MAJOR] The heartbeat design can block the asyncio event loop for up to 30 seconds

**Lens:** Performance / operability / availability  
**Files:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §6; `ai_provider.py` `_anthropic`, `_openai`, `_scaleway`

The design specifies:

> “One asyncio task in BEA ... every 60 s ... claim and send ONE probe” (§6)

But all provider adapters in `ai_provider.py` use synchronous `httpx.Client(...)` calls. Their default timeout is 30 seconds:

```python
def complete(... timeout=30):
```

If the asyncio heartbeat task calls `complete()` directly, an unreachable provider can block the event loop for up to 30 seconds. In a typical single-process Uvicorn async application, this can delay unrelated async work, including request handling, scheduled work, and administrative actions.

The “one probe per tick” cost protection does not protect availability.

**Required design correction:** define one of the following explicitly:

- use an async adapter path based on `httpx.AsyncClient`;
- run the synchronous probe in `asyncio.to_thread()` / an executor;
- make the heartbeat an external process/job rather than an in-process coroutine.

Also give probes their own short timeout budget rather than reusing user-request timeout behavior. A health probe should fail fast; it should not spend 30 seconds proving that a provider is unavailable.

---

### [MAJOR] The P2 design bypasses the architecture’s required provider registry and per-task chains without formally superseding that decision

**Lens:** Architecture / maintainability / internal consistency  
**Files:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §5, §9; `AI_SWAP_ARCHITECTURE.md` §3, §4, §6

`AI_SWAP_ARCHITECTURE.md` makes the registry and capability-aware per-task chains core P1 work:

> “A single global chain is wrong because capability differs” (§3)

> “Provider registry (the one new core object)” (§4)

> “P1 — Registry + manual swap v2 ... per-task chains” (§6)

The P2 design instead proposes:

> “Chain build: `[active] + others`” (§5)

and:

> “dict order is a valid chain” (§5)

It defers the chain table to:

> “the full provider registry (P1++)”

This is not merely a harmless simplification. It makes priority implicit in source-code insertion order and keeps routing control coupled to `AI_ACTIVE` / an asserted active-provider override. It also means there is no durable operator-managed ordering, no explicit eligibility metadata, and no per-task forced-primary interface matching the architecture’s intended manual-swap model.

The design says all three present lanes currently support all four tasks, which reduces immediate capability risk, but it does not resolve the architectural contradiction. The P2 design only explicitly supersedes the fail-back doctrine; it does not supersede the registry prerequisite.

**Required design correction:** either:

- make the registry/per-task chain table a prerequisite of breaker deployment, as the architecture says; or
- formally amend `AI_SWAP_ARCHITECTURE.md` with a narrowly defined interim implementation, including its limitations, migration path, and explicit source of task-specific routing priority.

---

### [MAJOR] T3 classification risks converting content/policy failures into manual-lockout “account actions”

**Lens:** Correctness / reliability / product behavior  
**File:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §3

The design treats:

> “unauthorized / credit_exhausted (401/403/provider ban body)”  
> “T3, immediately”

HTTP 403 does not reliably mean account suspension or a provider ban. Depending on provider and endpoint, it may mean organization policy, model access restrictions, IP/region controls, safety policy enforcement, or a request-specific moderation/policy decision. Some of these are account-wide; others are caused by one user’s prompt or image.

A content-triggered 403 classified as T3 would trip the provider/task and require manual restoration, potentially removing a healthy primary lane due to one disallowed request. Conversely, treating all 403s as a generic T3 can conceal a deployment/configuration regression that needs immediate engineering action.

**Required design correction:** define classification against provider-specific structured error codes/types, not status alone. At minimum, retain distinct categories such as:

- invalid API key / revoked key;
- exhausted credits / account suspended;
- model entitlement / organization policy;
- region/IP restriction;
- request content/safety policy rejection;
- unknown 403.

Only verified account-wide failures should create T3. Unknown 403s should alert with enough operational context and have a deliberately chosen trip policy.

---

### [MAJOR] The proposed failover path can still impose very large user-visible latency before the breaker opens

**Lens:** Performance / user experience / operability  
**Files:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §1, §4, §5, §6; `ai_provider.py` `complete()`

The stated motivation is:

> “the app stops sending calls to that lane (each one would only add its timeout to a user’s request)” (§1)

But before the first trip, T1 requires three consecutive failures. The current seam applies the full timeout to each adapter call and then walks fallback providers:

```python
res = fn(... timeout)
if not res.ok:
    for alt in ...:
        r2 = ADAPTERS[alt](..., timeout)
```

With 30-second adapter timeouts, each of the first three requests can spend roughly 30 seconds waiting for the failed provider before reaching the successful fallback. If multiple fallback providers are also unavailable or unconfigured, latency can be worse. The breaker only improves subsequent calls after sufficient failed live requests have paid this cost.

**Required design correction:** specify a failover latency budget. Examples:

- use a significantly shorter connect/read timeout for first-attempt failover-sensitive calls;
- distinguish connect timeout from total read timeout;
- use task-specific budgets;
- permit immediate short-circuiting from recent failures before the formal T1 threshold;
- ensure unconfigured providers are excluded before invocation, as P2 intends.

Without this, “automatic failover” may technically succeed while still producing unacceptable request latency during the first outage minutes.

---

### [MAJOR] The document’s claim that all callers already degrade safely cannot be verified and conflicts with the architecture’s narrower wording

**Lens:** Reliability / correctness / testability  
**Files:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §5; `AI_SWAP_ARCHITECTURE.md` §3; `ai_provider.py`

P2 states:

> “The seam returns an honest failed AIResult when all lanes are down; each caller already degrades.” (§5)

But the architecture says:

> “Every chain ends in a deterministic, zero-AI fallback **where one exists**” (§3)

and gives only examples such as search interpretation and market notes/templates. These are not equivalent claims. “Where one exists” does not establish that all 22 callers safely handle a failed `AIResult`, nor that none dereference `text`, token fields, or provider output under an assumption of success.

The supplied `ai_provider.py` returns failed results, but no call sites or regression test RG-0017 are included. This is a potentially serious availability and correctness claim being assumed rather than demonstrated.

**Required design correction:** require a caller inventory test or explicit test matrix row for every AI call site under all-lanes-down conditions. The test must validate the externally observable result, not merely that `complete()` returns `ok=False`.

---

### [MAJOR] Error sanitization is underspecified for persistence and outbound n8n delivery

**Lens:** Privacy / security / compliance  
**File:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §2, §7

The design stores `last_error` and sends:

> “SANITIZED error summary (≤200 chars, request-ids and echoed content stripped, never prompt/image data)” (§7)

This is the right objective, but it is not an implementable sanitization specification. Provider error bodies may include user-supplied content in quoted messages, JSON fragments, URLs, request metadata, or vendor-specific diagnostic fields. A length limit does not remove personal data. Sending the result to n8n also creates a further data-processing and retention boundary.

The schema has no indication of whether raw error bodies are prohibited, hashed, or retained elsewhere. The phrase “request-ids ... stripped” is also operationally counterproductive: request IDs are often the most useful non-sensitive support correlation value.

**Required design correction:** define an allow-list formatter, not a regex/redaction aspiration. For example, retain only:

- normalized `error_kind`,
- HTTP status,
- provider,
- task,
- provider error code/type from an allow-list,
- a generated local correlation ID,
- optionally provider request ID if assessed non-sensitive.

Do not persist or webhook arbitrary exception text or response bodies. Define n8n retention/access controls and ensure alerts do not carry user-derived values.

---

### [MAJOR] `ai_provider.py` has inconsistent secret loading; Anthropic may not work in the deployment model described by its own module

**Lens:** Security / operability / correctness  
**File:** `ai_provider.py` `envkey()`, `_anthropic()`, `_openai()`, `_scaleway()`

`envkey()` documents:

> “the systemd unit does not export [the server `.env`] to this process”

OpenAI and Scaleway use `envkey()`, allowing fallback to `/var/www/marketsquare/.env`:

```python
key=envkey("OPENAI_API_KEY")
key=envkey("SCALEWAY_API_KEY","FAILOVER_API_KEY")
```

Anthropic does not:

```python
key=os.getenv("ANTHROPIC_API_KEY")
```

Under the stated deployment condition, an Anthropic key placed only in the same `.env` file would appear absent, causing Anthropic to return a generic failed `AIResult`. P2 then needs to distinguish this from real provider failure and mark the lane disabled, but current code has no status/error classification to do so.

This may be masked if Anthropic is separately injected into systemd today, but the supplied material does not establish that.

**Required correction:** use one documented secret-loading mechanism for every provider, preferably avoiding direct application parsing of a broadly readable `.env` file. At minimum, `_anthropic()` should use the same approved resolver and test method as the other adapters.

---

### [QUESTION] What exactly is the manual restore transition, and can it restore a T3 lane before it has reached `ready`?

**Lens:** Correctness / admin safety  
**File:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §1, §5, §7

The T3 sequence says a healthy probe moves the lane to:

> “`ready`, dashboard READY TO RESTORE, routing still excluded until manual restore.” (§5)

But `POST /admin/ai-restore {provider, task?}` is described without state-machine preconditions. The following need a precise answer before implementation:

1. Is restore allowed only from `ready`, or may David override directly from `tripped`?
2. Does restore set `state='closed'`, clear `trip_reason`, reset probe counters, and invalidate routing caches atomically?
3. If `task` is omitted, is the request all tasks for that provider—and is that appropriate if only vision or only text was affected?
4. What happens if a restore races with a failing live request or an in-flight probe?
5. What is the “history” table/schema referenced by “written to the breaker row’s history,” since no history table is defined in §2?

---

### [QUESTION] How will P2 obtain the asserted per-call DB-backed active provider when `ai_provider.complete()` currently only knows module-level `AI_ACTIVE`?

**Lens:** Integration / maintainability  
**Files:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §0, §5; `ai_provider.py` module global and `complete()`

P2 says:

> “The DB-backed active-provider switch ... is passed into the seam per call” (§0)

But the supplied seam’s default is:

```python
AI_ACTIVE = os.getenv("AI_ACTIVE", "anthropic")
...
prov = provider or AI_ACTIVE
```

No call-site code is supplied showing the claimed `provider=` value being passed, and no P2 integration contract defines how the DB-selected provider, breaker exclusions, drill overlay, and per-task task chain combine.

This matters because a module-level environment value is fixed at import time, while the design claims a roughly ten-second DB-cache-driven live switch.

Please provide the actual invocation path and define precedence explicitly, e.g.:

1. drill exclusion;
2. forced/manual active provider;
3. breaker routing exclusion;
4. configured/capable chain;
5. deterministic caller fallback.

---

### [QUESTION] Why are probes excluded during drill mode if the drill is intended to simulate a T3 ban?

**Lens:** Test design / operability  
**File:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §8

The design says the overlay excludes named lanes:

> “from chains and probes exactly as if T3-tripped”

and deliberately writes no breaker state. This is appropriate for preventing drill effects from mutating production health, but it means the drill does not exercise:

- T3 classification;
- T3 trip persistence;
- hourly T3 probe scheduling;
- `ready` transition;
- ready-to-restore alert;
- manual restore authorization and routing effect.

The stated drill validates fallback routing, which is valuable, but it is not a full “ban drill.” Should the runbook distinguish:

- a **routing-overlay continuity drill**, and
- a **sandbox T3 state-machine drill** with isolated DB/webhook destinations?

Those should have separate pass criteria.

---

### [MINOR] The schema needs constraints and timestamps with an unambiguous time basis

**Lens:** Maintainability / correctness  
**File:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §2

`state` and `trip_reason` are free-form `TEXT`; timestamps and bucket keys are free-form ISO strings. This invites invalid states, inconsistent timezone formatting, and hard-to-debug comparison behavior.

Suggested minimum safeguards:

- `CHECK (state IN ('closed','tripped','half_open','ready'))`;
- `CHECK` for known `trip_reason` values or a separately normalized reason enum;
- UTC RFC3339 timestamps with `Z`, or integer epoch milliseconds;
- indexes appropriate for heartbeat eligibility queries, e.g. `(state, probe_after)`.

The current primary key is appropriate for per-provider/task isolation.

---

### [MINOR] The drill environment variable is an operationally fragile control plane

**Lens:** Security / operability  
**File:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §8

`AI_DRILL_BAN` is evaluated on every call and is cleared by unsetting the environment or restarting:

> “Unset the env (or restart without it) and the drill is over instantly.”

For a systemd-managed service, changing an environment variable normally requires a unit/environment-file change plus restart or reload. This creates opportunities for a drill setting to survive unexpectedly, be inconsistently applied across future multi-worker processes, or be altered outside the audited admin control plane.

This is acceptable for a sandbox-only mechanism if tightly controlled, but the design should state that it is forbidden in production or make activation auditable and process-consistent.

---

### [PRAISE] Direct, no-fallback probes correctly fix a subtle but severe attribution error

**Lens:** Correctness  
**File:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §5

This is a strong correction:

> “Probes are direct: `complete(..., provider=target, allow_fallback=False, probe=True)`”

The explicit explanation that fallback success must not mark the failed provider healthy demonstrates sound circuit-breaker reasoning. The atomic claim condition is also substantially better than naïvely allowing every request or heartbeat tick to probe independently.

---

### [PRAISE] The design now separates transient health recovery from T3 routing restoration

**Lens:** Reliability / human factors  
**File:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §1, §5

The T1/T2 auto-close hysteresis versus T3 `ready`/manual restore distinction is well reasoned. In particular:

> “This separates HEALTH (what probes measure) from ROUTING (who gets traffic)”

That separation avoids the common error of treating a successful auth/transport probe as sufficient proof that an account-action incident is resolved operationally.

---

### [PRAISE] T2 now has a denominator and a retention policy

**Lens:** Correctness / cost  
**File:** `AI_AUTO_FAILOVER_P2_DESIGN.md` §2, §4

The rolling `attempts` and `failures` buckets, minimum-attempt threshold, and 15-minute retention are a meaningful improvement over raw failure counts. The rule:

> “attempts ≥ 10 AND failures/attempts ≥ 20%”

avoids tripping a lane because of one noisy failure and keeps the stored telemetry bounded.

---

## The three findings the System Engineer should discuss first

1. **T1 schema impossibility:** `ai_breaker` and `ai_breaker_stats` cannot represent “three consecutive T1 failures within 120 seconds.” This must be corrected before coding starts.

2. **Multi-worker/cache claim and heartbeat blocking:** the design is not actually safe across workers with a local 10-second cache, and the proposed asyncio heartbeat can block the event loop because the seam is synchronous. These are deployment-level availability risks.

3. **Registry/chain architectural divergence:** P2 replaces the approved registry and explicit per-task chains with `[active] + dict-order others` without formally changing the architecture. The System Engineer should decide whether P1 registry work is required before P2 or whether an interim architecture is consciously accepted.

---

## What I could not verify from the supplied material

I could not verify:

- the claimed migration of all 22 call sites to `ai_provider.complete()`;
- the alleged DB-backed `launch_switches.ai_active` provider selection or its per-call integration;
- whether every caller correctly handles all-lanes-down `AIResult(ok=False)`;
- the existing `/admin/flags` authentication dependency, token strength, authorization model, CSRF posture, or audit logging;
- the actual n8n webhook security, data retention, access controls, or alert delivery guarantees;
- live provider model availability, pricing, capability, golden-set results, or server key provisioning;
- SQLite/Postgres choice, transaction behavior, migration framework, and deployment topology beyond the documents’ assertion of one current systemd-owned Uvicorn process;
- the existing cost-rail implementation and whether spend logging is transactionally consistent with provider invocation results.
