## 2026-09-27 — Terms v1.19 published, and the app now does what it says (R7: PROPERTY-ONE-1, BUYER-TERMS-1, EULA-1.19, COUNTRY-OPEN-1, KENYA-CONSENT-1, INTRO-WITHDRAW-1)

David, 26–27 Sep 2026, on the Terms review: *"Publish; all re-accept"*, *"One at a time"*, *"Accept all 8"*, and on the
countries: *"we decided to not add Germany and Botswana for now, please proceed with your option 1"*. His later word on
banking, given to the other session (RUL-176: *"we dont store the customers banking details"*), wins over the 26 Sep
"identity only" — this round's banking wording was dropped and that session's removal kept.

- **EULA-1.19** — v1.19 is the text at /terms and in the app (eula_sync.py: one source, three copies). New accounts
  accept it at once; accounts opened earlier get the clause-15.1 notice by email (the daily sweep, once per account,
  table `eula_notices`) and as an in-app card, and on **12 October 2026** every earlier acceptance is set aside and each
  person accepts once, at her next listing, edit, introduction request or top-up (`EULA_V119_EFFECTIVE`, the dated
  `_EULA_MATERIAL_STEPS`). The notice summary and the Seller Terms box say what changed in five languages.
- **BUYER-TERMS-1** — a Buyer accepts the Terms once, one tap on the real text, before her first introduction request,
  Local Market request or top-up; the server refuses first (428) so nothing is held or charged; a plan payment opens
  the Seller sheet (scroll + two ticks) instead.
- **PROPERTY-ONE-1** — a request pauses a Property listing under the wallet lock; the next buyer is told why and when;
  accepting, declining, the buyer withdrawing or the 96-hour removal opens it again; the seller cannot reopen it by
  hand while a buyer waits; her own pause stays hers; Cars keep their queue. How-it-works and the seller's card say so.
- **INTRO-WITHDRAW-1** — Terms 5.4 promised withdrawal only by an email that no tool performed. My Space now has a
  Withdraw button on a request the seller has not answered; the 1T hold returns in full, exactly once.
- **SENT-LIST-1** — found walking that button in a real browser: every sent request crashed My Space's list (a numeric
  listing id met `.split`), so no buyer ever saw a request she had sent. The row now names the listing, escaped.
- **COUNTRY-OPEN-1** — Germany, Botswana and Mozambique are "coming soon": browse only; publishing, introductions and
  Quick refuse there with a plain sentence, and the country list marks them. South Africa, Namibia and Kenya are open.
- **KENYA-CONSENT-1** — a Kenyan seller ticks consent once, herself, before her ID upload or a Kenyan property listing
  goes live (Data Protection Act s.49). Registering with Kenya's ODPC is David's step (OPEN_LOOPS L24;
  `KENYA_ODPC_HANDOVER.html` has the form's answers).
- **Terms text** — Schedules H — Kenya and I — Namibia (researched 26 Sep); the merged draft's five short schedules
  had been placed between Argentina's G6 and G7, and G7 is back after G6; 2.4/9.3 Buyer acceptance; 5.3 Property one at
  a time; 5.4 withdraw in the app; 13.5 coming soon; 15.1 the express re-acceptance; D8/E9 without the closed EU ODR
  platform; 9.2 carries the other session's identity-checks row (RUL-178).
- **BANKING words (RUL-176 follow-through)** — the other session removed the banking route and form; three screens
  still said "Add your banking details … when you buy Tuppence". They now describe the bank name check, in five
  languages; the publish note no longer mentions banking.
- **LM-WORDS-1** — the Local Market tile says the seller pays 1T when the first buyer asks; its in-app clauses 1 and 4
  say what the code does.
- **Integration fixes** — Quick's language block regenerated from its source with the other lane's 'Share' carried
  into roles/quick_i18n.json, and genie/HARNESS.html is again byte-identical to quick.html.

Ledger: RG-0503 (re-aimed to RUL-176/178 by the Circle lane) now also refuses the old banking words on the three
screens; RG-0511 PROPERTY-ONE-1, RG-0512 BUYER-TERMS-1, RG-0513 EULA-1.19, RG-0514
KENYA-CONSENT-1, RG-0515 COUNTRY-OPEN-1, RG-0516 LM-WORDS-1, RG-0517 INTRO-WITHDRAW-1, RG-0518 SENT-LIST-1 — each
red on a deliberate break and green on the real tree. Rulings RUL-181/182/183, with reflections for RUL-176/177/178.
Translations: migration 061 (af, zu, xh, nso). Stranger test PASS, 324 routes (two new routes declared).
Cost model impact: none.
