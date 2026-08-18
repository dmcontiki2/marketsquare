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

## The Ghan — Ocean to Ocean  (12 photos)

- **photo_dir:** `assets/journey/aurail`
- **output:** `adventures_au_rail_map.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial rail-travel photography, Australia end to end on The Ghan — polished stainless sleeper cars, red-centre desert and ghost gums, Flinders dusk, Top End monsoon green, cinematic warm light, deep navy and warm amber accents (#0c1a2e / #C8873A), shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `l1_start.jpg` | Adelaide Parklands — boarding — Champagne on the platform as a kilometre of silver carriages waits to cross a continent. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l1_view.jpg` | The Flinders Ranges at dusk — Ancient folded mountains turn purple beyond the saltbush as the dining car pours the Barossa. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l1_over.jpg` | First night — into the red — Your cabin made down, the train running steady into the true outback dark — no lights to the horizon. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l2_view.jpg` | Marla — outback sunrise — The train pauses in the darkness; fires are lit beside the track and the desert dawn comes up over breakfast. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l2_over.jpg` | Alice Springs — the red heart — The town in the MacDonnell gap — an afternoon for the Desert Park, a camel ride, or the flight to Uluru. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l2_view2.jpg` | Simpsons Gap — the West Macs — A red cleft in the ranges holding permanent water — rock wallabies on the scree at sundown. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l3_sight.jpg` | Karlu Karlu — the Devils Marbles — Giant granite spheres balanced on the plain — a sacred place of the Warumungu, glowing at first light. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l3_view.jpg` | Nitmiluk Gorge cruise — Off the train at Katherine for a cruise between hundred-metre sandstone walls — freshwater crocs on the banks. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l3_food.jpg` | Dinner crossing the tropics — Barramundi and Territory beef as the light turns green and gold — the desert already a thousand kilometres behind. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l4_view.jpg` | The Adelaide River country — Floodplains, magnetic termite mounds and the big rivers of the Top End sliding past the window. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l4_finish.jpg` | Darwin — ocean to ocean — The line ends at the Timor Sea — sunset on the waterfront, a continent crossed top to bottom. Wide closing shot with a sense of arrival and completion, golden light. |
| `l4_food.jpg` | Stokes Hill Wharf — landfall dinner — Chilli prawns and cold beer over the harbour where the journey ends. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |

---

## Great Barrier Reef Dive & Snorkel  (10 photos)

- **photo_dir:** `assets/journey/aus`
- **output:** `adventures_au_map.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial travel photography, shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `leg1_01.jpg` | Port Douglas · cast off — Morning departure from the marina — a briefing over the water as the mainland drops away and the reef line appears ahead. Wide establishing shot with a clear sense of departure and journey ahead. |
| `leg1_02.jpg` | Agincourt Ribbon Reefs — The outer edge of the Great Barrier Reef — clear ocean water over ribbon reefs that fall away into the deep blue, the base for the day's dives and snorkels. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg2_01.jpg` | Coral gardens — Shallow bommies of staghorn and plate coral in every colour — the classic first snorkel, clownfish guarding their anemones. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg2_02.jpg` | The reef wall — A guided dive down the ribbon-reef wall — sea fans, giant clams and white-tip reef sharks cruising along the drop-off. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `leg2_03.jpg` | Manta cleaning station — A cleaning station where manta rays and turtles hover while cleaner wrasse tend them — one of the reef's great gathering points. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `leg3_01.jpg` | Turtle bommie — Green and hawksbill turtles resting on the coral heads — often calm enough to drift quietly alongside as they rise to breathe. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg3_02.jpg` | The bait ball — A silver river of trevally and fusiliers wheeling over the reef — the whole school turning as one when a mackerel drives through. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg3_03.jpg` | Michaelmas Cay — A tiny sand island on the reef and a protected seabird rookery — thousands of terns and boobies wheeling above the white sand. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg3_04.jpg` | Reef Island Eco-Stay — Where the trip ends — a low-impact island eco-stay of timber and canvas, the reef at the doorstep and no crowds. A generic composite, not a specific resort. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `leg3_05.jpg` | Sundowner over the water — The day's last snorkel, then a cold drink at the water's edge as the reef flat turns gold and the terns come in to roost. Wide closing shot with a sense of arrival and completion, golden light. |

---

## Botswana, water to salt  (32 photos)

- **photo_dir:** `assets/journey/bwa`
- **output:** `adventures_bw_map.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial safari photography, Botswana — Okavango channels, mopane woodland and white salt pan, warm golden-hour light and dust, deep navy and warm amber accents (#0c1a2e / #C8873A), shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `f1_start.jpg` | O.R. Tambo · departure — A prop-heavy departure board and safari duffels on every shoulder — Maun is where the tar ends.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=JNB&destination_iata=MUB" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Wide establishing shot with a clear sense of departure and journey ahead. |
| `f1_view.jpg` | The pans from the window — White salt to the curve of the earth on one side, the green smudge of the delta beginning on the other. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `f1_sight.jpg` | Maun · arrival — Twelve-seaters queuing on the apron like taxis — the busiest bush-plane airport in Africa.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=JNB&destination_iata=MUB" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `f1_over.jpg` | River guesthouse · Maun — A shady stoep above the Thamalakane, fish eagles calling the afternoon through. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
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
| `f2_start.jpg` | Off the salt, back west — The vehicle the only vertical thing for an hour, then the first cattle posts and the smell of rain. Wide establishing shot with a clear sense of departure and journey ahead. |
| `f2_sight.jpg` | Maun · departures — Sand out of the boots, a last look at the bush-plane ballet, boarding for Johannesburg.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=MUB&destination_iata=JNB" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `f2_finish.jpg` | Johannesburg · home — Mokoro-calm in the blood and salt in the camera bag — go siame, Botswana.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=MUB&destination_iata=JNB" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Wide closing shot with a sense of arrival and completion, golden light. |

---

## Cape to Cairo — rail, wings &amp; the Nile  (38 photos)

- **photo_dir:** `assets/journey/c2c`
- **output:** `adventures_c2c_map.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial rail-travel photography, Africa end to end — grand stations, sleeper-car interiors in brass and teak, Karoo, Zambezi, savanna and Nile desert, cinematic warm light, deep navy and warm amber accents (#0c1a2e / #C8873A), shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `l1_start.jpg` | Cape Town · the platform — Table Mountain filling the window, brass, teak and a station clock — the journey starts formally. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l1_food.jpg` | Cape Malay farewell lunch — Spiced mince baked under savoury custard with yellow rice, then syrup-soaked plaited doughnuts with coconut. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l1_view.jpg` | Through the winelands — Whitewashed gables, vineyards in rows, and a wall of blue mountains the train has to find a way through. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l1_sight.jpg` | Victorian halt on the plateau — A perfectly preserved railway village on the empty Karoo — gaslamps, a double-storey verandah, one street. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l1_over.jpg` | First night in the sleeper — Berth made up while you dine; the rhythm of rail joints and a lit lamp somewhere far out on the plain. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l1_bread.jpg` | Roosterkoek at the halt — Griddle bread off the coals at a Victorian siding — split, buttered and eaten hot with apricot jam. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l2_start.jpg` | Dawn on the Karoo — Pink light on flat-topped hills, windmills, sheep, and not one other vehicle. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l2_food.jpg` | Karoo lamb, slow-roasted — Lamb raised on wild aromatic scrub, so the meat arrives pre-seasoned — served pink with pumpkin fritters. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l2_sight.jpg` | The Big Hole — A 200 m crater dug by hand by fifty thousand men with picks and buckets, now filled with green water. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l2_view.jpg` | Highveld grassland — Grass to the horizon in every direction, thunderheads stacking up in the afternoon. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l2_over.jpg` | Second night, rolling north — Dinner in the dining car under lamplight, then the long climb onto the highveld in the dark. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l2_potjie.jpg` | Potjie under the stars — Lamb, potatoes and sweet wine simmered for hours in a three-legged pot beside the line, under a sky thick with stars. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l3_start.jpg` | Jacaranda capital — Purple streets in spring, union buildings on the ridge, and the last big-city platform for a while. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l3_food.jpg` | Biltong & braai on board — Air-dried spiced beef sliced thin as a snack, then flame-grilled steak and coiled farm sausage for dinner. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l3_sight.jpg` | The smoke that thunders — A kilometre-wide curtain dropping 100 m into a gorge; the spray column is visible 50 km away. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l3_view.jpg` | The bridge over the gorge — A 1905 steel arch spanning the chasm — the original dream of this whole railway, and the point it stalled. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l3_over.jpg` | Colonial hotel by the falls — Verandahs, ceiling fans, high tea, warthogs on the lawn and permanent thunder in the background. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l3_bream.jpg` | Zambezi bream by the river — Whole bream off the coals at the water's edge, lemon-buttered, with the spray of the falls drifting over. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l4_start.jpg` | Onto the long line — The famous cross-continental service: two nights, one train, minimal fuss. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l4_view.jpg` | Game from the window — The line runs through a national park — giraffe, elephant and buffalo from the dining-car window at walking pace. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l4_food.jpg` | Grilled meat & maize — Charcoal-grilled goat and beef with stiff maize porridge and a fierce tomato-chilli relish, eaten with hands. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l4_sight.jpg` | Spice port on the ocean — Indian Ocean harbour thick with the smell of clove, cardamom and cinnamon from the islands offshore. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l4_over.jpg` | Harbour-side rooms — Carved doors, a courtyard, call to prayer at dusk and dhows on the water at first light. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l4_chai.jpg` | Chai na mandazi at dawn — Sweet, gingery tea and warm fried dough as the miombo woodland slides past — Tanzania's answer to breakfast in bed. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l5_crater.jpg` | Ngorongoro Crater rim — Sundowners on the lip of the world's largest unbroken caldera, the game grazing two thousand feet below. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l5_migration.jpg` | Serengeti · the Great Migration — A million wildebeest and zebra on the move — often called the greatest show on earth. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l5_gorilla.jpg` | Gorillas of the Volcanoes — One quiet hour with a mountain gorilla family in the bamboo forests of Rwanda. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l5_injera.jpg` | Injera in Addis Ababa — Sour flatbread piled with spiced stews and lentils, eaten by hand from one shared platter. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l5_coffee.jpg` | Coffee, born in Ethiopia — The ceremony: green beans roasted at your feet, pounded, brewed three times — coffee in the country that gave it to the world. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l5_lalibela.jpg` | Lalibela, carved from rock — Eleven medieval churches chiselled straight down into the mountain, still in daily use. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l5_abusimbel.jpg` | Abu Simbel colossi — Ramses II at twenty metres, rescued stone by stone above Lake Nasser. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l6_cruise.jpg` | Casting off at Aswan — Three slow nights on the river — dinner on deck as the palms slide by and the banks turn copper. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l6_sight.jpg` | Temple city at dawn — Avenues of stone rams, hypostyle halls of vast painted columns, cut sharp by early light. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l6_food.jpg` | Rice, lentils & fried onion — The great street dish — rice, lentils and macaroni under spiced tomato sauce, vinegar and crisp onions. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l6_view.jpg` | The green Nile valley — A ribbon of intense green a few kilometres wide with hard desert on both edges — the whole country in one view. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l6_food2.jpg` | Mint tea in sight of the tombs — Sweet mint tea on a rooftop with the three pyramids filling the skyline behind the cups. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l6_start.jpg` | The night sleeper to Cairo — Boarding at dusk with the river turning copper — dinner served in the cabin as the palms slide by. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l6_finish.jpg` | Journey's end · Cairo — Ten thousand kilometres, one continent, and a last look back down the line from the Giza plateau. Wide closing shot with a sense of arrival and completion, golden light. |

---

## Stonehenge & Wessex Heritage Tour  (12 photos)

- **photo_dir:** `assets/journey/gbr`
- **output:** `adventures_gb_map.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial travel photography, shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `leg1_01.jpg` | Stonehenge · the sarsen circle — The most famous prehistoric monument in Europe — a ring of sarsen and bluestone raised on Salisbury Plain around 2500 BC and aligned to the solstice sun. A UNESCO World Heritage Site. Wide establishing shot with a clear sense of departure and journey ahead. |
| `` | The Avenue & Heel Stone — The ceremonial approach the builders walked — a low earthwork running to the outlying Heel Stone, where the midsummer sun rises over the circle. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `` | Durrington Walls & Woodhenge — A vast henge and the builders' village beside it — where the people who raised Stonehenge lived and feasted midwinter. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg2_01.jpg` | Avebury · the great circle — The largest stone circle in the world — so vast a village sits inside it. Older and greater in span than Stonehenge, ringed by a huge Neolithic bank and ditch. UNESCO World Heritage. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `` | Silbury Hill — The tallest prehistoric mound in Europe — 30 m of chalk raised by hand about 4,400 years ago, its purpose still unknown. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg2_03.jpg` | West Kennet Long Barrow — A 5,600-year-old chambered tomb you can still step inside — one of the largest and best-preserved Neolithic burial mounds in Britain. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg2_04.jpg` | Uffington White Horse — A 3,000-year-old chalk-cut horse streaming across the downs — the oldest hill figure in Britain, best read from the ridgeway above. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `leg3_01.jpg` | Old Sarum — The great Iron-Age hillfort that became the first Salisbury — ramparts, a ruined royal castle and the footings of the original cathedral. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg3_02.jpg` | Salisbury Cathedral — Britain's tallest spire at 123 m, and home to one of only four surviving 1215 originals of Magna Carta, in a cathedral close little changed in 800 years. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg3_03.jpg` | Cranborne Chase · downland dusk — A protected chalk landscape of ancient droves and fallow deer — the golden-hour run back, hares in the barley and red kites overhead. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `leg3_04.jpg` | The Country House · your stay — Where the day ends — a Georgian manor of mellow stone, log fires, a walled garden and a long candle-lit table. A generic composite, not a specific hotel. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `leg3_05.jpg` | Slow country morning — Breakfast in the orangery before you set out — local eggs, garden fruit and a pot of proper tea. Wide closing shot with a sense of arrival and completion, golden light. |

---

## The Great British Rail Journey  (12 photos)

- **photo_dir:** `assets/journey/gbrail`
- **output:** `adventures_gb_rail_map.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial rail-travel photography, Britain by train — brass-and-teak Pullman carriages, cathedral-city stone, Northumberland coast, Rannoch Moor mist and a steam viaduct finale, soft northern light, deep navy and warm amber accents (#0c1a2e / #C8873A), shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `l1_start.jpg` | London King's Cross — boarding — Under the great twin arches where the East Coast expresses have left for Scotland since 1852. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l1_sight.jpg` | York Minster & the walls — North Europe's largest Gothic cathedral above medieval streets — an evening walk on the city walls. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l1_over.jpg` | York — railway-hotel night — A grand Victorian railway hotel beside the station — and the National Railway Museum next door for the morning. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l2_sight.jpg` | Durham — cathedral on the rock — The Norman cathedral and castle rise over the Wear — the finest view from any railway in England. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l2_view.jpg` | The Northumberland coast — Castles and cold blue sea — Alnmouth, Bamburgh's outline, Holy Island across the sands. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l2_over.jpg` | Edinburgh — under the Castle — Waverley station sits in the garden valley below the Castle rock — the Old Town rises straight from the platform ends. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l3_food.jpg` | Glasgow — a Highland breakfast — Queen Street station and a proper breakfast before the line turns north along the Clyde. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l3_view.jpg` | Rannoch Moor — the empty miles — The line floats on brushwood across a wilderness no road crosses — deer on the moor, weather rolling in. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l3_over.jpg` | Fort William — beneath Ben Nevis — The Highland junction town under Britain's highest mountain — sleeper carriages idle at the platform. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l4_view.jpg` | Glenfinnan Viaduct — Twenty-one arches curving above the glen with Loch Shiel beyond — steam, whistle and the most famous railway view in the world. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l4_view2.jpg` | The silver sands of Morar — White shell-sand bays and turquoise water — the Hebridean light at the carriage window. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l4_finish.jpg` | Mallaig — journey's end — The rails end at the harbour wall: landed prawns on the quay, the Isle of Skye across the Sound. Wide closing shot with a sense of arrival and completion, golden light. |

---

## Kenya, city to savannah  (32 photos)

- **photo_dir:** `assets/journey/ken`
- **output:** `adventures_ke_map.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial travel photography, shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `d1_start.jpg` | Cape Town International · departure — Table Mountain out the left window as you climb, the Cape Flats falling away — next stop, the equator.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=CPT&destination_iata=NBO" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Wide establishing shot with a clear sense of departure and journey ahead. |
| `d1_view.jpg` | The Rift from seat 23A — The Great Rift's lakes glinting silver below, thunderheads stacked over the escarpments — Africa end to end from ten kilometres up. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d1_sight.jpg` | Jomo Kenyatta International · arrival — Karibu Kenya — a stamp, warm equatorial evening air, and a driver holding a board with your lodge's name.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=CPT&destination_iata=NBO" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d1_over.jpg` | Arrival night · Karen cottage — Lamplight, a pot of chai and the smell of rain on red earth — asleep before the jet lag notices. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d2_start.jpg` | Nairobi · departure — Matatus in full graffiti colour, hawkers with the morning papers, and the park gate twenty minutes from the towers. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d2_sight.jpg` | Nairobi National Park · dawn drive — The only national park on earth inside a capital — black rhino grazing while the city hums on the horizon. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d2_view.jpg` | Karen Blixen Museum — The farmhouse at the foot of the Ngong Hills where 'Out of Africa' began — lawns, verandahs and old coffee ghosts. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d2_food.jpg` | Nyama choma lunch — Goat and beef straight off the grill, cut at the table with kachumbari and ugali — Kenya's great shared meal. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d2_over.jpg` | Coffee-garden cottage · Karen — A stone cottage under old trees in coffee country, log fire lit at seven, colobus monkeys in the canopy at dawn. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d3_start.jpg` | Out of the highlands — Up through eucalyptus and tea-green shambas to the lip of the escarpment. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d3_view.jpg` | Great Rift Valley viewpoint — The floor drops six hundred metres and the valley runs unbroken to the horizon, volcano cones floating in the haze. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d3_sight.jpg` | Lake Naivasha by boat — Fish eagles calling from dead acacias, pelicans in formation, and hippo eyes everywhere in the papyrus shallows. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d3_food.jpg` | Lakeside tilapia lunch — Whole tilapia fried crisp, lemon and chilli, eaten at a plank table with the lake glittering behind. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d3_over.jpg` | Lakeshore tented camp — Canvas under yellow-barked acacias; after dark the hippos come ashore to mow the lawn around the tents. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d4_start.jpg` | Hell's Gate · cycling the gorge — Ride a dirt road between red basalt walls, zebra and warthog trotting alongside — the gorge that inspired a lion king. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d4_sight.jpg` | Geothermal vents & towers — Steam hissing from the rock, a lone volcanic plug rising from the valley floor like a chimney. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d4_food.jpg` | Chai & mandazi · Nakuru — Sweet milky chai and warm mandazi doughnuts at a formica table — the mid-journey ritual of every Kenyan road. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d4_view.jpg` | Lake Nakuru · flamingos & rhino — A soda lake ringed pink at the shallows, white rhino grazing the shoreline meadows below a fever-tree forest. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d4_over.jpg` | Ridge lodge above the lake — Rooms along a cliff line with the whole lake below — baboons on the lawn at six, eagles at eye level all day. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d5_start.jpg` | South through the wheatlands — Big-sky farming country rolling toward Narok, combines raising dust on the horizon. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d5_food.jpg` | Narok market stop — Pyramids of avocados and red onions, shuka cloth snapping in the wind, the last town before the grass takes over. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d5_sight.jpg` | Maasai homestead visit — Red shukas against green grass, beadwork with a meaning for every colour, and a jumping dance you will be invited to lose. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d5_view.jpg` | First game drive · Mara plains — Elephant families in the croton thickets, giraffe on the skyline, and grass to the curve of the earth. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d5_over.jpg` | Tented camp by the river — Lantern-lit canvas above a bend in the river; hippos grumbling below and a lion somewhere north, twice, before sleep. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `d6_start.jpg` | Dawn balloon over the Mara — Lift off in the dark, sunrise from a basket, shadows of hot-air balloons drifting over waking herds. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d6_view.jpg` | Big cats on the hunt — A cheetah using a termite mound as a watchtower; lion cubs in the grass pretending not to be seen. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `d6_sight.jpg` | Mara River crossing — Wildebeest massing at the bank, dust and spray and crocodiles — the migration's great gamble, August to October. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d6_food.jpg` | Bush breakfast on the plains — Eggs and sausages off a tailgate grill, Kenyan AA coffee from an enamel pot, zebra grazing a respectful distance away. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `d6_finish.jpg` | Journey's end · escarpment sundowner — A camp chair on the Oloololo edge, the whole Mara going gold below — asante sana, and one more night of lion song. Wide closing shot with a sense of arrival and completion, golden light. |
| `d7_start.jpg` | Bush airstrip · the Mara — A grass strip mown out of the savannah, a twelve-seater bouncing in, and one last low turn over the herds on climb-out. Wide establishing shot with a clear sense of departure and journey ahead. |
| `d7_sight.jpg` | Nairobi connection — Across town to Jomo Kenyatta, one last plate of nyama choma in the terminal, and the board flips to CAPE TOWN.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=NBO&destination_iata=CPT" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `d7_finish.jpg` | Cape Town · home — Table Mountain rising out the window on approach — asante sana, Kenya; the photos will take weeks to sort.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=NBO&destination_iata=CPT" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Wide closing shot with a sense of arrival and completion, golden light. |

---

## Mozambique, down the coast  (32 photos)

- **photo_dir:** `assets/journey/moz`
- **output:** `adventures_mz_map.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial travel photography, Mozambique Indian Ocean coast — turquoise water, dhow sails, coral-stone and whitewash, bright tropical light with deep navy and warm amber accents (#0c1a2e / #C8873A), shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `f1_start.jpg` | O.R. Tambo · departure — The shortest hop of the lot — barely time for coffee before the descent begins.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=JNB&destination_iata=MPM" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Wide establishing shot with a clear sense of departure and journey ahead. |
| `f1_view.jpg` | The Lebombo range from above — The lowveld patchwork giving way to green hills, then the flat silver of the bay. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `f1_sight.jpg` | Maputo · arrival — Sea air through the terminal doors, Portuguese on the tannoy, prawns already on your mind.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=JNB&destination_iata=MPM" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `f1_over.jpg` | Guesthouse in the old city — A tiled courtyard behind a heavy door, ceiling fans and the evening call of the city. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
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
| `f2_start.jpg` | Across the three-kilometre bridge — Off the stone island on the long low bridge, then baobab country rolling toward Nampula. Wide establishing shot with a clear sense of departure and journey ahead. |
| `f2_sight.jpg` | Nampula · departures — A last pastel de nata in the terminal and sand shaken from every bag.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=APL&destination_iata=JNB" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `f2_finish.jpg` | Johannesburg · home — Salt on your skin and dhow sails in your camera roll — kanimambo, Moçambique.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=APL&destination_iata=JNB" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Wide closing shot with a sense of arrival and completion, golden light. |

---

## Namibia, end to end  (30 photos)

- **photo_dir:** `assets/journey/nam`
- **output:** `adventures_na_map.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial travel photography, Namibia — red Sossusvlei dunes, gravel plains and Atlantic fog, hard clean desert light with long shadows, deep navy and warm amber accents (#0c1a2e / #C8873A), shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `f1_start.jpg` | O.R. Tambo · departure — Boarding for the desert — the highveld falling away, the Kalahari turning apricot below.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=JNB&destination_iata=WDH" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Wide establishing shot with a clear sense of departure and journey ahead. |
| `f1_view.jpg` | The Kalahari from above — Red dune-streets in parallel lines to the horizon, a single farm light every hundred kilometres. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `f1_sight.jpg` | Hosea Kutako · pick up the 4x4 — Heat shimmer on the apron, keys to a kitted twin-cab, two spare wheels and a fridge in the back.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=JNB&destination_iata=WDH" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `f1_over.jpg` | Windhoek · first night — Jacaranda streets and a first braai under a highland sky — the gravel starts tomorrow. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
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
| `f2_start.jpg` | The long road south — Four hundred kilometres of straight gravel and mirage — one last kudu crossing at dusk speed. Wide establishing shot with a clear sense of departure and journey ahead. |
| `f2_sight.jpg` | Hosea Kutako · drop the keys — Dust off the twin-cab, one last biltong stop in the terminal, boarding for Johannesburg.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=WDH&destination_iata=JNB" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `f2_finish.jpg` | Johannesburg · home — Red dust in the tread and ten thousand photos of dunes — tot siens, Namibia.<br><a href="https://www.aviasales.com/?marker=758984&origin_iata=WDH&destination_iata=JNB" target="_blank" rel="noopener nofollow sponsored" style="font-weight:700;">Check live fares ↗</a> <span style="opacity:.7;font-size:11px;">your agency confirms & books</span> Wide closing shot with a sense of arrival and completion, golden light. |

---

## Yellowstone Country Big-Game Safari  (11 photos)

- **photo_dir:** `assets/journey/usa`
- **output:** `adventures_us_map.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial travel photography, shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `leg1_01.jpg` | Lamar Valley · America's Serengeti — Broad glacial grasslands where bison herds graze thousands strong and pronghorn run the flats — the richest wildlife-watching in Yellowstone. Wide establishing shot with a clear sense of departure and journey ahead. |
| `leg1_02.jpg` | Slough Creek · wolf country — Spotting-scope country at first light — the meadows where wolf-watchers gather to follow the Lamar packs and their pups. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg1_03.jpg` | Tower–Roosevelt — Pine ridges and the Tower Fall overlook on the road to the north range — black bear, moose in the willows and elk along the river. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `leg2_01.jpg` | Hayden Valley — Bison, elk and coyote on the Yellowstone River flats, steam drifting from the far bank — one of the best places in the park to glass for grizzly. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg2_02.jpg` | Grizzly overlook — Where the guides glass the tree line at dusk — grizzly and their cubs turning over the meadows above the river. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg2_03.jpg` | Grand Canyon of the Yellowstone — Artist Point over the Lower Falls — a 300 m gorge of yellow and rose volcanic rock that gave the park and its river their name. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg3_01.jpg` | Old Faithful — The most famous geyser on earth — erupting to 55 m roughly every 90 minutes, at the heart of the densest concentration of geysers in the world. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg3_02.jpg` | Grand Prismatic Spring — The largest hot spring in the United States — a 90 m pool ringed in bacterial bands of orange, gold and deep blue. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `leg3_03.jpg` | Willow flats · moose — Wet meadows where moose browse the willows in the low light — the quiet end of the day on the north road. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `leg3_04.jpg` | The Great Lodge · your stay — A timber-and-stone retreat with a great stone hearth, elk over the mantel and a long porch on the pines. A generic composite, not a specific lodge. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `leg3_05.jpg` | Firepit & big sky — Where the day ends — a fire under the Milky Way, the guides' stories of the day's sightings, and the elk bugling in the dark. Wide closing shot with a sense of arrival and completion, golden light. |

---

## The Great American Crossing  (15 photos)

- **photo_dir:** `assets/journey/usrail`
- **output:** `adventures_us_rail_map.html`

### Style block — paste FIRST into every prompt in this journey
> Photorealistic editorial rail-travel photography, the American West by train — stainless-steel double-deck rail cars, observation-lounge glass, Mississippi crossings, Rockies river canyons, high-desert dawn and Sierra snows, cinematic warm light, deep navy and warm amber accents (#0c1a2e / #C8873A), shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.

| File | Prompt (after style block) |
|---|---|
| `l1_start.jpg` | Chicago Union Station — boarding — Beneath the Great Hall's skylight the great western trains still depart — your sleeper waits on the lower level. Wide establishing shot with a clear sense of departure and journey ahead. |
| `l1_view.jpg` | The Mississippi crossing — The train slows onto the high bridge at Burlington — America's river wide and slow beneath the dining car. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l1_over.jpg` | Roomette night — the prairie run — Your first night in the roomette: beds made down while you dine, Nebraska rolling past in the dark. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l2_food.jpg` | Breakfast into Denver Union — Eggs and coffee as the Rockies fill the horizon — Denver's restored Union Station gleams beneath the mountains. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l2_view.jpg` | The Front Range tunnels — The train coils up the wall of the Rockies through thirty tunnels — flatland to alpine in an hour, finishing under the Divide itself. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l2_view2.jpg` | Winter Park & the high parks — Out of the Moffat Tunnel into a bowl of ski country and high meadow — the roof of the route. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l3_view.jpg` | Gore Canyon — the wild Colorado — No road reaches here: whitewater a thousand feet below the window, canyon walls closing to the sky. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l3_over.jpg` | Glenwood Springs — hot-springs stopover — Step off for the night: the world's largest hot-springs pool steams under the mountains a walk from the platform. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l3_food.jpg` | Dinner in the canyon dusk — White tablecloths and canyon light — the dining car's best hour, or a grill on the springs terrace. Close, appetising food photography — shallow depth of field, steam or char visible, hands only if anyone appears, natural setting behind. |
| `l4_view.jpg` | Ruby Canyon at dawn — Red sandstone walls catch first light on the Utah line — river, rock and not a road in sight. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l4_sight.jpg` | Salt Lake City — the midnight call — The Mormon capital glitters against the Wasatch as the train pauses in the small hours. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l4_over.jpg` | Reno — the biggest little stopover — Out of the desert night into Reno's neon — a stopover night before the Sierra day. Warm inviting accommodation shot at dusk or night, lamplight, no people visible or only distant silhouettes. |
| `l5_view.jpg` | Donner Pass — the Sierra crossing — The train hangs on the mountain wall above Donner Lake — the hardest-won miles in American railroading. Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent. |
| `l5_sight.jpg` | Sacramento — gold-rush capital — Down through the gold country to the state capital and the great railway museum beside the tracks. Characterful detail or mid shot of the landmark or subject, strong sense of place. |
| `l5_finish.jpg` | San Francisco Bay — journey's end — The rails end at the water: across the bay, the city on its hills — one continent, coast to coast, behind you. Wide closing shot with a sense of arrival and completion, golden light. |

---

**Total: 236 photos across 11 journeys.**

Suggested order — do one journey per overnight run so a bad style lock costs one set,
not four. Generate, then re-run the builder and check the map before starting the next.
