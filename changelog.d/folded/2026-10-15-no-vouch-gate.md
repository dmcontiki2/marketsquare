## 2026-10-15 — NO-VOUCH-GATE-1: casual workers visible on publish (RUL-233)
- bea_main.py: CASUAL_VOUCH_GATE = False — the stranger gate no longer hides an unvouched casual advert; a vouch or
  ID check still earns its Trust Score points. Clearance (RUL-153) and licence (RUL-156) branches unchanged.
- Trigger: listing 554 (seamstress, Sunnyside, live 15 Oct 09:33 via SMS) was missing from Browse. RG-0986 locks it.
