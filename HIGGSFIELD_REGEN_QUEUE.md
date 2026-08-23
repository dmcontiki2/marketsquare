# Higgsfield Regen Queue — from Launch-Readiness Audit (21 Jul 2026)
Model: Nano Banana Pro · 3:2 · house style: SA golden-hour, navy/amber accents.
Every prompt ends with: "Absolutely no text, letters, numbers or writing anywhere in the image."
Use the REFERENCE button with the named anchor image so the item stays identical.
SWAP RULE (learned 15 Aug, VERSIONED-PHOTO-1): never swap same-filename — /static/ ships
immutable 1-year cache headers, so clients keep the old photo forever. Save the replacement
under a NEW versioned name (…_v2.jpg) and update EVERY store the app reads — ALL THREE:
(1) photo_urls JSON, (2) the [photos:...] prefix inside description (the FEA viewer reads THIS),
(3) thumb_url/medium_url if the swapped photo is the thumb. Then purge. VERIFY AT THE USER-VISIBLE
LAYER — open the listing the way a user does; a fix verified only at origin is not verified.
PARITY RULE (SO-2, 15 Aug): every prompt with any person carries "clean, well-kept workwear,
nobody identifiable, no face, no bare skin" — never one person neat and another dirty anywhere
in the app. Prefer hands-and-tool framing.

## 0. DONE 15 Aug 2026 — Electrician second shot (replaces sup_svctech_2_cover.jpg) · 2 credits · FAULT TS-0034 / LIST-003
**RUN COMPLETE 15 Aug 2026 ~14:30 — render generated, swapped live, hash-verified, CDN purged (see TS-0034 fix_note). No further action on item 0.**
Reference: sup_svctech_3_toolkit.jpg (same kit, NOT the DB-board scene — that is the duplicate
being removed). Prompt: "South African electrician in navy work overalls and beige leather
gloves installing a modern white light switch on a warm cream plaster wall, screwdriver in
hand, cable ends neatly stripped, golden-hour light through a nearby window, no face visible,
photorealistic trade photography. Absolutely no text, letters, numbers or writing anywhere in
the image."  → save as sup_svctech_2_cover.jpg (backup old first; same filename = no DB change,
listing 267 photo_urls untouched). Then scp + chmod 644 + purge cache, machine-verify the three
photos are distinct (perceptual hash), set TS-0034 → fixed.

## 1. HIGH — Tutor whiteboard (replaces sup_tutors_1_main.jpg) · 2 credits
Reference: sup_tutors_2_desk.jpg (same room). Prompt: "Bright tutoring study room in a South
African home, large whiteboard on the wall photographed at a steep oblique angle so the
handwriting is softly out of focus and unreadable, warm golden-hour light through a window with
a blooming purple jacaranda outside, tidy desk with laptop and mathematics textbooks, two beige
chairs, photorealistic interior photography. Absolutely no text, letters, numbers or writing
anywhere in the image."  → save as sup_tutors_1_main.jpg (backup old first)

## 2. MEDIUM — Property garden shot (replaces sup_property_6_garden.jpg) · 2 credits
Reference: sup_property_1_main.jpg (THE house). Prompt: "Rear garden of the SAME white
double-storey house with stone-clad feature wall and timber accents, large manicured lawn,
built-in braai area, mature blooming purple jacaranda, NO swimming pool visible in this view,
golden-hour light, Pretoria hills behind, photorealistic real-estate photography. Absolutely no
text anywhere in the image."  → save as sup_property_6_garden.jpg

## 3. MEDIUM — Sideboard open shot (restores 3-photo set on id 272) · 2 credits
Reference: sup_lm_1_main.jpg (THE 4-door sideboard). Prompt: "The SAME 1960s teak sideboard
with four doors and polished brass bow handles, both centre doors open revealing interior
shelves, warm plaster room with large window, oak floor, photorealistic furniture photography.
Absolutely no text anywhere in the image."  → save as sup_lm_3_open.jpg, then re-add
/static/super/sup_lm_3_open.jpg to listing 272 photo_urls + [photos:] prefix and restore the
description phrase about interior shelving.

## 4. LOW — Top six 3-photo sets to 5 photos (~24 credits)
Sets: tutors, svctech, svccas, advexp, advacc, collect — two extra angles each, reference-chained
to each set's main. Purpose: literal 100 listing-quality on every exemplar.

After any regen: scp to /var/www/marketsquare/static/super/ + chmod 644 + purge cache.


## 5. MEDIUM — Study & Work Abroad example photos (6 images, ~12 credits) · SAW-2, RUL-043
Save all to assets/studywork/ (new media lane section [1b] in media_push.bat -> /static/studywork/).
Representation parity rule (RUL-018/SO-2) applies: clean, well-kept workwear, identical standard
across every image; prefer wide or hands-and-task framing; absolutely no text in any image.
1. "Young crew member in crisp white cruise-line service uniform setting a table in an elegant
   ship dining room, ocean through the windows, photorealistic" -> sw_cruise_1.jpg
2. "Large modern cruise ship leaving harbour at golden hour, aerial three-quarter view,
   photorealistic" -> sw_cruise_2.jpg
3. "Wooden canoes on a calm New England summer-camp lake at dawn, pine forest, camp cabins on
   the shore, photorealistic" -> sw_camp_1.jpg
4. "Ski-resort base village in Colorado in fresh snow, lifts running, staff member in neat resort
   jacket clearing the walkway, wide shot, photorealistic" -> sw_h2b_1.jpg
5. "Sunlit American suburban family kitchen, young au pair and host parent preparing lunchboxes
   together, faces turned away, warm documentary style, photorealistic" -> sw_aupair_1.jpg
6. "Moraine Lake, Banff, Canada, turquoise water and peaks at sunrise, no people, photorealistic"
   -> sw_canada_1.jpg  (used on the honest 'CLOSED for SA passports' card)
After generation: run media_push.bat (section 1b ships them, hash-gated).

## 6. HIGH — Dossier persona-journey photos (12 images, ~24 credits) · SAW-4, David 23 Aug
Model Nano Banana Pro, aspect 3:2, higgsfield.ai/ai/image. Downloads land in MarketSquare\_incoming
(GRANT-KILL-1); claim = mv to assets/studywork/ with the exact names below, then
`python3 scripts/build_dossier_pdf.py` re-embeds them and media_push.bat [1b] ships them.
PERSONA CONSISTENCY: generate image 1 of each set first, then reference-chain ("the SAME young
woman/man") for the rest. Parity rule RUL-018/SO-2: clean, well-kept clothing, identical dignity
standard, faces natural or angled away; absolutely no text anywhere in any image.

LERATO SET — "a young South African woman, 18, natural hair, smart navy jacket over white tee":
1. "...at an airport departures hall with a silver suitcase and boarding pass in hand, looking up at
   the departures board, warm morning light, photorealistic" -> sw_hu_1_airport.jpg
2. "Aerial view through an aircraft window over Budapest at golden hour, the Danube curving past the
   Parliament building far below, wingtip in frame, photorealistic" -> sw_hu_2_aerial.jpg
3. "The SAME young woman arriving at a grand European university entrance with her suitcase, autumn
   trees, morning light, seen from behind at three-quarter angle, photorealistic" -> sw_hu_3_arrival.jpg
4. "Historic European university courtyard with students crossing between lectures, autumn morning,
   warm stone facades, photorealistic" -> sw_hu_4_campus.jpg
5. "Budapest Chain Bridge and Parliament across the Danube at dusk, lamps just lit, seen from the
   embankment, photorealistic" -> sw_hu_5_city.jpg
6. "Interior of Budapest Great Market Hall, produce stalls under the iron roof, morning shoppers,
   photorealistic" -> sw_hu_6_life.jpg

PIETER SET — "a young South African man, early twenties, short beard, clean olive work shirt":
7. "...at an airport departures hall with a canvas duffel bag, work gloves tucked in the side pocket,
   looking at the departures board, photorealistic" -> sw_us_1_airport.jpg
8. "Aerial view through an aircraft window over the American Midwest, a vast quilt of green and gold
   crop circles and section-line roads, late afternoon, photorealistic" -> sw_us_2_aerial.jpg
9. "The SAME young man greeted with a handshake at a farm gate by an older farmer in a clean plaid
   shirt, white pickup truck behind, both faces angled away, golden hour, photorealistic" -> sw_us_3_arrival.jpg
10. "A modern green combine harvesting a vast cornfield at golden hour, dust glowing, flat horizon,
    photorealistic" -> sw_us_4_farm.jpg
11. "Small American Midwest town main street with a tall white grain elevator at the end of the
    street, pickup trucks, summer evening, photorealistic" -> sw_us_5_town.jpg
12. "A farmstead porch at dusk, work boots by the door, distant silos against an orange sky,
    photorealistic" -> sw_us_6_life.jpg

MAP SNAPSHOTS (no generation - Chrome screenshots): open /static/studywork_hu_map.html and
_us_map.html (or the local files), all layers on, screenshot -> sw_hu_mapshot.jpg / sw_us_mapshot.jpg
into assets/studywork/, rebuild PDFs.
