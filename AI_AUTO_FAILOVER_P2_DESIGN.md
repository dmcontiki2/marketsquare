# AI Auto-Failover — P2 Implementation Design (breaker · heartbeat · drill)

*31 Jul 2026 · designed for David's go · grounded in AI_SWAP_ARCHITECTURE.md §2/§4,
AI_VENDOR_STRATEGY_DECISION Addenda 3–5, and the live seam (ai_provider.py, 22/22 call
sites as of today). Build size: one session for P2a, one short session for P2b+P2c.*

## 0. Where we stand after today (audited)

- The seam is TOTAL: all 22 AI call sites route through `ai_provider.complete()`
  (vision-draft, the last raw site, migrated 31 Jul — RG-0017 asserts it stays that way).
- Three lanes wired: Anthropic (active), Scaleway EU (keyed standby, golden-set passed),
  OpenAI GPT-5.6 (wired, awaiting key — RG-0016 locks the ids).
- Failover today is a NAIVE per-call any-of: a failed call walks the chain once, every
  call, forever. No memory (a dead provider is re-tried on every single call, adding its
  timeout to every user request during an outage), no alerting (David learns from users),
  no distinction between blip and ban, no drill mode.

P2 adds the memory, the judgment, and the alarm bell. Doctrine unchanged: **fail-over is
automatic, fail-back is manual** (§1 of the architecture doc).

## 1. The one new object: `ai_breaker` (SQLite, sibling of launch_switches)

    CREATE TABLE IF NOT EXISTS ai_breaker (
      provider    TEXT NOT NULL,            -- anthropic | openai | scaleway
      task        TEXT NOT NULL,            -- haiku | sonnet | vision | triage
      state       TEXT NOT NULL DEFAULT 'closed',   -- closed | tripped | half_open
      fail_count  INTEGER NOT NULL DEFAULT 0,
      window_start TEXT,                    -- ISO ts of the current failure window
      trip_reason TEXT,                     -- T1_outage | T2_degraded | T3_account | drill
      tripped_at  TEXT,
      last_error  TEXT, last_error_at TEXT, last_ok_at TEXT,
      probe_after TEXT,                     -- when the next half-open trial is allowed
      PRIMARY KEY (provider, task));

Per provider·task, not global — vision can trip while text lanes stay up (§3 of the
architecture doc: capability is the constraint). Read through a ~10 s cache exactly like
`_ts_active_provider()` so the hot path costs one dict lookup, not one DB hit per call.

## 2. Trip rules (mapped to the §2 taxonomy — machine judgment only where unambiguous)

| Trigger | Rule | Action |
|---|---|---|
| T1 hard outage | 3 consecutive adapter failures (exception/timeout/5xx) within 120 s for one provider·task | trip → `tripped`, probe_after = now + 5 min, alert |
| T2 degradation | over a rolling 10 min: ≥ 10 calls AND ≥ 20 % not-ok | trip (sustained window, never one blip), probe_after = now + 5 min, alert |
| T3 account action | any 401/403, or the provider's explicit ban/credit-exhausted error body | trip IMMEDIATELY, probe_after = now + 60 min (it won't self-heal), LOUD alert |
| T4a runaway cost | existing `_check_cost_ceiling` rails — unchanged, they already degrade | no breaker involvement; rails stay senior |
| drill | `AI_DRILL_BAN` names this provider (§6) | treated exactly as T3, tagged `drill` |

Adapters must surface the STATUS CLASS for this to work: `AIResult` gains one field,
`status` (int HTTP status or None on exception). One-line change per adapter; no call-site
churn (dataclass default keeps the signature compatible).

## 3. Mechanism placement — inside `complete()`, nowhere else

The seam is the only chokepoint every call already crosses; the breaker lives there:

    def complete(...):
        chain = [active] + [others]                  # today's order, unchanged
        chain = [p for p in chain if breaker.allows(p, task)]   # skip tripped lanes
        for prov in chain:
            res = ADAPTERS[prov](...)
            breaker.record(prov, task, res)          # ok -> reset window / close half-open
            if res.ok: return res                    # fail -> count toward T1/T2/T3
        return last_res                              # all lanes down -> honest failure

`breaker.allows()` returns True for `closed`, True-once for `half_open` when
`probe_after` has passed (that single live call IS the probe — success closes the
breaker and fires a "ready to restore" notice; failure re-trips and pushes
`probe_after` out again), False for `tripped`. Zero extra spend: probes are real user
calls, not synthetic ones, except the idle heartbeat below.

Deterministic floors stay senior: chains still end in the zero-AI fallback where one
exists (search interpret, template drafts) — the platform limps, never dies.

## 4. Heartbeat (idle recovery detection) — smallest honest version

A tripped provider with zero traffic would stay tripped forever without probes. One
asyncio background task in BEA, started at boot: every 60 s, ONLY IF some breaker row is
`tripped`/`half_open` AND its `probe_after` has passed AND no real call has probed it in
the last window, send a 10-token ping through the seam for that provider·task
(~$0.00002 on Luna/Haiku). It writes the breaker row like any call. No tripped rows =
the task sleeps; the idle system spends nothing. (Nothing-on-disk-schedules-itself
doctrine is respected: this rides the BEA process, which systemd already owns.)

## 5. Alerts + fail-back (manual, on the dashboard)

- Alert transport: reuse the existing n8n spend-alert webhook (`_maybe_fire_spend_alert`
  pattern). Payload: provider, task, trip_reason, last_error, timestamp. T3 marked LOUD
  (n8n can escalate to email — David's existing flow).
- `/flags.ai_provider` gains `breaker`: per provider·task state + trip_reason +
  tripped_at + last_error. The Page-4 registry card shows amber TRIPPED with the reason,
  and a **Restore** button when a half-open probe has reported ready.
- `POST /admin/ai-restore {provider, task?}` (admin-token) closes the breaker manually.
  There is NO automatic fail-back (flapping; §7 doctrine).
- Spend attribution: `_log_ai_spend` gains the provider column in the SAME change (the
  P1 leftover — after a swap, spend must be attributable per provider or the cost rails
  report fiction).

## 6. Drill mode — the sandbox ban test, first-class

`AI_DRILL_BAN=anthropic` (env, or comma list) makes the seam treat that provider as
T3-tripped WITHOUT touching keys: adapters never called, breaker rows tagged
`trip_reason='drill'`, dashboard shows a DRILL badge so a real outage is never confused
with an exercise. Unset the env (or POST /admin/ai-restore) to end the drill.

**Sandbox independence protocol (David's #4):**
1. OPENAI_API_KEY lands in the sandbox .env (platform.openai.com credit — the $20
   ChatGPT subscription is separate and contributes nothing to the API; $5–10 credit is
   ample: a full golden set + drill on Luna costs cents).
2. Dashboard: OpenAI shows STANDBY; press Test (live 1-call probe through the seam).
3. Golden-set eval vs Luna/Terra (the standing gate — an available provider is not an
   equivalent provider).
4. Drill: `AI_DRILL_BAN=anthropic` (or simply remove the Anthropic key in the sandbox —
   today's SEAM-GATE change means vision-draft and every other endpoint stays alive on
   the surviving lanes).
5. Run the BIT journeys + one real vision-draft + one paid-tier flagship. PASS = the app
   served every AI feature with Claude absent. That is the independence proof.
6. Restore, then log the drill as the first T0 entry (monthly cadence per §2).

## 7. Build plan (each phase shippable, David lands each deploy)

- **P2a (~1 session):** `AIResult.status` + breaker table + breaker logic in
  `complete()` + `AI_DRILL_BAN` + provider column in spend log. Unit tests: transition
  table (closed→tripped→half_open→closed; T3 immediate; drill). Ledger: new entry
  asserting the breaker table exists and `complete()` consults it.
- **P2b (short):** /flags breaker block + registry-card lights + Restore endpoint/button
  + n8n alert wiring.
- **P2c (short):** idle heartbeat task + first live drill (T0) + promote its ledger entry.

## 8. What NOT to do (inherited, binding)

No auto fail-back. No global binary switch. No Chinese-jurisdiction endpoints for user
content (weights yes, endpoints no). No lane carries production traffic without a
golden-set pass. Cost rails never fail open after a swap — degraded-provider spend counts.
