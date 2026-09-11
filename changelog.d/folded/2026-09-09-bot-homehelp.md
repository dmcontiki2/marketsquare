## 2026-09-09 — BOT #3 Home Help: housekeeping registration, built as a working prototype

David's direction, 9 Sep 2026: a click, register a service, get listed — for the South African
house cleaning market. A green circle with a rotating photo of a room being cleaned; she talks,
gives the minimum, and is listed; she sends her employer a link so they can book her; she marks
her open days on a weekly schedule; her area is visible.

**Built:** `genie/bots/homehelp/BOT_HOMEHELP.html` + `homehelp.webmanifest`.
Design only — nothing wired, no flag, no line in `ops/autodeploy/deploy_manifest.txt`, not
launch scope. Same footing as BOT #1 Collector and BOT #2 Sell It.

**PROBED live before building** (`GET /listings?category=services`, 9 Sep 2026): the entire
Services category is two seeded listings nationwide — an electrician and a garden service, both
Pretoria, both trust 85. No cleaner, housekeeper, laundry or ironing listing exists. Against
831,000 domestic workers employed in South Africa (Stats SA QLFS Q2 2026, down from ~1,000,000
in Q4 2019).

**What the prototype does, verified in a rendered browser end to end:**
- The green circle (`#16A97C`) with four drawn placeholder scenes, random start, rotating every 5s.
- Spoken registration in en-ZA / af-ZA / zu-ZA using the phone's own free recognition.
- The REAL `_import_quality_score()` services branch: trade 25, 15-word description 25, price 6,
  suburb 4, photos 10+8. She reaches 60/100 on four spoken answers and no photo — because the BOT
  writes the description for her.
- One sentence carrying both states ("I work for Mrs van Wyk Monday and Tuesday, and I am free
  Wednesday and Friday") parses to Mon/Tue TAKEN, Wed/Fri OPEN.
- Employer link: confirmation lifts trust 38 → 85; the existing employer books her FREE (nothing
  to introduce); a stranger booking the same open day pays 1 Tuppence. Nothing but Tuppence
  through the till — model-correct.
- Wage floor: NMW R30.23/ordinary hour from 1 Mar 2026 applies to domestic workers; the BOT does
  the arithmetic aloud and REFUSES a rate below it (R150/day refused, R242 offered).

**Gaps found in the app, flagged not changed:** service listings have no `open_days` and no
`serves_suburbs`, so a recurring free day and a travel-to area cannot be stored, scored or
searched — and "housekeeping, Menlyn, Wednesday" is the only search anyone looking for a cleaner
runs. Schema + search filter, so not in launch month.

**Guard proposed, built into the prototype:** until one employer confirmation or an ID check
lands, only people she has sent her own link to can contact her. Highest-trust transaction on the
platform; it protects the buyer and it protects her.

**Decisions taken (RUL-037):** jade `#16A97C` for Home Help, Sell It moves to TrustSquare gold
when built (no icons exist yet). The circle lives both as the BOT's home-screen icon and as one
green circle in the app's Services category.

**Reserved to David:** whether housekeeping goes ahead of Collector and Sell It in the build order.
Claude's answer is yes — it is the only one of the three whose supply already exists, already has a
phone, and arrives with somebody willing to vouch for her.
