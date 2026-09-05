## 2026-09-05 — five questions, three of them "no" (GLOBAL-REACH-1, CLUB-LANE-1, WAVE-CITIES-DISCOVER-1, COUNTRY-NAME-ALIAS-1)

David asked whether the goal-driven task is actually working: are the teachers and the
clubs/unions templates in the waves, are the addresses identified globally and not just
locally, does the app still work, does the plan adapt. Probed all five. **Three were no.**

### The fault behind all of them

Every gap was **a list that did not match another list, failing silently.** Nothing went red,
because nothing asserted it — the wave simply never mentioned the missing people, and an
absent line reads like an absent problem.

- **CLUB-LANE-1.** `sports_club_outreach.html`, the federation letter and `club_reader.py`
  existed; 577 real club contacts had been harvested into `club_lists/` on 4 Sep. There was
  **no importer, no 'Sports Clubs' row in the prospect table, and the category was in neither
  `agency_categories` nor any city's priority list.** Two days of work that could not reach one
  person. Built `scripts/club_import.py` (host-side only — the 31 Aug SQLite ban), made the
  category drawable in 43 cities, and queued the import. Deliberately NOT person-only: a club is
  an organisation reached through its committee (RUL-059), so the desk guards must not fire.
- **WAVE-CITIES-DISCOVER-1.** `launch_day_wave.bat` named 14 cities in its own text while the
  policy held 31. Los Angeles, San Jose, Austin, Houston, San Diego, Phoenix and San Antonio
  were armed, green, and held 33 people no wave could visit. The bat now asks the policy.
  **43 cities.** Same class as STOPLOSS-DISCOVER-1 earlier the same day.
- **GLOBAL-REACH-1.** 19 cities across AU, NZ, GB, AR and ZA held 40 guard-clean, law-cleared
  people the policy had never heard of. Added.
- **COUNTRY-NAME-ALIAS-1.** 5 rows carried the country as `'South Africa'` rather than `ZA`,
  which `country_of()` resolves to None — and None means refuse to send. Right behaviour, wrong
  cause: quietly unmailable in our own home market. Full country names now alias to their codes.
  The fence is untouched: an *uncleared* country still refuses.
- **The orphan-letter sweep** that CLUB-LANE-1's new assertion made possible then caught three
  more letters drawable by nothing: individual collectors, individual property, casual work.
  Zero rows today, so no send changes — but a future scrape writing 'Property' would have
  vanished exactly like the clubs did.

### What the app is doing (probed, not recalled)

`/health`, `/flags` and `/auth/providers` all answer under half a second. The three gates that
were stopping a stranger publishing are green on the live site: the price step saves, an invited
seller gets the photo draft, a first-time seller can publish.

### The legal fence, held

**179 people in France and Portugal cannot be emailed.** GDPR art.27 requires a named EU
representative and none is configured, so the code refuses to build those messages. That is a
fence, not a bug, and it was not coded around. Appointing a representative is David's act. FR
and PT cities are deliberately absent from the policy.

### Sent

David: *"If there are no blockers and some of these new cities can be emailed now, please do
it. You don't need to stop based on a previous time schedule as if it is a rule."* The
measure-only calendar is retired and replaced by a rule: **gates, not calendars.** A send waits
for a real gate — stop-loss, the day gap, provider limits, a clearance we do not hold — and
nothing else. Fired a wave of **129 people across 38 cities** (New York correctly held by its
one-day gap). Batch cap stays at 6 per city; that is the restraint now, and it is a dial.

### The plan

ONBOARDING_PLAN.md rewritten. The old one asserted a supply shortage for a day after the
shortage was disproved, because nobody edits a plan. New standing rule in it: **when a
session's measurement contradicts the plan, the plan is edited in that session** — the same
rule the ledger and the rulings register already have. Real reachable universe: **1,441 people
today**, and 20 publishers needs click→publish at about 15%.

Ledger: RG-0276, RG-0277, RG-0278 added. Three of my own first drafts were caught by existing
assertions — a duplicate id, a regex that counted the bat's own loop variable, a bare subprocess
where RG-0187 requires the harness — and fixed before locking. All green; 18 open unchanged.

The number is still **0**.
