# Higgsfield Regen Queue — from Launch-Readiness Audit (21 Jul 2026)
Model: Nano Banana Pro · 3:2 · house style: SA golden-hour, navy/amber accents.
Every prompt ends with: "Absolutely no text, letters, numbers or writing anywhere in the image."
Use the REFERENCE button with the named anchor image so the item stays identical.

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
