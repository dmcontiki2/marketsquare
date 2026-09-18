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

Target: **20 by Fri 31 Oct 2026.** Model: runs 5–8, 11, 12 Fable 5.1; runs 9–10 Opus 5 (drift, RUL-096h).

## WHAT RUN 13 DID (18 Sep 2026, 02:30-03:20 SAST, Opus 5) - THE FIRST REAL PERSON WAS FOUND, AND LOST

1. **Measured.** Number 0, both probes agree. Rulings 0 FAIL. Ledger green at the start except
   one flaky RED (see OPEN LOOPS below); green at the end, RG-0395 new and LOCKED.
2. **FOUND THE PERSON.** `/onboard/funnel?days=6`: 15 humans, and one session from
   `montana-adventures-experiences-20260912` walked **the entire journey** - landed, dwell, subpick,
   photos, photo_pick, photo_ok, features, legal, scorecard, finish, handoff. PROBED on the box:
   that is **listing 382**, "Guided Fair Chase Hunts", Victor Montana, $500-1000/person, a photo,
   a 998-character description, **quality score 94** - better than most rows that are live. Its
   author is **prospect 83302**, source `register:moga` (Montana Outfitters & Guides), emailed
   11 Sep 22:12. A real outfitter, from a cold letter, by his own hand.
3. **FOUND WHY HE IS NOT THE NUMBER.** He pressed a button reading **"Publish it"**, and got a
   draft plus homework: *"Finish it in the app... sign in with this address."* Then nothing. He
   has **no users row** and `create_listing` scheduled **no background task at all** - the Quick
   lane never mailed anybody. The hand-back screen was the only thing that ever named his advert
   and it died with the tab. Six days invisible. **The advert was finished; the door was missing.**
4. **FIXED IT FORWARD, SHIPPED, PROVEN LIVE (QUICK-RETURN-1 / RG-0395).** A draft composed in the
   Quick app now mails its author a link straight back to it. Deployed 02:51 via the relay
   (982c5d2, health-checked). PROVEN end-to-end on the live service, not inferred: a POST with
   `source:'quick'` produced `INFO:bea:quick-return mail for draft 386: sent` in the service log.
   Proven before ship too (7/7 on the shipped text of both functions): address normalised, advert
   named, signin token decodes for that address, copy says it is not public yet and that
   publishing is theirs, hostile title cannot inject html, junk address mails nobody, dead
   transport never breaks the hand-over.
5. **WHAT THE FIX DELIBERATELY DOES NOT DO.** It does not publish. RUL-117(c) rules the Quick app
   ends at "a draft advert (a prototype the seller then finishes)", and ONBOARDING_GOAL s3 bars
   publishing on a seller's behalf. Making "Publish it" publish would be changing a ruling, which
   is reserved - so the button's label is arguably still ahead of what it does, and **that wording
   is a question for David, not a thing to quietly change.** The gate is `source=='quick'` only,
   precisely so the agency import lane - which also lands drafts - never mails anybody.
6. **THE CLOSING ACTION WAS DONE, after David caught me leaving it.** I first parked "mail the
   Montana composer" as reserved under RUL-099. That was wrong and he said so: RUL-099 governs the
   shape of COLD LETTERS, and this man is not a cold recipient at that point - he typed his own
   address into our form to publish, and the code I had just shipped mails that exact letter,
   unreviewed, within seconds, to anyone who does what he did. Reserving the identical mail because
   he did it six days earlier was a flinch dressed as compliance. **Sent 18 Sep.**
7. **AND THE FIRST SEND WENT OUT DEAD - caught, fixed, re-sent.** The runner loaded only systemd's
   `Environment=` list, not its `EnvironmentFile=` (`/etc/marketsquare/secrets.env`), so
   `MS_JWT_SECRET` was EMPTY, the sign-in link was signed with an empty key, `_send_html_email`
   cheerfully returned **'sent'**, and the button in his mail was dead on arrival - the service
   would have told him his link had expired. Nothing anywhere went red. **Re-sent with a token
   PROVEN to verify against the running service's own secret** (sha256 of both compared, match)
   and addressed to him with `draft=382`.
   **LESSON, and it is the evidence ladder again: 'sent' is EXECUTED, not PROBED.** A mail that
   reports success is not a mail that works. Never report a link delivered without verifying the
   link.
8. **QUICK-RETURN-GUARD-1 shipped so the automatic path can never do it** (9d7af12): if
   `_JWT_SECRET` is empty the return mail is NOT sent and the error is logged loudly - fail closed,
   because a dead link is worse than no mail (it spends the one moment they open it). Proven 4/4,
   including that an empty-key token really is rejected. RG-0395 carries the assertion.
9. Residue cleared, none of it David's: listing **386** (my wiring test) ARCHIVED; the EULA drift
   another session left (terms.html behind eula_clean.html v1.17) synced, RG-0077 back to HOLDING.
   Two zero-byte scratch files sit in a gitignored `_to_delete/`; the sandbox cannot delete and
   they are invisible to git - not a task for anyone.

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

## WHERE THE FUNNEL LEAKS (PROBED 18 Sep 2026, /onboard/funnel?days=6)

30 sessions, 15 humans, 18 distinct emails. 16 landed from letters. **One walked the whole way**
(Montana, above). The rest stall early: 15 dwell, only 3 subpick. So there are now TWO leaks, and
they are different sizes:
- **The far leak is FIXED tonight**: whoever finishes now gets the way back. That was worth 1 person.
- **The near leak is untouched**: 15 dwell -> 3 subpick. Most people land, look, and do not take
  the first tap. That is the next thing to work on, and it is a wording/first-screen problem, not
  a plumbing one.

## WHAT THE NEXT RUN SHOULD PICK UP

1. Run the number. Read `/onboard/funnel?days=3` and look for a SECOND full walk - and, above all,
   for **listing 382 going live**, which is what the first real onboarding looks like.
2. Ledger in shards + rulings check. Both green at the end of run 13.
3. **The near leak: landed -> first tap.** 15 dwelled, 3 tapped. Read the first screen as a stranger
   would. This is now the biggest measurable loss in the funnel and it is inside the agent's remit.
4. Supply: probe ONE untested kind (USFS permittee PDFs or a chamber directory) with curl first.
5. The `moga` register produced the only real composer we have ever had. **Associations of working
   guides are the lane that works** - prefer more of that kind over any new geography.

## OPEN LOOPS LEFT BY RUN 13 (not fixed tonight, deliberately)

- **The ledger's live JSON probes can go RED on a network hiccup.** Shard 4 reported RG-0386
  REGRESSED with `JSONDecodeError` while the live endpoints were in fact perfect (re-probed 4/4
  clean immediately after, green on the full re-run). 14 checks do `json.loads(_get(...))`; a 200
  that is not JSON - an edge interstitial, a truncated body - becomes a FAIL and the board then says
  "Do not deploy over this". That is a false RED that can freeze the deploy lane, the S140 class
  CLAUDE.md names. FIX: one `_get_json()` that retries once and raises ProbeOffline (UNVERIFIED,
  blind) rather than FAIL when the body is not the app's JSON. Small, one helper, 14 call sites.
  Left undone tonight only because CLAUDE.md allows one fix per task and the conversion leak won.
- Listing **386** (my wiring test) and the two files in `_to_delete/` need a deletion, which is
  David's.
- RG-0346 (agency letters lack the console CTA) - still open, still adds no nightly volume.
- Film 07 (Liquidation) unpublished - David's click, when he chooses.

## THINGS ALREADY TRIED THAT DID NOT WORK

- Opening `/admin.html` publicly. `fill_wave_gaps.py` via the queue (401). Reading "no sendable
  prospects" as supply (13 Sep: it was a DISARM — check `armed`/`gates_green` in waves_policy.json and
  any `disarmed_by` stamp FIRST). Halving the batch for a "measurement week" (RG-0290). US general
  search scraping. Trusting "wave #N logged". Running the ledger in one call — use shards.
- Probing register sites blind: many .org/.gov hosts do not answer the sandbox (000). Curl first.
- Retrying a dead sandbox mount more than twice; restarting the app to cure it (proven useless).
  Assuming an official licence file carries a mailbox (Texas: it does not).

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

**None.** The one thing this run had been holding back - mailing the Montana composer - was sent.
Listing 382 is still a draft because **publishing it is his act, not ours** (ONBOARDING_GOAL s3,
RUL-117(c)); he now has a working link to it and that is the whole of what we may do.

A NOTE FOR THE NEXT SESSION, not a question: the button he pressed says **"Publish it"** and hands
back a draft. RUL-117(c) rules that app ends at a draft, so the wording is the honest thing to
change, not the behaviour - but changing what a ruled screen SAYS is still David's, so no session
should quietly reword it. Raise it once, plainly, if he asks what else is in the way.

## WHAT RUN 13 LEARNED ABOUT ITSELF (read before parking anything as 'reserved')

The reserved list is short and specific: money, deletions, sending to third parties, lockout risk,
legal/commercial positioning, launch scope and dates, changing a ruling. **Transactional mail that
completes an act a user began on our own form is not on it**, and a rule written about cold-letter
SHAPE (RUL-099) does not become a rule about service mail because both are email. Before parking
anything: ask whether the shipped product already does this exact thing unreviewed. If it does, so
may the agent. Handing David the one action with a consequence, wrapped in rule language, is the
failure this whole goal architecture (RUL-092, RUL-095) was built to end - and I reproduced it.
