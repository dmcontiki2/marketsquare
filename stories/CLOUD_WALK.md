# Cloud story walks — the brief for a Claude Code cloud session

*QA-CLOUD-1 / CLOUD-SHIP-1, 30 Sep 2026. David approved these walks ("GO", 29 Sep): one full story per
flow, on the live site, with QA people and real (test-granted) Tuppence, turned into the in-app How guide.
Publishing a QA advert, asking for an intro and accepting it on trustsquare.co are the point of the walk,
not side effects to avoid. Everything happens as QA test addresses (`dmcontiki2+qa-...@gmail.com`) only.*

## 0. Check the key first (10 seconds)

    python3 stories/cloud_kit.py ping        # must print (200, {'ok': True, 'qa_key': True})

A 404 means the QA key is not reaching trustsquare.co: stop and say so — the environment's API
credential (header `X-QA-Key`, site `trustsquare.co`) is missing or wrong. Do not work around it.

## 1. What you have instead of Gmail, admin and SSH

| Need | Use | Limits |
|---|---|---|
| Sign a person in (no emailed code) | `await signin_context(ctx, "qa-thandi1001", "Thandi", review=True)` | QA addresses only; `review=True` also sets the tester cookie, so Quick shows **How** |
| Tuppence for an intro / paid check / accept | `python3 stories/cloud_kit.py grant qa-thandi1001 3 "F2: intro"` | 1–5T a call, 20T per address per day; logged as a tester grant |
| A guide screen | `python3 stories/cloud_kit.py image <type> <key> shot.png` | JPEG ≤ 400 KB, written to `/help/img/<type>/<key>.jpg`, local copy in `stories/img/` (git ignores it) |
| Know whether your commit went live | `python3 stories/cloud_kit.py ship-status` | last 20 lines of the server's ship job |

Browser: Playwright's Chromium, phone 390×844, `is_mobile=True`, iPhone UA (as `stories/help.html` screens are).
Emails the app sends go to David's inbox, which you cannot read. Where a step's proof is an email
("the seller gets the intro email"), prove it on screen instead (the intro shows in her Intros tab) and
list the email in the report under **Checked next on the laptop**.

## 2. The flows still to walk

| Flow | Listing types in it | What its story must prove |
|---|---|---|
| F2 Casual worker with licence or clearance | nanny, caregiver, au pair, crèche assistant (police clearance); car guard, security guard, bodyguard (PSIRA); delivery rider (licence) | the gate is asked, checked and shown before buyers see her |
| F3 Technical trade | plumber, bricklayer, tiler, carpenter, roofer, welder, motor mechanic, solar PV, appliance repair | work examples, call-out fee, intro 1T, accept |
| F4 Licensed trade | electrician (DoEL), gas installer, air-con (SAQCC), CCTV, gate, locksmith, drivers (PrDP) | licence asked and shown; buyer sees it before asking |
| F5 Tutor | 17+ subjects, 5 levels, online or in person | parent finds by subject and level; regular students on Buzz |
| F6 Property for sale | house, flat, townhouse … farm, commercial | Area Dossier 3T and fair price 1T for the buyer; intro; accept |
| F7 Property to rent | the same, to let | Yield Estimate 1T; intro; accept |
| F8 Vehicle for sale | car/bakkie/SUV, motorcycle, caravan & trailer, boat, truck/bus/tractor | Car Purchase Dossier 3T and fair price 1T; intro; accept |
| F9 Vehicle for hire | the same, for hire | hire terms shown; intro; accept |
| F10 Collectors item | stamps, trading cards, coins, memorabilia (Quick: militaria, watches, art) | Collectables report 5T, attach report, fair price 1T from catalogues |
| F12 Adventures stay | guest house, bush camp, chalet, hostel, self-catering, camp site, huts | found by place and environment; intro; accept |
| F13 Adventures experience | hiking, water sports, wildlife … sky & extreme | difficulty and season shown; intro; accept |
| F14 Agency-listed | estate agency for owners; placement agency for workers | an agent lists for someone else; the right person receives the intro |

Done already: F1 (`stories/home_cleaner.json`), F2 (`stories/nanny.json`, family half waits on L28), F8 (`stories/cars_bakkie.json`), F9 (`stories/cars_for_hire.json`), F10 (`stories/collectors_coins.json`, report steps wait on L34), F11 (`stories/localmarket_food_preserves.json`). Walk
one flow per session, picking the first one here with no `stories/<type>.json` yet.

## 3. The walk (the story template)

Seller: 1 finds the door (Quick, or TrustSquare's Sell) → 2 answers her type's questions → 3 saves by email
(here: `signin_context` stands in for the code) → 4 photo, terms, publish → 5 passes the gate if her flow has
one → 6 sends her Buzz link to her regulars if it has regulars.
Buyer: 7 finds the advert by area and type → 8 runs the flow's paid checks (charged only when a real figure
comes back — check the balance before and after) → 9 asks for an intro (1T).
Close: 10 seller accepts (1T), contacts shared, both balances update on screen → 11 one of them passes
Quick on.

Rules that come from David:
- **People**: a fresh QA address per person per walk (`qa-<firstname><mmdd>`); first names from one naming
  tradition across the whole story (Annatjie/Sannie/Hettie/Karin; Elsabe/Riana/Elna).
- **Check on the rendered page**, as a person on a phone sees it — never "the API said 200".
- **A fault found is fixed in the same session and walked again**, never parked. Fix the smallest thing;
  add a ledger entry in `scripts/regression_ledger.py` (next free RG number, above `if __name__`), and a
  line in `changelog.d/<date>-<slug>.md`. Plain words in everything a user reads.
- **After the walk, pause every QA advert** you published (Seller Hub → the advert → Pause) so buyers do
  not reach a test mailbox. Pause, never delete.
- Never a real person's account, never a real payment, never a password.

## 4. The story file

Copy `stories/localmarket_food_preserves.json` as the pattern: `type` = `<category key>_<slug of the
type label>` (as Quick's How finds it), `flow`, `label`/`title` in **en, af, zu, xh, nso**, `people`,
`chapters`, `steps`. Each step: `n`, `ch`, `who`, `cost` (free | 1T | 1T_check | 1T_accept | <n>T_report for a paid AI report such as the 3T dossier), `img`,
`pass` (true only if it passed this walk — a failed step stays false and the guide hides it),
`quick` (the Quick screen keys it belongs to: door, what, where, days, price, ship, draft, saved, buzz),
and `[title, text]` in all five languages. App words the user taps stay English inside `[[ ]]`
(`[[Sell something]]`); the guide colours them as quotes. Screens are not translated.

Then:

    python3 scripts/build_help.py            # writes gallery.json + the manifest block
    python3 scripts/build_help.py --check    # 0 errors, 0 stale
    cmp quick.html genie/HARNESS.html        # if you touched Quick, copy it across

Report: `docs/E2E_<yyyy-mm-dd>_<flow>.md` — the table (step, saw, would a stranger stop here), the fixes
with their RG numbers, the QA adverts paused, and **Checked next on the laptop**.

## 5. Ship it

Commit on your `claude/...` branch with **`[ship]`** in the message, then push. Within about 2 minutes
the server merges it into main (fast-forward or clean merge), runs the gates (compile, JS parse,
route_policy.json, quick.html = HARNESS, build_help --check against the screens you uploaded, no change
to ops/ except the generated guide block) and ships it health-checked with auto-rollback.

    python3 stories/cloud_kit.py ship-status   # SHIPPED ... or REFUSED ...: <why>

A REFUSED line says what to fix; fix it, commit again with `[ship]`, push. Then open
`https://trustsquare.co/help/<type>` and Quick's **How** on the phone viewport and check the guide as a
user would — that is when the walk is done.
