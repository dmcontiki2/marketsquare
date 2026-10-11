## 2026-10-11 — SUBSCRIPTIONS-AUDIT-1: the three apps say the same thing about the plans (PLANS-TRUTH-1, SLOT-FULL-QUICK-1, RUL-RENUMBER-1)

David, 11 Oct 2026: audit TrustSquare, Quick and Traders against the latest subscription rulings and make them consistent.
`scripts/check_pricing_canon.py` passes (code ↔ PRICING_CANON ↔ EULA agree); the drift was on the user-facing surfaces:
- **PLANS-TRUTH-1 (marketsquare.html):** the Pro plan card said "plus the AI research suite and Squire" while Squire is
  flag-dark (`_squire_on()` = `baseline_q4`, not armed) — a $20 buyer was promised an agent he cannot open. The static card
  now ends at the AI research suite; `/pricing/ladder` adds the Squire line the day baseline_q4 is armed (RUL-126), the
  same rule RG-0267 applies to BOTs: nothing dark on a price card.
- **Free carries the free Nationwide switch (RUL-220)** on all three plan surfaces: the static Free card, `/pricing/ladder`
  (its Free rung said "Local buyer reach (your city)", half-true since REACH-NATIONAL-1) and the subscription screen's
  `_SUB_TIERS` bullets.
- **SLOT-FULL-QUICK-1 (quick.html + genie/HARNESS.html, identical):** a signed-in member whose plan slots are full got
  `{live:false, status:402}` from `/listings/quick-publish` and Quick showed "Your listing is saved — open it in TrustSquare
  to finish" with no reason. It now says "Your plan's listing slots are full." and "Your advert is saved, not published. Choose
  a bigger plan, or rest one of your adverts to make room — nothing is deleted." with a **See plans** button to `/?plans=1`
  (KEEP-CHOICE-1, RUL-180); a raw 402 in `qSaveFail` says the same instead of "try again". Strings carry every Quick language
  (af/zu/xh/nso + the per-country lists). This is also the message the Traders fast lane's `slots_full` fallback lands on.
- **RUL-RENUMBER-1 (branch `fastlane`, private, IP hold):** the fast lane's rulings were RUL-220 (fast lane, CC-006) and RUL-221
  (option D) — the numbers main took today for REACH-NATIONAL-1 and the tier cascade. Renumbered on the branch to **RUL-222 /
  RUL-223** across 25 files (code comments, RULINGS.md, CHANGE_REGISTER, ledger, stories, i18n scripts); QUICK_FASTLANE_BRIEF.md
  carries the note. Nothing on main changed its number.
- **Squire-2 Phase 1 was never committed:** the 10 Oct build run left its work uncommitted in `_squire2_wt` because the
  worktree's `.git` pointer named a dead session path. Pointer repaired (relative), 13 engine tests re-run green, committed on
  branch `squire2` (ebe3398). Still private under the IP hold; nothing pushed, nothing deployed.
- Ledger **RG-0958** (LOCKED) asserts all of the above and that HARNESS stays identical to quick.html.

Not changed, put to David: the one-$5-tier fold (RUL-128) and Squire are built and wait on him arming `baseline_q4` (RUL-126
batch); the Traders lane and Squire-2 wait on the CIPC filing receipt (provisional-2 submitted 10 Oct, not filed).
Cost model impact: none. Schema: none.
