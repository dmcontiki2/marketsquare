## 2026-08-11 — CV-GUARD-1: the seller CV crashed on an empty roster or an off-city card (maintenance loop, second run)

- **Where it came from:** the daily maintenance loop, chasing the two console tails that
  testers' fault reports carried with them — `undefined is not an object (evaluating
  'l.trust')` (TS-0006, Safari/iPhone) and `Cannot read properties of undefined (reading
  'headline')` (TS-0021, Chrome/Windows). Chasing a console tail rather than only the
  sentence a tester typed is how this one surfaced at all.
- **The fault:** `openSellerCV` dereferenced two things it had not proved existed.
  `SELLERS` can be empty on a cold or live-only load, and `findListing()` misses whenever
  the card is not in the ACTIVE city — `LISTINGS` only ever holds one city at a time.
  Either absence blanked the seller CV screen with an uncaught throw.
- **What makes it worth writing down:** the function had **already** guarded `l` one line
  earlier — `const cvScore = s.trustScore!=null ? s.trustScore : (l ? l.trust : 0)` — and
  then dereferenced `l.trust` raw twice in the markup below it. The author knew the listing
  could be missing and guarded only the arithmetic, not the render. `renderProfilePreview`
  carried the identical `const s = SELLERS[0]` deref plus an unguarded `CATS[s.cat].icon`,
  sitting a few lines above an existing fix comment that had already paid for exactly this
  lesson ("SELLERS[0] threw and the button died silently").
- **Why RG-0031 did not already cover it:** RG-0031 scoped itself to "the whole openDetail
  call graph". `openSellerCV` is a **sibling entry point**, not in that graph. Same class,
  different door — the recurring shape CLAUDE.md rule 3 warns about.
- **The fix (`ms.js`, +13 lines):** `openSellerCV` falls back to an empty seller skeleton
  when the roster is empty, renders trust from the already-guarded `cvScore`, and only calls
  `fspark(l)` when there is an `l`. `renderProfilePreview` renders a "profile not set up yet"
  prompt instead of throwing, and tolerates an unknown category.
- **Evidence (AIK-VERIFY-1):** `scripts/repro_cv_guard.js` — a new, permanent harness that
  extracts the two functions from any `ms.js` you point it at and runs them against an empty
  roster and a missing listing. Against the pre-fix backup: **3/3 CRASH, exit 1**. Against
  the fixed file: **3/3 pass, exit 0**. The failing action, reproduced clean.
- **Ledger RG-0054 LOCKED** — asserts both functions keep their guards and that the repro
  tool stays with the fix. 54 entries, 51 holding, 0 regressed.
- **Deliberately NOT claimed:** that this is the source of the TS-0006 / TS-0021 tails.
  `s.trustScore` is read *before* `s.headline`, so an undefined seller in `openSellerCV`
  would report `trustScore`, not `headline` — TS-0021's tail comes from somewhere still
  unidentified (`formatDescJSON` was checked and cleared: its only caller wraps it in
  try/catch). The crash class fixed here stands on its own evidence; the fault attribution
  does not, so neither fault was advanced on the strength of it.
- **TS-0001 closed out properly:** "the 15 matching list button doesnt work" was fixed on
  5 Aug but the row was never updated, so it had been sitting in `new` for six days.
  Verified this session by live probe of the DEPLOYED asset — `GET /static/ms.js` (HTTP 200,
  1,056,818 bytes) contains `upBox.onclick = function () { goTo('wishlist'); }` — and moved
  to `verified`.
- Committed, not deployed. NIGHTLY-SHIP-1 carries it through the gates.
