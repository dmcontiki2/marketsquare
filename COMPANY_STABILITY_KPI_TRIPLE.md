# Company-Stability KPI Triple — the first "simple-complex" BIT
**9 July 2026 · MarketSquare / TrustSquare · David's worked example of the 3-D KPI principle (see `AI_SOVEREIGNTY_PHYSICAL_LAYER_DECISION_2026-07-09.md` → "dimensionality of intent"). Same principle, pointed at company health instead of model manipulation.**

## The triple (each axis a measurement; the meaning lives in the interaction)
| Axis | Metric | Window / cadence | Funnel role |
|---|---|---|---|
| **T1** | **EBIT** | 3-month rolling, sampled **every 2 days** | **lagging** — realized profitability (outcome) |
| **T2** | **Daily subscriptions** | per-month rate, averaged to the **last 2 days** | **converting** — commitment to recurring revenue |
| **T3** | **Daily intros** | per-month rate, averaged to the **last 2 days** | **leading** — marketplace activity / liquidity (earliest signal) |

The axes form a **funnel across time-lag**: intros lead → subscriptions convert → EBIT realizes. The holistic view beats the parts because the **phasing and divergence** between a leading, a mid, and a lagging metric is the actual stability signal — no single axis can show it.

## Regime table (the holistic reading — sign of each axis)
| Intros (lead) | Subs (mid) | EBIT (lag) | Regime | Read |
|:---:|:---:|:---:|---|---|
| ↑ | ↑ | ↑ | **Healthy compounding growth** | funnel converts end to end, in phase — sustainable |
| ↑ | ↑ | ↓ | **Investment phase** | growth spend suppresses profit; healthy *only while EBIT bends back up* |
| ↑ | ↓/→ | ↓ | **Hollow growth (vanity)** | activity up, not converting, costing money — leading metric flatters |
| ↓ | ↓ | ↑ | **Harvesting / profitable decline** | EBIT alone looks great; pipeline drying — the cliff a single metric never sees |
| ↓/→ | ↓ | ↓ | **Broad contraction** | sliding in funnel order; already reaching profit — fix the top first |
| ↓ | ↑/→ | ↑/→ | **Leading-edge warning** | intros rolled over before subs/EBIT caught up — earliest axis warns first |
| ↑/→ | ↓ | ↑/→ | **Conversion / retention leak** | top holds, mid breaks — a conversion/churn problem not yet in EBIT |

## Context first — the attribution layer (David, 9 Jul 2026)
**A triple cannot be read without conditioning on the world around it. The same signature means opposite things depending on context — so attribution runs BEFORE the regime playbook, never after.** Intros up + subscriptions down + EBIT up is an internal "conversion/retention leak" only if nothing external moved. In a downturn it is the textbook **distressed-selling** signature: more people list to raise cash (intros up), less discretionary money for subscriptions (subs down), transactional intro revenue rises with volume while growth spend is paused (EBIT up). Not a leak — a resale platform catching counter-cyclical volume.

**Macro snapshot (9 Jul 2026 — refresh each read; do not treat as standing fact):**
- No *declared* global recession, but a real slowdown/squeeze: Middle-East energy shock, renewed inflation, executive sentiment the worst since 2022; Canada in technical recession; JPMorgan ~35% global-recession odds.
- **South Africa (our core users): not in recession but fragile and squeezed right now** — SARB ~1.2% 2026 GDP (cut toward ~1.0% post-shock), economic activity *slipped in June 2026*, weak rand, high fuel, households "feeling the squeeze," Q2 possibly flat/negative.
- **Resale is structurally counter-cyclical:** ~1 in 5 shoppers buy secondhand *more* because of the economy; resale growing 2–3× first-hand.
- **Verdict:** the intros↑/subs↓/EBIT↑ pattern is exactly what a squeeze produces for us — so "leak" is NOT the default reading in this environment.

**Four differential tests that separate cause (same logic as the sovereign differential check):**
1. **Geographic** — is the signature uniform across all our geographies (→ global-macro or a global product change) or concentrated in SA (→ SA-local squeeze or an SA-specific change)?
2. **Change / temporal** — did one of *our* releases or a **Tuppence costing** change coincide with the turn? (endogenous). *Checked 9 Jul: no recent Tuppence price rise; the recent "free intro" change was conversion-positive; recent work was top-of-funnel. Endogenous cause looks unlikely — but re-check every time.*
3. **Category** — distressed selling shows up as **discretionary / high-value resale listings rising** (cars, furniture, collectables — "sell furniture for food"). Even spread argues less for a food-money driver.
4. **Peer / benchmark** — are resale peers seeing the same lift? (external validation; structurally yes).

**Action inverts if the cause is exogenous:** do NOT push subscriptions harder on cash-strapped users, and do NOT protect EBIT by cutting — both deepen the wrong thing. Instead lean into the recession-resilient **transactional 1T intro revenue** (rising with necessity-selling), offer **downgrade / pause / pay-as-you-go** instead of cancel, and recognise you may be a counter-cyclical winner. Worry only if the subs erosion is **structural churn that will not recover when the macro does** — that is the one case where the internal-leak playbook still applies. Same numbers; only context tells you which response is right.

**Generalises:** context-conditioning applies to the manipulation triples too — a frontier-vs-sovereign divergence spike *during a known model update* is expected, not an attack. Every complex-KPI trigger is gated by "did the world change first?"

## Why it is a "simple-complex" KPI
Simple in inputs (three ordinary business numbers), complex in reading (a 3-D regime, not three gauges). It is the same construction rule as the manipulation triples: **each axis is individually ambiguous** (EBIT down could be investment; intros up could be vanity), and **the meaning only resolves in the joint 3-way structure plus the correct funnel phase-lag.** EBIT read alone is the classic liar — it can point up while the company is dying at the top of the funnel; the triple catches exactly that.

## As a BIT (per `BIT_ARCHITECTURE.md`)
- **Type:** complex KPI BIT (longitudinal, interaction-based), not a simple PASS/FAIL.
- **Cadence:** every 2 days (matches the sampling), a slow-cadence tick — well inside the BIT budget.
- **Trigger:** fires on the *regime*, not any single axis crossing a line. "Harvesting" and "Hollow growth" are the S2/S1-worthy triggers (profitable-looking decline / money-burning vanity); "Investment phase" is watch-only while EBIT's second derivative is positive.
- **Baseline:** each axis measured as a trend vs its own rolling baseline; sign + slope feed the regime classifier.

## Status
- ✅ Interactive regime monitor built this session (three-dial demonstrator; classifies all seven regimes live). Working result shown in chat.
- ▢ Wire to live figures (`/dashboard/summary` + subscriptions + intros counters) when David wants it real — the classifier logic is the demonstrator's `classify()` function.
- ▢ Confirm the exact source definitions of "intros" and "subscriptions" against the live schema before productionising (assumed here: intros = buyer→seller/listing introduction events; subscriptions = recurring paid signups).
