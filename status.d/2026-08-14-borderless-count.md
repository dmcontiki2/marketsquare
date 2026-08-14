- **Tester queue cleared to zero new (14 Aug, evening).** TS-0032 + TS-0033 were one fault:
  the Adventures tile counted city-scoped listings while the Adventures page is borderless by
  design, so the number never survived the tap. Fixed at class level (**BORDERLESS-COUNT-1**,
  RG-0078) with `scripts/repro_borderless_count.js` as named evidence — it reproduces the
  testers' exact numbers (Sydney 2→6, Maun 1→6) against the pre-fix file and passes against the
  fixed one. Both rows set **fixed**, not verified: the fix is in source and gated, and reaches
  the reporters on the next nightly deploy. TS-0031 (cars AI vehicle details) is **triaged**:
  its honest half shipped (**SPEC-PROVENANCE-1**, RG-0079 — the attestation screen now says the
  specs were read from photos, not looked up), while whether to ground the lane in real vehicle
  data is David's call and sits in BACKLOG.md with three options. RG-0065, RG-0066 and RG-0069
  promoted OPEN → LOCKED, as each entry instructed, now that they pass.
- **Not mine, flagged:** the ledger's last run went red on **RG-0019** (live AI lane is
  `anthropic`, `ai_price_card.json` records `openai`). That file was edited at 21:59 by a
  concurrent session — my 21:56 run was green — so it is in-flight work on the model register,
  not a fault in this session's changes. Left untouched deliberately rather than raced; the
  register needs the switch reason recorded by whoever made the switch.
