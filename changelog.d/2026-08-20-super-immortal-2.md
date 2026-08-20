## 2026-08-20 — SUPER-IMMORTAL-2: the supers faded overnight because the exemption watched the wrong flag

David, first thing: *"Claude we lost a lot of adverts? Why"* — the Collectors and Services tiles
read **0 listings**. He was right, and he was right again when he asked whether it was the
fade-out design. It was.

**What happened.** The 19 Aug 20:17 release restarted the service. `_lifecycle_daily_loop` fires
its first sweep **two minutes after boot** — so a deploy is a sweep trigger — and at **18:21Z**
it flipped all eight ZA supers to `faded`: 265 Cars, 266 Tutors, 267/268 Services, 269
Collectors, 270/271 Adventures, 272 Local Market. All were seeded 20 Jul, which had just crossed
the free-tier 30-day window. Collectors, Services and Local Market fell to zero because the super
**was** the whole shelf; Property/Cars/Tutors/Adventures survived only because their supers were
re-seeded 25 Jul–17 Aug and have not aged in yet.

**Why RUL-026 did not save them.** SHOWCASE-IMMORTAL-1 (18 Aug) exempted `showcase = 1`. Every
seeded super carries `super_example = 1` with **`showcase` NULL** — and the candidate query said
`AND (l.showcase = 0 OR l.showcase IS NULL)`, so the exemption did not merely miss them, it
*positively selected* them. Migration 024 heals on the same wrong key, so it would not have
brought them back either. The guard, the heal and the ledger entry all agreed with each other
and were wrong together.

**Class fix (source, rides the next deploy).**

- `_lifecycle_sweep`: candidate query **and** archive step now exempt
  `COALESCE(super_example,0) != 1` as well as `COALESCE(showcase,0) != 1`.
- Both delete guards (`DELETE /listings/{id}` and the seller-email path) now treat
  `super_example` as admin-managed too — the showcase-only guard had left every seeded super
  deletable with the app key that ships publicly in `ms.js`.
- `migrations/027_super_immortal.py` revives any faded/archived super or showcase listing,
  clears stale fade stamps, and **verifies zero left hidden** before returning 0.

**Ledger.** RG-0123 added (OPEN — its live half names all eight faded ids and every dark shelf;
flips READY TO LOCK the moment 027 lands). RG-0106's assertion **corrected, not weakened**: it
pinned two literal SQL strings, which is why it sat green through a fault it was written to
catch, then went red when the SQL was strengthened. It now asserts the property.

Also cleared while here: the funnel snapshot regression (card `2026-08-19.1` vs snapshot
`2026-08-01.1`) — regenerated, so the deploy gate is not held by an unrelated red.

**Standing lesson.** A restart is a sweep trigger. Any lifecycle guard has to be correct in
SOURCE before a deploy, because the deploy itself is what runs the machinery.
