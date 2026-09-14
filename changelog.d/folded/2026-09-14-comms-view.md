## 2026-09-14 — COMMS-VIEW-1: the Comms tab, and what it found on the way in (CATPRIO-2, RG-0368)

David: *"the ops dashboard is still lagging... what visibility do I have on the buzz and comms,
status, impact, some form of metrics."* Building the panel meant measuring the lanes first, and
the measurement found a real fault.

**What was actually wrong with outreach.** The nightly wave had NOT stopped — it ran at 00:10 and
sent 87. But it has decayed: 398 on 5 Sep to 87 on 13 Sep, and it had narrowed to ONE category in
THREE US states while 3,941 never-contacted people sat in the database. Probed, not guessed:

- **1,354** are `teachers_trainers`, held on purpose by PERSON-ONLY-1 — a list of schools, upheld
  twice by measurement. Correct, untouched.
- **718** were stranded by CATPRIO-1: their category was in `agency_categories` but in no city's
  `category_priority`, so no wave could ever reach them. Estate Agents 288, Collector Shops 98,
  Tutor Institutions 87, Car Dealers 86, Service Companies 66, Travel Agencies 58, Tour Operators 35.
- Most of the rest are held by SOURCE-QUALITY-1 because their source bounces above 5%.

**CATPRIO-2 — priority orders the ladder, it never excludes.** `city_categories()` now appends the
remaining allowed categories after the city's priority head. Exclusion keeps its own two mechanisms
(`blocked_categories` and the source-quality gate) untouched. Cities with anyone sendable went
**3 → 9** and the sendable pool **659 → 724**, putting Pretoria, Johannesburg, Cape Town, Durban,
Port Elizabeth and Bloemfontein back on a ladder that had gone all-US. The modest gain is itself the
finding: the binding constraint is address QUALITY, not plumbing. **RG-0368 LOCKED** — this is the
fifth instance of a fault class four previous fixes each closed by typing one more name into one
more list.

**The number that was missing entirely: runway.** `scripts/publish_sendable.py` now measures what
every guard would actually accept and publishes it to the dashboard; step [3d] of the nightly wave
runs it. First reading: **724 sendable, 9 of 95 cities, 131/night, 5 nights left.** A send count
falling to zero and a supply falling to zero look identical from outside and need opposite responses.

**The panel.** New `/dashboard/comms` endpoint (admin-gated) and a Comms tab. Two lanes, each with
its own validated hue *and* its own written label: Buzz `#2E93D9`, Outreach `#C98420` — checked with
the dataviz validator against this page's `#0b0d10` surface (lightness band, chroma, CVD ΔE 24.6
protan, normal-vision ΔE 27.4, contrast — all pass). Green and red stay STATUS and are never a lane
hue. Buzz shows connections, both/one switch on, closed, buzzes over 24h/7d/all, and the delivery
split — push vs email fallback vs reached nobody. Outreach shows runway with a spoken verdict,
14 days of sends as bars, bounce rate, opens, onboarded and published. Every metric carries its own
`measured` flag: unmeasured paints grey and says **NOT MEASURED**, never a zero.

**On the AI in the loop, plainly:** `wave_runner` passes `--no-ai` by design (zero API cost,
deterministic titles) and the maintenance agent runs in SHADOW with its kill switch off, so it can
observe but not act. That is why nothing has been measuring and improving the letters — it was
built to watch, not to change.
