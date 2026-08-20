## 2026-08-20 — Supers faded by the 19 Aug release restart; class fix in source, awaiting deploy

- **Cause proven, not guessed:** listings 265-272 read `listing_status=faded`,
  `status_changed_at=2026-08-19T18:21Z` on live — the sweep that runs 2 minutes after every
  boot, triggered by the 20:17 release. Seeded 20 Jul, so they had just crossed the 30-day
  free-tier fade window.
- **Why the RUL-026 exemption missed:** it keys on `showcase = 1`; the supers carry
  `super_example = 1` with `showcase` NULL, and `showcase IS NULL` INCLUDED them as candidates.
- **Fixed in source (SUPER-IMMORTAL-2):** sweep candidates + archive step + both delete guards
  now exempt `super_example`; `migrations/027_super_immortal.py` revives the eight and
  self-verifies. RG-0123 OPEN; RG-0106's literal-SQL assertion corrected to a property.
- **NEEDS DAVID: one deploy.** Nothing brings the shelves back without it — the supers stay
  hidden until 027 runs. The grace clock matters: faded -> archived is 14 days from 19 Aug,
  i.e. **~2 Sep**, the day after the 1 Sep full launch (RUL-001).
- Ledger after this session: 1 REGRESSED cleared (funnel snapshot regenerated), RG-0123 open
  by design until the deploy.
