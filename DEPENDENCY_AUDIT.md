# TrustSquare Kill-Switch / External-Dependency Audit

**Date:** 27 June 2026 · **Trigger:** the BIT self-test was found to depend on Claude/Cowork to run — the watchman that certifies our independence was itself dependent on a third party. The Fable case (a dependency a government used as a kill switch) makes this a first-class architectural fault, not a footnote.

## The principle (restated as a testable rule)
TrustSquare's prosperity must not hinge on any **irreplaceable** external variable. The danger isn't dependency per se — it's *coupling that can't be swapped*. A kill switch only kills you if the thing behind it is wired in everywhere and cannot be changed in one place. The standard we already applied to the app's AI *feed* providers (`ai_service_tiers.DEFAULT_PROVIDERS` — any-of, config-selected, swap in one place) must apply to EVERY external dependency, including the inference provider (Claude) and the agent layer.

**The test for every dependency below:** *"If this vendor switched us off tonight, what breaks, how fast can we swap, and is the swap in ONE place or many?"*

---

## Dependency register (by kill-switch exposure)

| # | Dependency | What it powers | If it dies | Swap seam today? | Exposure | Mitigation |
|---|---|---|---|---|---|---|
| D1 | **Anthropic / Claude** (inference) | All AI features (vision draft, rewrite, price-check, yield, triage, market-note, coach) AND the BIT/Fix agent layer | Every AI feature errors; the self-test/fix loop goes dark | **NO single seam** — `ANTHROPIC_API_KEY` + raw `api.anthropic.com` + `x-api-key`/`anthropic-version` headers + model strings hardcoded across **~15 BEA call sites** | **HIGH** — Fable-class. Swapping = editing 15 sites. | **Build `ai_provider` seam (D1-FIX): one module, any LLM behind it, config-selected, all call sites route through it.** Mirror DEFAULT_PROVIDERS. Then Claude = a plug-in, swappable in one place. |
| D2 | **BIT/Fix trigger = Claude/Cowork scheduler** | Runs the self-test, mitigator, fix loop | Self-test stops cycling exactly when most needed | Partial — the BIT code is already a separate, stdlib-only, zero-dep article; only the TRIGGER is Claude | **HIGH** | **Move the load-bearing loop to a Hetzner cron/systemd timer (system Python).** Claude becomes a cockpit (view/explain/propose), never life-support. |
| D3 | **Paystack** (payments) | Top-ups, the money-in path (31 refs) | No new Tuppence can be bought; existing balances still work | Single provider, no abstraction | **HIGH** (revenue) but **graceful** (read paths survive) | Wrap payment init/verify/webhook behind a `payment_provider` seam; keep a second processor (e.g. Stripe/Flutterwave) configurable. Cash non-refundability already insulates ledger. |
| D4 | **Hetzner** (single host) | The entire BEA + DB + dashboard live on one box (178.104.73.239) | Total outage — site down | None — single point | **HIGH** | Documented restore path + off-box backups; medium-term: image/snapshot + a warm-standby plan. The BIT's S1 watcher should ideally run OFF this box so a box death is still reported. |
| D5 | **Cloudflare** (edge, CDN, email worker, cache) | TLS, caching, inbound email routing (8 refs) | Edge errors / stale assets / inbound mail drops | None | **MEDIUM** | DNS can repoint to origin; email worker has a safety-net forward. Document the origin-direct fallback. |
| D6 | **Gmail / SMTP** (outbound mail) | Auto-emailer, support replies (27 refs) | No outbound notifications | App-password config, single sender | **MEDIUM** | Already noted: a transactional sender (Resend, used in CityLauncher) behind a `mail_provider` seam. |
| D7 | **AI feed providers** (eBay, Scryfall, BrickLink, Numista, JustTCG, Mapbox, Google Places, OSM) | Fair-price/value chips | A feed dies → that chip goes quiet | **YES — already seamed** (`DEFAULT_PROVIDERS`, any-of, source_health ladder) | **LOW** | This is the model to copy. Independence already correct here. |

---

## Findings, ranked

1. **D1 (Claude inference) is the worst offender and the most ironic** — we seamed the *feeds* but hardwired the *brain*. ~15 call sites each carry the Anthropic key, endpoint, headers, and model. This is the Fable exposure in its purest form. **Highest priority.**
2. **D2 (BIT trigger on Claude)** — the safety system inherits D1's exposure. Fixed cheaply by moving the trigger to the box.
3. **D3/D4 (Paystack, Hetzner)** are high-impact but partly graceful (read paths / ledger survive). Seam + standby plan.
4. **D5/D6** are medium and already have partial fallbacks.
5. **D7** is the proof the principle works — copy it everywhere.

## The unifying fix: the "provider seam" pattern (one place to swap)
For each irreplaceable vendor, introduce ONE module that the rest of the code calls, with the vendor chosen by config — never hardcoded at the call site:
- `ai_provider`   → Claude / OpenAI / local model   (D1)
- `payment_provider` → Paystack / Stripe / …        (D3)
- `mail_provider` → Gmail-SMTP / Resend / …          (D6)
- feeds → already done (`DEFAULT_PROVIDERS`)          (D7)

A vendor going dark then becomes a one-line config change, not a 15-site emergency. That is the operational meaning of "independent."

## Status
- ✅ Audit recorded (this file).
- ▢ **D1-FIX** `ai_provider` seam — designed next (AI_PROVIDER_SEAM.md); staged refactor of the ~15 call sites, gated (touches AI/cost paths) — David lands the deploy.
- ▢ **D2-FIX** BIT trigger → Hetzner cron/systemd; Claude demoted to cockpit.
- ▢ D3/D4/D5/D6 seams + standby — backlog, prioritised after D1/D2.
