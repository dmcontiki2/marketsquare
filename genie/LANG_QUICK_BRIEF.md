# LANG_QUICK_BRIEF — language layer + Quick Listing audit fixes

Source: David's airport session on his phone, 23 Sep 2026 (review board "Languages + Quick audit",
claude.ai artifact BYDm6Dpzqx5PZXu8TA6QWa; copy in genie/LANGUAGES_QUICK_AUDIT_BOARD.html).
The original brief file from that chat never reached disk; this is rebuilt from the board on
23 Sep 2026 evening. Ruling: RUL-162.

## 1 — The language design (two layers)
1. The APP speaks the user's language: buttons, menus, emails — English or any language David
   approved for that country.
2. The ADVERT speaks the lister's language: published as written, plus ONE extra language the
   lister picks and approves.
3. Codes, never flags (ZU, EN, AF...). A flag names a country; SA has twelve official languages.
4. A small language-identifying icon/chip in the app.

### How an advert gets its second language
1. She writes in her own language; the Quick door picks it from her phone; the advert stores it
   as its ORIGINAL language.
2. She picks one extra language, only from the approved list for her country.
3. The app drafts it and shows her a back-translation into her own language, so she approves
   what it really says.
4. The original publishes at once; the extra language waits for her tap.
5. Every advert carries an English search layer, so an isiZulu-only advert is found by an
   English search.
6. The buyer sees his language if an approved version exists; otherwise the original, with the
   code chip saying which language it is.
- Loop: if she edits the original, the extra language drops back to draft and asks again.

## 2 — Approved languages per country (David, 23 Sep 2026; up to four beside English, RUL-149)
Ranked by home language. "Needs a human reader first" = stays unoffered until a human signs off.
- South Africa (census 2022): English · isiZulu · isiXhosa · Afrikaans · Sepedi (replaces Sesotho)
- Namibia (2011): English · Oshiwambo · Khoekhoegowab · Afrikaans · Otjiherero
- Botswana (2011): English · Setswana · Ikalanga
- Mozambique (2017): Portugues (leads) · English · Emakhuwa · Xichangana · Cisena
- Kenya (2019): English · Kiswahili · Gikuyu · Luhya · Kalenjin (census counts ethnic groups — proxy)
- Germany: Deutsch (leads) · English · Turkce · Russkiy · Arabic
- United Kingdom (2021): English · Cymraeg · Polski · Romana · Punjabi
- United States: English · Espanol · Chinese · Tagalog · Tieng Viet
- Australia (2021): English · Mandarin · Arabic · Tieng Viet · Cantonese
Weaker machine-translation languages (the dashed chips on the board) are drafted but NOT offered
until a human reader signs them off (RUL-160 reviewer persona + human sign-off).
Sepedi strings for Quick are drafted for the human readers.

## 3 — Quick Listing audit (walked live at phone size, 23 Sep; ms.js v723)
Breaks the flow (from David's 15 Sep test):
- Q1 Quick is a one-way door — hand-over must land her signed in, on her draft, inside the app.
- Q2 The app re-asks what Quick already knows — every Quick answer travels with the draft.
- Q3 Two scores for one advert (Quick 60, app 80) — both call the one server scorer.
- Q4 Published but invisible until refresh — listing list reloads the moment Publish succeeds.
Friction (seen 23 Sep):
- Q5 "Every day" shows as "Any day".
- Q6 The language pill covers the bottom tile row ("Creche assistant").
- Q7 "Where can you work?" area tiles show house interiors — use plain area chips on a small map.
- Q8 Days screen floats apart — Next button far from the day buttons.
- Q9 "Demo: new here" test toggle is visible to real users — hide it.
- Q10 RS / TS / LS mean nothing to her — plain words for each score + one thing that raises it.
Polish:
- Q11 Lift the first-screen carousel; photo leads, buttons nearer the thumb.
- Q12 Make the language pill obvious — most SA phones are set to English even for isiZulu speakers.
Keep: photo tiles, the trail of chosen thumbnails, "6 taps to get here", door language pre-ticked.

## 4 — How the build runs
- Quick fixes go into BOTH genie/HARNESS.html and quick.html, which must stay identical.
- Only approved languages switch on; the rest wait as drafts.
- The language layer ships switched on for testers only; David reviews before the public sees it.
- Done = checked in the rendered app at phone size, then one commit and one deploy after the
  other lanes are quiet.
- Board saved into Projects\Visuals and tiled in the gallery.
