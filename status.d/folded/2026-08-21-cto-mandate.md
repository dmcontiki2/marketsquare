- **RUL-037 (21 Aug) — Claude is the CTO.** Technical decisions are made against the specs and
  executed, not handed back to David. Trailing "left for you" / option menus on technical matters
  are banned; an unexecutable technical item becomes an OPEN ledger entry instead. Reflected in
  CLAUDE.md, STANDING_ORDERS SO-4, rulings_check (37 rulings, 0 FAIL).
- **AIPROV-VERIFY-1 + GOLDEN-AUTHORITY-1 (21 Aug):** the +1 page's AI Providers card was asserting
  three unverified states — green dot on config alone, a hardcoded "flip pending" banner a week
  after the flip, and `openai (golden-set-passed)` on all four tiers when the production golden run
  was never done. All three now derive from facts. Ledger RG-0130/RG-0131 LOCKED, **RG-0132 OPEN**
  (run `scripts/golden_seam_v2.py` on the Hetzner box with the production key, then add openai to
  GOLDEN_PASS). Repo-side only — rides the next deploy.
