## 2026-08-07 (later) — STAYS-SHOWCASE-1 completed + ZA 4-LAYER MAP PILOT (David: "please ship")

Supersedes the "NOT DONE, deliberately" items in the STAYS-SHOWCASE-1 entry above — David gave
the nod for the card swap and asked for the map pilot completed, so both landed in this release.

**Phone cards (3).** `phone_stay_thatch/jacaranda/marula.jpg`, 352x728, 57-75KB, built from each
property's hero and matched to the 28 Jul card design (navy frame, notch, status bar, gold
"TrustSquare · Stays" band, photo, suburb chip, title/price/trust badge, navy CTA). CTA reads
"Request Introduction · 1T" — the fixed intro price, not a booking. Placed in
`CityLauncher/emailer/assets/`; registered in `inline_images.py` (17 entries; all three asset files
asserted present on disk). They ship on the MEDIA lane (`media_push.bat` step 3/7), never the code lane.

**The Stays email track's fake cards are gone.** `adventures_accommodation_outreach.html` lines
189-279 replaced (8,409 chars): out went three MOCKUP phone cards depicting listings that do not
exist ("Waterberg Private Lodge", "Boutique Hotel · Cape Town", "Sossusvlei Desert Lodge") with
hand-typed prices in a format the app itself rejects; and with them THREE HOTLINKS TO
images.unsplash.com, which fetched a third party at open time and leaked each recipient's IP.
In went the sibling pattern: three real cards, two anchors each, six bare `https://trustsquare.co`
hrefs matching `flip_showcase_hrefs.py`'s exact BARE constant. Asserted after the edit: 0 unsplash,
0 mockup listings, 3 card images, 6 bare hrefs, balanced table/td tags, intro CTA intact.
The Stays track now has the same 3 showcase cards as its three siblings — the 0-vs-3 gap David
caught on 2 Aug is closed.

**ZA 4-layer map pilot — `adventures_za_map.html` (162KB), the canon-correct ZA filename.**
Built from `ADVENTURES_FULLMAP_CONCEPT.html`, the design David approved 5 Aug, reusing its INLINED
Leaflet 1.9 (CSS + JS) verbatim. Four independently-switchable layers with colour-dotted checkboxes
top-right, exactly as the concept specifies: ROUTE (4 driving pins + dashed polyline, blue),
HERITAGE (2 sites, gold), STAYS (the 3 new B&Bs, green), PARTNERS (2 referrals, purple).
Plus the legend, the geolocation "My location" control, and `geo:` navigate links that work on a
phone. Verified by headless render: 11 pins, 4 layer switches, correct legend, all four popup
types checked.
- RG-0025 held by construction and asserted in the build: the ONLY `<script src>` on the page is
  `/static/ts_report.js` (our own tester-fault widget, per RG-0030). Build refuses on any of
  unpkg / tp-em.com / jsdelivr / googleapis. Tiles are plain OSM.
- INTROS ARE 1T. The stays popup button reads "Request introduction · 1T" and the build asserts
  the string "20T" appears nowhere.
- Partner pins are INERT (`<span>`, no href) and labelled "(pending)" — Travelpayouts' tours review
  was declined 5 Aug. When it passes they become plain affiliate LINKS; never a script.
- Listing deep links: `STAY_IDS` at the top of the file is `{thatch:null, jacaranda:null, marula:null}`
  because ids are assigned by migration 009 at deploy time. Until they are set, each stay button
  falls back to the Stays category screen — a real destination, never a dead link. Harvest the three
  ids from the deploy log and set them; that one edit is the only thing the file still wants.
- Added to `ops/autodeploy/deploy_manifest.txt` -> `static/adventures_za_map.html` (47 rows now;
  every manifest source verified to exist). NOT yet pointed at from `ADV_COUNTRY_MAP.ZA`: that
  would replace the Big Five reserve map on the Dinokeng super listings, which is a product call,
  not a pilot step. The map is live and linkable at `/static/adventures_za_map.html`, and static
  maps bypass the pre-launch gate, so it can be opened cold.

**Found, not fixed (no ledger change during a ship): RG-0011 is a false green.** Its regex is
`file:'adventures_([a-z0-9]+)_map\.html'` — requiring the closing quote immediately after `.html`.
Every real entry in `ADV_COUNTRY_MAP` carries a `?v=` cache-buster inside the quotes, so the regex
matches NOTHING and the check has been passing vacuously. It therefore never caught the two canon
debts it was written for (`GB` -> `adventures_uk_map.html`, `ZA` -> `adventures_reserve_map.html`).
Filed for the daily watch; fixing the regex will turn those two red, which is correct but is a
deliberate decision, not a mid-ship surprise.

Pre-deploy scan: verdict **ok**. Cost model impact: none.
