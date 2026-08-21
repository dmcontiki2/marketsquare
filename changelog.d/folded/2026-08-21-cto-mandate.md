## 2026-08-21 — RUL-037: Claude is the CTO; technical decisions stop being lobbed at David

David, on the trailing "one thing I left for you" that had become a per-session habit:
*"this is a build in destruction mechanism, because i am currently managing the project on a
management level and using you as the details and technical expert... I depend on you to be the
CTO of this project and to make the technical decisions based on the specifications which sets
the rules and the requirements to reach our goals."*

- **RUL-037** recorded, reflected in `../CLAUDE.md`, `STANDING_ORDERS.md` SO-4 and
  `scripts/rulings_check.py` (37 rulings, 0 FAIL).
- The specs are the delegated authority. Where RULINGS/STANDING_ORDERS/canon/ledger answer a
  question, Claude answers and executes; David is not the tie-breaker for anything written down.
- **Banned:** trailing "left for you", "say the word and I'll…", option menus on technical matters.
- **The replacement mechanism:** a technical item Claude cannot execute this session becomes an
  **OPEN regression-ledger entry**, not a sentence to David. The ledger already prints READY TO
  LOCK when it clears — it is the correct home for a pending technical step.
- **Reserved to David** (batched, stated as business trade-offs): money, deploys, deletions,
  sending on his behalf, lockout risk (RUL-027), legal/commercial positioning, launch scope and
  dates, money- or jurisdiction-bearing vendor selection (RUL-009 unchanged), and changing a ruling
  rather than executing one.
- Applied immediately in the same session: the `_apv3PendingFlip` banner and the golden-gate
  contradiction — both previously handed to David as "your call" — were decided and executed
  against `AI_LANE_GUIDANCE.md` and `ai_scoreboard.GOLDEN_PASS`. See the AIPROV-VERIFY-1 fragment.
