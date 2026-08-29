## 2026-08-29 — Auction plan review delivered (RUL-067 follow-through)

**Deliverable:** `MarketSquare/Auction Module Review — nice.docx` (Professional Navy). Full review
of the mothballed Auctions & Offers plan against RUL-067 and today's canon. Verdict: remap, not
rethink. Key findings: the hold-to-bid ledger primitive (tuppence_held + conditional release)
already runs in production via intros; four stale items (scp deploy lane → ONE_DEPLOY, 5-tier refs
→ Starter/Pro, Jun-2026 AI prices → lane machinery, week-plan bravado → gated cadence); one real
tension (live-theatre liquidity — solved by sequencing offer-mode/async first); legal is the
longest pole (EULA section, CPA ratification, patent supplement — start Q4 2026). Proposed
sequence: Q4 make-an-offer → Q1 async auctions → Q2 live theatre + Pro gate → Q3 Regal + sim
variable. Seven amber decisions remain David's; only offer semantics blocks the first ship.
