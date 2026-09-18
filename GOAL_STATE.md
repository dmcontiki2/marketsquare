# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Under 100 lines: it is a state file, not a
diary — the changelog is the diary.*

---

## SUNDAY SUMMARY — 13 Sep 2026 (plain language)

**The number is still 0 of 20.** Nobody we emailed has published a listing yet. 6,748 people are on
the list and 1,482 have been emailed. **What moved this week:** the US outfitter letters went out
every night until Friday, then stopped — not because the list ran dry, but because a session on
Friday morning switched off every US, UK and Australian city, reading a document heading rule
against three of David's earlier decisions. Found and reversed tonight; 854 people in Maine, Alaska,
Montana and Colorado are sendable again, and the re-run wave sent **108 letters** at 01:31 (0 failed). **Next:** watch the funnel for
the first real person from a letter, and find the next member directory that publishes mailboxes —
the Texas licence file turned out to have no email column.

> **NOTE FOR THE 20 Sep SUNDAY SUMMARY (written by run 14, Fri 18 Sep):** the paragraph above and
> every "N people landed / N dwelled" figure before it counted mail scanners as people. Run 14
> proved it and fixed the instrument. Write Sunday's summary from the numbers in RUN 14 below,
> not from any figure in this file dated before 18 Sep.

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`
If the sandbox is dead, run it host-side: queue `run_py MarketSquare\scripts\onboarding_number.py`.

| date | published by own hand | probe A | probe B | notes |
|------|----------------------|---------|---------|-------|
| 2026-09-04 → 08 (runs 1–7) | **0** | 0 | 0 | baseline; raw 2 = e2e_test seeds, barred by §3 |
| 2026-09-09/10 (runs 8–10) | **unknown** | — | — | NOT MEASURED: sandbox dead (KB5124008) |
| 2026-09-12 (run 11) | **0** | 0 | 0 | 6,748 on the list · 1,482 emailed · 5 registered |
| 2026-09-13 (run 12, 01:00 SAST) | **0** | 0 | 0 | 6,748 · 1,482 emailed at 01:00, +108 at 01:31 (re-armed wave) · 5 registered |
| 2026-09-18 (run 13, 02:30 SAST) | **0** | 0 | 0 | 6,748 · 1,942 emailed · **25 registered** (was 5) · first full journey walked |
| 2026-09-18 (run 14, 12:20 SAST) | **0** | 0 | 0 | 6,748 · 2,491 emailed · 25 registered · **8 human clicks ever** (probed, see below) |

Target: **20 by Fri 31 Oct 2026.** Model: runs 5–8, 11, 12 Fable 5.1; runs 9–10 Opus 5 (drift, RUL-096h).

## WHAT RUN 13 DID (18 Sep 2026, Opus 5) — condensed by run 14; full detail in RG-0395/0396/0400/0401

Run 13 found the first real person and removed the wall in front of him. In short:

- **Found him.** Listing **382**, "Guided Fair Chase Hunts", Victor Montana, quality 94 — built by
  **prospect 83302** (`register:moga`, a cold letter) entirely by his own hand, then left as a draft
  for six days. `create_listing` scheduled no task at all: the hand-back screen was the only thing
  that ever named his advert, and it died with the tab.
- **QUICK-RETURN-1 / RG-0395** — a Quick-app draft now mails its author a link back to it. The first
  send went out with a token signed by an EMPTY `MS_JWT_SECRET` (the runner loaded systemd's
  `Environment=` but not its `EnvironmentFile=`) and `_send_html_email` still returned 'sent'.
  **LESSON: 'sent' is EXECUTED, not PROBED. Never report a link delivered without verifying it.**
  QUICK-RETURN-GUARD-1 now fails closed on an empty key; QUICK-RETURN-TTL-1 gives the link 7 days
  (it was borrowing the 20-minute sign-in TTL, so every earlier send was dead before he woke).
- **HUB-EULA-1 / RG-0396** — the hub's Publish used to dead-end: *"You must accept the Terms"* with
  no way to accept them, for EVERY first-time Quick composer (quick.html creates no account, so
  `eula_accepted_at` is NULL). Now it hands the draft to the Terms screen. **The whole walk —
  emailed link -> hub -> draft -> Publish -> Terms -> tick -> live — was proven end to end in a real
  browser for the first time on 18 Sep 07:29, both probes agreeing.** Test rows archived after.
- **Deliberately NOT done, and still correct:** nothing publishes on a seller's behalf
  (ONBOARDING_GOAL s3, RUL-117(c)). The "Publish it" label in the Quick app is arguably ahead of
  what the button does; changing it is changing a ruling, which is David's.
- **Do not send prospect 83302 a third reminder.** Two letters and a resend is the limit.
- **RG-0400 (open): the EULA a seller actually ticks is a FOURTH, unsynced copy** — the
  `sob-eula-box` in marketsquare.html reads v1.10 while the site publishes v1.17, and
  `eula_sync.py` knows only three copies. Left open on purpose: it is restyled markup, not a byte
  copy, and auto-transforming the text of a legal gate unattended is how you get a consent record
  nobody can defend. Needs its own session.

## WHAT RUN 14 DID (18 Sep 2026, 12:00-13:30 SAST, Opus 5) — THE NEAR LEAK DOES NOT EXIST

1. **Measured.** Number 0, both probes agree. 2,491 emailed (was 1,942), 25 registered. Listing 382
   is STILL a draft — the Montana man has not tapped Publish. That is his act; do not chase it.
2. **Ledger opened RED on two entries (RG-0015, RG-0197) — same single cause:** a stranded
   `.git/index.lock` (0 bytes, >60 min, survived every self-heal). Healed with
   `scripts/git_unlock.py`; 9 tmp_obj orphans still await the host sweep. Both green at the end.
   **This is worth knowing: two REDs that read as two faults were one lock.** Clear the lock first,
   re-run, and only then believe a red.
3. **KILLED RUN 13's "NEXT THING TO WORK ON". It was an artefact of the instrument.**
   Run 13 wrote: *"the near leak is untouched: 15 dwell -> 3 subpick... the biggest measurable loss
   in the funnel."* It is not a loss. `GET /onboard/funnel` reported `humans` (sessions that stayed
   12 s AND touched the page) in one field and its `funnel` step counts over EVERY non-bot session
   in the next — two different populations in one table, with the docstring calling the first one
   "the denominator a conversion rate may be built on". PROBED on the live DB, 21 days:
   - 156 non-bot sessions -> **28 dwelled**. Of those 28, only **3 had a `landed` row at all**.
     The other 25 are ordinary visitors with no letter, so no category, so nothing to sub-pick.
   - **65 letter landings were never graded as bots and never dwelled. 26 of them arrive inside the
     22h UTC hour the nightly wave fires** (00:10 SAST) — the FUNNEL-HUMAN-1 scanner signature, one
     layer on from where that fix stopped. The `subpick`/`photos` rows they generate are real code
     paths: a letter pre-selects the category, `sfInit` calls `sfStartCat`, and the scanner's own
     render logs landed+subpick+photos **in the same second**. It looks exactly like a funnel.
   - So: nobody is stalling on the first screen. **Almost nobody is reaching it.**
4. **FUNNEL-DENOM-1 / RG-0402 — fixed, shipped (db931d6), PROBED live.** `/onboard/funnel` now also
   returns `human_funnel` (per-step counts over exactly the sessions `humans` counts) and
   `letter_humans` (arrived on an outreach link AND stayed), and the note names which to read. Raw
   `funnel` left byte-identical so no existing reader changes meaning underneath itself. Proven 9/9
   on a fixture before ship (scanner, real letter arrival, walk-in human, graded bot); proven on the
   live box after. **Live, 21 days:** raw `landed 63 · subpick 23 · photos 22` vs honest
   `landed 2 · subpick 2 · photos 4`, `humans 27`, `letter_humans 2`.
5. **THE EMAIL LANE AGREES, INDEPENDENTLY — and this is the real number.**
   `click_register.tier` has graded every recipient since the campaign began:
   **human_click 8 · human_open 321 · machine 163 · uncertain 84.**
   **Eight real humans have clicked, ever, out of 2,491 letters.** `rickwemple@aol.com` — Montana —
   is one of the eight. Two instruments built on different evidence now agree within single digits.

## WHERE THE FUNNEL ACTUALLY LEAKS (run 14, probed 18 Sep) — READ THIS, NOT THE OLD SECTION

The honest chain, all-time, every figure probed:

    2,491 letters  ->  ~329 real people opened one  ->  8 clicked  ->  1 built a complete advert  ->  0 published

- **Letters reach inboxes.** The outreach wave sends via **Resend**, From
  `David at TrustSquare <david@mail.trustsquare.co>`, a Resend-verified subdomain.
  `api.resend.com` answers the box **200 in 0.19 s** — run 13's note that "Resend is unreachable
  from the box, everything goes via the Gmail SMTP fallback" is **WRONG for the outreach wave** and
  should not be repeated. It confused a Cloudflare block on `trustsquare.co` with a block on Resend.
  (It may still be true of the *app's* transactional mail in `bea_main.py` — that was not re-probed.)
- **The loss is between reading the letter and clicking it: 8 clicks from ~320 human opens (2.4%).**
  That is the one big measurable leak, and ONBOARDING_GOAL section 5 names "change the email" as
  mine to do without asking.
- **The app is not the bottleneck and has not been.** Of the 8 who clicked, 1 built a finished
  advert scoring 94 — a 12.5% build rate from a cold click, which is good. The wall behind him
  (HUB-EULA-1) was removed on 18 Sep.

**THE TRAJECTORY, STATED PLAINLY (ONBOARDING_GOAL section 9).** 4,257 letters remain unsent. At the
measured rate (8 human clicks per 2,491 letters, ~1 finished advert per 8 clicks) the rest of the
list yields roughly **14 more human clicks and perhaps 2 more finished adverts**. **20 by 31 October
is not reachable on how the letter currently performs.** It needs the human-open -> click rate to go
from 2.4% to roughly 20% — about eightfold — or a different channel. This is NOT a BLOCKED state:
nothing reserved to David is in the way, and the letter is mine to rewrite. It is a trajectory
warning, made now rather than on 31 October.

## SUPPLY — ASSOCIATION LANE NEARLY DONE; LICENCE FILES CARRY NO MAILBOX

- Harvested + drawn: rrca, pacific, moga, wyoga, coa, apha, mpga. New association = one dict entry in
  `CityLauncher/us_register_assoc.py`; run via `run_us_registers.bat`. ZA Durban/PMB rows = blocked category, 0 sendable.
- **NOT harvestable, do not re-probe:** Idaho IOGA (form) · NM NMCOG (Airtable) · Utah UOGA (Wix/
  Guidefitter) · NY NYSOGA + Oregon OOGA (Cloudflare-obfuscated) · WA WOGA (no directory) · Colorado
  DPO lookup (form) · Vermont VOGA (525) · Nevada (one mailbox) · **Texas TREC file (no email column)**
  · Idaho IOGLB board site (000 from sandbox) · Oregon Marine Board guide search (404) · Alaska CBPL
  licence search (403) · Wyoming board home page (200, no mailboxes on the front page — a list page may exist).
- **Working kinds:** member directories that PUBLISH a mailbox. Untested leads of that kind: US Forest
  Service outfitter-guide permit-holder lists (per-forest PDFs, often with email); chamber-of-commerce
  member directories (GrowthZone/ChamberMaster pages are server-rendered); state fly-fishing / hunting
  guide associations not yet probed (AZ, NV, SD, ND, NE, KS, OK, AR, MO, MN, WI, MI, PA, VA, NC, TN).
- Older dead ends stand: USATF finder/regionals · NY DEC guides · US search scraping · orienteeringusa
  · skifederation · americancanoe · americanhiking · adventurecycling · coloradooutfitters.org.

## WHAT THE NEXT RUN SHOULD PICK UP — **DIRECTION CHANGED BY DAVID, 18 Sep evening**

**READ `QUICK_LISTING_SPEC.md` BEFORE DOING ANYTHING ELSE. It supersedes the letter-rewrite
plan below it.** David redirected the goal on the evening of 18 Sep: the target market is
South African casual services — **housecleaners first**, then waiters, petrol jockeys, truck
drivers — reached through the Quick door, in the shape *promise → visual → 4 clicks → email →
EULA → list → AI-guided trust score*. The US outfitter letter lane is no longer the main line.

1. Run the number. Read `human_funnel` / `letter_humans`, never `funnel` (FUNNEL-DENOM-1).
   **NEW: the Quick door now reports too** — `q_door`, `q_step_<n>`, `q_draft`, `q_handover`
   (QUICK-FUNNEL-1, shipped 18 Sep evening). This is the first data we have ever had on it;
   read it before forming any opinion about the Quick lane.
2. Ledger in shards (`--shard=k/8`, then `--combine=8`) + rulings check. If the board opens
   RED, clear `.git/index.lock` with `scripts/git_unlock.py` and re-run before believing it.
3. **DO NOT start building the spec's items 3-5 until David has answered D1-D7.** They are
   listed in `QUICK_LISTING_SPEC.md` sections 4 and 7 and several of them change a ruling,
   which is reserved. He was asked on 18 Sep and is away at a chess tournament on 19 Sep.
4. **What IS unblocked and worth doing without him:** watch the new Quick beacons; prove one
   walk end to end from `/q/homehelp` in a real browser at phone width as a stranger, and
   write down exactly where it breaks. That walk has never been done for a Quick-origin
   draft — the 18 Sep proof used seeded rows.
5. Do not rewrite the outfitter letter yet. The letter analysis in section 5 below still
   stands and is still true; it is simply no longer the first thing.

## OPEN LOOPS (run 13 + run 14)

**FOUND 18 Sep EVENING — three things another lane or an old deploy left, none of them David's:**
- **The EULA is mid-landing and the version register has not moved.** `eula_clean.html`,
  `terms.html` and ms.js's `_EULA_HTML` were bumped **v1.16 -> v1.17 (version stamp only, no
  clause text changed)** by another lane at ~19:13 while this session was running, and they sit
  UNCOMMITTED in the working tree. `canon.yml` and `LEGAL_VERSIONS.md` still say v1.16, so
  `rulings_check.py` now reports **1 FAIL on RUL-133** — correctly: landing a version is atomic
  (P5/P10) and this landing is half done. **Deliberately not touched and not committed by run 14**:
  it is legal text and another lane owns it (SO-5). Whoever finishes it must do the whole landing,
  not just green the checker — and must NOT `git add -A` it in passing.
- **The CityLauncher dashboard on the server is weeks stale.** `/var/www/citylauncher/
  citylauncher.html` is **54,945 bytes** against the repo's **92,569**, and carries NONE of the
  markers the repo copy has — not even OPTOUT-COUNT-1, which shipped 31 Aug. So the API half of
  STATS-HUMAN-1 (RG-0403) is live and correct, and the PAGE half never arrived, which is exactly
  the "honest API, raw repaint" split that entry was written to prevent. **Ask David where he
  actually reads the board before deploying over it** — the server copy may not be the page he opens.
- **The sandbox cannot remove `.git/index.lock`** (mount refuses unlink), so a sandbox commit needs
  `scripts/git_unlock.py` run before AND after. Two locks were healed this evening; 19 orphaned
  `tmp_obj` files await the host sweep.

- **RUN 14: `_get_json()` still does not exist.** Run 13 specified it; nothing wrote it. RG-0401
  (EDGE-BLIND-1) fixed `_get()` to raise ProbeOffline on an edge refusal, which covers most of it,
  but the 14 `json.loads(_get(...))` call sites are still individually unprotected against a 200
  that is not JSON. Small, one helper. RG-0402 uses `json.loads(_get(...))` and inherits the gap.
- **RUN 14: the ledger's `rg_no_third_party_script_on_surface` downloads ~16 MB per run** (ten
  `/static/adventures_*_map.html`, up to 2.5 MB each). Cold, that is ~172 s — on its own it is why
  a whole-board run gets killed and why shard 1 is the slow one. A HEAD/Range or a cached digest
  would make the board runnable in one call again.
- *(run 13, superseded in part by RG-0401)* **The ledger's live JSON probes can go RED on a network hiccup.** Shard 4 reported RG-0386
  REGRESSED with `JSONDecodeError` while the live endpoints were in fact perfect (re-probed 4/4
  clean immediately after, green on the full re-run). 14 checks do `json.loads(_get(...))`; a 200
  that is not JSON - an edge interstitial, a truncated body - becomes a FAIL and the board then says
  "Do not deploy over this". That is a false RED that can freeze the deploy lane, the S140 class
  CLAUDE.md names. FIX: one `_get_json()` that retries once and raises ProbeOffline (UNVERIFIED,
  blind) rather than FAIL when the body is not the app's JSON. Small, one helper, 14 call sites.
  Left undone tonight only because CLAUDE.md allows one fix per task and the conversion leak won.
- Listing **386** (wiring test) is ARCHIVED, not deleted; 387/388 likewise. The two files in
  `_to_delete/` and **9 orphaned `tmp_obj` files in `.git/objects`** need a deletion, which is
  David's (`git_unlock.bat` sweeps the tmp_objs).
- RG-0346 (agency letters lack the console CTA) - still open, still adds no nightly volume.
- Film 07 (Liquidation) unpublished - David's click, when he chooses.

## THINGS ALREADY TRIED THAT DID NOT WORK

- **Reading `funnel` step counts as people (run 13 did, and built a plan on it).** They include mail
  scanners the UA grader missed. Read `human_funnel` / `letter_humans` (FUNNEL-DENOM-1).
- **Believing a ledger RED before clearing `.git/index.lock`.** Two REDs, one lock (run 14).
- **`request_deploy.py --files <x> "reason"`** — it does not commit, prints `relay: Everything
  up-to-date`, advances the ref to the PREVIOUS head and reports "live in ~2 min". Nothing ships.
  Use `--all "reason"`, then PROBE the live endpoint. Another "reports success, did nothing".
- **Repeating run 13's "Resend is unreachable from the box".** It is reachable (200 in 0.19 s); the
  outreach wave goes out through it from a verified subdomain.

- Opening `/admin.html` publicly. `fill_wave_gaps.py` via the queue (401). Reading "no sendable
  prospects" as supply (13 Sep: it was a DISARM — check `armed`/`gates_green` in waves_policy.json and
  any `disarmed_by` stamp FIRST). Halving the batch for a "measurement week" (RG-0290). US general
  search scraping. Trusting "wave #N logged". Running the ledger in one call — use shards.
- Probing register sites blind: many .org/.gov hosts do not answer the sandbox (000). Curl first.
- Retrying a dead sandbox mount more than twice; restarting the app to cure it (proven useless).
  Assuming an official licence file carries a mailbox (Texas: it does not).

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

**None.** Nothing from run 13 or run 14 is waiting on David, and nothing reserved is in the way.

Listing 382 is still a draft because publishing it is the seller's own act (ONBOARDING_GOAL s3,
RUL-117(c)). He has a working link and, since 18 Sep 07:29, a path behind it that actually works.
If he taps it, the number becomes 1.

**One thing David should KNOW, not decide (run 14):** on how the letter performs today — 8 real
clicks from ~320 real readers of 2,491 letters — 20 by 31 October is not reachable through this
channel. Nothing is blocked; rewriting the letter is mine and is the next run's job. This is stated
now rather than on 31 October because he makes real decisions on this number.

## WHAT RUN 14 LEARNED ABOUT ITSELF

**The instrument is part of the goal.** Run 13 was careful, honest and thorough, and still handed
the next run a target that did not exist — because it trusted a number the endpoint itself had
mislabelled. ONBOARDING_GOAL s2 says PROBED beats EXECUTED beats READ beats RECALLED; a figure
returned by our own API is only READ. Before spending a run on "the biggest measurable loss in the
funnel", go behind the endpoint to the rows and check the denominator is the same one.

**And the corollary, which cost this run twenty minutes:** a deploy tool that prints a success line
is EXECUTED, not PROBED — exactly run 13's own lesson about 'sent'. The same class bit twice in two
days. Probe the live thing.

## WHAT RUN 13 LEARNED ABOUT ITSELF (read before parking anything as 'reserved')

The reserved list is short and specific: money, deletions, sending to third parties, lockout risk,
legal/commercial positioning, launch scope and dates, changing a ruling. **Transactional mail that
completes an act a user began on our own form is not on it**, and a rule written about cold-letter
SHAPE (RUL-099) does not become a rule about service mail because both are email. Before parking
anything: ask whether the shipped product already does this exact thing unreviewed. If it does, so
may the agent. Handing David the one action with a consequence, wrapped in rule language, is the
failure this whole goal architecture (RUL-092, RUL-095) was built to end - and I reproduced it.
