## 2026-10-03 — RUL-196 HOME-EX-SWITCH-1: the AI-examples switch also sits on Home, and every Home count follows it

David opened Home (Afrikaans) and read Eiendom 16, Onderrig 2 and 0 everywhere else: "i had the adverts switched off, but that
switch only shows on the Browse page and not the Home page". The tiles were obeying the switch (RUL-194), but Home gave no sign
the examples were hidden, so the numbers read as wrong. Measured in his Chrome: `ts_show_examples` = '0'; switched on, the tiles
read Property 20, Tutors 3, Services 2, Adventures 9, Collectors 1, Cars 4, Local Market 2 -- the live DB's counts.

- **Home switch:** the same "AI examples on/off" pill now sits beside the Categories heading (`msExPaintHome`, painted by
  `renderCatCounts`), by the Browse rule: shown whenever examples are in view, always while it is off.
- **Local Market tile:** it counted the hidden example (Pretoria read 2; #273 is real, #272 an example). `initLMHomeTile` and the
  demo-mode count now follow the switch, and flipping the switch refreshes the tile.
- **Fallback count:** a city holding only examples fell through to `renderCatCounts`' fallback branch, which counted them while
  hidden -- it now skips them too.
- **Afrikaans:** the switch read "AI-voorbeelde af" beside "KI-voorbeelde aan"; checked words "KI-voorbeelde aan/af" (and the two
  toasts) in `roles/app_i18n_af.json`, applied by migration 064, browsers refreshed by DICTV 8.
- Ledger RG-0803 (OPEN until proven on the rendered live page); rulings_check RUL-196.

Cost model impact: none. Schema: none.
