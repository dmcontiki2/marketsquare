# Property rainbow — Higgsfield prompts (27 Jul 2026)

For the agency_outreach.html (estate agency) hero — same approved treatment as email_hero_tours.jpg.
Workflow identical to the journey photos: higgsfield.ai/ai/image · model **Nano Banana Pro** · aspect **3:2** · 2 credits each.
Save the eight results as `MarketSquare\assets\email\properties\prop1.jpg … prop7.jpg` **plus `strip.jpg`**, then run:
`python scripts\compose_email_rainbow.py assets\email\properties static\email_hero_property.jpg`

Shared style tail — append to every prompt:
> photoreal, golden-hour light, inviting and lived-in, no people, no visible brand names or signage text, cinematic colour grade, 3:2

1. `prop1.jpg` — A gracious Cape Dutch homestead with white gables and a vine-covered veranda, winelands rising behind, —
2. `prop2.jpg` — A modern family home in Waterkloof with a sparkling pool and level lawn, jacarandas in bloom over the street beyond the wall, —
3. `prop3.jpg` — A sleek city penthouse terrace at dusk, skyline lights beginning to glow, —
4. `prop4.jpg` — A Karoo farmhouse with a broad shaded stoep, windpump and open veld to the horizon, —
5. `prop5.jpg` — A whitewashed coastal apartment with a glass balustrade balcony over a turquoise bay, —
6. `prop6.jpg` — A thatched bushveld lodge-style home with a fire pit boma, golden grass and acacias beyond, —
7. `prop7.jpg` — A restored Victorian cottage with broekie-lace ironwork on a leafy avenue, —
8. `strip.jpg` (the wide panorama under the arc — the property equivalent of the winelands train) — A leafy suburban avenue seen from above at golden hour, jacarandas in full purple bloom over rooftops and gardens stretching to blue mountains, — *(same style tail; cropped to a wide letterbox, keep the avenue running through the middle)*

Composition note: the seven span settings (winelands → city → Karoo → coast → bushveld → heritage) and warm-to-cool light,
so the arc reads as one property market with every kind of home in it.
