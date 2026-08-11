# SUPER-AFRICA-1 — Expansion Research Canon
*Started 10 Aug 2026 from David's research (Google/State Dept screenshots) + session data pulls. Add to this file as more arrives ("there will be more" — David). This is the reference the ZW/AO/EG/NA/MZ/BW replication phase reads FIRST.*

## 1. Safety / travel advisories (US State Dept, as screenshotted 10 Aug 2026)
| Country | Level | Notes that shape our journeys & sequencing |
|---|---|---|
| Namibia | Low risk | Ideal self-drive — matches our existing NA journey. Petty theft in Windhoek only. |
| Botswana | Low risk | Most stable safari destination — matches existing BW journey. |
| Zambia | Low risk | Peaceful; guided Vic Falls tours run smoothly. **NOT currently in our 7-country list — David's searches include Zambia (not only Zimbabwe). Vic Falls straddles ZM/ZW. SCOPE DECISION = DAVID'S: add ZM, or serve Vic Falls from the ZW side, or both.** |
| Egypt | L2 | Main tourist corridors (Cairo, Luxor, Nile, Giza) heavily protected — our C2C leg and future EG journey stay in corridors. Avoid N/M Sinai + Western Desert unless licensed tour. Petty theft/harassment common — copy should steer to guided/agency products (which is our model anyway). |
| ~~Angola~~ | **REMOVED from scope (David, 10 Aug 2026)** — L2 country, Luanda metro L3, rural landmines | Crime, health, unrest, rural landmines. Luanda was our chosen AO city — L3 on the metro argues for sequencing AO LAST and/or an organized-travel-only journey design. Flagged in waves_policy Luanda note. |
| Mozambique | Caution | Coastal/archipelago fine via organized transfers — our MZ journey (Maputo→Bazaruto) is EXACTLY that and stays south. Cabo Delgado (far north) active terrorism threat — never route there. |

**Design rule from the above:** every journey in caution-flagged countries is built agency-first (organized transfers, guided corridors) — which is the introduction model anyway. Say it in the cap line.

## 2. Operator / agency landscape (outreach TARGETS — never advert content, SO-1)
Real operators from David's research — these go into CityLauncher agency pools for the relevant cities, NOT into super-advert copy (supers stay generic so a real operator can claim them):
- **Live the Journey** — rare multi-region: NA + BW + AO 4x4/specialty + vetted EG. Prime outreach target — one operator could claim supers in several of our countries.
- **Amazing Africa** — NA, BW, ZM, MZ + East Africa hubs.
- **Discover Africa Safaris** — custom luxury/mid across NA, BW, ZM, MZ.
- **Wilderness** — high-end conservation camps NA/BW/ZM.
- Pattern: Southern-Africa specialists cover NA/ZM/BW/MZ; EG and AO need niche/custom planners — thinner agency pool, later sequencing.

## 3. Travelpayouts integration (the rules — do not relearn these)
- **RG-0025 (inverted, post-breach 3–4 Aug 2026): NO TP script ever loads on app pages.** Affiliate/monetization is server-side or link-out only. Maps carry TP data as BUILD-TIME text, never a widget.
- Aviasales **Data API** is live (token server-side as TRAVELPAYOUTS_TOKEN + local gitignored `.secrets/tp_token.txt`; partner ID 758984). ZAR native. Empty `{}` = thin route → agency-card fallback, not an error.
- Fares are **indicative cached data** → "confirm with agency" copy (supplier-fallback doctrine). Flat cost only if Duffel refresh is ever added (capped) — no ad-valorem costs, ever.
- Tours programs (GYG/Viator/Booking.com etc.) remain BLOCKED pending re-review (OPEN_LOOPS D10) — do not resubmit unchanged.

## 4. Live fare snapshot — CPT ⇄ NBO return, ZAR (Data API, 10 Aug 2026)
R8,864 (TAAG, 1 stop) · R9,496 (1 stop) · R12,676 (Kenya Airways, 1 stop) · R12,865 · R12,971 · R13,264 (Ethiopian). Cheapest ~R8,900, median ~R12,900. No non-stop in cache this pull. Used on the Kenya map as "indicative return from ~R8,900".

## 5. Flight-bookend pattern (shipped for Kenya, 10 Aug 2026 — reuse for every country)
Journey spec gains Day 1 "Fly in" + final day "Fly home" as `mode:"air"` days (existing template convention — dashed line, ✈️ stat; zero builder changes). Origin airport → gateway airport with 1-2 curve points, fare in the day summary, agency-books-it in the cap. Replication: pull `<origin> ⇄ <gateway>` fares from the Data API at build time, per country.
