## 2026-08-08 — STAYS-SHOWCASE-1 fix: migration 009 died on a NOT NULL column

First live `--apply` of `migrations/009_stays_showcase_adverts.py` failed on the first INSERT:

    sqlite3.IntegrityError: NOT NULL constraint failed: listings.rental_status

My bug, and a self-inflicted one. The CLONE_JUNK guard — added precisely so the trio would be
born clean after migration 002 had to heal six rows of inherited junk — blanked every foreign-
category column to None. `listings.rental_status` is declared NOT NULL, so blanking it is an
invalid write rather than a clean one. The guard was right in intent and too blunt in execution.

FIX: ask the live schema which columns tolerate NULL (`PRAGMA table_info(listings)`) and blank
only those. A NOT NULL column keeps the template row's own value, which is by definition legal
for that column. Self-adjusting — a future NOT NULL column needs no further edit here. The script
now prints the columns it is protecting, so the exception is never silent again.

No damage: the DB was snapshotted before the attempt
(`marketsquare.db.bak-20260808-035727-staysshowcase`) and the failure came before the commit, so
the transaction rolled back whole. Verified from outside afterwards: `/listings` unchanged at 47
rows, max id 335, zero partial rows. The dry-run passed cleanly beforehand — worth noting that a
dry-run cannot catch this class, because it never attempts the write.

Rehearsed the patch against a local SQLite reproducing the exact shape (a NOT NULL
`rental_status` on a cloned template): insert succeeds, clone junk still scrubbed to NULL,
`rental_status` retained, `super_example=0` and `price_num` correct.

Also corrected from 7 Aug: the three cards this trio replaces in
`adventures_accommodation_outreach.html` were described as depicting "listings that do not
exist". Too strong. They depicted `demo_stay_1`, `demo_stay_5` and `demo_stay_9` — real rows in
the demo fixtures (Waterberg Private Lodge, the Cape Town boutique hotel, Sossusvlei). What was
true, and what justified the swap, is that those ids are not deep-linkable `?listing=` targets
and the card photos were hotlinked from images.unsplash.com.

Still untested: whether migration 007 also halts the chain before 009 is reached. 009's own bug
is sufficient to explain the missing adverts, so the 007 theory is unproven — `.migrations_done`
plus the deploy log settle it, and both need only SSH, which is working again as of this morning.
