## 2026-10-05 — EMAIL-EXAMPLES-INTL-1 + INTL-VIEW-1: US/UK/AU letters get their own example adverts; the dashboard shows them

David asked whether the letters work for non-ZA readers as well as for ZA ones, and noted he could not see a US version.
PROBED: they did not — the example cards are South-Africa-only, so every US/UK/Australian letter ended on an example
heading with nothing under it; links were fine (187 checked). Built: migration 066 adds 39 showcase adverts (484–522) in
New York, London and Sydney so each country has three per category (Stays/Experiences use the two existing each), and
corrects the car details of 287/292/297 (a Classic Mini showed Toyota Hilux specs). CityLauncher/emailer/intl_examples.py
fills a new {{intl_examples}} marker with the reader's own country's cards from intl_examples.json (written from the live DB
by refresh_intl_examples.py). The Email Templates view now renders every letter through the real send path for a reader
in New York, London and Sydney ("See it as a reader in: US · UK · AU" on each card). Found on the way: ms.js showed
'$65 / hour' over 'per hour' on every non-rand rate advert — fixed (PRICE-BASIS-INTL-1). Ledger RG-0882, RG-0883.
