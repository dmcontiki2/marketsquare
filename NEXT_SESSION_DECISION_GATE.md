# Next session: wrap the AI decision-gate process (David + Claude, agreed 31 Jul 2026)

Context: today shipped GPT-5.6 lane, Peer Reviewer (3 reviews in Records/), P2 design
v1.1, Live-Values kit (ai_price_card.json + price_truth.py + RG-0018, Addendum 7).

TO BUILD (Addendum 8 — "decision-gate process"):
1. Funnel: VALUE PROPOSES (aa_index points-per-$ ranking, capability floor per tier),
   FITNESS DISPOSES (golden set = binary accept/reject, never re-ranks; cheapest passer
   wins the tier; #1 fails -> try #2, never lower the bar).
2. Triggers only (Addendum 3): measured failure, forced exit, or deliberate review —
   sitting models are not re-auditioned continuously.
3. STABILITY / ANTI-JITTER (David's ruling 31 Jul, to parameterize tomorrow —
   numbers below are PROPOSALS): a switch must show REAL added/lost value, e.g.
   >=30% sustained cost delta at equal-or-better gate result, or measured capability
   regression on our tasks; sustained across >=2 price-card refreshes (>=30 days);
   "one model beats another by 2 cents today" NEVER moves production.
4. Implement: aa_index + value-score column in ai_price_card.json + price_truth.py
   (funnel output per tier: shortlist -> gate verdict -> eligible winner);
   pin missing AA v4.1 scores (Sonnet 4.6, Mistral Medium 3.5 — chart-only on AA site);
   record all as Addendum 8; ledger entry if a new invariant emerges.

STANDING OPEN ITEMS: David: Scaleway console price check (card note pending);
OpenAI server key + Luna/Terra golden set (pin effort level — Luna max=51, low=33);
P2a build (design v1.2 first: fold full-sweep findings — T1 consec state, async-safe
heartbeat, _anthropic envkey consistency, timeout stacking).

CONSOLE FINDINGS (David, 31 Jul evening): Scaleway Cost Manager verified — 2026 Generative APIs usage EUR 0.12, fully offset by "Generative APIs Free Tier" credit -0.12 -> net EUR 0.00. (1) reconciliation path works; (2) FREE TIER exists and has absorbed all usage — find its monthly cap and record it on the price card; (3) Medium unit-rate check still open (Cost Manager shows aggregates, not rates — use the per-product detail or console pricing panel).
UPDATE (later 31 Jul): Cost Manager granularity ends at PRODUCT level (no per-model lines/rates); billed rate unobservable while free tier nets everything to EUR 0. RESOLUTION for card: pricing-page rate EUR 1.50/7.50 STANDS as the live value; mark console check "not observable until free-tier exhaustion, reconciliation will confirm"; record free tier on card. Close the pending flag this way tomorrow.
