# Adventures Super-Advert Expansion — Higgsfield Prompt Pack (24 Jul 2026)

10 new photos (5 per listing) to deepen the two Adventures SUPER ADVERTs, plus an
interactive Dinokeng map. Same house look as HIGGSFIELD_PROMPT_PACK.md.

Targets:
- advexp = "Private Big 5 sunset game drive — Dinokeng, max 8 guests"  (has 3 photos -> 8)
- advacc = "Stone-and-thatch lodge suite with private plunge pool"      (has 3 photos -> 8)

## Style block — paste FIRST into every prompt
> Photorealistic editorial travel & wildlife photography, South African bushveld
> (Dinokeng, Gauteng), warm golden-hour light, deep navy and warm amber accents
> (#0c1a2e and #C8873A tones), shallow depth of field, high detail, natural colour,
> aspect ratio 3:2, NO identifiable human faces (people from behind, in silhouette,
> or in shadow only), no readable text, no logos, no watermarks.

Brand rule (PHOTO-ANON-1): nobody's face is ever recognisable. Guides in silhouette,
guests from behind, workers by their hands. Anonymous until introduced.

Consistency: use the existing hero as a reference image where Higgsfield allows, and
lock the seed/style after the first frame you love, so the SAME vehicle / SAME lodge
carries through the whole set.

---

## GAME DRIVE (advexp)  —  reference: sup_advexp_2_vehicle.jpg + sup_advexp_3_sundowner.jpg
THE VEHICLE (bake into every one): a cream / beige open-sided safari Land Cruiser
game-viewer, tiered pale canvas-and-leather bench seats, black tubular roll bars,
rolled brown blankets and binoculars on the seats, weathered wooden trim.

| File | Prompt (after style block) |
|---|---|
| sup_advexp_4_lions.jpg | A pride of lions — a dark-maned male and two lionesses — resting in long golden grass under a flat-topped acacia, AWAY from any water; the cream open safari Land Cruiser (tiered pale seats, black roll bars) parked close in the left foreground with guests watching from behind in silhouette; dusty warm side-light, Dinokeng bushveld. |
| sup_advexp_5_leopard.jpg | A leopard draped along the thick branch of a marula tree in early-evening light, amber eyes, tail hanging; the cream open safari game-viewer stopped just below on a sandy track in the lower foreground, a khaki-capped guide seen from behind; soft golden dust. |
| sup_advexp_6_buffalo.jpg | A herd of Cape buffalo, a heavy old bull in front with worn boss, staring toward camera through golden dust; the cream open safari Land Cruiser at the right frame edge with guests watching from behind; low three-quarter angle, bushveld at sunset. |
| sup_advexp_7_snake_meerkat.jpg | Low, tense action on a sandy bush track: a raised Cape cobra flared in a defensive strike posture facing a single meerkat standing tall on its hind legs a metre away, dust in the golden light; the front of the cream safari Land Cruiser (bonnet, black bull-bar, one headlight) framing the top foreground as if watched from the vehicle; shallow focus on the standoff. |
| sup_advexp_8_rhino.jpg | Two white rhino, a cow and calf, grazing in open golden grassland kicking up light dust; the cream open safari game-viewer at a respectful distance mid-ground left, guests silhouetted; warm low sun, acacia silhouettes on the horizon — completing the Big Five. |

## LODGE (advacc)  —  reference: sup_advacc_1_main.jpg + sup_advacc_3_dinner.jpg
THE LODGE (bake into every one): rough warm-stone walls, heavy thatch roof, weathered
timber deck, navy-cushioned safari furniture, brass hurricane / paraffin lanterns,
honeymoon-grade bush lodge on a ridge with a savanna view.

| File | Prompt (after style block) |
|---|---|
| sup_advacc_4_bar.jpg | Interior of the stone-and-thatch lodge bar at sunset — a rustic timber-and-stone bar counter with a row of amber spirit bottles and cut-glass tumblers, brass lantern glow, thatched ceiling and timber beams, large picture windows behind framing a fiery orange savanna sunset over acacia trees; no people; warm amber and navy tones. |
| sup_advacc_5_braai.jpg | A night braai on the lodge's timber deck — a big open wood fire and glowing coals under a steel grid loaded with sizzling boerewors and lamb chops (braai vleis), sparks rising; two or three guests stand around it as warm-lit shadowy silhouettes, faces not distinguishable in the darkness; stone-and-thatch lodge and hanging lanterns behind, deep night-blue starry sky. |
| sup_advacc_6_boma.jpg | A circular stone boma at night with a large central campfire throwing tall flames and orange light; guests seated on low canvas safari chairs are dark silhouettes against the fire, drinks in hand; brass lanterns on the ground, sparks drifting into a starlit bushveld sky — intimate and warm. |
| sup_advacc_7_lounge.jpg | The lodge's living corner at night — a low stone fireplace with a small fire, a worn leather armchair with navy cushions, an animal-skin rug, brass reading lantern and a decanter on a timber side table, thatch beams overhead, warm pools of lamplight, a dark window showing the last blue of dusk; no people. |
| sup_advacc_8_sunrise.jpg | Early-morning coffee on the lodge deck — a wooden tray with a French press, enamel mugs and rusks on the deck rail, the small plunge pool mirror-flat, soft pink-gold sunrise over the savanna with a distant herd of impala and a giraffe in the misty golden light; a single guest wrapped in a blanket seen from behind; serene and fresh. |

## Wiring (after generation)
Compress each to ~150–250KB, 1200px wide, place in assets/super/ with the filenames
above, extend both listings' photo arrays to 8, add the Dinokeng interactive map,
bump ms.js, then ship + verify.
