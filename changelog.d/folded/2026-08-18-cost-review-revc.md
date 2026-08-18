## 18 Aug 2026 — PRE-LAUNCH COST REVIEW Rev C (COST-REVC-1)

Full re-costing 11 days before the gate comes down. `MarketSquare_Cost_Breakdown_v2_AIcosts.xlsx`
gains nine Rev C sheets (627 formulas, recalculated clean); Rev A and Rev B sheets preserved
unchanged. Backup: `.bak-20260818-065905-prerevc`.

**New / restated cost lines**
- HUMAN OPERATIONS — 3 people x 2 hrs/day (David's instruction). $1,690/mo at R150/hr, 7-day
  roster. 78% of the fixed base and 5.2x the entire tech stack. Fully parameterised with a
  rate/roster sensitivity grid. THE RATE IS CLAUDE'S PLACEHOLDER, NOT DAVID'S NUMBER.
- ACCOUNTANT from MONTH 1 — R2,000 + R500 software = $154/mo (was $0 in Y1, R2k from Y2).
- AI SWAP-OUT PROVISION — $40 x 7 models = $280 one-off at launch (supersedes $20/lane).
- AI RUNNING COST restated onto the OpenAI base lane: metered API falls 60% (3-yr $10,317 -> $4,127).
- HETZNER — actual bill $32/mo replaces the modelled EUR15.49 line; 2026 repricing documented.
- POSTGRES — budgeted from month 7 at $22/mo (option B), 5 options priced. Launch stays SQLite.
- SUBSCRIPTION REGISTER — 45 rows, every external dependency on-budget for the first time
  (was 5 infra lines). 20 run at $0 on free tiers / open data.
- CASH FLOW + CASH RESERVE — first monthly cash view of Year 1; recommended reserve $16,400.
- FX — ZAR/USD 18.50 -> 16.21 (live). The model was 14% stale.

**Business case impact:** Y1 costs $11,131 -> $35,735; margin 95.3% -> 84.8%; break-even
131 -> 764 sellers (~2.2 -> ~13 founding cities); cash trough -$5,361 at month 6, positive
from month 7. Survives a 75% ramp miss at 50.6% margin.

**Findings raised:** Hetzner grandfathering is one rescale from +129% (RUL-025); CX43 gives 2x
CPU/RAM for +EUR0.50 but must not be taken pre-launch; the Postgres descent rule has taken zero
ground since the July ruling (53 -> 53 expressions, +1 added); 86% of AI spend is subscriptions,
not metered API; external uptime monitor is still an open launch gate with no vendor.

**Superseded:** `Cost_Breakdown_GlobalLaunch.xlsx` and the `3-Year Summary` sheet — banner added.

Deliverable: `PRE_LAUNCH_COST_REVIEW_2026-08-18 — nice.docx` (Professional Navy house style).
Rulings recorded: RUL-023, RUL-024, RUL-025.
