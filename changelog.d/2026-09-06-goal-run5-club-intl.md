## 2026-09-06 — Goal run 5 (Sunday 01:00): the first US club wave crashed to zero and nobody saw it; club contacts were landing on the wrong screen; a third US register (CLUB-INTL-1, WAVE-CRASH-VISIBLE-1, INVITE-CAT-2, USATFNE-1)

Model: Fable 5.1, as David asked (RUL-096h). The number is **0** (probe A 0, probe B 0; the
raw query still says 2, both e2e_test seeds). 4,470 on the list, 570 emailed, 5 registered.

**CLUB-INTL-1 — the 00:10 wave sent 0 of ~450 US club letters and reported success.** Read off
`logs/launchday_06Sun09_2026010.log`: Pretoria 12, New York 12, Cape Town 12, Durban 9, Port
Elizabeth 8, Kimberley 1 went out (55); then all 51 RRCA-1 state buckets died in
`emailer.render` at localize's fail-closed rand guard — *"US: 1 rand amount(s) survive
localization (e.g. R700)"*. The rand was not in the template (`tests/test_intl_templates.py` was
green) but in `_CLUB_EXAMPLES['example_price']`, substituted in Python after the template test
looked. `wave_runner` ignored the subprocess return code and printed "wave #1 logged". Fixes:
per-country example card (`_CLUB_EXAMPLES_INTL`: $ / £ / A$ / NZ$, "10k to marathon" instead of
Comrades, currency-free fallback for an unmapped country); the South African worked-example page
link is now `<!--ZA-ONLY-->`; `Police clearance` → `Background check` in the US map; and a new
send-path test `tests/test_render_intl.py` that renders every armed city × drawable category
through `emailer.render` (34 assertions, green). **WAVE-CRASH-VISIBLE-1:** `wave_runner` now reads
the emailer's rc, prints one greppable `!! EMAILER CRASHED` line per category, records it in
`wave_log.json` and exits nonzero. Proven by a dry-run on 12 real Texas rows (`From $45 / month`,
no rand). The gap gate was unaffected (no sent event = no `last_emailed_at`), so the states were
re-queued the same night via `launch_day_wave.bat` (55 of 250 daily cap used). **RG-0298** LOCKED.

**INVITE-CAT-2 — every club contact who clicked landed on the generic "what are you selling?"
tiles.** PROBED `GET /onboard/funnel?days=2`: 9 sessions landed, 0 reached `photos`; 4 carried a
real src (pretoria-sports-clubs-20260905/06), 5 a scanner-mangled one. READ `ms.js` `sfInit`: the
invite map had no `sports clubs` key — INVITE-CAT-1 (3 Sep, "no ledger entry; cosmetic") predated
the club lane by a day. GOAL_STATE had described the invited path as "lands on Step 1, Photos";
true for Tutors, never for a club. Routed `sports clubs` / `sports club` / `sports_clubs` → Tutors
(the club letter's worked example IS a Tutors listing), plus the remaining template aliases the
sweep found (accommodation, tour guide agency, casual services, casuals, services (technical)).
**RG-0299** LOCKED: every key of `emailer.TEMPLATES` and every category in `waves_policy.json`
must resolve in `_map`, and the live funnel must not show a real src with ≥10 landings and
nothing further. Shipped via `request_deploy`.

**USATFNE-1 — third US register.** USATF New England publishes every registered club on one
static page (`usatfne.org/member/clubs.html`), mailbox obfuscated as `javascript:email('domain;
local')`. New adapter `usatfne`: 268 clubs with a mailbox (MA 187, NH 31, RI 29, VT 17, ME 2),
bucketed into the existing state buckets. CSV written from the sandbox; import queued via
`run_us_registers.bat` (now `pausatf rrca usatfne`). Probed and rejected this run: USATF
Mid-Atlantic and Three Rivers publish no club emails. RRCA result read: **+903 clubs imported
5 Sep 21:30**, 'Sports Clubs' now 1,568 rows / 1,301 distinct clubs.

**RG-0287 regression fixed the same run:** the dashboard club card said 577 → 313; the database
holds 1,568 / 1,301. Card rewritten with today's probe (36 ZA clubs emailed).

**Visibility (RUL-103):** youtube-pack for film #1 — `feature-videos/01-collectables/
collectables-FINAL-4K-v3-03jul_youtube/` (3 titles, description with chapters read off a
2-second frame strip, 14 tags, 1080×1920 cover, pinned comment). LAUNCH_SERIES.md updated. Which
film goes first is David's.

**US search scraper (RG-0297, still OPEN):** the 21:30 measurement run never searched — DDG reset
the connection at preflight (`ERR_CONNECTION_RESET`), likely rate-limited after the 33-minute run.
Not re-queued; registers are the supply.

Also: `emailer/test_localize.py` (21 Aug) asserted exactly 14 templates and a byte-identical ZA
output; both stale since INTL-COPY-1 (28 Aug). Count relaxed to ≥14; the identity assertion is
superseded by `tests/test_intl_templates.py` and left as is.
