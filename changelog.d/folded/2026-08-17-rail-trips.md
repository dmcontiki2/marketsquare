## 2026-08-17 — Three Great Rail Journeys built (the c2c comparables) + trips as PRODUCTS
David's clarified ask executed in full: the trips are 80% maps no more — each carries the
product. NEW tours (generator specs, ~200 KB each, placeholder tiles pending a photo
session): usrail "The Great American Crossing" (Zephyr route, 5 legs, $6,900pp),
gbrail "The Great British Rail Journey" (London→Mallaig incl. Jacobite finale, 4 legs,
£4,450pp), aurail "The Ghan — Ocean to Ocean" (4 legs, A$5,900pp). Each has:
TRUE-PRICE line in the route bar (real benchmarks: Zephyr ±$150 coach/±$1,100 roomette,
luxury ±$6,000; scheduled GB ±£420 vs Royal Scotsman ±£3,750/2n; Ghan Gold ±A$3,300 /
Platinum ±A$7,500 — all ±, "confirm with agency" per travel canon), 3 priced excursions
in ADV_TOUR_EXTENSIONS (Yosemite/Glenwood/Napa · Royal-Scotsman-night/Skye/Castle ·
Uluru/Nitmiluk/Kakadu), benchmark listings via seed_super_global (COUNTRIES+COPY rows,
tour-stamp loop generalized from the c2c hardcode), ADV_TOUR_MAP entries, corridor-
filtered HERITAGE layers from wonders.json (GB 6 sites, US 3, AU Kakadu+Uluru).
ALSO FIXED (David's catch): the three DAY demos had empty heritage layers — now carry
Yellowstone / Stonehenge / Daintree cards. Listing photos staged to assets/super via
the media lane (sup_{usrail,gbrail,aurail}_*). Cost model impact: none — static pages +
idempotent seed rows.
