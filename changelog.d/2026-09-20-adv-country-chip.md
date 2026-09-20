## 2026-09-20 — ADV-CO-CHIP-1: the Adventures country chip lied, so the currency fix looked lost

David, 20 Sep: *"the trustsquare app are still showing the adventures examples with South African
Prices. We did fix this, how did it reappear again?"*

**It had not reappeared — a different fault wore its face.** Probed in the RENDERED app, not the API:
ZA renders R3,200, Australia A$540, the UK £350, the US $420, and every live Adventures row carries a
correct `country`. RG-0002..RG-0006 hold. The currency model is intact.

**What David was actually looking at.** The country chip in the Adventures header is the only country
statement a buyer reads, and it was a hardcoded `🇿🇦 South Africa` literal in `marketsquare.html`
(Session 22, **19 Apr 2026** — never touched since). BORDERLESS-COUNT-1 (14 Aug) fixed the *state*
— `advCountry = 'ALL'` — and never touched the *markup it renders into*. So on a cold load the header
said South Africa while the grid was unfiltered, and the ZA exemplars that sort first under it read as
rands everywhere. **A fix and the thing the user reads were never connected.**

**Two further paths re-pinned it, both silent:**

- `ms.js` city sync (3698) overwrote `advCountry` with the selected city's country — picking Pretoria
  re-selected South Africa, defeating the borderless default without a tap on the picker.
- `selectAdvCountry` persists to `localStorage.ms_adv_country` (COUNTRY-FILTER-1) and `advResetAll`
  — "one-tap escape from any filter combination" — did **not** clear it. One accidental pick held that
  browser on one country permanently, with no control on the screen able to take it back.

**The fix (the class, not the instance).**

- The chip is now PAINTED FROM THE STATE on every load (`advPaintCountryChip`), so markup can no
  longer disagree with what is filtered; the literal in the HTML is `🌍 All countries` to match.
- The city sync no longer touches `advCountry` — a buyer planning a trip is not local to the
  destination (the BORDERLESS-COUNT-1 reasoning, now enforced where it was being contradicted).
- `advResetAll` releases the country pin and removes its saved copy.

**Why nothing caught it.** Every currency entry in the ledger asserts a *symbol*. None asserted what
the picker *defaults to*, so the one control that decides which market a buyer sees had no guard at
all. New entry added so this cannot rot back a third time.
