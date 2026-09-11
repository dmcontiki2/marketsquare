## 2026-09-09 — Home Help BOT, second pass: real room photos, and place understanding fixed at class level

David on the first prototype: *"the photos can again be the AI generated photos we have for the
current services, no none photos please. And the AI did not understand Moreleta Park, written or
spoken."* Both fixed the same session, verified in a rendered browser.

**Photos.** The first pass drew four SVG scenes — wrong, we own a real AI photo library. First
correction used `static/super/` (the electrician and garden photos): right library, wrong trade.
The answer was in **`assets/super/`**: five of our own photographs of South African rooms — a lodge
room made up at sunset, a bedroom, a bathroom, a lounge, a kitchen. Every one is a room AFTER it has
been done, which reframes the product: **a housekeeper does not sell the cleaning, she sells the
room afterwards.** Embedded as data URIs; no network needed, nothing ever blank. Nothing to generate
and nothing to pay for — the Higgsfield prompts stay recorded but are off the path.

**RUL-114 — no listing publishes without a photograph.** David's "no none photos" closes the hole
Claude flagged on the Sell It BOT on 7 Sep: `_import_quality_score()` lets a listing with zero
photos clear the 50-point bar at 60/100. One photo is now a floor, not ten points. Built into the
BOT (button reads "One photo first" and stays disabled at 60/100). Class ruling — every category,
every BOT, and the publish gate itself. Live gate NOT moved in launch month.

**Place understanding — three defects, not one.** Reproduced: (a) the suburb was stored but never
said back, so it looked ignored; (b) a hard list of 15 suburbs meant Mabopane, Midrand and
Olievenhoutbosch failed silently; (c) exact matching meant a spoken "Morelia Park" failed. Fixed at
class level: the list is now only a spelling aid, anything after stay in / live in / work in / from
/ near is accepted whether known or not, a near-miss is snapped to the closest known name by edit
distance, the verb decides home-vs-travels-to, the bare name on its own works, and a place must sit
behind a preposition (without that "I work FOR Mrs van Wyk" made a person into a suburb). It now
says the name back. Nine cases pass, written and spoken-style.

**Finding worth more than the bug: `assets/suburbs_seed.json` has no townships.** 119 suburbs across
twelve cities — Arcadia, Brooklyn, Waterkloof, Centurion — but not Mamelodi, Soshanguve, Mabopane,
Tembisa, Khayelitsha, Umlazi, Chatsworth, Mdantsane. **The seed lists where the work is, not where
she lives**, so every housekeeper on the platform would have hit it. The prototype carries the
townships in its own list; the real fix is the seed file, which search and CityLauncher also read.
Flagged, not changed — launch month.

Files: `genie/bots/homehelp/BOT_HOMEHELP.html`, `genie/bots/README.md` (SECOND PASS section),
`RULINGS.md` (RUL-114). Still design only — nothing wired, no flag, no deploy manifest line.
