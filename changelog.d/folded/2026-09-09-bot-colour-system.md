## 2026-09-09 — The BOT colour system: the app's own seven tile colours fail as icons, measured

David: *"i also love the green full phone screen, this can also be done with the other categories,
but different colors for each?"*

Built: `genie/bots/BOT_FAMILY.html` — all seven category BOTs as full colour-washed phone screens,
each carrying a real photograph from `assets/super/`, plus the measurement behind the palette.
Eight webmanifests written to `genie/bots/*/`. Design only, nothing deployed.

**The colours were already decided** — `BRAND_ASSETS.md` carries seven app tile colours from the
`CATS` config. Reused rather than re-invented. But as ICONS they fail, and it is measurable
(CIEDE2000; under ~20 too close for two icons, under 10 the same colour to the eye):

- **6 of 21 pairs collide.** Tutors vs LocalMarket **ΔE 6.1**; Tutors vs Adventures 6.7; Adventures
  vs LocalMarket 11.1; Property vs Cars 11.3. Three of the seven are green, two are near-black navy.
- Lightness L* 9–37 across all seven, so on a dark home screen they are seven dark squares.

**The sibling palette** keeps the hue each category already owns (hues come from the explainer
video's pastel set, David's own pick) and pulls it to icon strength: Property #2E86E0, Cars #5B4BD6,
Tutors #4FA83F, Services #B4441F, Collectors #C98A2E, Adventures #12A5A5, LocalMarket #D8447E.
**0 of 21 pairs collide; closest pair ΔE 22.8.** The app tiles are unchanged — this is a second
palette for icons and BOT screens only.

**The rule, recorded in BRAND_ASSETS.md so no BOT colour is argued about again:** hue = the category
(canon, never taste); shade = the individual BOT, a trade inside a category taking a lighter or
deeper shade of its family and never a hue of its own; ring = the family hue on a sub-trade BOT.

**One thing reserved to David.** Home Help is a Services BOT, so the system puts it at clay #C96B4A
(ΔE 12.0 from its Services parent — intended family resemblance — and 18.8 from its nearest
outsider). His jade #16A97C measures ΔE 13.4 from Tutors and 15.0 from Adventures, two *other
categories*, so on a home screen it is a third green. The board toggles between the two and shows
the numbers. Until he rules, the prototype stays jade.

Files: `genie/bots/BOT_FAMILY.html`, `genie/bots/{property,cars,tutors,services,collectors,adventures,localmarket}/*.webmanifest`,
`BRAND_ASSETS.md` (BOT icon palette section), `genie/bots/README.md` (FOURTH PASS).
