# TrustSquare — Master Roadmap (post-orchestrator)
**v1.0 · 2 June 2026 · synthesized from 6 parallel planning agents**

Each stream has its own detailed doc. This is the sequencing + cross-cutting view.

## Streams & status
| # | Stream | Deliverable | Status | Headline |
|---|--------|-------------|--------|----------|
| 1 | Home-page redesign | `ROADMAP_1_HOME_REDESIGN.md` + `home_mockup.html` | Designed + mockup | Model is taught at the paywall; hero is empty. Add value-prop + first-run explainer, lift the sub-12px type floor, emoji→SVG, desktop frame. |
| 2 | BEA modularization M1 | `ROADMAP_2_BEA_MODULARIZATION.md` | **Build-ready** | 7 symbols → `core_spend.py`; 18 call sites all re-import (zero logic edits); only `_fire_webhook` needs an injection seam. (`smoke_test.py` = 32 checks, not 30.) |
| 3 | FEA streamline | `ROADMAP_3_FEA_STREAMLINE.md` | Plan ready | `ms.js` 11,996 lines / 308 fns / no IIFE → classic scripts, 14 files. `PROP_PHOTOS` (0 refs) + `PROSPECTS` (1) dead-weight candidates. |
| 4 | AI-independence | `ROADMAP_4_AI_INDEPENDENCE.md` | Plan ready | Move Sensor + Orchestrator plumbing to server cron, Sonnet for sparse checkpoints, retire Haiku → **~70–90% maintenance-token cut**. |
| 5 | CityLauncher revive (the gem) | `CityLauncher/CITYLAUNCHER_REDESIGN.md` | Spec ready | The orchestration brain **never ran** (`orchestration.db` = 0 bytes). Dead-source memory resets each cycle (the Gumtree burn). Fixes specced. |
| 6 | Email overhaul | `ROADMAP_6_EMAIL_OVERHAUL.md` + `property_outreach_v2.html` | Plan + 1 draft | 9 templates pre-rebrand (legacy navy+gold vs current steel-blue/Syne); badges don't match canonical `trustTier()`. Inherits #1's look. |

## Cross-cutting findings that shape the plan
1. **The gem's brain never actually ran.** CityLauncher's `orchestration.db` is empty — Haiko/scheduler/expansion is scaffold that never executed against data; the 219 prospects came from the simpler pipeline. So #5 "didn't deliver" because the smart layer was never switched on — *not* tried-and-failed. Reframes #5 from "revive" to "finish + first real run," under the redesign.
2. **Hetzner box constraints (hit #5 + email):** the server IP is already flagged by DuckDuckGo/Bing — server-side SERP harvest is throttled (OSM-first sidesteps it; a residential proxy is the only full fix = a zero-cost-gate exception needing David's nod). Outbound **port 25 is commonly blocked**, so email verification must be **MX-only (free)** + paid-API fallback, not live SMTP.
3. **#1 gates #6.** Email visuals inherit the home-page design language — lock #1 first; the v2 email draft ships on current tokens meanwhile.
4. **#4 is the cheap win:** ~70–90% maintenance-token cut, mostly deterministic migration, and it sets the model-tiering that #5 inherits.
5. **#2 is build-ready today** (surgical, gated, atomic, clear of the 03:30/04:00/05:00 orchestrator windows).

## Recommended sequence (token-aware)
**Wave A — growth + cost (lead):**
- **A1 · #4 P0–P1** — set the model-tiering policy (Opus design / Sonnet sparse checkpoint / deterministic default / Haiku retired) and move the Sensor to server cron. Zero-token, low-risk, immediate saving; establishes the policy #5 inherits.
- **A2 · #5 CityLauncher** — durable dead-source memory + Sonnet checkpoint-strategist + server-side saturation scheduler + MX email-verify (clean the 219) + agent-targeted sources. Biggest build; spec ready. 60-city = ~4–8 truly concurrent draining a rolling 1–3 day pass; self-hosted Overpass to go wider.

**Wave B — foundation (attended, parallelizable):**
- **B1 · #2 BEA M1** (build-ready) → then M2+.
- **B2 · #3 FEA F-series** after M1 proves the pattern. (Modularization is itself what unlocks safe parallel-agent work.)

**Wave C — pre-launch polish:**
- **C1 · #1 home-page** implement (designed + mockup ready).
- **C2 · #6 email** full set after #1 locks the look (v2 draft already in hand).

## Decisions for David
1. **Lead** — confirm Wave A (revive #5 + the #4 cost-cut) leads, or reprioritize.
2. **SERP harvest** — rely on OSM-first only (free), or approve a residential proxy (zero-cost-gate exception) for DDG/Bing?
3. **Email verify** — MX-only free path (recommended), skip live SMTP given port 25, paid API only if too noisy?
4. **FEA plan** — keep `ROADMAP_3` standalone, or fold into `MODULARIZATION_PLAN.md` as siblings?
5. **Cron timezone** — confirm server TZ (UTC vs SAST) for #4 scheduling.

## Token note
Wave A is net cost-*negative* over time: #4 cuts standing maintenance tokens ~70–90%, while #5's Sonnet usage is hard-capped (~6 calls/city/cycle, checkpoints only) and used sparingly pre-launch. The heavy spend was today's parallel planning pass — execution is far cheaper.
