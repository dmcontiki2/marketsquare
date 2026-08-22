# Independent Peer Review — 2026-08-22-0715

*Peer: gpt-5.6-terra (second vendor, read-only) · Lens: performance · Author: Claude · System Engineer: David*

**Scope:**
  - Records/FORENSIC_C1C2_BRIEF.md (26,631 chars)
  - Records/PEER_PACK_BEA_EXTRACT.md (120,000 chars TRUNCATED)

**Usage:** 40516 in / 4530 out tokens · actual cost ≈ $0.1354

---

# Performance Peer Review Report

## Overall assessment

The audit correctly identifies that launch-scale capacity is **not measured**, but the supplied code extract exposes several concrete latency and concurrency risks that neither Cycle 1 nor Cycle 2 appears to weigh sufficiently. In particular, one KYC path performs blocking network work directly on the async event loop, and several user-facing workflows can consume shared worker/thread capacity for 20–120 seconds per request or vendor failure.

The current small dataset makes some of these issues unlikely to manifest at 59 sellers, but they are precisely the kinds of failures that become severe during a traffic spike, upstream AI/vendor incident, or a small amount of malicious traffic.

---

## Findings

### [BLOCKER] KYC verification performs synchronous network/AI work inside an `async` function, with a 120-second timeout

**Evidence**

`Records/PEER_PACK_BEA_EXTRACT.md`, `bea_main.py` lines 11112–11177:

```python
async def _sonnet_verify_identity(...)
...
img_bytes = _fetch_kyc_document(doc_url)
...
_sr = ai_provider.complete(
...
    provider=_ts_active_provider(), allow_fallback=False, timeout=120)
```

Unlike the normal AI service endpoints, which use `await asyncio.to_thread(...)` (for example, AI rewrite at lines 16323–16327 and batch cards at lines 17561–17564), this function calls both `_fetch_kyc_document()` and `ai_provider.complete()` directly.

**Impact**

Assuming these are ordinary synchronous HTTP/client functions—as the call style strongly indicates—each KYC request can block the asyncio event loop for up to **120 seconds**, plus document-fetch time. On a single-worker async deployment, this can stall unrelated async routes while a provider is slow or unavailable. Concurrent KYC attempts amplify the problem rather than being naturally isolated.

This is especially concerning because KYC is an image-transfer plus model-inference path, so normal tail latency is likely materially higher than text inference. A vendor brownout turns this into an application-wide latency incident, not simply a failed KYC request.

**Why I disagree with the existing audit posture**

Cycle 1 calls the app “genuinely hard” and Cycle 2 focuses on security properties of KYC rather than its execution model. The explicit `timeout=120` and absence of `to_thread` is a launch-relevant availability defect, independent of whether the KYC security controls are correct.

**Required discussion**

The System Engineer should establish whether `_fetch_kyc_document` and `ai_provider.complete` are synchronous. If so, this route must not execute them on the event loop. It also needs a bounded end-to-end KYC deadline, not merely a 120-second vendor-call timeout.

---

### [MAJOR] Introduction relay can tie up worker threads for up to 40 seconds per accepted introduction and 20 seconds per inbound message

**Evidence**

`Records/PEER_PACK_BEA_EXTRACT.md`, `bea_main.py` lines 5249–5263:

```python
r = _hx.post("https://api.resend.com/emails", ..., timeout=20)
```

`_relay_send_intro_notes()` sends two messages serially:

```python
_relay_forward(seller_email, ...)
_relay_forward(buyer_email, ...)
```

at lines 5289–5291.

`accept_intro()` schedules this as a background task at lines 5764–5769. The inbound relay endpoint invokes `_relay_forward()` inline at lines 5304–5339.

**Impact**

A successful accepted introduction can occupy a background-task thread for up to approximately **40 seconds** when Resend is degraded, because the two 20-second calls are serial. An inbound relay request can occupy a request-handling thread for 20 seconds.

FastAPI/Starlette normally runs synchronous endpoints and synchronous background tasks through a shared thread pool. Under an email-provider incident or an intro burst, relay tasks can consume that finite pool and delay other synchronous endpoints, including database-heavy application paths. The effect is worse because failed sends do not appear to have a short retry/deadline budget or a durable queue that separates customer response capacity from email-delivery capacity.

**Relevant contradiction**

The relay is described as “Background task — never raises” (`bea_main.py` lines 5273–5278). “Background” avoids extending the immediate `accept_intro` response, but it does **not** make the work capacity-free. It still consumes in-process worker resources and shares failure fate with the web process.

---

### [MAJOR] SQLite balance/accounting reads are unindexed full aggregates, and several are executed synchronously in async request paths

**Evidence**

The initial `transactions` schema has no index on `user_email`:

`database.py` lines 57–71:

```sql
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    type TEXT NOT NULL,
    amount INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

The listed indexes cover listings, users, and intro requests, but not `transactions.user_email`.

Balance checks aggregate every transaction for an account:

`bea_main.py` lines 16227–16244:

```python
SELECT COALESCE(SUM(amount), 0) as bal
FROM transactions WHERE user_email = ?
```

`_require_tuppence()` opens another fresh connection to make this aggregate query (`bea_main.py` lines 16261–16267). The AI rewrite route does this from an `async def` and directly invokes synchronous database operations before and after the AI request (lines 16284–16295 and 16346–16350). The same pattern appears in AI audit.

The history endpoint additionally loads **all** a user’s transactions to calculate running balances, before applying pagination:

`bea_main.py` lines 17621–17630:

```python
SELECT COUNT(*) FROM transactions WHERE user_email=?
...
SELECT id, type, amount, description, created_at
FROM transactions WHERE user_email=? ORDER BY id ASC
```

**Impact**

At current traffic and transaction volume this is probably harmless. It does not remain harmless as repeated paid actions, introductions, and transaction histories accumulate:

- Every balance check becomes a scan/aggregate over all matching ledger rows.
- The absence of a `user_email` index makes this increasingly expensive.
- The history implementation has per-user linear read cost even when the caller requests a small page.
- SQLite’s single-writer characteristics combine poorly with many separate connections and synchronous commits.
- In `async def` handlers, synchronous SQLite activity holds the event-loop thread during query and lock waits.

This is a predictable degradation path in a product whose revenue model relies on frequent Tuppence transactions. Cycle 1 identifies SQLite as a future “600–6000” scalability wall, but this particular ledger hot path can become a user-visible latency problem earlier than broad listing-table scale.

---

### [MAJOR] No demonstrated end-to-end timeout budget exists for AI workflows or fallback chains

**Evidence**

Individual endpoint calls set different per-call timeouts:

- AI rewrite: `timeout=20`, lines 16323–16327.
- AI audit: `timeout=20`, lines 16427–16431.
- Batch cards: `timeout=60`, lines 17561–17564.
- KYC: `timeout=120`, lines 11166–11177.
- Breaker heartbeat: `timeout=20`, lines 19478–19480.

Cycle 1 says three AI lanes are live and failover is proven “in the decision layer,” but its test harness “stubs only the vendor sockets.” Cycle 2 notes that the OpenAI base lane serves 100% of live traffic without a production golden run. Neither document states the complete request deadline, retry count, backoff policy, fallback ordering, or whether a timeout in one lane consumes the whole user-facing timeout budget.

The `ai_provider.complete` implementation, which would decide these questions, is not included.

**Impact**

A nominal per-vendor timeout is not a customer latency SLO. If a request serially tries two or three vendors, worst-case latency may be 40, 60, 120 seconds—or more if retries and connection setup are outside the stated timeout. In the batch-card path, a 60-second timeout per attempted lane is particularly dangerous. Failover can improve success rate while making tail latency dramatically worse.

This is exactly the failure mode likely during a partial vendor outage: the system may “eventually succeed” after users have abandoned the UI and retried, multiplying request load and AI spend.

**Required discussion**

The System Engineer should require an explicit matrix for every AI class:

| Workflow | Client-visible total deadline | Per-lane deadline | Maximum lane attempts | Retry policy | Cancellation behavior |
|---|---:|---:|---:|---|---|

Without it, “13/13 failover harness” is not sufficient evidence for acceptable production latency.

---

### [MAJOR] Batch-card requests have a count cap but no evident byte/pixel cap before base64 images are copied into an AI request

**Evidence**

`bea_main.py` lines 17495–17505 cap only image count:

```python
images = req.images[:10]
card_count = len(images)
```

Each supplied base64 string is then inserted into the provider message payload without an apparent decoded-size, encoded-size, dimension, or total-request-size check:

`bea_main.py` lines 17536–17556:

```python
for _, img_b64 in enumerate(images):
...
    content_blocks.append({
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": img_b64,
        }
    })
```

The route then permits a 60-second model call (lines 17561–17564).

**Impact**

“Maximum ten images” is not a meaningful resource bound when each base64 string can be very large. A client can impose memory allocation, JSON parsing, request buffering, outbound payload, model preprocessing, and long inference latency costs before the AI timeout is reached. Concurrent requests can exhaust RAM, CPU, upstream bandwidth, and provider quota.

The Cycle 1 hostile-input test used a 2 MB junk body against `/app/fault`; that does not demonstrate protection for the materially different base64 image ingestion path.

**Note**

This is both performance and cost exposure. The 2T fixed price has no visible relationship to image size or model-input cost.

---

### [QUESTION] The startup loops appear to start once per application process; is the deployment deliberately single-worker, and is nightly work leader-elected?

**Evidence**

The scoreboard registers an application startup handler and starts an infinite loop:

`bea_main.py` lines 19419–19434:

```python
@app.on_event("startup")
async def _ts_scoreboard_nightly():
    async def _sb_loop():
        while True:
...
            await asyncio.get_running_loop().run_in_executor(
                None, _ts_scoreboard.run_nightly)
...
    asyncio.get_running_loop().create_task(_sb_loop())
```

The breaker heartbeat similarly starts a loop on every startup at lines 19443–19486.

The heartbeat does call `_hb_brk.claim_probe()` (line 19467), which suggests an attempt at cross-process coordination for probe ownership. No comparable lease, lock, or leader election is visible around `_ts_scoreboard.run_nightly`.

**Question and performance concern**

If the production ASGI service has multiple workers, or if an overlapping deployment briefly has old and new processes, does every process run the nightly scoreboard? If yes, each can perform vendor probes, database writes, and ranking generation at the same time. That creates duplicate cost, SQLite write contention, and an avoidable overnight load spike.

I cannot determine from the extract whether `run_nightly()` itself is locked/idempotent or whether production is pinned to one process. This should be answered before relying on the job as a low-impact nightly monitor.

---

### [MINOR] AI spend logging is documented as non-blocking but is invoked inline from async request handlers

**Evidence**

The documentation says:

`bea_main.py` lines 1769–1775:

```python
"""Background task: log AI call cost + trigger alert check if threshold crossed.
Non-blocking — called via background_tasks.add_task() after every AI call.
```

However, AI rewrite directly calls it after inference:

`bea_main.py` lines 16323–16332:

```python
_sr = await asyncio.to_thread(...)
...
_log_ai_spend(email, "/listings/ai-rewrite", ...)
```

`_log_ai_spend()` opens a database connection, inserts, commits, invokes alert checks, and closes the connection (lines 1804–1817).

**Impact**

The functional impact is currently small, but the stated non-blocking property is not true for these shown call sites. The response cannot return until the SQLite write/commit and any synchronous alert logic complete. Under database lock contention, this adds tail latency after an already expensive AI request.

This should either be explicitly treated as synchronous, or the actual logging must be made safely asynchronous/durable. The current documentation makes performance reasoning harder because it describes a different execution model from the code shown.

---

### [PRAISE] Most ordinary AI request paths correctly isolate synchronous inference from the event loop

**Evidence**

- Listing rewrite: `await asyncio.to_thread(...)`, lines 16323–16327.
- Seller audit: `await asyncio.to_thread(...)`, lines 16427–16431.
- Batch cards: `await asyncio.to_thread(...)`, lines 17561–17564.
- Heartbeat: `await asyncio.to_thread(...)`, lines 19478–19480.

**Assessment**

This is the right basic pattern when using a synchronous provider abstraction from async routes. The KYC implementation is conspicuous precisely because it deviates from this otherwise sound approach. The use of finite provider timeouts is also better than unbounded outbound requests, although they need to be composed into a true end-to-end deadline.

---

## Internal audit observations

### [MINOR] The load-testing explanation in Cycle 1 was corrected by Cycle 2, but the resulting action remains too weak for the identified risk

**Evidence**

Cycle 1 says Cloudflare blocked a default Python user agent and therefore the origin could not be measured. Cycle 2 falsifies this, reporting that curl, `python-requests`, and browser UAs all receive 200.

Cycle 2 correctly states that the honest reason for no test is a safety choice, not a technical block. However, the proposed fast-follow in Cycle 1 remains merely:

> “a browser-UA, rate-bounded load probe should be built and run in a window David approves, or against a staging copy.”

**Assessment**

Given that the public gate is down and endpoints are anonymously reachable, this should be an explicit launch gate with a staging-or-production-safe method, a defined traffic profile, and acceptance thresholds—not a discretionary fast-follow. The code findings above provide concrete reasons: single-process event-loop blocking, SQLite contention, provider timeout stacking, and unbounded image payloads cannot be assessed by a `/health` snapshot or 120 ms read sample.

---

## The three findings the System Engineer should discuss first

1. **[BLOCKER] KYC blocks the async event loop for up to 120 seconds**  
   `bea_main.py` lines 11112–11177. Confirm whether the calls are synchronous and establish an end-to-end KYC latency/failure budget.

2. **[MAJOR] AI timeout/fallback behavior has no demonstrated user-facing deadline**  
   Per-lane timeouts range from 20 to 120 seconds, while the failover implementation is absent. Require a concrete bound on serial fallbacks, retries, and cancellation before treating multi-lane failover as resilience.

3. **[MAJOR] Relay and image workloads can exhaust limited in-process capacity under vendor slowness or large inputs**  
   Relay sends can consume threads for 20–40 seconds, while batch cards allow up to ten apparently unbounded base64 images. These need resource limits and isolation from interactive request capacity.

## What I could not verify from the material given

- The implementation of `ai_provider.complete`, including actual fallback ordering, retries, connection timeouts, total deadlines, cancellation, and whether it is synchronous.
- The implementation and resource limits of `_fetch_kyc_document`.
- Production ASGI topology: worker count, thread-pool limit, process supervisor behavior, CPU/RAM limits, SQLite journal mode, connection configuration, and reverse-proxy request-size/time limits.
- Whether `ai_scoreboard.run_nightly()` has its own distributed lock/idempotency protection.
- Actual request latency distributions, concurrent-user behavior, database lock contention, queue/thread saturation, or origin capacity under any sustained workload.
- Whether migrations outside the supplied schema add a `transactions.user_email` index or otherwise change the shown SQLite behavior.
