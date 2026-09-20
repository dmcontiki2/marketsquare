# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Under 100 lines: it is a state file, not a
diary — the changelog is the diary.*

> **This file is 231 lines and has been over budget since run 13. Stated rather than quietly
> inherited.** The overrun is real cost: every run pays to read it. The fix is not a trim — it is
> that "WHERE THE FUNNEL LEAKS", "THE SUPPLY FLOOR" and "THINGS ALREADY TRIED" are durable
> reference, not state, and belong in one `GOAL_FACTS.md` this file points at. **Next run that is
> not shipping against the wave should do that split**, leaving here only: the number table, what
> the last run did, what the next should pick up, and the open questions.

---

## SUNDAY SUMMARY — 20 September 2026

**The number is 0.** Both probes agree: nobody we contacted cold has published a listing by their
own hand. The database says nobody, and there is nobody for a logged-out visitor to find. Two
records in the raw count are our own test seeds and do not count.

**What moved this week.** Registrations went from 5 to 42 — people who opened an account. Not one
of them has published. Nothing was emailed on 18 or 19 September because you asked for the pause,
and the pause held exactly as asked.

**What I found this week, and it is the thing that matters.** The cold email list is nearly empty.
There are 6,748 names on it. 2,499 have been written to. Of the rest, almost none can be written
to at all: wrong place, invalid address, already bounced, opted out, a company rather than a
person, a general info@ desk, a second mailbox at a firm we already contacted, or sitting in a
source our own sending history shows bounces too often to use. **What is genuinely left is 466
addresses.** That is why the nightly sends fell from about 400 a day to 43. Nothing is broken and
no gate is stuck — we have simply been consuming the list, and we are near the bottom of it.

**What that means, said plainly.** Those 2,499 letters produced about 330 real people reading one,
8 people clicking, 1 finished advert and 0 published listings. On that performance the last 466
letters will not produce 20 listings. They will most likely produce none. Cold email is not a
channel that is underperforming — it is a channel that runs out this month.

**I did not force more letters out.** I could have raised the nightly batch and emptied the list in
two nights. It would have bought perhaps one extra click and spent the sending reputation we will
need for whatever channel comes next. That is a bad trade and I did not make it.

**What I did instead.** I rewrote the letter that carries 428 of the 466 addresses left — the one
that goes to licensed guides in Maine. It now leads with the only thing we offer that the
platforms already emailing them do not: we take no commission on their trips. It is honest that we
are new rather than hiding it. And it asks them to look at their own advert rather than to commit
to a listing, because nothing is published and no account is created until they say so. It goes
out with the next wave.

**What is next, in one line.** The employer side you called on 19 September is no longer an
addition to outreach — it is the replacement for a channel that ends this month, and it is the
only route to 20 that is still open.

---

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`
If the sandbox is dead, run it host-side: queue `run_py MarketSquare\scripts\onboarding_number.py`.

| date | published by own hand | probe A | probe B | notes |
|------|----------------------|---------|---------|-------|
| 2026-09-04 → 08 (runs 1–7) | **0** | 0 | 0 | baseline; raw 2 = e2e_test seeds, barred by §3 |
| 2026-09-12 (run 11) | **0** | 0 | 0 | 6,748 on the list · 1,482 emailed · 5 registered |
| 2026-09-13 (run 12) | **0** | 0 | 0 | 1,482 emailed at 01:00, +108 at 01:31 · 5 registered |
| 2026-09-18 (run 13, 02:30) | **0** | 0 | 0 | 1,942 emailed · **25 registered** · first full journey walked |
| 2026-09-18 (run 14, 12:20) | **0** | 0 | 0 | 2,491 emailed · 25 registered · **8 human clicks ever** |
| 2026-09-19 (run 15, 01:00) | **0** | 0 | 0 | 2,499 emailed · 40 registered · listing 382 still a draft |
| 2026-09-20 (run 16, 01:00) | **0** | 0 | 0 | 2,499 emailed (pause held) · **42 registered** · **466 sendable left** |

Target: **20 by Fri 31 Oct 2026.** Runs 5–8, 11, 12 Fable 5.1; runs 9–10, 13–16 Opus 5.

## THE SUPPLY FLOOR — RUN 16'S FINDING, AND THE MOST IMPORTANT NUMBER AFTER THE GOAL ITSELF

**466 addresses are sendable anywhere in the world. Tomorrow night's wave composes 42.**
PROBED by running the wave's own composer over all 102 cities, not by reading a note:

    6,748 on the list -> 2,499 already emailed -> 2,055 scraped rows in armed cities
      -> minus sources our own send history condemns (openstreetmap 10.6%, google_maps 7.0%,
         club:agn 12.5%, club:wpa 11.1%, usatf-new-england 40% — the 5% stop-loss is correct)
      -> minus info@ desks (216), second mailboxes at a firm already written to (225+89),
         government domains (37), placeholder names (15)  ->  **466**

- **All 95 armed cities gate GREEN. The guards hold 8 rows in total. Nothing is stuck.** Do not go
  looking for a broken sender or a disarmed policy — run 16 did, and the answer is consumption.
- Where the 466 sit: **Maine 428** · Pretoria 20 · Cape Town 6 · Durban 4 · Johannesburg 3 · rest 5.
- **The decay 398→43/day was never a fault.** Batch is 12 a city, only 8 cities have any pool left,
  so 42 is the honest arithmetic. **Do not raise the batch to empty the list faster** — RAMP-1 and
  the 250/day cap protect the sending domain (RUL-111), and the trade buys ~1 click.
- `teachers_trainers` (1,114 rows on dbe_emis) is held by **blocked_categories**, not by the source
  gate. Unblocking it is a person-only/POPIA decision, not a technique — it is David's, not mine.

## WHERE THE FUNNEL LEAKS (probed 18 Sep, re-confirmed 20 Sep)

    2,499 letters  ->  ~330 real people opened one  ->  8 clicked  ->  1 built an advert  ->  0 published

- Read `human_funnel` / `letter_humans`, **never** raw `funnel` (FUNNEL-DENOM-1): raw counts include
  mail scanners. Over 30 days `letter_humans` is **2** — arrived on an outreach link AND stayed.
- **The loss is open→click: 8 from ~330 (2.4%).** That is the one measurable leak and it is mine.
- **The app is not the bottleneck.** Of the 8 who clicked, 1 built an advert scoring 94.
- Letters do reach inboxes — Resend, verified subdomain, answers in 0.19 s.

## WHAT RUN 16 DID (20 Sep 2026, 01:00–04:00 SAST, Opus 5)

1. **Measured.** 0, both probes agree. 2,499 emailed, 42 registered (was 40). Pause held: zero sent
   on 18 and 19 Sep, confirmed off `prospects.emailed_at`. **There was no sending fault to find.**
2. **THE FINDING — the supply floor above.** Ran the wave composer across all 102 cities and took
   the exclusion apart row by row. 466 left, 42 tomorrow, and the decay explained without a defect.
3. **SECOND FINDING — RG-0419 QDOOR-ZA-ONLY-1 (open). The Quick door is a South African product.**
   PROBED on the live page: every price chip is in rands (R250–R450 a day), suburb tiles are Menlyn
   and Midrand; `localize_html()` proves the US render carries no door strip and no `/q/` link at
   all. The ZA-ONLY fence is RIGHT and must not be removed. **Consequence nobody had written down:
   428 of the 466 left are US, so the five-tap lane serves none of them, and the `q_*` beacons will
   stay near zero however well the letters perform.** Full reasoning in the ledger entry.
4. **BUILT AND SHIPPED — RG-0418 LETTER-CLICK-1.** Rewrote the letter carrying 428 of the 466 and
   its subject. Was "A free listing for your outfit in <city> — TrustSquare" (the shape every
   lead-gen directory sends a licensed guide); now "No commission on your trips — a free listing in
   <city>". Body no longer opens on being three weeks old; commission leads; one ask, not three,
   and it asks him to LOOK — nothing is published and no account created until he says so, which is
   true of the flow. **No A/B split, deliberately:** 428 letters at 2.4% cannot separate two
   subjects from noise. CityLauncher deploy requested — **next run must PROBE that it shipped.**
5. **CORRECTED A CHECKER THAT WOULD HAVE PUNISHED THE RIGHT ANSWER.** `rulings_check` RUL-104 pinned
   the literal "a global marketplace that opened"; the rule is that we call ourselves a global
   marketplace and name no country of origin. My rewrite separated those two sentences and FAILed a
   letter that obeys the ruling. **My copy was also genuinely wrong — it had dropped "global" — so
   both were fixed:** the word is back, and the assertion now tests the claim, not the sentence.
   **Proven still able to catch the original fault**, in both directions, before it was accepted.
   Exactly where run 15 said to look after RUL-133. `rulings_check`: 137, **0 FAIL**.
6. **Ledger green before and after** (shards + `--combine=8`), 0 regressions both times. The board
   caught two of my own mistakes on the way — a CSS class name matched where I meant a div, and the
   ops email-template mirror gone stale against the sending copy. Both fixed, not argued with.

## WHAT THE NEXT RUN SHOULD PICK UP

0. **TIMING RISK, AND IT IS THE ONE THING THAT COULD WASTE THIS RUN.** The rewritten letter was
   still QUEUED when run 16 ended (`CL_DEPLOY_REQUEST.flag` present). The server wave fires at
   **22:10 UTC on 20 Sep** — *before* the next nightly goal run — so if the host autodeploy agent
   does not tick before then (David's laptop asleep), the wave sends the OLD letter to all 428
   Maine addresses and the rewrite is wasted on the largest batch left. Run 16 tried to register a
   one-off pre-wave check and **the scheduled-task registration needed an approval nobody was
   awake to give**, so it does not exist. Told to David in the run's notification instead. **If you
   are reading this before 22:10 UTC on 20 Sep, do step 1 FIRST.**
1. **Confirm the CityLauncher deploy landed** (`CL_DEPLOY_RESULT.txt`, then PROBE the server's copy
   of the template) **before 22:10 UTC.** A deploy tool printing success is EXECUTED, not PROBED.
2. Run the number. Read `human_funnel` / `letter_humans` and the `q_*` beacons — and read the `q_*`
   ones against RG-0419: near-zero is EXPECTED while the remaining list is US.
3. Ledger in shards (`--shard=k/8`, then `--combine=8`) + `rulings_check`. If the board opens RED,
   clear `.git/index.lock` with `scripts/git_unlock.py` and re-run **before** believing it.
4. **Read the new letter's first numbers** after the 21 Sep wave. Clicks arrive tagged
   `src=<city>-<category>-<yyyymmdd>`, so the new letter's are separable by date. **Do not call it
   either way on one night** — 42 letters at any plausible rate is one or two clicks.
5. **The employer lane is now the main line, not a second track.** The 92-role slate is under review
   with David (`ROLE_SLATE_REVIEW.md`) and that review changes its shape, so build the parts that
   hold under every scenario: `speaks[]` on the seller, and RG-0414 DOOR-RETURN-1.
6. **RG-0419 is the highest-value door work left** — per-country question sets. The magic link
   already carries `?country=`. Price bands are per-market judgement: R250 and $250 are not the
   same offer, and that part is worth putting in front of David as a question, not guessing.
7. Still carried from run 15 with the reason each was deferred: **RG-0409** ladder values + cap 40 ·
   **RG-0410** reachability gate + post-confirm glimpse · **RG-0411** taxi-drop area unit ·
   **RG-0412** EULA in the launch languages (**must wait on RG-0400**).

## OPEN LOOPS

- **RG-0400 (open): the EULA a seller actually ticks is a FOURTH, unsynced copy** — `sob-eula-box`
  in marketsquare.html reads v1.10 while the site publishes v1.18. Restyled markup, not a byte
  copy, so there is no safe mechanical sync; the real fix is rendering the box from the one source.
  Needs its own session and eyes on the rendered result. **Blocks RG-0412.**
- **RG-0419 (open): the Quick door prices only in rands** — see above. Not a defect to paper over.
- **RG-0414 (open): the only way back from the public door** is an emailed sign-in link plus one
  browser's localStorage — the two things this market is least likely to have.
- `_get_json()` still does not exist (specified by run 13, unwritten). RG-0401 covers most of it;
  14 `json.loads(_get(...))` sites remain individually unprotected against a 200 that is not JSON.
- The ledger's `rg_no_third_party_script_on_surface` downloads ~16 MB per run — why shard 1 is slow.
- `marketsquare.html` reports `[TORN]` to `mount_guard.py` as "mount LARGER than committed but
  git-clean". Probably CRLF normalisation, not a tear — but **never bash-write that file**.
- Listing 386/387/388 ARCHIVED not deleted; 2 files in `_to_delete/` and 9 orphaned `tmp_obj`
  files need a deletion, which is David's (`git_unlock.bat` sweeps the tmp_objs).
- RG-0346 (agency letters lack the console CTA) — open, adds no nightly volume.
- Film 07 (Liquidation) unpublished — David's click, when he chooses.

## SUPPLY — THE ASSOCIATION LANE IS THE ONLY ONE STILL PRODUCING

- Harvested + drawn: rrca, pacific, moga, wyoga, coa, apha, mpga. New association = one dict entry
  in `CityLauncher/us_register_assoc.py`; run via `run_us_registers.bat`.
- **Registers are the best addresses we own** — rrca 2.55%, mpga 2.5%, moga 2.63%, apha 0% bounce,
  against 7–12% for every scraped source. A new register is worth more than a new scraper.
- **NOT harvestable, do not re-probe:** Idaho IOGA · NM NMCOG · Utah UOGA · NY NYSOGA · Oregon OOGA
  · WA WOGA · Colorado DPO · Vermont VOGA · Nevada · **Texas TREC (no email column)** · Idaho IOGLB
  · Oregon Marine Board · Alaska CBPL · Wyoming board home page.
- **Untested leads:** US Forest Service outfitter-guide permit-holder lists; chamber-of-commerce
  (GrowthZone/ChamberMaster) directories; state guide associations not yet probed (AZ, NV, SD, ND,
  NE, KS, OK, AR, MO, MN, WI, MI, PA, VA, NC, TN).
- **There is still no acquisition channel at all for the SA housecleaner market** (QUICK_LISTING_
  SPEC D5, David's, open). The product idea is strong and the way to reach her does not exist yet.

## THINGS ALREADY TRIED THAT DID NOT WORK

- Reading raw `funnel` step counts as people (they include scanners) — read `human_funnel`.
- **Instrumenting a lane without checking which URL the letters use** (RG-0405 measured `/quick/`
  while every letter points at `/q/<cat>`) — and its sequel, **assuming a lane that exists serves
  the readers you are sending to** (RG-0419: the door is ZA-only, the list is US).
- **Reading "the sends are decaying" as a fault.** Run 16 checked gates, policy, guards and the
  sender before the answer turned out to be that the list is nearly used up. Count the sendable
  pool FIRST: `wave_runner.sendable_by_category` over every city takes 90 seconds.
- Believing a ledger RED before clearing `.git/index.lock`. Two REDs, one lock (run 14).
- "Resend is unreachable from the box" (run 13) — wrong; it answers 200 in 0.19 s.
- Pinning an assertion to today's version number or today's phrasing (run 15: RUL-133; run 16:
  RUL-104). Assert the property. A checker pinned to a constant will one day punish a correct fix.
- Backgrounding work in the device shell — `nohup`/`setsid` are both killed when the call returns.
  Run shards in the FOREGROUND, in parallel, with `wait` (8 shards ≈ 85 s).
- Opening `/admin.html` publicly. `fill_wave_gaps.py` via the queue (401). Halving the batch
  for a "measurement week" (RG-0290). US general search scraping. Trusting "wave #N logged".
  Running the ledger in one call. Probing register sites blind (curl first). Retrying a dead
  mount twice. `request_deploy.py --files <x>` (ships nothing — use `--all`, then PROBE).

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

**None of these blocks anything in flight. All are positioning or strategy, not technique.**

- **D3 — what is she called?** "Housecleaner", "domestic worker", "home help", "cleaner" carry very
  different weight in South Africa. The Quick door is labelled `homehelp` today.
- **D4 — do the South African letters get re-aimed at the Quick door** as the primary call to
  action, rather than sitting as a strip under a "list your business" letter written for companies?
- **D5 — where does she come from at all?** We have no list of housecleaners and no directory to
  harvest. This decides whether the redirection is a four-week or a four-month move.
- **NEW, D8 — the 1,114 teachers on the education register.** They are the single largest reachable
  block left and they are held by `blocked_categories` as a person-only/POPIA call, not by anything
  technical. Whether they may be written to is yours, not mine.

**One thing David should KNOW, not decide:** the cold list has 466 addresses left in it. On measured
performance that is not 20 listings, and it is very likely 0. Nothing is blocked; the letter is
rewritten and shipping; the employer lane is the only route to the goal still open.

## WHAT RUN 16 LEARNED ABOUT ITSELF

**A wrong hypothesis that survives one check will survive ten.** This run nearly built a
country-neutral Quick-door link into the Maine letter on the strength of a correct-sounding chain:
the door is instrumented, the letters should point at it, the strip is fenced ZA-only, therefore
unfence the door. Every step was true and the conclusion was wrong, because nobody had opened the
door itself. One fetch of the live page — rand price chips, Gauteng suburb tiles — killed it in
thirty seconds and turned a bad build into a real finding. **The cheapest step in the chain was the
one nobody had taken.** Same shape as run 15's stale dashboard: PROBED beats READ, and the thing
most worth probing is the assumption the whole plan rests on.

**A truncated tool output is not evidence of absence — and I nearly shipped a fix on one.** Late in
the run I grepped `deploy_citylauncher.bat` for the letter I had just rewritten, saw it was not in
the output, and concluded the deploy would print SHIPPED while the wave sent the old copy. It was a
real-sounding finding of exactly the shape this run had already produced twice. It was wrong: my
grep was `| head -20` and the filename sits below the cut, added by WAVE-SERVER-1 on 18 Sep for
this very reason. **Two minutes from editing a deploy script that was not broken** — run 15's
"verify before you fix", and the reason it is worth writing down twice is that the false finding
felt exactly like the two true ones. The salvage was to assert the PROPERTY instead: every template
`emailer.py` can select must be on the list the deploy ships. That list is hand-typed and has gone
stale before, so the assertion is worth more than the edit would have been.

**And the board is a colleague, not a gate.** It caught two of my own errors tonight and one of them
— a CSS class name matching where I meant a div — I had already convinced myself was a false
positive. It was not. Read the red before arguing with it.
