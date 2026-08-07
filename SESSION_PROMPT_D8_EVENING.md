# Tonight: close D8 — the Stays/B&B trio + the 4-layer "planned trip" map

Context FIRST — read these before doing anything:
1. `MarketSquare/OPEN_LOOPS.md` loop **D8** — David's 5 Aug ruling: B&Bs are BOTH the missing email-showcase trio AND one of four map layers (ROUTE driving pins + HERITAGE sites + near-by B&B INTROS via Tuppence + Travelpayouts PARTNER referrals as pure link-out).
2. `MarketSquare/ADVENTURES_FULLMAP_CONCEPT.html` (also in Projects\Visuals) — the working concept David approved 5 Aug. Its colours, legend, popups and buttons are the design truth: blue route + dashed line, gold heritage, green B&B "Request introduction · 1T", purple partner "link-out, pending TP approval". Plus SELECTIVE LAYER SWITCHES (colour-dotted checkboxes, top-right) — each layer toggles independently; keep this in any real-map wiring.
3. `MarketSquare/JOURNEY_PHOTO_RUNBOOK.md` — Higgsfield photo-run rules already paid for: ONE generation at a time, never claim downloads by count, the Downloads folder grant is per-session.
4. `MarketSquare/DAILY_WATCH/OPEN_ITEMS.md` — 10 items open; do not reopen closed ones. Run `python3 scripts/regression_ledger.py` BEFORE starting and AFTER finishing.

Plan, in order:
**A. Photo session (David at the keyboard, Higgsfield):** 3 sets — (1) Thatch & Bushveld Safari Lodge B&B, Pilanesberg; (2) Jacaranda Boutique Guesthouse, Hartbeespoort; (3) Marula Bush Camp, Magaliesberg. Follow the runbook exactly.
**B. Adverts:** 3 born-clean showcase adverts, category `adventures_accommodation`, via the hardened clone-271 script + a `migrations/NNN_*.py` (NEVER hand-edit live data). Real specs, correct sort prices, super flag per the 28 Jul pattern (adverts 315-323).
**C. Email track:** build the Stays outreach cards + deep links (2 anchors per card) to match the other three tracks. NOTE: `adventures_accommodation_outreach.html` no longer exists on disk — find where the four flipped templates actually live now (D5a, 2 Aug changelog.d) and follow that pattern; do not recreate a dead filename.
**D. If time:** wire the 4 layers into ONE real adventures map (ZA pilot), reusing the concept page's layer/legend/popup code.

Rules that bite (all standing, all verified this week):
- Writes via bash python heredoc ONLY — Edit/Write truncate on this mount. Backup + verify (wc -l, tail, py_compile) every file.
- CHANGELOG/STATUS via `changelog.d/` and `status.d/` fragments only — never whole-file edits.
- NO third-party scripts on app pages (ledger RG-0025) — maps stay inlined-Leaflet + OSM; Travelpayouts is link-out only, marked pending until their tours review approves.
- MarketSquare is an INTRODUCTION service: B&B buttons fire intros at the fixed intro price — INTROS ARE ALWAYS 1T (David, 5 Aug; an earlier draft said 20T — that was wrong); no booking, no money through the till, no ad-valorem costs.
- Deploy ONLY via /tsl, only if David says ship tonight. Any fix gets a ledger entry in the same session.

Done bar: adverts verifiable on the live DB, ledger green, fragments written, D8 in OPEN_LOOPS closed or narrowed to exactly what remains.