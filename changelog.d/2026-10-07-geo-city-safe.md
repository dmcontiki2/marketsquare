## 2026-10-07 — GEO-CITY-SAFE-1 (RUL-213): the network picks the country, never the city; an empty city points to the full one

David, 7 Oct: Maroushka (Pretoria) found herself set to Johannesburg, saw zero listings and thought the app was broken; "how can we keep the tracker without confusing the user or force her to change it?" then "Please do Claude."

Cause: GEO-AUTO-1 (RUL-211, this morning) placed a visitor without phone location in the city nearest her network's position. South African providers route most homes through Johannesburg, so Pretoria homes landed in Johannesburg, VPN or not.

Now: the network decides only the country. The city is her own pick, else her phone's location (accurate), else the city most of her own adverts are in when she is a seller, else the country's main city. Home's banner says which ("from your phone's location", "where your own listings are", "your country from your internet connection"). A Home whose city has no real adverts shows "Nothing listed in Johannesburg yet - Pretoria has N listings" with Show Pretoria / Stay buttons, fed by the new public GET /geo/city-counts (counts of live, stranger-visible, non-example adverts per city; nothing about any seller). Visitors already auto-placed in the wrong city are corrected on their next visit. Ledger RG-0935; RG-0915 amended.

Cost model impact: none.
