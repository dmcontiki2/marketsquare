### 2026-09-15 — Three guards that were red, and one that could not see

The daily maintenance loop ran with an empty fault queue, so the work was the board itself.

**The Postgres-readiness ratchet had been red for nine days running.** The Buzz and Comms work
of 14 Sep added eight new SQLite-only date expressions to `bea_main.py`. They are now written
through one named helper and bound as parameters, so the later Postgres move stays as cheap as
David's ruling requires. The baseline was NOT raised — it is byte-unchanged at 17.

**Three deployed pages had no way to report a fault** — including the new Quick door that was
just put on the front page. Fixed with the one-line widget every other tester page carries.

**The pre-deploy scan was blind and said so as "clean".** It reported an empty working tree
against five modified files because its git call hung on the FUSE mount and the failure was
swallowed as no-output. That also meant its torn-file check — the one thing that aborts the
strict nightly ship — had been silently dead. It now sees the tree, and when it cannot see, it
says so instead of printing a reassuring zero.

Three new ledger entries (RG-0376/0377/0378), each sabotage-proven to actually bite. Board is
green: 365 entries, 0 regressed, 0 unverified. Nothing was deployed — the nightly ships it.
