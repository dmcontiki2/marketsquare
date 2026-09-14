## 2026-09-13 — The coaching spoke with a housekeeper's voice in every category

David, testing Collectors on his phone, 13 Sep 2026: *"why is 'say which area you work in'
applicable here? I would rather expect card collectors type relationships"* — and a second
question about the price on a collectible.

### The area question was wrong words, not a wrong field

The FIELD is right: the server scores suburb/area 4 points on every category, and the shelf fills
local-first (RUL-118), so a listing with no area cannot be placed in a band at all. What was wrong
was one hardcoded housekeeper sentence wearing all eight categories' clothes. Now each category
asks in its own words — *"Say where it can be collected"* for Collectors, *"Say where the car can
be seen"* for Cars, *"Say where the trip starts"* for Adventures. The same fault was in the trust
gate line, which told a coin collector her score opens *"when one employer confirms you"*; it now
reads *"when somebody outside vouches for you"*, which is what RUL-115 actually says.

### The collector relationships he expected DO exist — on the other half of RS

They were invisible because they are not listing quality. Grading partners, third-party
authentication certificates, provenance documents and association membership are all in the VEL
credential catalogue in `bea_main.py` and they raise the **TRUST** score. So the draft screen now
carries one small block, taken verbatim from that catalogue — names and points are the ladder's
own, nothing invented — saying plainly that these raise TS rather than LS, and that they are added
once and count on every listing afterwards.

Collectors: authentication certificate **+8**, provenance **+8**, association membership **+3**.
Also wired for Cars, Tutors, Housekeeping, Services and Adventures.

**Property and Local Market are deliberately left out.** Their top catalogue entries are
PPRA/EAAB registration and named association office-bearer roles — agent and committee
credentials, not something a private seller listing one house or one batch of jam can hold. Telling
them to get those would be worse than silence. **This is a real gap in the private-seller lane of
the ladder and it is David's to rule on, not Claude's to paper over.**

### The price is an asking price, and for collectibles we can say more for free

Every draft now carries one line: *"This is your asking price — buyers see it as asked, not as a
valuation."* For Collectors it says more, because the app already has the data: Scryfall (cards),
Numista (coins) and BrickLink (LEGO) are all marked live and **unpaid** in `ai_service_tiers.py`,
and `bea_main.py` already resolves `scryfall_id` at listing creation. So the line tells the lister
a verified market price can be looked up from free public sources *and that it never changes what
they asked*. No new cost, no new complexity, no new tap.
