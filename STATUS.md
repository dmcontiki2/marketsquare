# MarketSquare — Live Status

## Live State
Session 62 complete. Demo mode (?demo=1) fully audited and clean across all 4 cities × 7 categories (290 listings, 0 issues). All seller profiles correctly wired. Trust scores in range. Process rules now AI-enforced in CLAUDE.md and AGENT_BRIEFING.md.

## Last Completed (Session 62 — continued·6)
- **Full 290-listing audit**: all 4 cities × 7 categories systematically verified — 0 issues after fixes
- **70 Pretoria sellerIdx fields added**: all Pretoria listings were missing sellerIdx, showing wrong seller profiles
- **30 trust scores fixed**: Pretoria Collectors/Cars/LM had scores 44–64, all corrected to 72–94
- **Process rules added**: CLAUDE.md Rule + AGENT_BRIEFING.md Rules 8–9 now AI-enforce demo-mode wiring and data integrity audit every session — no human memory dependency
- **Adventures city sync, World Heritage country sync, LM titles, SELLERS, demo badges, POI disclaimer** (continued·5)

## Architecture note (important)
The SELLERS array and sellerIdx are demo-only constructs. Live BEA listings use openBEASellerProfile() which fetches seller data from the database — the SELLERS array is never used for live listings. Demo misalignment cannot occur in production.

## Next Session
- Remove all `TODO:REMOVE BEFORE LAUNCH` blocks when going live
- Paystack live mode (pending CIPC registration)
- n8n email notification flows

## Blockers
None.
