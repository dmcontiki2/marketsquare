## 2026-08-26 — RUL-057 (Johannesburg as second proving city) · LAUNCH-METRICS-1 · CHIP-GREEN-1 · WAVE-CAP-1

**RUL-057 — Johannesburg promoted to wave 1.** David's call: JHB is likely the biggest SA
market, so it belongs in the evidence, not behind it. It now runs Pretoria's ladder
day-for-day from 28 Aug. Wave board → v3.1: new JHB row under Pretoria, lagged block down to
**9 SA cities**, volume row recomputed (60/day warm-up; 1–2 Sep unchanged at 420/330; 3 Sep
300→270; 4–6 Sep 390→360). `data/cities.json` and the dashboard `CITIES_JSON` in CityLauncher
moved JHB to wave 1 / active. rulings_check RUL-057 asserts it and trips if "10 SA cities"
ever returns.

**WRONG-FILE-1 — a near miss worth recording.** The JHB edit was first applied to
`Visuals/MarketSquare/WAVE_PLAN_LAUNCH_2026.html`, which is a **stale v2-era snapshot** that
ships nowhere. The canonical board is `MarketSquare/WAVE_PLAN_LAUNCH_2026.html` (in the deploy
manifest as `static/wave_plan.html`). The stale copy still carried the PROPERTY day that
RUL-056 removed, so publishing from it would have silently reinstated a ruling David had
already reversed. Caught by reading RULINGS.md before writing, not by any assertion. The
Visuals copy was restored untouched. **Lesson: `Visuals/` holds INDEX COPIES; never edit one —
edit the file the deploy manifest names.**

**WAVE-CAP-1 — the scraper could not reach the quota the plan assumes.**
`CityLauncher/pipeline/run.py` capped at `CAP_PER_CATEGORY = 20` while RUL-053 sends 30 per
category per city per day and `fill_wave_gaps.py` already computed shortfall against 30.
Observed live on the first Johannesburg run: `[SKIP] Estate Agents 41/20`, `Tutors 25/20`,
`Services 32/20` — the three biggest categories skipped outright. Raised to 30; the spec
decides, the cap follows. Verified live on the re-run (`41/30`).

**LAUNCH-METRICS-1 — eight launch-day numbers on one view** (David's request). New
`GET /dashboard/launch-metrics` + a LAUNCH METRICS card on `dashboard.server.html`. Gated
behind `_require_admin_or_key` — it carries the **Paystack balance**, and LAUNCH-API-
FAILCLOSED-1 was landed hours earlier the same day precisely because a convenience endpoint
had been left anonymous. Every tile carries its own `measured` flag; unmeasured tiles paint
grey **NOT MEASURED** and never show a number. **FNB is permanently unmeasured** — no FNB
integration exists and bank-login automation is out of scope, so the gap is stated on the face
of the dashboard rather than omitted. Ledger **RG-0190** (LOCKED).

**CHIP-GREEN-1 — 21 Ops Map chips shipped pre-painted GREEN.** RG-0172's needle list
enumerated only three chips, so 21 others still carried `class="om-chip g"` in static markup
with a placeholder value of "—" — a counterfeit verdict before any feed answered, the exact
RG-0133 class. Found by audit, not by the assertion, which is the point. All 21 reclassed to
`om-chip nw`; RG-0172 now enforces it **structurally** (any id-bearing chip carrying the green
class in static markup trips red), so the class cannot return one chip at a time. Four
remaining `om-chip g` without ids are static statements of fact ("free tier", "cost R 0"), not
measurements, and are left alone.
