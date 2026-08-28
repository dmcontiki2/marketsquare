## 2026-08-28 — CONTAGION-SAT-1 (the plateau explained, and the model now says so)

David asked why profits stagnate in the last slope of year three — good growth from December of
year two to about April of year three, then decline. Traced, and the model knew the answer without
ever reporting it.

### It is saturation of the seller pool. Not competition.

No clone ever arrives — `compW` defaults to 157 = never — and the incumbent share is a fixed haircut
on the addressable market, not a rival taking our people. What actually happens:

| | wk 78 (Feb 28) | wk 104 (Aug 28) | wk 120 (Dec 28) | wk 136 (Apr 29) | wk 156 (Aug 29) |
|---|---|---|---|---|---|
| Share of addressable sellers who have listed | 85.1% | 92.8% | 93.9% | 94.9% | **96.0%** |
| First-time listers per week | **10,854** | 397 | 323 | 260 | **239** |
| Churn out per week | 7,353 | 5,103 | 4,579 | 4,352 | 4,303 |
| Came back per week | 2,157 | 3,527 | 3,662 | 3,713 | 3,764 |
| Net sellers per week | +5,658 | −1,179 | −594 | −379 | −300 |

New recruitment collapses **45×** between week 78 and week 156 while churn stays roughly flat. The
return trip (dormant → listing again) is what stops it falling off a cliff: it supplies ~3,760 a week
against ~4,300 leaving. The dormant pool ends at 161,223 against 249,207 active — the model has become
a churn-and-return equilibrium against an exhausted recruiting ground.

### Revenue lags sellers by about a year, and that is the shape David is seeing

Across 24 seeds: **sellers peak at week 83 (April 2028)** and decline from there; **revenue peaks at
week 156** and in 0 of 24 runs is it more than 2% below its peak at the end. So revenue does not fall —
it **bends**. The cause is compositional: revenue rides on buyers (planner runs 75% of it, buyer subs
and introductions most of the rest), and only **4.0% of the reachable public** has become a buyer by
week 156, against 96% of sellers. The buyer side is nowhere near exhausted — but the buyer engine is
*powered by sellers* (`impr` × active sellers), so buyer growth decelerates as the seller base
flattens. Money curve bends without ever falling.

### The plateau DATE is robust; the LEVEL is not

Sweeping `smeDen`, the model's number-one driver and still a pure guess:

| smeDen | Addressable pool | 80% listed | Peak sellers |
|---|---|---|---|
| 0.6 | 159,208 | wk 77 (Feb 2028) | 106,215 |
| 1.2 | 318,171 | wk 81 (Mar 2028) | 212,912 |
| 1.8 (mid) | 477,173 | wk 76 (Feb 2028) | 319,629 |
| 3.0 | 795,211 | wk 77 (Feb 2028) | 531,905 |
| 4.0 | 1,060,264 | wk 84 (Apr 2028) | 710,325 |

A 6.6× larger addressable market delays saturation by about **eight weeks**, because the growth is
exponential — the pool size sets the ceiling, not the timing. Same for the incumbent haircut: 30% →
85% moves the 80% mark only from week 81 to week 73. **So the shape and the date of the plateau are
robust findings; the height of it is an artefact of the least-grounded number in the model.**

### Fixed: the model was silent about its own binding constraint

Saturation never appeared in the binding-constraint strip, even when it was the thing actually
governing the curve. Added:

- Two new exposed stocks — `addressable` (sum of the per-city seller pool after the incumbent haircut)
  and `publicPool` — plus `sellerLeft` and a true first-time-lister counter `newListers`.
- A diagnostic that fires above 50% penetration (amber above 85%): names saturation explicitly, prints
  the penetration, the collapse in first-time listers, states that **no competitor has arrived**, and
  flags that the whole plateau sits on `smeDen`.
- A paired diagnostic on the other side: how little of the reachable public has been converted, and why
  revenue keeps climbing after sellers stop.
- Two rows on the comparison strip: **New listers /wk** and **Seller pool left**.

### Verification

`node --check` clean; headless page harness green end to end; flow balance reconciles
(new + returned − churned = net, checked at weeks 78/104/120/136/156); backup `*.bak-presat-*`.

Standing caveat unchanged: 96% of the world's addressable sellers listing is the runaway regime, not a
forecast. The S-curve, the year-two seller peak and the year-three revenue bend are the findings; the
levels are not.
