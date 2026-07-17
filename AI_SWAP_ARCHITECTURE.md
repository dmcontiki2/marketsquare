# AI Swap-Out Architecture — Manual & Automatic Provider Failover
*17 Jul 2026 · David + Claude · Grounded in the live seam (ai_provider.py), the unwired
failover module (failover/ai_backends.py), and the locked decisions in
AI_VENDOR_STRATEGY_DECISION_2026-07-11 / AI_PROVIDER_DEPENDENCY_POSTURE_2026-06-19 /
AI_SOVEREIGNTY_PHYSICAL_LAYER_DECISION_2026-07-09.*

## 0. Where we actually stand (audited today)

The good news: the manual switch **already exists**. `launch_switches.ai_active` in the DB,
flippable from the Page-4 admin UI without a deploy, 10-second cache, instant effect
(`_ts_active_provider()`, bea_main.py:1244). `ai_provider.complete()` even has a naive
any-of fallback.

The bad news: **the switch is two-thirds decorative.** Of 22 AI call sites, only 7 route
through the portable `complete()` seam. 15 still build Anthropic-shaped request bodies and
parse Anthropic-shaped responses (they'd break the moment `ai_active=openai`), and 1 (KYC
ID verification) uses the Anthropic SDK directly. `OPENAI_API_KEY` was never provisioned,
and the OpenAI model strings in the seam are 2024-era. Separately, a clean open-weight
failover module (`failover/ai_backends.py`: Qwen3/DeepSeek via any OpenAI-compatible
endpoint, with cost-hook and dry-run support) sits on disk **unimported**.

**Conclusion: before any trigger design matters, the wiring must be finished. A failover
switch connected to 7 of 22 circuits is a hope, not a mechanism** (same doctrine as backups).

## 1. Two swap modes

**Manual swap (strategy-driven).** Human flips the provider — per task tier, not only
globally. Exists today for anthropic|openai; extend to a *provider registry* (§4).
Used for: cost decisions, jurisdiction decisions, deprecations, quality regressions,
planned drills.

**Automatic failover (ops-driven).** A health monitor + circuit breaker flips traffic to
the next provider in a per-task chain, within seconds, and alerts. Used for: outages,
degradation, account actions. **Fail-over is automatic; fail-BACK is manual** — auto
restore invites flapping, and restoring the primary is a judgment call (was the ban real?
is quality unchanged?). A half-open probe keeps testing the failed provider and *reports*
readiness; David (or the morning /pulse) confirms restore.

## 2. Trigger taxonomy

| # | Trigger | Detection | Response | Who decides |
|---|---------|-----------|----------|-------------|
| T1 | **Hard outage** (5xx, timeouts, connection refused) | ≥N failures in M seconds per provider·task (circuit breaker) | AUTO failover, immediate; alert | Machine |
| T2 | **Degradation** (sustained 429 throttling, p95 latency > 3× baseline, error rate > 20%) | Rolling-window stats on live traffic + 60s synthetic heartbeat when idle | AUTO failover after sustained window (not one blip); alert | Machine |
| T3 | **Account action** (401/403 key revoked, org suspended/banned, credits exhausted) | Distinct status-code class; never retried as transient | AUTO failover + LOUD alert (this won't self-heal); half-open probes throttled to hourly | Machine flips, human investigates |
| T4a | **Runaway cost** (daily ceiling approach/breach) | Existing `_check_cost_ceiling` + `_maybe_fire_spend_alert` rails | AUTO degrade: route to cheaper tier/provider, or deterministic fallback (search already does this); never silent overspend | Machine degrades, human reviews |
| T4b | **Price change** (provider reprices, as Moonshot just did at $3/$15) | AI-Watch / manual | MANUAL swap after golden-set eval of the alternative | Human |
| T5 | **Regulatory / geopolitical** (sanctions, export controls, POPIA/GDPR data-residency shifts, the posture doc's trip-wires: model restrictions, regional throttling, gov-routed logging) | External daily AI-Watch + validator divergence signal | MANUAL, deliberate — these are strategy events, not ops events | Human (Solar Council-level) |
| T6 | **Deprecation / forced model migration** | Provider announcements | MANUAL, scheduled, golden-set eval before cutover | Human |
| T7 | **Quality regression** (golden-set score drop, Karoo validator divergence, BIT 3-KPI triples) | Monthly `eval_golden_set.py` cadence + always-on validator | ALERT + manual — quality judgment needs a human | Human |
| T0 | **Planned drill** (monthly) | Calendar | Manual swap to secondary for one hour of live traffic, then back. An untested failover is a hope. | Human |

The taxonomy is deliberately split: **machines handle T1–T3 and T4a because seconds matter
and the right answer is unambiguous. Humans handle T4b–T7 because those are judgment calls
where a wrong automatic answer is worse than a slow right one.**

## 3. Per-task failover chains (capability-aware)

A single global chain is wrong because capability differs — **vision is the constraint**
(8 of 22 features need it: photo orient/draft, anon scans, vision-draft, card grading, KYC).
Each task tier gets its own ordered chain; the circuit breaker trips per provider·task.

    text-fast   (haiku tier):   anthropic → openai → mistral-small → hosted-open (Kimi/DeepSeek/Qwen) → karoo-qwen
    text-reason (sonnet tier):  anthropic → openai → mistral-large → hosted-open → karoo
    vision      :               anthropic → openai → mistral-small(pixtral) → qwen3-vl (hosted → karoo)
    triage      :               anthropic → openai → deterministic rules (already exists for search)

Every chain ends in a **deterministic, zero-AI fallback** where one exists (search
interpret, market notes can degrade to templates) — the platform must limp, not die,
even if every provider is down.

## 4. Provider registry (the one new core object)

Replace the binary `ai_active` with a DB table `ai_providers`:

    id · family(us|eu|open) · jurisdiction · endpoint · key_env · per-task model map ·
    capabilities(text,vision,reason) · status(active|standby|tripped|disabled) ·
    breaker state (fail count, window, half-open) · last_error · last_ok · priority per task

Page-4 admin shows the registry with live status lights; manual swap = reorder/force;
`ai_active` remains as "forced primary" override. `_log_ai_spend` gains a **provider
column** (today it logs only tier — after a swap you can't attribute spend; that must be
fixed in the same change).

## 5. Jurisdiction tiers — US vs EU vs Chinese

**US (primary, locked decision):** Anthropic Haiku/Sonnet stays primary generator;
OpenAI is the second vendor (outage backup + monthly read-only auditor). Both US —
explicitly *not* a jurisdiction hedge. Honors AI_VENDOR_STRATEGY_DECISION_2026-07-11.

**EU (API-level jurisdiction hedge):** Mistral is now the credible option — Small 4
(vision+reasoning+coding merged, ~$0.15/M input, cheap enough for haiku-tier work) and
Large 3 (open-weight MoE), EU-hosted by default, EU AI Act-aligned, on-prem possible.
Add as registry family `eu`, standby. Golden-set eval before it carries live traffic.

**Chinese models — the self-reliance tier, consumed the right way:**
The strategic value of the Chinese labs (Moonshot/Kimi, DeepSeek, Qwen) is that they
publish **open weights at near-frontier quality** — capability you can *hold*, not rent.
But there is a sharp line:

- **Never send user data to Chinese-jurisdiction APIs.** A trust-branded platform holding
  POPIA-regulated seller IDs and KYC documents cannot route that content to Beijing
  endpoints. This is a red line regardless of model quality.
- **Consume Chinese models as weights** — two lanes:
  (a) *Hosted open-weights on neutral infra* (OpenRouter/Together/Fireworks etc. serve
  Kimi/DeepSeek/Qwen from US/EU datacenters): Chinese capability, Western jurisdiction,
  available today, registry family `open`.
  (b) *Self-hosted on the Karoo cluster* (the locked sovereignty decision): hash-pinned
  weights, air-gapped, the gate-closed fallback generator + always-on validator. This is
  the only lane that survives every trigger in §2 simultaneously.

**Kimi K3 specifically** (announced this week): 2.8T-parameter open-weight MoE, 1M context,
native vision, benchmarking at/above Opus 4.8 and GPT-5.6 on early boards — but (1) weights
only release ~27 July, (2) benchmarks are mostly vendor-reported so far, (3) at $3/$15 per M
tokens its API is priced like a frontier model, and (4) **2.8T is not a Karoo workload** —
you don't self-host a 2.8T model on a modest cluster. Practical posture: watch K3 as a
*hosted-open* chain member once independently verified; the Karoo lane stays on the
mid-size weights the failover module already defaults to (Qwen3-32B/VL, DeepSeek distills),
refreshed as better small weights ship. K3's real significance is confirmation that the
open-weight frontier keeps closing the gap — the self-reliance strategy compounds.

### 5b. The ban scenario and the cost argument (David, 17 Jul 2026)

David's stress test: *if the US government bans Claude and ChatGPT exports, the rest of
the world has only Chinese models — EU/UK/Canada/AUS customers must not be disadvantaged.
And cost: if the options are $50 vs $5, everything else fades until EU/UK/AUS have viable
alternatives.* Ruling that follows:

- **Models vs endpoints is the load-bearing distinction.** A US export ban removes US
  *endpoints*; it cannot remove open *weights* already published — Kimi/DeepSeek/Qwen run
  on EU/neutral hosts or on Karoo, under Western jurisdiction, GDPR/POPIA intact. The ban
  scenario therefore makes the open-weight lane MORE important, not Chinese APIs more
  acceptable. Weights already pulled and hash-pinned are un-bannable: **download before
  the ban, not after.**
- **The cheap lane and the safe lane are the same lane.** Open weights create a
  competitive serving market → cents-per-million pricing on neutral infra. The $5 option
  never requires Beijing endpoints. (Kimi K3's own API at $3/$15 is frontier-priced —
  the cheap form of Chinese capability is the weights.)
- **Consequence for priorities:** the hosted-open registry entry (P3) is promoted to
  P1 scope — a standby cheap open-weight endpoint should exist from day one of the
  registry, golden-set-evaluated, so both the ban trigger (T5) and the cost trigger (T4)
  have a live landing zone. Mistral remains the EU hedge alongside, not instead.
- Red line restated precisely: **no customer PII/KYC content to Chinese-jurisdiction
  endpoints. Chinese models themselves: yes — as weights, anywhere we or our hosts run
  them.** Non-PII, non-listing workloads may use any endpoint the registry marks eligible.

## 6. Build plan (phased, each phase shippable)

- **P0 — Finish the wiring (prerequisite, ~1 session):** migrate the 15 raw call sites to
  `complete()`; replace the KYC SDK call with the seam; update stale OpenAI model strings;
  provision OPENAI_API_KEY (blocked on David); run `eval_golden_set.py`. Until P0, every
  other line in this document is theory.
- **P1 — Registry + manual swap v2 (~1 session):** `ai_providers` table, per-task chains,
  Page-4 status lights, provider column in spend log, add Mistral + one hosted-open
  endpoint as standby entries (keys can come later; registry shows them greyed).
- **P2 — Health monitor + circuit breaker (~1 session):** rolling stats per provider·task
  from live traffic, 60s synthetic heartbeat when idle, trip rules per §2 T1–T3, auto
  failover down the chain, n8n alert (reuse spend-alert webhook), half-open probes,
  manual fail-back button.
- **P3 — Open-weight lane (~1 session):** wire `failover/ai_backends.py` into the registry
  as family `open`; golden-set eval monthly (locked cadence); first monthly T0 drill.
- **P4 — Karoo activation (per sovereignty decision timeline):** point family `open`'s
  second entry at the cluster; validator divergence feeds T7.

## 7. What NOT to do
- No auto fail-back (flapping). No global binary switch (capability differs per task).
- No Chinese-jurisdiction APIs for user content, ever — weights yes, endpoints no.
- No swap without a golden-set pass — an available provider is not an *equivalent* provider.
- Don't let the cost rail fail open silently after a swap — degraded-provider spend counts.

## 8. EU lane — LIVE-VERIFIED 17 Jul 2026 (Session 141)
Scaleway Generative APIs (Paris, GDPR-resident) provisioned by David: org TRUSTSQUARE
(PTY) LTD, application `trustsquare-backend`, policy GenerativeApisFullAccess scoped to
the TrustSquare project, key `trustsquare-failover` (expires Jul 2027 — renewal noted
for /housekeep). Live probes through failover/ai_backends.py with primary dead:
- FAST  mistral-small-3.2-24b-instruct-2506 — 1.3s, clean answer
- REASON qwen3.5-397b-a17b — 19.1s (reasoning model: ~250 thinking tokens; needs token
  headroom or thinking disabled for short tasks)
- VISION qwen3.6-35b-a3b — 4.9s (text probe; vision golden-set still pending)
Integration findings for P1: FAILOVER_BASE_URL must EXCLUDE /v1 (module appends it);
Qwen tiers need max_tokens budgets sized for reasoning overhead; parser should fall back
to the `reasoning` field when `content` is null. Credentials: server .env via
add_scaleway_key.bat (gitignored). Cost of full verification: <€0.01.
