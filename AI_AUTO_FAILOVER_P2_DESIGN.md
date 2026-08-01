# AI Auto-Failover — P2 Implementation Design v1.1 (breaker · heartbeat · drill)

*31 Jul 2026 · v1.1 — revised same day after the first independent Peer review
(Records/PEER_REVIEW_2026-07-31-0608.md, GPT-5.6-terra: 3 BLOCKER, 6 MAJOR, 3 MINOR,
3 QUESTION, 2 PRAISE — all three blockers accepted and folded in) and David's recovery
ruling. Grounded in AI_SWAP_ARCHITECTURE.md §2/§4, AI_VENDOR_STRATEGY_DECISION Addenda
3–6, and the live seam (ai_provider.py, 22/22 call sites). Build: one session P2a, one
short session P2b+P2c.*

## Plain language first: what "tripped" means

The same as the breaker in an electrical panel. When a provider keeps failing, its
breaker TRIPS: the app stops sending calls to that lane (each one would only add its
timeout to a user's request) and traffic runs on the surviving lanes. A tripped lane is
then probed until it proves healthy. What happens NEXT is David's ruling below.

## 0. Where we stand (audited 31 Jul)

- The seam is TOTAL: all 22 AI call sites route through `ai_provider.complete()`
  (RG-0017 asserts it stays that way). The DB-backed active-provider switch lives in
  bea_main.py (`launch_switches.ai_active`, `_ts_active_provider()`, ~10 s cache) and is
  passed into the seam per call — noted here explicitly because the Peer, given only
  ai_provider.py, correctly flagged that it could not see this. AI_SWAP_ARCHITECTURE §0
  describes the HISTORICAL 17-Jul state (7/22); this document describes today.
- Three lanes wired: Anthropic (active), Scaleway EU (keyed standby, golden-set passed),
  OpenAI GPT-5.6 (wired + keyed for the Peer; server key pending — RG-0016 locks ids).
- Failover today is a naive per-call any-of: no memory, no alerting, no blip-vs-ban
  distinction, no drill mode. P2 adds the memory, the judgment, and the alarm bell.

## 1. Recovery doctrine (David's ruling, 31 Jul 2026 — supersedes blanket manual-fail-back)

| Trip class | Fail-over | Recovery |
|---|---|---|
| T1 outage / T2 degradation ("dropouts") | automatic | **AUTOMATIC**, with anti-flap hysteresis: 3 consecutive probe successes spanning ≥ 5 min → lane closes, traffic returns, "recovered" notice sent |
| T3 ban / account action (and drill) | automatic | **MANUAL ONLY.** Probes may prove health → state becomes `ready` and the dashboard says READY TO RESTORE, but routing stays excluded until David presses Restore — a ban has a REASON, and he considers it before walking back in |

Rationale: for dropouts the outage was the provider's problem, and auto-return with
hysteresis cannot flap (the old blanket-manual rule existed to prevent flapping — the
hysteresis window does that job without the dashboard chore). For bans, context first.
This separates HEALTH (what probes measure) from ROUTING (who gets traffic) — the
Peer's blocker #2, resolved.

## 2. State objects (Peer blocker #1 folded in)

    CREATE TABLE IF NOT EXISTS ai_breaker (
      provider TEXT NOT NULL, task TEXT NOT NULL,
      state TEXT NOT NULL DEFAULT 'closed',   -- closed | tripped | half_open | ready
      trip_reason TEXT,                       -- T1_outage | T2_degraded | T3_account
      tripped_at TEXT, probe_after TEXT,
      probe_ok_streak INTEGER NOT NULL DEFAULT 0,
      first_probe_ok_at TEXT,                 -- start of the current success streak (hysteresis)
      last_error TEXT,                        -- SANITIZED summary, ≤200 chars (see §7)
      last_error_at TEXT, last_ok_at TEXT,
      PRIMARY KEY (provider, task));

    -- rolling stats: T2 needs a DENOMINATOR, not just a failure count (Peer blocker #1)
    CREATE TABLE IF NOT EXISTS ai_breaker_stats (
      provider TEXT NOT NULL, task TEXT NOT NULL,
      bucket_minute TEXT NOT NULL,            -- ISO minute, e.g. 2026-07-31T06:41
      attempts INTEGER NOT NULL DEFAULT 0,
      failures INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY (provider, task, bucket_minute));
    -- retention: delete buckets older than 15 min on write; T2 reads the last 10.

Per provider·task, not global — vision can trip while text lanes stay up. Hot-path reads
go through a ~10 s in-process cache; ALL state TRANSITIONS are authoritative atomic
writes, never cache-mediated (§5), and every transition busts the cache.

## 3. Failure classification (Peer majors #4/#5 folded in)

`AIResult` gains `status` (HTTP int or None) and `error_kind`, set even on malformed
bodies: `timeout | connection | http_5xx | rate_limited | unauthorized |
credit_exhausted | unconfigured | invalid_request | unknown`.

| Signal | Counts toward |
|---|---|
| timeout / connection / http_5xx | T1 (consecutive) and T2 (failure) |
| rate_limited (429) | T2 only — one 429 is throttling, not an outage |
| unauthorized / credit_exhausted (401/403/provider ban body) | T3, immediately |
| invalid_request (400/422) | NEITHER — that is OUR bug; separate "deployment bug" alert, never a lane trip |
| unconfigured (no key) | NOTHING. The lane shows DISABLED, is excluded from chains silently, never trips, never alerts. An unkeyed standby is configuration, not an outage |

A success resets the T1 consecutive counter. A fallback provider's success NEVER credits
the failed provider (probes are direct — §5). p95-latency degradation from the
architecture's T2 is explicitly DEFERRED to P2c (needs a latency baseline first) — the
doc discrepancy the Peer flagged, now a stated decision instead of an omission.

## 4. Trip rules

| Trigger | Rule | Action |
|---|---|---|
| T1 hard outage | 3 consecutive T1-class failures within 120 s per provider·task | trip → probe_after now+5 min, alert |
| T2 degradation | last 10 min of ai_breaker_stats: attempts ≥ 10 AND failures/attempts ≥ 20 % | trip (sustained, never one blip), alert |
| T3 account action | one T3-class signal | trip IMMEDIATELY → probe_after now+60 min, LOUD alert (won't self-heal) |
| T4a cost | existing `_check_cost_ceiling` rails, unchanged | rails stay senior to all of this |

## 5. Mechanism — inside `complete()`, nowhere else (Peer blocker #3 folded in)

- Chain build: `[active] + others`, minus lanes whose state or `unconfigured` status
  excludes them. Today all three lanes cover all four task tiers (verified: every row in
  TASK_MODEL is complete and vision-capable), so dict order is a valid chain; the
  capability-aware per-task chain table arrives with the full provider registry (P1++)
  and this section is where it plugs in.
- Every REAL call records attempts/failures into the stats buckets for the provider that
  actually served or failed it — attribution is per adapter invocation, never per chain.
- **Probes are direct**: `complete(..., provider=target, allow_fallback=False,
  probe=True)` — no chain walk, so a probe's outcome is unambiguously the target's
  (the Peer's blocker #3: a probe that silently fell back to Scaleway would mark
  Anthropic healthy). Probe claiming is ATOMIC:
  `UPDATE ai_breaker SET state='half_open', probe_after=<now+lease> WHERE provider=? AND
  task=? AND state IN ('tripped','half_open') AND probe_after <= now` — rowcount 1 claims
  the probe; anything else does not probe. Safe even if BEA ever runs multiple workers
  (today it runs one systemd-owned uvicorn process; this survives that changing).
- Probe success paths: T1/T2 lane → streak+1; when streak ≥ 3 AND ≥ 5 min since
  first_probe_ok_at → state 'closed', traffic returns (auto-recover per §1). T3 lane →
  state 'ready', dashboard READY TO RESTORE, routing still excluded until manual restore.
- Deterministic zero-AI floors stay where they live today — at the call sites
  (search-interpret degrades to the deterministic parser; draft-from-photo degrades to
  the template draft; deliver-then-charge makes a no-result free). The seam returns an
  honest failed AIResult when all lanes are down; each caller already degrades. Named
  here explicitly because the Peer correctly noted the seam itself holds no fallback.

## 6. Heartbeat (idle recovery detection)

One asyncio task in BEA (systemd owns the process — nothing on disk schedules itself):
every 60 s, if any row is eligible (tripped/half_open, probe_after passed, no real
traffic probed it), claim and send ONE probe — one per tick TOTAL, round-robin across
eligible rows, so a bad night can never multiply cost. Text ping only (~$0.00002): it
proves transport/auth/model health; true VISION quality remains the golden-set eval's
job, not a heartbeat's. T3 rows probe hourly and alert LOUD once at trip, not hourly.
Heartbeat spend is logged through `_log_ai_spend` like all spend.

## 7. Alerts, dashboard, data handling (Peer major #9 folded in)

- Transport: the existing n8n webhook lane. Payload: provider, task, trip_reason,
  SANITIZED error summary (≤200 chars, request-ids and echoed content stripped, never
  prompt/image data), timestamp. Alerts: trip (LOUD for T3), recovered (T1/T2 auto),
  ready-to-restore (T3), deployment-bug (invalid_request class).
- `/flags.ai_provider` gains `breaker` per provider·task: state, trip_reason, tripped_at,
  sanitized summary. Registry card: green ACTIVE/STANDBY · amber TRIPPED (reason) ·
  blue READY TO RESTORE (button) · grey DISABLED (no key).
- `POST /admin/ai-restore {provider, task?}` — same admin-token auth dependency as
  `/admin/flags` (the existing state-changing admin pattern), and every restore is
  written to the breaker row's history (who-when) for the audit trail.
- Spend attribution: `_log_ai_spend` gains the provider column in the SAME change.

## 8. Drill mode (Peer major #8 folded in: overlay, never state)

`AI_DRILL_BAN=<provider>[,provider]` is a NON-PERSISTENT ROUTING OVERLAY evaluated on
every call: the named lanes are excluded from chains and probes exactly as if T3-tripped,
but NO breaker rows are written, real health state is never mutated, and alerts route to
a distinct "DRILL" notice (never the LOUD T3 alarm). The dashboard shows a DRILL badge.
Unset the env (or restart without it) and the drill is over instantly — nothing to clean.

**Sandbox independence protocol:** key into sandbox .env → OpenAI STANDBY on the card →
Test → golden-set eval vs Luna/Terra → `AI_DRILL_BAN=anthropic` → run BIT journeys + one
vision-draft + one paid flagship → PASS = every AI feature served with Claude absent →
unset, log as the first monthly T0 drill. NOTE (Peer question #15, correct): REMOVING the
Anthropic key instead tests the `unconfigured` path — also worth one pass, but it is a
different test than a ban simulation; the runbook runs both and expects DISABLED (silent)
for the first, DRILL badge for the second.

## 9. Build plan

- **P2a (~1 session):** AIResult status+error_kind · both tables · breaker logic +
  direct-probe mode in `complete()` · drill overlay · provider column in spend log.
  Mandatory test matrix (adopted from the Peer's review): T2 rolling denominator and
  bucket expiry · concurrent probe claim (atomicity) · probe with fallback disabled ·
  attribution to the correct provider·task · unconfigured lane trips nothing · 401/403 +
  credit-body classification · malformed/non-JSON error bodies retain status ·
  T1/T2 auto-recover hysteresis (no flap) · T3 requires manual restore · restore's
  routing effect · drill on/off leaves no state · all-lanes-down honest failure.
- **P2b (short):** /flags breaker block · card lights + Restore · n8n alert wiring.
- **P2c (short):** heartbeat task · latency baseline + p95 T2 clause · first live T0
  drill · ledger entry LOCKED.

## 10. What NOT to do (inherited, binding)

No global binary switch. No Chinese-jurisdiction endpoints for user content. No lane
carries production traffic without a golden-set pass. Cost rails never fail open after a
swap. And the one amendment: automatic fail-back is now ALLOWED for T1/T2 with the §1
hysteresis — and remains FORBIDDEN for T3/bans, where David decides.
