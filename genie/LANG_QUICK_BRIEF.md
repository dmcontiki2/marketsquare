# LANG-LAYERS-1 + QUICK-POLISH-1 — build brief (from chat, 23 Sep 2026)

Source: David's airport chat on his phone, 23 Sep 2026, pasted into the home session the same
evening. This is the authoritative text; it replaces the reconstruction written earlier from the
board. Board: `genie/lang_quick_board.html` (also in Projects\Visuals). Ruling: RUL-162.
Build status per item: see the end of this file.

David approved the design below in chat on 23 Sep 2026 and will review the result on return. Build it, verify it in the rendered app at 390 px, and report per item. The visual board for this brief is `lang_quick_board.html` (same chat); save it to `Projects\Visuals` and tile it in the gallery (`refresh_visuals.py`).

## Sequencing (added 23 Sep 2026)
- Re-run the Adventures regression check before anything else.
- David reviews the Q4 batch (BASELINE_BATCH_2026Q4.md) on his own computer first, switch on for him only.
- Build this brief INTO the Q4 batch, behind the same switch, so it rides the 30 Oct test copy and the single switch-on.
- Merge the 18 Sep unbuilt item "terms in the launch languages" into Part D.
- Part C item 1 (the handover) is built first.
- Do not translate Quick strings until David has decided D3 (the Quick-door worker's name).

## House rules for this run
- Diff local against the server copy before editing any shared file; other lanes deploy mid-day.
- `genie/HARNESS.html` and `quick.html` must stay identical — every Quick change goes into both.
- Bump the `ms.js` / `ms.css` `?v=` cache stamps on any change to them.
- Wait for silence (no other lane writing), then one commit and one deploy via the deploy ref.
- "Done" = checked in the rendered page at phone size, not at the API or DB layer.
- No AI model is named anywhere in code, labels or UI; translation is done by the "translation agent" tier.
- Existing rulings stand: RUL-149 (four most prevailing languages per country), RUL-151 (languages she works in), RUL-160 (i18n draft awaits David's readers and the Language reviewer).

## Part A — App language layer (interface)
1. Add a per-country approved-language config (e.g. table `country_languages(iso2, lang, status)`); seed ZA = `en, zu, st, af, xh` from the existing `QLANGS` list, English is the global default everywhere.
2. Quick's `QLANGS` must read from that config for the user's country instead of the hard-coded ZA list.
3. Main app: add a globe + language-code pill in the header (e.g. `ZU`), reusing the Quick i18n mechanism (`roles/quick_i18n.json` pattern) for the app shell first: bottom nav, listing card labels, detail-screen labels, sell-flow step titles.
4. Strings with no approved translation stay English (same rule as Quick today).
5. Ship Part A behind a flag that is on for the three authorised testers only, off for the public, until David reviews.

## Part B — Advert language layer (content)
1. `listings.lang_orig` — set from the lister's door language at creation (Quick already knows it via `QLANG`).
2. New table `listing_translations(listing_id, lang, title, body, back_translation, source_hash, status draft|approved, approved_at)`.
3. The lister may add at most ONE extra language, chosen only from her country's approved list.
4. The translation agent drafts it, plus a back-translation into her own language; the review screen shows both side by side.
5. The original publishes as normal; the extra language goes live only when she taps Approve.
6. If the original's text changes (`source_hash` differs), the translation returns to `draft`, is hidden, and she is asked to approve again.
7. Buyer render: show the approved translation matching the buyer's app language, else the original.
8. Search: store an English search layer per advert (`search_en`, machine-generated, never shown) so non-English adverts are found by English searches.
9. Advert badge: small language-code chips on the card and detail screen (original first, e.g. `ZU` `EN`); codes, never flags.

## Part C — Quick Listing fixes (from the 23 Sep audit)
Breaks the flow (from David's 15 Sep test):
1. Hand-over must land her signed in on her draft inside the app, with a working way back — this is what parked QUICK-DOOR-1.
2. Every Quick answer (category, service_class, role, area, days, rate, languages) must travel with the draft so the app never re-asks the service type.
3. Quick and the app must both call the one server-side scorer so the score is the same in both.
4. After Publish succeeds, the listing list reloads itself without a manual refresh.

Friction (seen in the rendered page 23 Sep):
5. Ticking all seven days must read "Every day" (or Mon–Sun) on the advert, not "Any day".
6. The language pill must not cover tiles — reserve bottom space or move it into the top bar beside ↻.
7. "Where can you work?" tiles show interiors (lounge, bathtub, bedrooms); replace with area chips or area/landmark imagery.
8. Days screen: pull the day buttons up under the heading and put the Next button directly beneath them.
9. Hide the "Demo: new here" toggle from public users (testers / `?operator=1` only).
10. Score block: replace RS / TS / LS with plain words and one thing that raises each score.

Stunning polish:
11. Lift the landing carousel so the photo leads and both buttons sit in thumb reach; remove the empty top third.
12. Make the language pill visible on first load (most ZA phones default to English even for isiZulu speakers).

## Part D — All nine active countries (APPROVED by David, 23 Sep 2026)
English is global everywhere; up to four local languages per country (RUL-149). Seed `country_languages` with these rows as `approved`, except languages marked `reader_needed` below, which stay unoffered until a human reader signs off.

| Country | Lead | Proposed local languages | Notes |
|---|---|---|---|
| ZA | en | zu, xh, af, nso (Sepedi) | APPROVED swap: Sepedi replaces Sesotho; in Quick replace `st` with `nso` in `QLANGS` and `roles/quick_i18n.json`, drafting the Sepedi strings (RUL-160 readers) |
| NA | en | Oshiwambo, Khoekhoegowab, af, Otjiherero | 2011: Otjiherero 8.6% vs RuKwangali 8.5% tie |
| BW | en | tn (Setswana), Ikalanga | Setswana covers most homes |
| MZ | pt | Emakhuwa, Xichangana, Cisena (+ en second) | Portuguese official; door defaults to pt |
| KE | en | sw (co-official), Gikuyu, Luhya, Kalenjin | Census counts ethnicity, not language |
| DE | de | tr, ru, ar (+ en second) | Door defaults to de |
| GB | en | cy, pl, ro, pa | Welsh official in Wales |
| US | en | es, zh, tl, vi | |
| AU | en | Mandarin, ar, vi, Cantonese | |

reader_needed (never offered to listers until a human reader signs off): Khoekhoegowab, Otjiherero, Ikalanga, Emakhuwa, Xichangana, Cisena, Gikuyu, Luhya, Kalenjin.
The door language comes from the phone; where a country's lead is not English (MZ, DE), the lead language is the fallback before English.
Draft `quick_i18n.json` entries only for approved rows, marked draft per RUL-160.

## Report back
One line per item above: shipped / not shipped + why, with a 390 px screenshot for every UI item.

---

## BUILD STATUS — 23 Sep 2026 evening (home session)

Sequencing
- Adventures check: RE-RUN — full ledger 0 regressions; RG-0425 (Adventures country chip) holding.
- Q4 review on David's computer: NOT DONE — David's own act at his PC.
- Built into Q4 batch: YES — the language layer switches on with baseline_q4 (LANG-Q4-1); testers see it now.
- "Terms in the launch languages" merged into Part D: RECORDED, NOT BUILT — the EULA translation is RG-0412, a separate legal-text job.
- C1 first: YES.
- Quick strings vs D3: Sepedi column drafted for the existing Quick words (Part D asked for it); no new worker-name word translated — D3 still David's.

House rules: server diff clean before edit; HARNESS.html NOT kept identical — it has been a stale prototype since 17 Sep (quick.html moved on); the one-door merge (RG-0436) retires it. ?v= stamps are bumped by the deploy engine. One commit/deploy after silence: yes. No model named: yes.

Part A: 1 shipped as roles/lang_countries.json (file, not table); 2 PARTLY — the preview carries the ZA five matching the file, but does not read it yet (Quick is ZA-only today); 3 shipped (header globe+code, tester-only) — shell strings use the hand-drafted dictionaries, not quick_i18n; 4 yes; 5 yes (tester cookie; public via Q4 switch).
Part B: 1 yes; 2 shipped as listing columns (lang_extra/title_extra/desc_extra/extra_back/extra_status), not a separate table — same behaviour; 3–5 yes; 6 yes (edit of title/description resets to draft); 7 yes; 8 yes; 9 yes (code chips on card and detail).
Part C: 1 shipped (email + WhatsApp link opens the hub on her advert with Publish); 2 shipped (role, class, area, rate, days as availability; languages in the text); 3 shipped in the preview (/quality/preview = the server scorer); 4 shipped (Browse re-reads after Publish); 5 live; 6 preview (top bar) + main-app pill lifted off the nav (live); 7 preview; 8 preview; 9 live; 10 preview; 11 preview; 12 preview.
Part D: nine lists seeded with reader_needed rows unoffered; MZ/DE lead-language fallback: NOT BUILT in Quick (Quick is ZA-only today).

### Update — 23 Sep 2026, later (David: "switch the languages on", one-tap publish, one door, draft words, arrival)
- Languages: ON for everyone (migration 049; /flags lang_layer = true, probed).
- Part C1 superseded by ONE-TAP-PUBLISH-1: the Quick door publishes in the tap (POST /listings/quick-publish); the live letter + arrival screen are her way back.
- One door: /quick/ and every /q/<category> serve the same file (md5-identical, probed); /quick_next.html 301s to /quick/.
- House rule HARNESS.html == quick.html: now TRUE (copied; the old door build is retired).
- Draft/publish/arrival words: drafted in zu, xh, af, nso (46 entries) for David's readers (RUL-160).
- Arrival celebration: built (photo + title rise into a card; reduced motion respected).
- Not fired live: a real one-tap publish (it would put a test advert in front of buyers); the refusal paths were probed live.
