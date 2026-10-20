## 2026-10-18 — CITY-ALIAS-1 + LIST-WORDS-1 (Goal run 43, RG-1062)

- WALKED: the queued SMS lanes' own links as a stranger (Afrikaans Cape Town gardener; isiXhosa Gqeberha).
- CITY-ALIAS-1: the door's city pack says "Gqeberha (Port Elizabeth)" and "Mbombela (Nelspruit)"; links, accounts and
  Cloudflare say "Port Elizabeth", "Gqeberha" or "Nelspruit". The exact match failed, so those links asked "Which city?"
  with Pretoria first. quick.html `cityKey` accepts either name; CityLauncher `quick_door._pack_city` now puts
  `city=Gqeberha` / `city=Mbombela` in the link, and `sms_wave` adds it only when it costs no extra SMS part
  (Port Elizabeth services and Nelspruit now carry it; every other city's links are unchanged).
- LIST-WORDS-1: an Afrikaans card showed "Mon, Wed, Fri" and "R350 / day" under "Beskikbaar: Ma, Wo, Vr ... R350 per dag".
  `qTr` translates a comma list word by word and gives a price chip the same units the advert already uses.
