### RULINGS.md born — decisions get the same machinery as fixes

The launch date was reviewed several times in sessions and never reached the canon; the sweep
read "launch date STILL NEEDED" as truth. Class-level fix, sibling of the regression ledger:

- **RULINGS.md** — append-only register, seeded with 12 rulings incl. RUL-001 (launch
  1 Sep / soft-public 29 Aug, fixed sequence).
- **scripts/rulings_check.py** — asserts each ruling is REFLECTED where the next session
  reads, and that repudiated wording is actually purged. First run found 3 genuine drifts
  (BACKLOG still carried the repudiated 23/60 threshold after 2 months, and the provisional
  01-Aug deadline) — all fixed same session. 12/12 reflected, exit 0.
- Standing rule appended to Projects/CLAUDE.md: a ruling is not made until it is in the
  register, same session. rulings_check runs alongside the regression ledger.
