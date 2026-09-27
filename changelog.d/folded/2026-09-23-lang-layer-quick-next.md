## 2026-09-23 — The language layer (RUL-162), South Africa's other three languages, and the Quick app reworked

David, from Cape Town airport: "perform this design change ... set up the other three launch country
languages ... review the quick listing app and fix/improve it -- easy/quick/fluid, but stunning."

**LANG-LAYER-1 (RUL-162).** The app speaks the reader's language; the advert speaks the lister's.
- `roles/lang_countries.json` — the nine approved country lists (David, 23 Sep); 'reader' languages
  are drafted but never offered. South Africa: English, isiZulu, isiXhosa, Afrikaans, Sepedi
  (Sepedi replaces Sesotho, census 2022; `st` stays accepted for readers who chose it before).
- `bea_main.py` — `GET /lang/countries`; `POST /listings/{id}/lang/draft|approve|remove`
  (original language, ONE extra language from her country's list, a back-translation into her own
  words so she approves what it really says, and an English search layer); new listing columns
  `lang_orig, lang_extra, title_extra, desc_extra, extra_back, extra_status, search_en`; editing
  the original drops an approved extra back to draft; `GET /listings?q=` also matches `search_en`;
  the public list never carries an unapproved extra; `POST /listings` stores `lang_orig`.
- `launch_switches.lang_layer` (default OFF). `/flags` turns it ON for any reader holding the tester
  cookie (`ts_review`), so David and his testers see it now; switching it on for everybody is David's.
- `ms.js` — the globe menu offers the reader's country list with codes; the detail view shows the
  advert in the reader's language when the seller approved one, else the original with a code chip
  and "Also in XX — show it"; adverts are never machine-painted; cards carry the code chip; the
  seller's edit screen gains an "Advert languages" panel.
- LANG-PILL-CLEAR-1 — the globe pill no longer sits on the bottom nav (public fix).

**I18N-SA5-1.** `roles/app_i18n_zu.json`, `app_i18n_xh.json`, `app_i18n_nso.json` — 1,569 phrases
each, hand-drafted (RUL-160: the Language reviewer proofreads, users' flags correct), loaded by
`migrations/048`. Probed the reason: the machine lane rendered "blue bicycle" as "white" in isiZulu.

**Quick app — repair lane (live now, `quick.html`).** QUICK-ADTEXT-1: the advert's description was
OUR coaching line ("Written from your N taps ... Change any word of it before it goes up") — the
words a buyer reads; it now says only what she told us, in plain sentences. QUICK-EVERYDAY-1:
seven ticked days read "Any day"; now "Every day". QUICK-DEMO-OFF-1: the "Demo: new here" switch
was visible to every real visitor. QUICK-DRAFT-LAND-1 (`ms.js`): the Quick way back (`?draft=`,
emailed and WhatsApp) now opens the hub on that advert with Publish in reach — nothing read it before.

**QUICK-NEXT-1 — the reworked Quick app, for David's review at `/quick_next.html`.** Language on
the first screen as big code buttons and in the top bar (never over the tiles), five SA languages;
the advert written in HER language and sent with `lang_orig`; "Where can you work?" as place chips,
not house interiors; Next right under the week and "Every day" moves straight on; trades name an
amount after the basis (no more "POA"); the draft leads with the advert and ONE strength ring,
score detail and what-happens-next folded away; "Save my advert" says what the button does;
readable button text on every category colour; the next step's pictures fetched ahead; `?c=<cat>`
with the /q/ aliases so one app can serve the outreach door. Replaces `/quick/` when David has seen it.

Ledger: RG-0431..RG-0436 (OPEN until their live legs are measured after the deploy).
Audit and screenshots: `genie/QUICK_NEXT_REVIEW.html`.
