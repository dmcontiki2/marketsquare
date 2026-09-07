## 2026-09-07 — EMAIL-FORENSIC-1 fixes: the road behind the click is open (INVITE-PLACE-1, INVITE-GATE-1, RENDER-PURE-1, HREF-SHIELD-1, RECONTACT-1)

The forensic walk-through of the same morning (EMAIL-FORENSIC-1) found the letter fine and the
app behind it blocked: 1,206 letters sent, 62 arrivals in 30 days, 15 reached the photo screen,
nobody ever passed it; the invited city was dropped at the last hop; the support page contradicted
the letter; a worked-example page shipped with a blank; two link parameters nothing read; and a
preview could take the prospect database offline. All six are fixed in this change; the six ledger
entries opened this morning flip as the live probes pass (RG-0330 locked in-session; RG-0325/0327/
0328/0329 on live verification after deploy; RG-0326 is behavioural and locks only when a REAL
invited arrival passes screen 1 — a probe session is excluded by design).

- **INVITE-PLACE-1 (RG-0325, RG-0327) — the invited seller's place reaches the listing.**
  `ms.js sfInit()` now seeds `sfState.city` from `magicLink.area` (the link's `?city=`) instead of
  the browse default, and `sfState.country` from a new `?country=` parameter — with a client-side
  inference (`_mlCountryFor`: launch cities + US state names + a few extra cities) for the 1,206
  links already in the wild that carry no country. Both `/listings/vision-draft` calls send
  `sfState.country` instead of a hard-coded `'ZA'`. The parser also reads `?suburb=` (and the
  localized `neighborhood`/`neighbourhood` names older US/AU/GB letters carried) into
  `magicLink.suburb`, and `sfStartCat()` seeds the "Suburb / area" box from it. On the builder
  side `build_magic_link()` emits `country=<ISO2>` (also appended to legacy stored links) and
  stops emitting `draft_id` — `prospects` has never had that column; the app's own name for a
  pre-seeded draft is `drafted=1`.
- **INVITE-GATE-1 (RG-0326) — screen 1 is no longer a wall.** The forward button on the Photos
  step is never disabled. With a photo accepted it goes straight on; without one it goes through
  `sfSkip()` (one warning line, then on) — "No photo handy? Continue and add one later →". The
  coach line says so too. Publishing needs no photo server-side; `sfRunMultiVision()` already
  guards for none.
- **HREF-SHIELD-1 (RG-0327) — prose maps never touch a URL.** `localize.localize_html()` stashes
  every `href="…"` before the per-country term substitutions and restores it after, so `suburb=`
  no longer ships as `neighborhood=`. `test_localize.py`'s ZA-identity assertion was stale
  (compared raw template to unwrapped output) — now compares against `_unwrap_za_only()`; green.
- **RG-0328 — /support agrees with the letter.** Three answers rewritten from PRICING_CANON:
  free account = 2 listings, no card/trial/registration fee; you list by tapping Sell in the app
  (never "the admin panel" — gone from all four answers; sellers use their dashboard); TrustSquare
  started in Pretoria and takes listings from ZA, US, UK, AU, NZ, AR, NA, FR, PT.
- **RG-0329 — the worked-example pages address the reader who clicks.** `assoc_athletics.html`
  (letter-linked) and `assoc_guides.html` no longer say "your provincial … body/association";
  they are prepared for "athletics clubs and their coaches" / "tour guides and their
  associations", and the "Nothing has been sent to anybody… proposal" line — false once letters
  went out — reads "This is a worked example… Every listing on it is invented." The same generic
  blank was fixed on `assoc_dance.html` and `assoc_teachers.html` (same class).
- **RENDER-PURE-1 (RG-0330, LOCKED) — a render never writes.** `_apply_launch_special()` reads
  `prospect['launch_code']`; `emailer.main()` issues it on the send lane via
  `launch_codes.issue_for_send()` immediately before `send_email`, and a dry run renders
  `launch_codes.sample_code()` (never stored — the DB is the only authority). The ledger
  assertion was refined the same day: it now reads the render lane's own bodies (code, not
  docstrings) AND asserts the send lane still issues, so the special cannot be silently dropped.
- **RECONTACT-1 (RUL-106, RG-0332 LOCKED) — 60-day re-contact floor.** David: "not re-email the
  people we have, even those that did not opt-out, at least for a two month period."
  `send_email()` now refuses any address contacted inside 60 days per BOTH records
  (`prospects.emailed_at` and `sent_log.json`); the only door is `TS_RECONTACT_PERMISSION` (his
  words + date, printed to the log). The GB/NZ footers' "We will not email you again" is now true.
- **RG-0331 (OPEN) — the server half of place.** `listings` has no country column and
  `class Listing` no country field; `_listing_country_iso2()` therefore reads every row as ZA.
  Fix shape recorded in the entry (migration + model + create + read). Tracked, not lobbed.

Verification: `node --check ms.js` clean; `py_compile` clean on emailer.py, launch_codes.py,
localize.py, regression_ledger.py, rulings_check.py; `test_render_intl.py` ALL PASS;
`test_localize.py` GREEN (14×4); `test_wave_hygiene.py` ALL PASS; render of a real US club and a
real ZA Services prospect left `prospects.db` byte-identical with no journal; `send_email()` for
the newest emailed address refused before any network call. Backups beside every file
(`*.bak-invitegate-*`, `*.bak-renderpure-*`, `*.bak-hrefshield-*`, `*.bak-recontact-*`,
`*.bak-letteragree-*`, `*.bak-blank-*`, `*.bak-rg0330-*`, `*.bak-rul106-*`).

**Live verification (7 Sep 2026, after deploy c4d7da4, PROBED from David's Chrome inside the gate):**
the real Maine club link (src=probe-invitegate so the funnel ignores it) arrived with
`sfState.city='Maine'`, `country='US'` (inferred — this link pre-dates the country parameter),
`area='Lewiston'`, currency `$`; the Photos step's forward button was enabled with no photo and
one click reached "Step 2 of 6 · Tutoring Details" with the Suburb/area box pre-filled
"Lewiston". Live `/static/ms.js` carries INVITE-PLACE-1 and INVITE-GATE-1 and no hard-coded ZA.
`/support` and all five worked-example pages read clean. Ledger: RG-0325/0327/0328/0329 promoted
to LOCKED (fixed_on 2026-09-07); RG-0326 stays OPEN by design until a real arrival passes.
Follow-up in the same session: the main photo slot's badge said "required" — now "recommended";
the chess/judo/plumbers example pages lose the now-false "Nothing has been sent to anybody" line.
