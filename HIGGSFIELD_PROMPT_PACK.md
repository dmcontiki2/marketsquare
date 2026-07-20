# TrustSquare Brand Photo Pack — Higgsfield prompts (AGENT-PHOTO-2, 20 Jul 2026)
15 images · one consistent look · every filename pre-mapped to an app slot.

## Style guide — paste this block FIRST into every prompt
> Photorealistic editorial photography, South African setting, warm golden-hour light,
> deep navy and warm amber accents in wardrobe/props (#0c1a2e and #C8873A tones),
> shallow depth of field, high detail, clean composition with clear space for text
> overlay at bottom, aspect ratio 3:2, no identifiable faces (subjects from behind,
> in silhouette, or hands only), no readable text except where specified, no logos,
> no watermarks.

**Brand rule (matches the app's PHOTO-ANON-1):** nobody's face is ever recognisable —
agents from behind, workers by their hands, guides in silhouette. It IS the brand:
anonymous until introduced.

**Consistency tips:** generate all 15 in one session with the same style block; if
Higgsfield supports a seed or style reference, lock it after the first image you love.
Export highest quality; we resize server-side.

---

## A · Agent scenes (replace the SVG placeholders)
| # | File | Prompt (after style block) |
|---|---|---|
| A1 | agent-stock/property.jpg | Estate agent in a tailored navy blazer photographed from behind, standing on a neat lawn facing a beautiful modern Pretoria family home at golden hour, a classic white "FOR SALE" board planted in the grass beside them, jacaranda tree hinting purple in the background. |
| A2 | agent-stock/cars.jpg | Car sales agent in a navy shirt photographed from behind, presenting a gleaming white SUV on a clean dealership forecourt at golden hour, small "FOR SALE" stand beside the car, warm light reflecting off the paintwork. |
| A3 | agent-stock/travel.jpg | Travel agent photographed from behind on a safari lodge deck, gesturing with a tablet toward an endless African savanna at sunset, acacia trees and distant elephants, leather travel bag at their feet. |

## B · Home "Categories" tiles (6 — Local Market stays a live scroll, excluded)
| # | File | Prompt |
|---|---|---|
| B1 | brand-photos/cat_property.jpg | Beautiful South African suburban family home with manicured garden at golden hour, inviting front entrance, no people. |
| B2 | brand-photos/cat_tutors.jpg | Warm study corner: open textbooks, notebook with handwritten maths, laptop and reading lamp, adult hands writing, afternoon light through a window. |
| B3 | brand-photos/cat_services.jpg | Skilled electrician's gloved hands working neatly on a modern distribution board, professional tools laid out on a clean cloth, workshop light. |
| B4 | brand-photos/cat_adventures.jpg | Drakensberg mountain vista at dawn with a winding trail, hiker in silhouette far in the distance, dramatic golden clouds. |
| B5 | brand-photos/cat_collectors.jpg | Collector's table elegantly laid out: vintage wristwatches, old coins in trays, magnifying loupe, soft directional light, hands in white gloves placing one coin. |
| B6 | brand-photos/cat_cars.jpg | Pristine modern hatchback parked on a leafy Pretoria street at golden hour, low three-quarter angle, no people. |

## C · SELL page tiles (6 — the app already looks for THESE filenames; open STATUS item)
Different energy: the SELLER preparing — "your item, made beautiful".
| # | File | Prompt |
|---|---|---|
| C1 | sf_cat_property.jpg | Hands holding a smartphone photographing a bright, styled living room, golden light flooding in, the phone screen showing the room in frame. |
| C2 | sf_cat_tutors.jpg | Tutor's desk being prepared: hands arranging books and a name-less certificate frame, laptop open to a lesson plan, warm study light. |
| C3 | sf_cat_services.jpg | Tradesperson's hands packing a spotless toolbox — spirit level, multimeter, neatly coiled cables — golden workshop light. |
| C4 | sf_cat_cars.jpg | Hands polishing the bonnet of a clean silver car with a microfibre cloth, water beads catching golden light, driveway setting. |
| C5 | sf_cat_collectors.jpg | Hands in cotton gloves laying rare trading cards and a vintage camera on dark felt under soft photographic light. |
| C6 | sf_cat_adventures.jpg | Packed adventure kit ready for guests: backpack, binoculars, wide-brim hat and map on a lodge table, savanna out of focus behind. |

*(sf_cat_local_market.jpg — skip: Local Market tile is becoming a live scroll window.)*

## After generation — the wiring (mine, one step)
Drop the files in `assets/brand-photos/` (and the 3 agent ones in `assets/agent-stock/`),
tell me, and I: compress to web weight (~150-250KB, 1200px wide), upload to
/static/…, switch the backend stock_photo paths svg→jpg, wire the home + sell tiles,
bump ms.js, ship, and verify live in the browser — measured, not guessed.
