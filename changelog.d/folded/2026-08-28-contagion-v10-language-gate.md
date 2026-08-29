## 2026-08-28 — CONTAGION-LANG-1 (the model spread worldwide for the wrong reason — v1.0)

David asked whether we could still reach Canada on English, visibility and referrals, and why we would
not then spread to every other country for the same reasons. Both halves turned out to be right, and the
second half exposed a defect that had survived nine versions.

### Yes to Canada — and we already do it

Toronto, Vancouver and Montreal receive no wave and never have (`pr = 0`). They arrive on the US corridor
(3.0), the South African diaspora corridor (1.8), shared English and public exposure — lighting up weeks
36 to 45. At three years Canada is **5,186 sellers, 3.3%, the eighth largest market**, on zero outbound.
David's intuition was correct and the model already supported it.

### But "why not everywhere else" was the real question, and the answer was: we did

**The public-exposure pathway had no language gate at all.** `sameLang` only ever touched the
seller-to-seller gravity graph — the cross-border trickle, a small term — while the `impr × pubBeta ×
pubReach` pathway that actually drives the whole simulation was purely population-proportional. The
consequence, unnoticed since v0.1: at three years the biggest markets were **Tokyo 13,854 · Delhi 12,171 ·
Seoul 9,328 · São Paulo 8,513 · Mexico City 8,262 · Cairo 7,998**, and **South Africa was 4% of all
sellers**. None of those markets was ever emailed, none shares a language with the product, and the model
reached them faster than it reached Toronto.

Verified against the product on 28 Aug 2026: `marketsquare.html` is `<html lang="en">`, there is no
language switcher and there are no translation strings. The app is English, full stop.

### The fix that did not work, and the one that did

First attempt applied `langPen` as a **rate** penalty. Tokyo dropped from 13,854 to 9,684 and stayed
second — because over a three-year horizon even a five-times-slower market still saturates. **Language is
a ceiling, not a speed bump:** someone who cannot read the app is not a slow convert, they are not in the
addressable market at all. Same shape as the incumbent haircut.

Corrected: `langFit` now scales `N` (addressable sellers) and `GP` (reachable public) at initialisation,
and the per-week multiplier is reduced to the residual friction of the period *before* we localise, so
nothing is double-counted. Countries where English is official or near-universal in commerce take no
penalty; the EF English Proficiency Index's top band (Nordics, Netherlands and neighbours) takes half;
everywhere else pays `langPen` (0.50 / 0.80 / 0.95, tagged **data** — it is a fact about our own HTML).

### What the model says now

| | Before the gate | After |
|---|---|---|
| Top markets at 3 years | Tokyo · Delhi · Seoul · São Paulo · Mexico City · Cairo | **US · India · South Africa · UK · Nigeria · Australia · Philippines · Canada** |
| Tokyo | 13,854 | **2,763** |
| South Africa share | 4% | **6.5%** |
| Total sellers | 248,185 | 158,585 |

Every one of the top ten is now English-official or English-in-commerce. **The spread follows English and
the diaspora exactly as David said it should — the model simply was not enforcing it.** The gate also
takes about 36% off the runaway, which is a bonus rather than the point.

### Localisation is now a costed decision rather than a shrug

Opening French, Portuguese and Spanish at week 26 is worth **+29%** (158,585 → 204,932 sellers) and brings
São Paulo and Mexico City into the top six. New `localiseW` lever, default 157 = never, which is today's
truth. That is the number to weigh against the build cost — and it is the first time the model could
answer the question at all.

### Also fixed: "Cities" was a misleading headline

The top bar counted cities with **≥ 1 active seller**. At week 26 that read 17 — of which **3** were above
the liquidity cliff. Split into **Cities lit** and **Cities working** (liquidity ≥ 0.35, the cold-start
half-works point), with the working figure turning amber when it falls below half of lit, plus both on the
comparison strip and a diagnostic: *"A city with one seller is a pin on a map — under the cliff a seller
lasts about ten weeks, over it about seventy-seven. Spreading wider makes this ratio worse, not better."*

### Verification

`node --check` clean; headless page harness green; before/after comparison run on the same seed with the
gate switched off and on; backups `*.bak-prev10-*` and `*.bak-prelangceil-*`.
