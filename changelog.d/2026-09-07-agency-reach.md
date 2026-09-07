## 2026-09-07 — AGENCY-REACH-1: verified agencies get multi-city reach, and the tier now follows verification (RUL-109, RG-0336)

David: *"Agencies should get national reach, do you see an issue if this is true?"* — then, shown that the
code has no notion of a national boundary, *"let sellers reach abroad"*.

**The grant was the easy half.** `agency` joins Starter and Pro in `_PAID_TIERS`, and no country boundary
is enforced for anyone: a qualifying seller may extend a listing to any active city, including across a
border. The old comment claimed "any city in their country" while the code never compared countries — the
claim was what was wrong, not the behaviour, and the claim is now corrected to match the ruling.

**The finding that mattered more: it would have landed on an empty set.** AGENCY-TIER-1 (3 Aug) declared
that a member of a verified agency carries the `agency` tier, but only ever stamped it inside
`invite_agent` — so it held only for agents invited *after* verification. Probed on the live database:
**8 agencies, all verified, 25 members between them, not one on the `agency` tier** (8 free, 17 starter).
A declared benefit with zero holders for five weeks, and no instrument said so, because nothing asserted
the relationship between the flag and the tier. Both halves were individually fine.

**The tier is now a derived property with one writer.** `_sync_agency_member_tiers()` is called from the
invite path and from a new ops-gated `POST /agencies/{id}/verify`, which moves verification in **both**
directions — previously `verified` could only be set at INSERT, so it was one-way and invisible. A member
who bought their own seat (RUL-048 `seat_paid`) or holds a live subscription is never touched, so the
writer cannot overwrite a tier somebody paid for.

**Proven before shipping, not after.** The writer was exercised on a throwaway replica (free and starter
lift to agency; un-verify returns them; a paying member and one with live billing are untouched; second run
moves 0). `migrations/036_agency_tier_resync.py` was dry-run **and applied against a copy of the real live
database**: 25 moved, re-run moved 0.

Safe to grant free because agency status is never self-served — every agency route is ops-key gated.

**Honest consequence, recorded not buried:** a seller can now appear "local" in a city on another continent
on their own say-so. The self-declaration is the only guard, which is thin for physical goods —
BACKLOG REACH-SHIP-1 (a "ships nationwide" toggle) is the honest fix and is David's to schedule.

Also corrected the same day: RUL-107's own reflection assertion pinned the literal
`_PAID_TIERS = {"starter", "pro"}`, which this ruling legitimately widened hours later, so a true
reflection read FAIL. Re-expressed as the property (no retired names present, canon `pro` present).
