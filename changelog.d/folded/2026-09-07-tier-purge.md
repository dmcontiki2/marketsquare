## 2026-09-07 — TIER-PURGE-1: the retired five-tier pricing model is out of the code (RUL-107, RG-0335)

David asked whether we had removed all remnants of the old tier process. We had not. The five-tier
model (Standard $12 / Professional $20 / Business $40 / Elite $100 / Premium $15) was retired in
June 2026 and pinned out by PRICING_CANON.md, but it was still live in seven places, two of which
were not inert.

**A retired tier was still payable.** `paid_tiers` accepted standard/professional/business/elite,
so a POST to `/payment/seller-subscription/initialize?tier=elite` would charge R1,800/month for a
tier nobody may hold. The docstring said "existing users only"; nothing in the code enforced it.

**The canon Pro tier was refused a feature it pays for.** `_PAID_TIERS`, the multi-city reach gate,
held starter plus the retired Premium name and did **not** contain `pro`, so a Pro seller extending
a listing got 402 "requires a Starter subscription ($5/month)" — told to buy a cheaper plan than
the one they were on. Latent: probed the same day, there are 0 Pro sellers.

**Probed before touching anything:** 71 users — 54 free, 17 starter, zero on any retired tier, zero
pending downgrades. The "existing users" the exemption protected did not exist.

**The most dangerous line was a comment**, deleted rather than moved: a NOTE in
`launch_redemption.py` instructing that any user whose row said `starter` be moved onto the retired
$12 tier before granting. Acted on today it would have taken all 17 live canon Starter sellers onto
a retired tier — the resurfacing itself, written down as an instruction.

**Why nothing caught it:** `check_pricing_canon.py` printed ALL IN LINE every day for three months
because every check asked only whether the CURRENT numbers were present. A guard that never asks
what should be ABSENT cannot see a remnant. Closed in the same commit (§3, retired-absent in code)
and given an independent second opinion as ledger **RG-0335 (LOCKED)**, which was proven to go red
by reintroducing both faults on a scratch copy.

Also corrected: `Codices/SOLAR_COUNCIL_MASTER_INDEX.md` stated the five-tier model as the current
seller model in three places — a session reading it would have taken it as canon.

Changed: bea_main.py (`_SELLER_SUB_TIERS`, `paid_tiers`, `_PAID_TIERS`, `_FADE_WINDOWS`),
launch_redemption.py (`TIER_TUPPENCE_MONTHLY`, `_TIER_LABELS`, `_DEFAULT_VELOCITY`, the NOTE),
ai_service_tiers.py (`PAID_FEED_ALLOWED_TIERS`), scripts/check_pricing_canon.py,
scripts/regression_ledger.py (RG-0335), scripts/rulings_check.py (RUL-107), RULINGS.md,
Codices/SOLAR_COUNCIL_MASTER_INDEX.md. PRICING_CANON.md unchanged — it was right all along.
