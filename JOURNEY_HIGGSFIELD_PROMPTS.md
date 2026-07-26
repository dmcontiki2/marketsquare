# Journey Super-Adverts — Higgsfield Prompt Pack

Photos for the interactive journey maps (Namibia, Botswana, Mozambique, Cape to Cairo).
GENERATED from `journeys/*.json` by `scripts/make_prompt_pack.py` — do not hand-edit;
edit the spec and re-run, so the prompts and the maps can never drift apart.

**Brand rule (PHOTO-ANON-1):** nobody's face is ever recognisable. Guides in silhouette,
travellers from behind, cooks by their hands. Anonymous until introduced.

**Consistency:** lock the seed/style after the first frame you love in a journey so the
SAME vehicle / SAME train / SAME lodge carries through that whole set.

**Wiring after generation:** drop the files into the `photo_dir` named below (filenames
must match exactly), then re-run `python3 scripts/build_journey.py` — the builder embeds
and shrinks them automatically and replaces the placeholder tiles. No other change needed.

---

## Botswana, water to salt  (25 photos)

- **photo_dir:** `assets/journey/bwa`
- **output:** `botswana_journey.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial safari photography, Botswana — Okavango channels, mopane woodland and white salt pan, warm golden-hour light and dust, deep navy and warm amber accents (#0c1a2e / #C8873A), shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `d1_start.jpg` | Maun · safari town — Dusty frontier town where every second vehicle is a converted game-viewer and every pilot is twenty-four. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d1_view.jpg` | The delta from the air — An inland delta that never reaches the sea — silver channels braided through ten thousand green islands. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d1_sight.jpg` | Poled through the papyrus — Standing in the stern with a long pole, reed tips brushing past, frogs the size of a thumbnail on the stems. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d1_food.jpg` | Bream on the coals — Freshwater bream caught that afternoon, split, salted and grilled over a driftwood fire on an island. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d1_over.jpg` | Island tented camp — Six tents under wild fig trees; hippo grunting in the channel all night, close enough to feel. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d2_start.jpg` | First light drive — Out before the sun with a blanket and a flask; the bush is loudest in the first forty minutes. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d2_view.jpg` | Wild dog on the hunt — A pack of painted dogs moving at a fast trot, ears like satellite dishes, absolutely committed. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d2_view2.jpg` | Lions in the shade — A pride flat on their backs under a leadwood, paws in the air, indifferent to everything. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d2_food.jpg` | Slow-pounded beef & sorghum — The national comfort dish — beef simmered for hours then pounded to threads, with fermented sorghum porridge and wild greens. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d2_over.jpg` | Camp on the floodplain edge — Raised decks looking over open grassland; elephants cross in front of the fire before dinner. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d3_start.jpg` | Sand-track transfer — Low range, windows down, four hours of mopane and deep sand to cover ninety kilometres. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d3_view.jpg` | Elephant highway — Bull elephants in single file on a path worn a metre deep by a century of the same walk. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d3_sight.jpg` | The marsh channel — A channel that mysteriously dried up for decades, then refilled — and the game came straight back. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d3_food.jpg` | Bush braai under the stars — Grilled meat, pot bread baked in the coals, and a long table set out in the open with lanterns. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d3_over.jpg` | Marsh-side camp — Canvas under a rock ridge; lion calling somewhere south, answered twice before midnight. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d4_start.jpg` | East to the river — Out of deep sand onto a tar road — the first hard surface in four days feels like flying. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d4_view.jpg` | Riverfront herds — Hundreds of elephants coming down to drink at once, calves shoulder-deep, crocodiles keeping their distance. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d4_sight.jpg` | Sundown on the water — A flat-bottomed boat drifting with the current while the sun goes down enormous and orange behind the reeds. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d4_food.jpg` | River-fish supper — Grilled tilapia with chilli, lime and a cold beer on a deck built out over the water. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d4_over.jpg` | Riverside lodge — Thatch and timber above the bank; hippos on the lawn at 2 a.m., which the staff mention casually. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d5_start.jpg` | South from the river — Green gives way to grey scrub, then to grass, then to nothing much at all. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d5_view.jpg` | The pan, edge to edge — A flat white plain so featureless the horizon curves; drive out onto it and the vehicle is the only vertical thing. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d5_sight.jpg` | Meerkats at their burrow — A habituated colony that will stand on your shoulder for a better view, entirely on their own terms. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d5_food.jpg` | Last supper on the salt — A table, white cloth and lanterns set out on the open pan; grilled meats, cold wine, and a full 360° sunset. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d5_finish.jpg` | Journey's end · the pan — Bedrolls on the salt, no tent, no tree, no sound — just the whole sky. Wide closing shot with a sense of arrival and completion, golden light. |

---

## Cape to Cairo, by rail  (31 photos)

- **photo_dir:** `assets/journey/c2c`
- **output:** `cape_to_cairo_journey.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial rail-travel photography, Africa end to end — grand stations, sleeper-car interiors in brass and teak, Karoo, Zambezi, savanna and Nile desert, cinematic warm light, deep navy and warm amber accents (#0c1a2e / #C8873A), shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `l1_start.jpg` | Cape Town · the platform — Table Mountain filling the window, brass, teak and a station clock — the journey starts formally. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l1_food.jpg` | Cape Malay farewell lunch — Spiced mince baked under savoury custard with yellow rice, then syrup-soaked plaited doughnuts with coconut. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l1_view.jpg` | Through the winelands — Whitewashed gables, vineyards in rows, and a wall of blue mountains the train has to find a way through. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l1_sight.jpg` | Victorian halt on the plateau — A perfectly preserved railway village on the empty Karoo — gaslamps, a double-storey verandah, one street. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l1_over.jpg` | First night in the sleeper — Berth made up while you dine; the rhythm of rail joints and a lit lamp somewhere far out on the plain. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l2_start.jpg` | Dawn on the Karoo — Pink light on flat-topped hills, windmills, sheep, and not one other vehicle. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l2_food.jpg` | Karoo lamb, slow-roasted — Lamb raised on wild aromatic scrub, so the meat arrives pre-seasoned — served pink with pumpkin fritters. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l2_sight.jpg` | The Big Hole — A 200 m crater dug by hand by fifty thousand men with picks and buckets, now filled with green water. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l2_view.jpg` | Highveld grassland — Grass to the horizon in every direction, thunderheads stacking up in the afternoon. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l2_over.jpg` | Second night, rolling north — Dinner in the dining car under lamplight, then the long climb onto the highveld in the dark. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l3_start.jpg` | Jacaranda capital — Purple streets in spring, union buildings on the ridge, and the last big-city platform for a while. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l3_food.jpg` | Biltong & braai on board — Air-dried spiced beef sliced thin as a snack, then flame-grilled steak and coiled farm sausage for dinner. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l3_sight.jpg` | The smoke that thunders — A kilometre-wide curtain dropping 100 m into a gorge; the spray column is visible 50 km away. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l3_view.jpg` | The bridge over the gorge — A 1905 steel arch spanning the chasm — the original dream of this whole railway, and the point it stalled. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l3_over.jpg` | Colonial hotel by the falls — Verandahs, ceiling fans, high tea, warthogs on the lawn and permanent thunder in the background. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l4_start.jpg` | Onto the long line — The famous cross-continental service: two nights, one train, minimal fuss. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l4_view.jpg` | Game from the window — The line runs through a national park — giraffe, elephant and buffalo from the dining-car window at walking pace. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l4_food.jpg` | Grilled meat & maize — Charcoal-grilled goat and beef with stiff maize porridge and a fierce tomato-chilli relish, eaten with hands. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l4_sight.jpg` | Spice port on the ocean — Indian Ocean harbour thick with the smell of clove, cardamom and cinnamon from the islands offshore. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l4_over.jpg` | Harbour-side rooms — Carved doors, a courtyard, call to prayer at dusk and dhows on the water at first light. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l5_start.jpg` | Northbound — Rail, road and river stitched together — the one leg where the dream of a single line still has gaps. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l5_view.jpg` | Where two Niles meet — Blue water from the highlands and white water from the lakes joining in one visible seam. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l5_sight.jpg` | Desert pyramids — Steep, narrow pyramids in golden sand — smaller than Egypt's, and often entirely empty of people. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l5_food.jpg` | Slow-cooked beans & flatbread — Fava beans stewed overnight with cumin, lemon and olive oil, scooped up with hot flatbread — breakfast for a continent. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l5_over.jpg` | Nubian village on the river — Blue and ochre houses, palm-shaded courtyards, and the Nile running fast and green below. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l6_start.jpg` | The Nile sleeper — Boarding at dusk with the river turning copper; dinner served in the cabin as the palms slide past. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l6_sight.jpg` | Temple city at dawn — Avenues of stone rams, hypostyle halls of vast painted columns, cut sharp by early light. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l6_food.jpg` | Rice, lentils & fried onion — The great street dish — rice, lentils and macaroni under spiced tomato sauce, vinegar and crisp onions. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l6_view.jpg` | The green Nile valley — A ribbon of intense green a few kilometres wide with hard desert on both edges — the whole country in one view. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l6_food2.jpg` | Mint tea in sight of the tombs — Sweet mint tea on a rooftop with the three pyramids filling the skyline behind the cups. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l6_finish.jpg` | Journey's end · Cairo — Ten thousand kilometres, one continent, and a last look back down the line from the Giza plateau. Wide closing shot with a sense of arrival and completion, golden light. |

---

## Mozambique, down the coast  (25 photos)

- **photo_dir:** `assets/journey/moz`
- **output:** `mozambique_journey.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial travel photography, Mozambique Indian Ocean coast — turquoise water, dhow sails, coral-stone and whitewash, bright tropical light with deep navy and warm amber accents (#0c1a2e / #C8873A), shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `d1_start.jpg` | Maputo · arrival — Wide jacaranda avenues, Mediterranean balconies and Indian Ocean humidity in equal measure. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d1_sight.jpg` | The iron market — A cast-iron market hall shipped out in pieces a century ago, still stacked with chillies, cashews and fish. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d1_food.jpg` | Peri-peri prawns — Giant prawns split, drowned in garlic, lemon and fierce bird's-eye chilli, grilled hot — with cold beer and rough bread. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d1_view.jpg` | The bay at dusk — Rooftop view over the harbour, cranes going quiet, the whole sky turning peach. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d1_over.jpg` | Colonial townhouse rooms — High ceilings, shutters, a slow fan and mosaic floors that stay cool all day. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d2_start.jpg` | Out of the capital — Coconut palms, roadside pineapple stalls and speed bumps in every village. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d2_food.jpg` | Cassava leaf & coconut stew — Pounded cassava leaves slow-cooked with coconut milk, peanuts and prawns, served over rice — the country's signature dish. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d2_sight.jpg` | Dhow across the bay — A lateen-sailed dhow ferrying passengers and bicycles across a turquoise bay, unchanged in centuries. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d2_view.jpg` | Whale sharks offshore — A shape the size of a bus rising slowly under the boat, spotted like a night sky. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d2_over.jpg` | Beach cabana in the dunes — Reed and thatch on a vegetated dune, ten steps down to a wide empty beach. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d3_start.jpg` | Morning on the reef — Warm water, soft corals, and manta rays queuing at a cleaning station like traffic. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d3_sight.jpg` | Roadside cashew stand — Cashews roasted in the shell over a drum fire, sold hot in newspaper cones by the kilo. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d3_food.jpg` | Bread, chilli & grilled fish — Crusty rolls baked in a wood oven, split and filled with grilled fish and a spoon of chilli oil. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d3_view.jpg` | First sight of the islands — Five sand islands strung along the horizon, water going from jade to deep blue. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d3_over.jpg` | Fishing-town guesthouse — Whitewashed rooms above a working beach where the boats are dragged up at dusk. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d4_start.jpg` | Dhow to the islands — Sailing out on the morning wind with the boom swinging low over your head. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d4_view.jpg` | Sandbank at low tide — A crescent of white sand that exists for four hours a day, surrounded by every shade of blue there is. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d4_sight.jpg` | Two-mile reef — Bright shallow reef thick with clownfish, parrotfish and the occasional passing turtle. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d4_food.jpg` | Lobster on the beach — Split lobster grilled over coconut husks with lemon and chilli butter, feet in the sand. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d4_over.jpg` | Island dune lodge — Thatched chalets high on a vegetated dune with nothing but ocean in three directions. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d5_start.jpg` | North along the coast — The coastline from above: reef, mangrove, river mouth, repeat, for eight hundred kilometres. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d5_sight.jpg` | The old stone town — Coral-stone streets, a Portuguese sea fort, and a chapel claimed to be the oldest European building south of the Sahara. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d5_view.jpg` | The long causeway — A three-kilometre single-lane bridge to the mainland, best walked at sunset. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d5_food.jpg` | Spiced coconut curry — Fish curry heavy with coconut, cinnamon and clove — Arab, Indian and Portuguese cooking in one pot. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d5_finish.jpg` | Journey's end · the island — Sundowners on a fort wall built in 1558, dhows coming home below. Wide closing shot with a sense of arrival and completion, golden light. |

---

## Namibia, end to end  (23 photos)

- **photo_dir:** `assets/journey/nam`
- **output:** `namibia_journey.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial travel photography, Namibia — red Sossusvlei dunes, gravel plains and Atlantic fog, hard clean desert light with long shadows, deep navy and warm amber accents (#0c1a2e / #C8873A), shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `d1_start.jpg` | Windhoek · departure — Highland capital, jacaranda streets, a last flat white before the gravel begins. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d1_food.jpg` | Roadside grill stop — Flame-grilled beef cut straight onto brown paper with a fist of coarse salt and chilli — the country's favourite roadside lunch. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d1_view.jpg` | Dune country, first light — Rust-red dunes 300 m tall, knife-edge crests, a dead white pan cracked like old porcelain. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d1_over.jpg` | Desert camp under the escarpment — Canvas and stone tucked below a rock wall; no light for 200 km, so the Milky Way does the ceiling. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d2_start.jpg` | Dawn on the dunes — Climb the high crest before sunrise; the sand goes from grey to blood-orange in four minutes. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d2_view.jpg` | Canyon & gravel plains — A deep rock gorge, then 200 km of pale gravel where the horizon shimmers and nothing moves. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d2_food.jpg` | Lagoon oysters & flamingos — Cold Atlantic oysters shucked at a lagoon shack, thousands of flamingos standing pink in the shallows. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d2_over.jpg` | Seaside colonial town — Pastel German colonial facades, palm-lined promenade, sea fog rolling in at four o'clock. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d3_start.jpg` | Out on the salt road — A road made of salt and gypsum, sea on the left, dunes on the right, fog between. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d3_food.jpg` | Coastal bakery stop — Apple strudel and strong coffee in a fishing village — a century-old German baking habit that never left. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d3_sight.jpg` | Cape fur seal colony — A hundred thousand seals on one headland: the noise, the smell and the sheer churn of it. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d3_view.jpg` | Shipwreck on the strand — A rusting hull half-swallowed by sand, the reason this coast earned its name. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d3_over.jpg` | Desert camp behind the dunes — Wind-scoured camp behind the first dune line; jackal tracks past the tent by morning. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d4_start.jpg` | Turning inland — The fog lifts within twenty minutes and the temperature climbs twenty degrees. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d4_sight.jpg` | Ancient rock engravings — Thousands of animals chipped into red sandstone by hunters six thousand years ago. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d4_view.jpg` | Desert-adapted elephants — A breeding herd moving down a dry riverbed, broad feet spread for sand, sixty kilometres between drinks. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d4_food.jpg` | Three-legged pot supper — Lamb, root vegetables and red wine left to collapse for five hours in a cast-iron pot over coals. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d4_over.jpg` | Camp among the boulders — Rooms built into a jumble of granite boulders, each one facing its own slice of valley. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d5_start.jpg` | North to the park gate — Mopane scrub thickens, the road reddens, and the first giraffe appears at the fence line. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d5_view.jpg` | The salt pan edge — A white nothing to the horizon, heat-shimmer turning distant zebra into floating smudges. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d5_sight.jpg` | Floodlit waterhole — Elephant, rhino and lion take turns at the same water through the night; you just sit still and let it come. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d5_food.jpg` | Braai under the thorn trees — Game fillet and boerewors over hardwood coals, dust settling, the pan glowing pink behind. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d5_finish.jpg` | Journey's end · the waterhole — Last night: a chair, a cold beer, and whatever chooses to walk out of the dark. Wide closing shot with a sense of arrival and completion, golden light. |

---

**Total: 104 photos across 4 journeys.**

Suggested order — do one journey per overnight run so a bad style lock costs one set,
not four. Generate, then re-run the builder and check the map before starting the next.
