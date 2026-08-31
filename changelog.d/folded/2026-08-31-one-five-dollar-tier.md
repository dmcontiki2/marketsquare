## 2026-08-31 — RUL-080: there is only one $5 tier (principle ruled); and the 30 Aug discussion did not touch $5

David asked, at the end of the Zoom/Squire session: "There should not be two $5 tiers, only one. If i
misled or mis-spoke then it should revert to one tier... And todays whole discussion should not have
effected the $5 tier?"

**He did not mis-speak, and the session changed nothing about $5.** PROBED: both $5 entries have sat
in PRICING_CANON.md since **16 Jun 2026, in the same commit (1a2d254)** — *Starter* $5 (10 seller
slots, §1) and *Global* $5 (buyer reach, §2). A **third** $5 exists as well: the **Agency Pro seat**
(RUL-048, 23 Aug) at $5/month for 20 slots + the Pro AI suite. RUL-078 added Global reach to **Pro
($20)** and takes nothing from either $5 product. No code, price or entitlement on $5 was altered.

**A defect of my own, corrected in place.** The note that first recorded the collision said "there are
NOW two distinct $5 products". That "now" wrongly implied same-day origin — a misdated status
assertion is the same defect class as an undated one (the ONETAP_SETUP lesson). PRICING_CANON §2c now
carries the 16 Jun provenance explicitly.

**The ruling:** there must be ONE $5 tier, carrying the functions and features already assigned to it.

**Mechanism NOT executed this session (CTO, RUL-037):** the three $5 products are genuinely different
bundles across two axes, `wishlist_subscriptions` is a LIVE table carrying Paystack refs, and full
launch is tomorrow (Mon 1 Sep, RUL-001). A billing-structure migration on launch eve is exactly the
class of change that must not be improvised — and the ruling is a PRINCIPLE, which needs no migration
to be true. Recommendation for the post-launch pricing pass, vetoable: fold Global buyer reach INTO
Starter — Free (local, 2 slots) · Starter $5 (10 slots + global reach) · Pro $20 (30 slots + reach +
Squire) — retiring the separate buyer subscription and re-expressing the Agency seat against Starter.
Same logic as RUL-078, one rung down. Consequence to weigh, and why the call is David's: a pure buyer
who never sells would then buy a seller plan to get reach.

**Concurrent-session note (this is the CHANGELOG-COLLISION-1 class, caught not suffered).** This work
was written 31 Aug ~09:15 SAST for a discussion held late on 30 Aug. Another session had meanwhile
claimed **RUL-079** (agency outreach at week 0) and **RG-0225/0226/0227**. Two collisions were caught
before landing: the ledger's own LEDGER-DUP-1 guard refused a duplicate RG-0222 at import (moved to
RG-0224), and a fresh re-read of RULINGS.md caught RUL-079 already taken (moved to RUL-080).
Append-only discipline held throughout — nothing was renumbered, overwritten or lost. The lesson
stands as canon already states it: re-read before writing, never assume the last number you saw is
still the last number.

Files: PRICING_CANON.md §2c · RULINGS.md RUL-080 · scripts/rulings_check.py RUL-080 ·
OPEN_LOOPS.md [D] pricing row. Rulings check: 80 checked, 0 FAIL. Ledger: 220 entries, 0 duplicates.
