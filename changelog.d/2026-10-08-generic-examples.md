## 2026-10-08 — GENERIC-EX-1 (RUL-216): every casual work role has a local AI example, made on the server

David, 8 Oct: "these should all be global generic, in terms of visible globally in the local country prices, languages, etc.? ... but it should not increase the users on phone app size".

The new public GET /examples/roles makes one AI example per casual work role (47) for the country and city being looked at: the role's own picture, its name in the asked language (Quick's checked word list, else the role registry, else English), and a rate in that country's currency starting from its legal minimum wage -- the same table as Quick's rate floor (ZA R320 / day, a car wash from R65 / car; KE KSh 840 / day; UK £140 / day; US $80 / day). Nothing is stored as an advert and nothing is added to either app: TrustSquare fetches about 15 KB once per city and language, Quick asks only for the role being searched, and each picture loads only when its card is on screen.

Quick's Find uses it when nothing real and no stored example fits a role (one card, her area, her currency). TrustSquare adds it to Services for each role nobody real (and no stored example) offers in that city: marked as an AI example, after real adverts, hidden by the same switch, never counted on a tile or as a listing, kept off the map. A tap opens a sheet that says there is nobody behind it yet and offers "I do this work -- list me free", straight into Quick's sell flow for that role. Ledger RG-0940 (also asserts the server's wage table equals Quick's).

Cost model impact: none.
