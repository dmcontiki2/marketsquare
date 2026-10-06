## 2026-10-06 — Maroushka listing 526: sizes lost on save, no way to re-add refused photos

- SIZE-CARRY-1 (RG-0905): the server's create model had no floor_area / erf_size, so EVERY new advert on every
  lane lost both sizes on first save (only Edit kept them). Added to the model + written on create. The sell flow
  now sends floor_area, erf_size and title_type on draft create and patch; the Simple Builder reads its own form's
  keys (floor_size, stand_size, bedrooms, bathrooms, property_type) — it had been sending nulls for all five.
- EDIT-ADD-PHOTO-1 (RG-0906): the Edit screen hid the "Add Photo" tile at a hard 10 photos; PHOTO-CAP-2 had raised
  the real cap to 24 for property but missed the tile. Maroushka had 10 accepted + 3 refused by the anonymity
  check, edited the 3, and had no button to add them back. Tile now follows msPhotoCap.
- Evidence (probed, server log 6 Oct 17:25 UTC): 13 x POST /listings/526/photo/draft, 3 x 422 (anonymity gate,
  working as designed), 10 x 200; PUT /listings/526 at 17:32 restored floor 100 / erf 2400.
