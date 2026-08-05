# Internal AI Services Audit — 2026-08-05

*Author's investigation (Claude) · Phase 1 of 2 — Phase 2 is the independent Peer audit
(GPT-5.6 via scripts/peer_review.py, David triggers). Requested by David 5 Aug 2026
(test report through the REPORT tab, then commissioned in session).*

**Scope.** The internal AI service estate end to end: the five user-facing Tuppence
services on the AI Services help card (AI Listing Rewrite, Why No Intros? Audit,
AI Batch Card Lister, Is This a Fair Price?, AI Yield Estimate), the internal AI call
sites behind them (vision orientation, anon rewrite/scan, trust guidance, card grading,
email triage, KYC identity), and the plumbing they all stand on: the provider seam
(ai_provider.py), circuit breaker (ai_breaker.py), tier/feed gating
(ai_service_tiers.py), scoreboard (ai_scoreboard.py), cost rails, and the governance
docs (AI_SWAP_ARCHITECTURE, AI_AUTO_FAILOVER_P2_DESIGN v1.2, AI_VENDOR_STRATEGY
Addenda 1–11). Method: code-on-disk review verified against the design canon and
today's cost-compliance sweep — claims checked, not assumed.

## 1. Verified sound (evidence cited)

- **Seam totality.** No direct Anthropic/OpenAI API calls or SDK imports exist in
  bea_main.py; every inference path routes through `ai_provider.complete()`
  (import at bea_main.py:13; 48 references; RG-0017 asserts it stays that way).
  Adapters: Anthropic (active), OpenAI GPT-5.6 Luna/Terra, Scaleway Mistral-Medium —
  all three use `envkey()` fallback and honest failure classification
  (`status` + `error_kind`, FAILOVER-PARITY-1 applied to all three).
- **Breaker (P2a) real and attached.** `ai_breaker.attach()` runs at BEA startup with
  the n8n alert hook (bea_main.py:72–84), fail-open by design. Atomic probe claim,
  T1/T2 auto-recover with anti-flap hysteresis, T3 ban → manual `/admin/ai-restore`
  only (bea_main.py:12502), stateless AI_DRILL_BAN overlay. 12/12 mandatory tests
  green per design v1.2; seam-level T0 drill executed 1 Aug with real keys.
- **Cost rails.** Today's cost sweep: 17/17 wrapped call sites ceiling-checked and
  spend-logged, 0 critical. Ceilings live in DB (`ai_spend_config`, defaults
  user $0.50/day, platform $100/day); `_check_cost_ceiling` runs BEFORE any Tuppence
  charge; `_log_ai_spend` carries provider attribution (P1). Month-to-date platform
  spend $0.65 over 102 calls.
- **Fixed-price doctrine holds.** All service prices are flat Tuppence (1T/2T/per-run);
  no ad-valorem cost anywhere in the estate (David's 1 Aug pricing ruling).
- **Tier/feed gating.** `ai_service_tiers.py` is pure and testable; every paid data
  provider is OFF (sweep-verified); the paid-feed Pro gate is dormant-but-present as
  designed; hide-where-we-can't-deliver logic intact.
- **Governance machinery live.** Model Register (ai_price_card.json v3, first-party
  prices, gates as tuples), funnel snapshot (RG-0020), lane-vs-register lock (RG-0019),
  price freshness (RG-0018), OpenAI model-id lock (RG-0016). Scoreboard (slow signals)
  wired, spend-gated OFF pending David's click. Peer-review lane operational
  (5 prior reports in Records/).
- **The fault loop is feeding fixes.** TS-0004 (seller's own brand label) and the
  agency-import moderation-parity gap were fixed 5 Aug from tester reports — the
  intake built on 5 Aug is already doing its job.

## 2. Findings

### F1 — HIGH · 15 endpoints hard-gate on ANTHROPIC_API_KEY (vendor-independence breach)

Fifteen endpoints — including all five user-facing services — open with
`if not ANTHROPIC_API_KEY: raise 503 "AI not configured"` (bea_main.py:3319, 4962,
5082, 5158, 5234, 8901, 9117, 9655, 13749, 13831, 14410, 14720, 14942, 15199, 16085)
even though the calls themselves go through the vendor-neutral seam. If the Anthropic
key is absent/revoked while OpenAI and Scaleway lanes are keyed and healthy, every AI
service 503s anyway. This contradicts Addendum 5.2 ("the APP must not need any single
vendor to run"). Note the class subtlety: the 1 Aug AI_DRILL_BAN drill could NOT catch
this (key present, lane banned); only the unconfigured-key variant of the drill —
planned in P2 design §8 but not yet run app-level — would have. **Scope: the whole
class, all 15 sites. Fix: replace with a seam-level "any configured lane" check
(e.g. `ai_provider` helper `any_lane_configured(task)`), then run both drill variants.
Ledger entry required on fix.**

### F2 — MEDIUM · Charge order contradicts the published refund policy (3 of 5 services)

The AI Services card states: "If the AI call fails due to a server error, no Tuppence
is deducted." True for AI3 Price Check (pre-flight `_require_tuppence`, charged only
after a verified result — bea_main.py:14420ff) and AI4 Yield (deliver-then-charge,
Session 95). False for AI1 Rewrite, AI2 Audit, AI5 Batch Cards: each runs
`_deduct_tuppence` BEFORE the model call (bea_main.py:13762, ~13857, ~14955) and AI1's
own failure path admits it — `"AI rewrite failed — Tuppence charged"` (bea_main.py:13813).
**Scope: class of 3. Fix: migrate AI1/AI2/AI5 to the Session-95 deliver-then-charge
pattern (or refund-on-failure inside the same transaction), and make code and copy
agree. Ledger entry required.**

### F3 — DECISION (David) · Help copy names "Claude" per service

Every service description says "Claude rewrites… Claude reviews… Claude estimates…".
Under the Phase-A cost-first routing policy (Addendum 2) and live failover, the serving
lane may lawfully be OpenAI or Scaleway on any given call — the copy would then name
the wrong vendor to users of a trust-branded platform. Options: (a) vendor-neutral
copy ("AI rewrites…"), (b) keep the Claude branding and accept it constrains routing
for those five services, (c) dynamic label from the active lane. **Not a code bug —
a positioning decision only David can make.**

### F4 — INFO · Known open item, re-confirmed

DW-009 (cost sweep WARN): dashboard.server.html:906 references Sonnet outside the
metered AdvertAgent registry — justify or downgrade. Already on the daily watch;
not double-filed here.

### F5 — INFO · P2b/P2c residue (as designed, not drift)

The breaker idle-recovery heartbeat (P2c) is not yet in bea_main.py — between nightly
scoreboard rounds, a tripped lane recovers only when real traffic probes it. Dashboard
breaker lights + Restore button (P2b) and the currency budget reservation are likewise
still queued. Matches the design's own build plan; listed so the audit is complete.

## 3. Phase 2 — the Peer audit (OpenAI, read-only)

Runner ready: `PEER_AUDIT_AI_SERVICES.bat` (repo root) feeds this report plus
ai_provider.py, ai_breaker.py, ai_service_tiers.py, ai_scoreboard.py and the failover
design to the Peer (GPT-5.6 Terra, full-sweep lens) with a focus question asking it to
confirm/refute F1–F5 and hunt for what the Author missed. Cost ≈ $0.05–0.10.
David double-clicks; the report lands in Records/PEER_REVIEW_<date>_full.md.
The Peer reads and reports; it never edits (Addendum 6 charter).

## 4. Status line

Investigation: done. F1/F2 fixes: NOT done (findings filed, awaiting David's go —
F1 is pre-launch blocking by the independence doctrine). Peer audit: prepared,
not run (key + spend are David's). Nothing in this audit was verified against the
live site beyond today's sweep artifacts — code-on-disk is the source of truth here.
