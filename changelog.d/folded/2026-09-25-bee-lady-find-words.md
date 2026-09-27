## 2026-09-25 — The Bee Lady's advert: Quick finds it, and nobody rewrites her words (LM-GROUP-FIND-1, ADVERT-WORDS-1)

David, 25 Sep 2026, on the Misty Forest honey advert (listing 273, Local Market, Garsfontein): the Afrikaans view read
"Misty Forest roupasteunings, propolis & byswas — deur die Bylady" ("raw honey is rou heuning"; "The Bee Lady is her
called name, it should not be translated"), and "in the quick listing app i looked for honey locally and her live advert
did not come up".

- **LM-GROUP-FIND-1 (RG-0488)** — Quick's Find turned the tile "Food & preserves" into the one search word `preserv*`,
  which her advert does not contain (`q=honey*` found it at once). A Local Market tile is a GROUP, not a word: Find now
  asks for the whole Local Market category in the city and matches the group on the advert's own title and text (the
  TRIP-TYPE-1 pattern). "Furniture" had the same fault against the teak sideboard. A typed word still searches as before.
  quick.html and genie/HARNESS.html kept identical.
- **ADVERT-WORDS-1 (RG-0489)** — the Afrikaans title was not hers and not an approved second language (listing 273 has
  none): the page translator rewrote her advert. RUL-162 keeps an advert in the seller's language plus one extra language
  only she approves, so every advert title and description now carries data-notranslate — main and Local Market cards
  and detail pages (the Local Market pages had none; the main detail had it only with the language layer on). The advert
  translator (her own second-language draft) now keeps nicknames ("deur die Bee Lady") and never invents a word; the
  Afrikaans glossary carries rou heuning / byewas.
