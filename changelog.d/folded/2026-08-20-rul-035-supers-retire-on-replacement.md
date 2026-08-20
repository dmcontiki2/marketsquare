## 2026-08-20 — RUL-035: the supers stay through launch, and retire one by one as real listings replace them

David, on being shown the fade: *"i think they are needed for the launch and a while thereafter.
We will remove them as they get good live replacements."* Recorded as **RUL-035** — a ruling, not
a note, so the next session cannot re-decide it.

What it fixes in the machinery:

- **No sunset date, no bulk removal.** Nothing automatic may ever remove a super — not the fade
  sweep, not the archive step, not expiry. That is now true of `super_example`, not just
  `showcase` (SUPER-IMMORTAL-2, same session).
- **Retirement is a deliberate admin act, per shelf**, taken only once that category carries a
  real seller listing good enough to be the measuring stick in its place.
- **A shelf may never go dark as a side effect.** RG-0123 now encodes exactly that asymmetry: a
  super that 404s is read as a RETIREMENT and passes; a super the machinery *hid* is a
  regression; and an empty category shelf in Pretoria is a regression either way. So the ledger
  will let David retire the Collectors super the day a real collector listing stands up, and
  will go red the day one disappears without a replacement.
- rulings_check now asserts RUL-035 across bea_main.py, migration 027, the ledger and RULINGS.md
  — and asserts the PROPERTY (`super_example` is in the protected set), never a literal SQL
  spelling, which is the mistake that let RG-0106 sit green through the fault it existed to catch.

Ledger after this session: 116 entries, 0 regressed, RG-0123 open by design until the deploy runs
027 and the eight supers come back.
