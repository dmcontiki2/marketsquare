## 2026-09-26 — David's four answers carried: one word 'listing', a real banking form with its true purpose, the pictures kept, Terms v1.19 drafted (INSPECT-FIX-5)

David, 26 Sep 2026, answering the four questions the closure board left him: *"Listing"*; *"we do need the users
banking details, we use it both as security to know our customer and also for them to purchase tuppence's. Dont remove
that. We just dont use it to pay them any money out"*; *"Keep for later"* (the nine Quick pictures no screen shows);
*"Yes, draft 1.19"*.

- **LISTING-WORD-1 (langt-21)** — one word for what a seller makes. Both apps and every message the server sends her
  say 'listing' (Quick: 65 English lines and 37 dictionary keys; the app and server: 124 lines; each translation
  re-keyed, isiXhosa 'Nantsi isibhengezo sakho'). RUL-040 AMENDED the same day: the AI example badge reads
  **AI EXAMPLE GENERATED LISTING**. Kept on purpose: the feature name 'Collectables Advert + Market Report' (RG-0493's
  key), AI prompts, code names, and the Terms (they change only by a new version). RG-0140, RG-0106, RG-0166,
  RG-0135, RG-0446, RG-0395 and the RUL-040 / RUL-026 reflections follow the new words.
- **BANKING-FORM-1 (langt-06, ts2-17)** — the server route existed and the form never did. The Billing tab now has a
  Banking details card, the nudges after publishing open the same form (holder, bank, account number, optional branch
  code), it sends only to her own signed-in account, and the card then reads 'On file · FNB · account ending 6789'.
  Every line says what the details are for — confirming who she is and when she buys Tuppence — and that nothing is
  ever paid out (Terms 5.2: Tuppence is never cash). The server keeps the last 4 digits only. Translated into
  Afrikaans, isiZulu, isiXhosa and Sepedi (migration 058; ms.js DICTV 6).
- **CARD-WORDS-2 (langt-04 leftovers)** — the free plan's line in the plan list and on the Billing tab says
  'Free forever · no card needed'.
- **R2-FALLBACK-EARLY-1** — found in the banking walk: a picture that failed before ms.js loaded threw
  'r2Fallback is not defined' and stayed broken. The page defines the same fallback first.
- **SUPPORT-HOLD-96** — found while drafting the Terms: the support assistant told buyers the hold is released if the
  seller does not answer within 48 hours; the app releases it when the request closes at 96 hours (the −5 lands at 48).
- **Pictures (quick-20)** — kept on David's decision; nothing changes today.
- **Terms v1.19 DRAFT** — `eula_clean_v1.19_DRAFT.html`, not wired and not published (eula_clean.html, terms.html and
  the app's copy are untouched; eula_sync.py not run). 88 corrections, so the Terms say what the app does: 35 from the
  inspection (drafting notes, code names, the blurred photo, the acceptance steps, Schedules A–G, one server fact) and
  53 more (the hold-and-burn model in 5.1 and 6.3, the 96-hour close, live Paystack top-ups, the free ID check before
  any introduction, AI prices Free / 1T / 2T / 3T / 5T, Cars, the ECT Act section 13, cross-references and list
  numbers, the privacy contact, no expiry of bought Tuppence). Eleven points wait for David — each with a
  recommendation on `Visuals/MarketSquare/TERMS_v1.19_REVIEW.html`.

Ledger: RG-0503 (the banking form and its purpose), RG-0504 (one word on every screen and server message, allowlist
explicit) and RG-0505 (the early r2Fallback) — each red on the deployed tree and on a deliberate break, green on the
real files. Full sharded run against the deployed tree: identical board except the three new entries and RG-0140,
whose live half reads the old badge until this deploy.
