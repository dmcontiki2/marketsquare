# Independent Peer Review — 2026-08-22-0717

*Peer: gpt-5.6-terra (second vendor, read-only) · Lens: maintainability · Author: Claude · System Engineer: David*

**Scope:**
  - Records/FORENSIC_C1C2_BRIEF.md (26,631 chars)
  - Records/PEER_PACK_BEA_EXTRACT.md (120,000 chars TRUNCATED)

**Usage:** 40520 in / 5053 out tokens · actual cost ≈ $0.1417

---

# Peer Review Report — Maintainability Lens

## Findings

### [BLOCKER] `accept_intro` is non-idempotent and can charge the buyer repeatedly

**Evidence:** `PEER_PACK_BEA_EXTRACT.md`, `bea_main.py` lines 5717–5787.

`PUT /intros/{intro_id}/accept`:

- reads the introduction (lines 5721–5725),
- unconditionally sets `status = 'accepted', tuppence_charged = 1` (lines 5740–5743),
- unconditionally inserts a `-1` transaction against the buyer (lines 5744–5748),
- has no check that the intro is currently pending,
- has no conditional update such as `WHERE status = 'pending'`,
- has no unique transaction key/idempotency key,
- does not use `_deduct_tuppence`, so it does not even enforce that the buyer has a positive balance before the extra debit.

A retry after a timeout, a repeated browser request, or an authorized seller intentionally repeating the request will create another debit and another “accepted” event. This is especially dangerous because the response always says `"Introduction accepted — 1T charged"` (line 5787), normalizing the repeated charge.

This is not merely an edge-case implementation issue: money-like ledger writes must be idempotent. The transaction schema at `database.py` lines 57–64 has no reference to an intro ID or uniqueness constraint that could protect against this route-level omission.

---

### [MAJOR] The core monolith is creating duplicated workflow logic and inconsistent correctness properties

**Evidence:**

- Cycle 1 scorecard: “`bea_main.py is a 1.0 MB single file`.”
- `PEER_PACK_BEA_EXTRACT.md`: `bea_main.py (19639 lines)`.
- AI endpoints are embedded in the same file at lines 16272 onward, 16935 onward, 17249 onward, 17484 onward, while relay, auth, flags, startup workers, schema migrations, operational routes, and dashboard state are also embedded there.

The extract demonstrates repeated copies of a similar paid-AI workflow:

1. determine charged identity,
2. apply cost ceiling,
3. preflight Tuppence balance,
4. call provider,
5. parse model JSON,
6. log spend,
7. deduct Tuppence,
8. commit,
9. return a service-specific result.

This pattern is separately implemented in:

- AI Rewrite: lines 16273–16357,
- AI Audit: lines 16362–16464,
- AI Price Check: lines 16935 onward,
- AI Yield: lines 17249 onward,
- AI Batch Cards: lines 17484–17607.

The duplication has already produced inconsistent ordering and identity handling:

- In AI Rewrite and AI Audit, `_bind_charged_email(...)` occurs before `_require_tuppence(...)` (lines 16281–16293 and 16370–16394).
- In AI Price Check, `_require_tuppence(email, _charge)` occurs **before** `_bind_charged_email(...)` (lines 16976–16978). The balance preflight can therefore be evaluated against caller-supplied identity rather than the ultimately bound session identity.
- In AI Batch Cards, `_bind_charged_email(...)` is called but its returned canonical email is discarded (line 17497); every later billing operation still uses `req.seller_email` (lines 17498, 17504, 17568, 17597).

The code comments present ACCOUNT-BIND-1 as a uniform enforcement mechanism, but this repeated endpoint logic means the next engineer cannot safely assume uniform behavior. This is exactly the maintenance failure mode of a single-file monolith: policy is implemented repeatedly rather than once.

---

### [MAJOR] AI Batch Cards discards the account-binding result, making the charged-identity policy structurally unreliable

**Evidence:** `PEER_PACK_BEA_EXTRACT.md`, `bea_main.py`:

```python
17497 _bind_charged_email(req.seller_email, ts_user, "ai5-batch-cards")
17498 _check_cost_ceiling(req.seller_email)
...
17504 _require_tuppence(req.seller_email, 2)
...
17597 remaining = _deduct_tuppence(_conn2, req.seller_email, 2, _bc_charge_desc)
```

Compare the intended helper contract at lines 5159–5177:

> “Returns the canonical charged email.”

AI Batch Cards invokes that helper but ignores its return. When binding is enabled and the supplied email matches the authenticated user, this happens to work. But the function’s policy result is not actually propagated through the service. A future refactor that permits a missing caller field, changes normalization, or modifies the helper’s binding behavior will silently cause the ceiling, ledger, spend log, and response to use a different identity from the authorization decision.

This is a maintainability concern with direct billing implications. The endpoint should have one canonical charged-email variable, assigned once from the binding function and used for every subsequent authorization, budget, accounting, logging, and deduction operation.

---

### [MAJOR] Background operational loops are process-local and have no visible single-runner or lifecycle control

**Evidence:** `PEER_PACK_BEA_EXTRACT.md`, `bea_main.py`:

- Scoreboard startup loop: lines 19419–19434.
- Breaker heartbeat startup loop: lines 19443–19486.
- In-memory lane-alert state: lines 1827–1828.

Both loops are started by FastAPI’s `@app.on_event("startup")` and then run indefinitely via `asyncio.create_task(...)`.

There is no evidence in the supplied material of:

- a leader-election mechanism,
- a distributed lock,
- a deployment guarantee of exactly one application worker/process,
- shutdown cancellation/await handling,
- persisted scheduler state.

Consequences:

- If the service runs multiple workers or overlapping instances during deploy, **every instance starts a nightly scoreboard loop**. Unlike the heartbeat loop, the scoreboard invocation at lines 19429–19431 has no visible claim/lock. This can multiply vendor calls, produce duplicate scoreboard records, and create contradictory results.
- The heartbeat has `claim_probe(...)` (line 19467), which may reduce duplicate work, but that behavior is not enough to establish correct multi-process operation from this extract.
- `_LANE_ALERT` is module-local state. A restart resets the “off-base since” clock, and multiple workers each maintain conflicting clocks. Thus the stated “>60 min” alert semantics in lines 1823–1825 are not durable operational semantics.

The code claims these loops are safe because failures are exception-walled, but silent multiplication and reset-on-restart behavior are different failure classes. The scheduling responsibility needs to be owned by a single explicit runner or a persistence-backed distributed coordination mechanism, not implicitly by every web process.

---

### [MAJOR] The claimed AI spend-control model has unclear and conflicting schema ownership

**Evidence:** `PEER_PACK_BEA_EXTRACT.md`:

- `ai_spend_config` creation, lines 885–895, defines only:
  - `monthly_income_usd`
  - `alert_threshold_pct`
  - `alert_email`
  - `last_alerted_at`
- `/admin/ai-spend/summary`, lines 6181–6195, reads:
  - `daily_user_ceiling_usd`
  - `daily_platform_ceiling_usd`
- The summary explicitly reports that a zero/unset platform ceiling means:
  > `"AI spend is UNCAPPED"` (line 6195).

The supplied creation schema and the operational query disagree. There may be omitted `ALTER TABLE` migrations elsewhere in the 19,639-line file, but that cannot be verified from this truncated pack. As presented, this is difficult to maintain because the authoritative schema is dispersed among initialization code, likely migrations, and route assumptions.

The inconsistency matters materially: `_check_cost_ceiling(...)` is presented repeatedly as a hard financial control, while the admin summary openly describes an unset ceiling as uncapped. A next engineer cannot tell whether a fresh deployment gets a functioning ceiling, a runtime SQL error, or an uncapped service without reconstructing migration history from the full file and production database.

---

### [MAJOR] User-facing AI-price copy materially contradicts the actual service contract

**Evidence:**

- `marketsquare.html` lines 1584–1586:
  > “Our AI compares the asking price to current SA market rates and gives a verdict — fair, above or below market — plus a suggested fair range.”
- `bea_main.py` lines 17089–17113:
  > “we do NOT sell a guess,”  
  and return `verdict: "cannot_verify"`, `source: "no_feed"`, `charged: False`, `official_range: "N/A"` where no verified feed exists.

The backend’s documented integrity model is substantially more conservative than the public help card. That conservatism is good, but the UI is advertising a general market-rate comparison and suggested fair range for “any listing,” whereas the backend explicitly refuses to do this without a verified feed.

This is not just copy drift: it creates support burden, refund/charge disputes, and future pressure for engineers to weaken the no-guess policy in order to make the marketed feature appear functional. The source of truth should be consolidated so product copy describes the actual category/tier/feed-dependent outcome.

---

### [MINOR] The AI spend logger’s contract says “background task,” but the shown service routes call it synchronously

**Evidence:**

- `_log_ai_spend` docstring, lines 1769–1775:
  > “Background task: log AI call cost + trigger alert check…”  
  > “Non-blocking — called via `background_tasks.add_task()` after every AI call.”
- AI Rewrite calls it directly at lines 16329–16332.
- AI Audit calls it directly at lines 16433–16436.
- AI Batch Cards calls it directly at lines 17566–17569.
- KYC calls it directly at lines 11187–11189.

The function writes SQLite data, commits it, invokes spend-alert logic, and invokes lane-alert logic. It is therefore not non-blocking in the shown code paths, despite its contract and implementation commentary saying it is.

This creates misleading maintenance documentation and makes response latency dependent on accounting/database/webhook-adjacent work. Either the function is deliberately synchronous and should be documented as such, or all call sites should consistently schedule it as background work with a defined reliability model. The current mixed interpretation is a trap for future changes.

---

### [MINOR] “Fail-open” broad exception handling is overused for load-bearing behavior, obscuring production diagnosis

**Evidence:**

- Breaker attach:
  ```python
  203 try:
  ...
  214     _ai_brk.attach(database.get_db, alert=_brk_alert)
  215 except Exception as _brk_e:
  216     ...warning("ai_breaker attach failed (fail-open)")
  ```
- Lane alert configuration fallback, lines 1831–1844, silently falls back to hard-coded defaults.
- Account-binding and relay-switch DB reads each catch broad exceptions and collapse to `False` (lines 5129–5140 and 5196–5207).
- `_log_ai_spend` catches all exceptions and only logs them (lines 1818–1819).

Some failure isolation is appropriate. However, in a monolith already relying on feature switches, filesystem config, SQLite, process-local caches, and startup tasks, this pattern makes the application remain “up” while silently losing billing controls, account binding, relay functionality, breaker behavior, or alerts.

The comments make these fallbacks sound uniformly safe, but they have different safety semantics:

- Account binding fails open to effectively legacy identity behavior when its flag read fails.
- Breaker attachment fails open to a “naive any-of fallback.”
- Spend logging failure can leave a reservation unsettled, depending on omitted `_settle_hold` and hold-cleanup behavior.
- Scheduler failures can result in no monitoring at all.

These should not all be represented by generic exception walls. At minimum, each needs an observable health state that the operational dashboard and launch checks can distinguish from a healthy enabled state.

---

### [MINOR] The relay feature combines transactional state changes, side effects, and fallback behavior in a way that is hard to reason about

**Evidence:** `bea_main.py` lines 5740–5769.

The route:

1. accepts and charges the intro,
2. commits it (line 5749),
3. then tries to mint relay aliases (lines 5755–5759),
4. on alias-mint failure, logs an error and sets `_relay_on = False` (lines 5760–5762),
5. thereafter follows the legacy contact-disclosure path for the webhook (lines 5770–5786).

The comment says this is a “legacy flow,” but the acceptance and charge have already committed. The final user-visible result can thus depend on a post-charge alias-mint operation. The exact behavior of other notification paths is not supplied, so I cannot determine whether this can disclose counterpart addresses, but the code’s own comment says relay-off preserves the pre-relay behavior in which raw addresses are used.

This is a difficult transaction boundary for a future maintainer: a privacy mode switch is being resolved after irreversible accounting state has been committed. The design needs a clearly documented state machine for “accepted, relay pending,” “accepted, relay active,” and “accepted, relay unavailable,” rather than a boolean changed in an exception handler.

---

### [QUESTION] Why do “computed totality” claims and local comments disagree on AI call-site count?

**Evidence:**

- “Computed totality evidence” lists `ai_provider.complete` at 23 line locations:
  `[15, 4023, 6292, 6428, 6498, 6797, 10322, 10518, 11137, 11166, 13523, 15877, 15882, 16325, 16429, 17118, 17403, 17562, 17785, 18749, 19479, 19495, 19563]`.
- The comment at lines 1688–1690 says migration completed at:
  > “P0 at 22/22 call sites.”
- The Cycle 1 report says the seam is proven but separately identifies an untested production OpenAI golden run.

Is line 15 a harmless import/reference, a call that the grep misclassified, or has a 23rd call site been added without the “22/22” invariant and related regression checks being updated? This is exactly the kind of stale totality claim that becomes dangerous in a monolith: reviewers may believe every invocation has the desired billing, fallback, KYC, and logging behavior when a newly added call path may not.

---

### [QUESTION] Is account binding actually enabled for launch, and is its state independently monitored?

**Evidence:**

- ACCOUNT-BIND-1 is described as:
  > “Dark until `launch_switches.account_binding = 1`” (lines 5122–5127).
- Its DB-read failure behavior returns `False` (lines 5129–5140).
- The Cycle 2 report calls app authentication “genuinely hard,” but does not state the live state of `account_binding`.
- `accept_intro` only checks actual listing ownership inside `if _account_binding_enabled():` (lines 5727–5739).

The material does not establish whether the production switch is enabled, whether launch checks assert it, or whether an inability to read the switch is surfaced as a red operational condition rather than silently treating binding as off. This is both a security and maintainability question because the code’s behavior changes substantially based on an unverified database flag.

---

### [PRAISE] The extract contains unusually useful inline operational intent and specific safety rationale

The code frequently records why non-obvious behavior exists, rather than merely what it does. Good examples include:

- pre-dispatch reservation rationale at lines 897–902;
- provider failover cost attribution at lines 1779–1785;
- KYC’s explicit `allow_fallback=False` privacy decision at lines 11166–11177;
- account-binding’s distinction between a user session and a review token at lines 5143–5156;
- relay’s explicit anti-header-injection sanitization at lines 5231–5233.

This is valuable engineering evidence. The principal maintenance concern is not lack of explanation; it is that these well-explained policies are distributed across a 19k-line file and reimplemented in endpoint-specific variants.

---

### [PRAISE] Cycle 2 correctly identified the monolith and duplicate admin-gate logic as a maintainability risk

**Evidence:** `FORENSIC_AUDIT_CYCLE2_PEER — nice.docx`, Maintainability row:

> “`bea_main.py` ~1.0 MB single file; RG-0075 CONFIRMED OPEN (admin-gate script duplicated across 5 files). Strong change machinery offsets but does not erase 2am-diagnosis risk.”

I agree with the downgrade to AMBER. The extract supports this conclusion. I would go further: the practical risk is not simply file size or a difficult 2 a.m. diagnosis; it is already visible as policy drift between billing endpoints, scheduled background behavior, public copy, and schema assumptions.

---

## Internal Documentation / Evidence Quality Observations

### [MINOR] Evidence-grade language in the audits is not consistently applied

Cycle 2 says:

> “Every green re-checked against a live probe this session”

and also says:

> “all PROBED this session”

Yet profitability is explicitly based on an “Independent economic model (recomputed from PRICING_CANON)” and table evidence says `EXECUTED+READ`; it is not a live probe of profitability. Similarly, the Cycle 1 “BIT 8/8 fresh PROBED” assertion is later qualified by Cycle 2 as containing disk/source-sourced subchecks.

Cycle 2 identifies the latter issue, which is good. But the document’s headline phrasing remains stronger than its own evidence taxonomy permits. This makes future audit comparison harder because “PROBED” is being used both narrowly and rhetorically.

---

## The Three Findings the System Engineer Should Discuss First

1. **Repeated introduction charges:** `PUT /intros/{intro_id}/accept` has no idempotency or status guard and inserts a new buyer debit on every successful repeat request. This is the highest-priority correctness and customer-impact defect.

2. **Policy drift caused by the monolith:** the repeated paid-AI endpoint template has already diverged in binding order and identity use, with AI Batch Cards explicitly discarding the canonical bound identity. The System Engineer should require a single reusable charged-service path before adding further services.

3. **Unowned background scheduling and monitoring:** startup-created infinite loops, module-local alert state, and no demonstrated cross-worker coordination make nightly probes and alerts nondeterministic under normal deployment/restart patterns. This is a direct cost, observability, and operational-maintenance risk.

## What I Could Not Verify From the Material Given

- Whether omitted migrations add the `daily_user_ceiling_usd` and `daily_platform_ceiling_usd` fields that `/admin/ai-spend/summary` requires.
- The live values of `account_binding`, `intro_relay`, scoreboard enablement, AI spend ceilings, and the actual deployment worker/process count.
- Whether `ai_breaker.claim_probe(...)` is database-atomic and sufficient to coordinate multiple service processes.
- The complete implementation of `_check_cost_ceiling`, reservation creation/expiry, `_settle_hold`, `auth.require_api_key`, `_require_admin`, and the omitted AI call sites.
- Whether external clients can trigger repeated acceptance in the deployed UI/API, although the supplied route code itself is plainly non-idempotent.
- Whether relay fallback after alias-mint failure actually exposes counterpart addresses through all downstream notification paths; the webhook path indicates it can, but the complete notification flow was not provided.
