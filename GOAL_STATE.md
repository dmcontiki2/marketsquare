# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Under 100 lines: it is a state file, not a
diary — the changelog is the diary.*

---

> **READ FIRST, RUN 16.** Nothing is waiting on David. `DECISIONS_2026-09-18_EVENING.md` is DONE
> (run 15). The trajectory warning below is the thing to read before choosing what to do.

## NOTE FOR THE 20 SEP SUNDAY SUMMARY (this is the next run's one required deliverable)

Write it from the RUN 14 and RUN 15 numbers below and from nothing dated before 18 Sep — every
"N people landed / N dwelled" figure older than that counted mail scanners as people. The honest
chain is in "WHERE THE FUNNEL ACTUALLY LEAKS". Say plainly: the number is 0, the letter is the
leak, and 20 by 31 October is not reachable on how the letter performs today.

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`
If the sandbox is dead, run it host-side: queue `run_py MarketSquare\scripts\onboarding_number.py`.

| date | published by own hand | probe A | probe B | notes |
|------|----------------------|---------|---------|-------|
| 2026-09-04 → 08 (runs 1–7) | **0** | 0 | 0 | baseline; raw 2 = e2e_test seeds, barred by §3 |
| 2026-09-09/10 (runs 8–10) | **unknown** | — | — | NOT MEASURED: sandbox dead (KB5124008) |
| 2026-09-12 (run 11) | **0** | 0 | 0 | 6,748 on the list · 1,482 emailed · 5 registered |
| 2026-09-13 (run 12) | **0** | 0 | 0 | 1,482 emailed at 01:00, +108 at 01:31 · 5 registered |
| 2026-09-18 (run 13, 02:30) | **0** | 0 | 0 | 1,942 emailed · **25 registered** · first full journey walked |
| 2026-09-18 (run 14, 12:20) | **0** | 0 | 0 | 2,491 emailed · 25 registered · **8 human clicks ever** |
| 2026-09-19 (run 15, 01:00) | **0** | 0 | 0 | 6,748 · **2,499 emailed · 40 registered** (was 25) · listing 382 still a draft |

Target: **20 by Fri 31 Oct 2026.** Runs 5–8, 11, 12 Fable 5.1; runs 9–10, 13–15 Opus 5.

## WHERE THE FUNNEL ACTUALLY LEAKS (probed 18 Sep, still the truth) — READ THIS, NOT AN OLD SECTION

    2,499 letters  ->  ~330 real people opened one  ->  8 clicked  ->  1 built a complete advert  ->  0 published

- Read `human_funnel` / `letter_humans`, **never** raw `funnel` (FUNNEL-DENOM-1): the raw step
  counts include mail scanners. The Quick door now reports too — `q_door`, `q_step_<n>`,
  `q_draft`, `q_handover`, and from run 15 `q_wa_self` / `q_wa_copy`.
- **The loss is between reading the letter and clicking it: 8 clicks from ~320 human opens
  (2.4%).** That is the one big measurable leak, and rewriting the letter is mine (§5).
- **The app is not the bottleneck.** Of the 8 who clicked, 1 built an advert scoring 94.
- Letters do reach inboxes — Resend, verified subdomain, `api.resend.com` answers in 0.19 s.

**THE TRAJECTORY, STATED PLAINLY (ONBOARDING_GOAL §9).** 4,249 letters remain unsent. At the
measured rate they yield roughly **14 more human clicks and perhaps 2 more finished adverts**.
**20 by 31 October is not reachable on how the letter currently performs** — it needs the
open→click rate to go from 2.4% to ~20%, or a different channel. NOT a BLOCKED state: nothing
reserved is in the way and the letter is mine to rewrite. Stated now, not on 31 October.

## WHAT RUN 15 DID (19 Sep 2026, 01:00–04:00 SAST, Opus 5) — DAVID'S EIGHT DECISIONS ARE NOW MACHINERY

1. **Measured.** 0, both probes agree. 2,499 emailed, **40 registered (was 25)** — the only
   number that moved this week. Listing 382 is STILL a draft; publishing it is his act, and he
   has had a working link and a working path behind it since 18 Sep 07:29. **Do not chase him.**
2. **Decisions 1–8 → RUL-142 … RUL-149**, reflected in `QUICK_LISTING_SPEC.md` (§1 ladder, §6
   rules, §8 WhatsApp verbatim, §9 taxi drop, §10 glimpse). `rulings_check`: 126, **0 FAIL**.
3. **BUILT AND PROVEN — WA-SELFSEND-1 / RG-0408.** The Quick hand-back screen now offers "Send it
   to myself on WhatsApp" on the numberless `wa.me/?text=` link. This is the Montana problem
   answered for a market with no email. **Walked end to end in a real browser at phone width as a
   stranger** — door → 5 taps → draft → the one email ask → hand-over → the button — with every
   beacon firing. **The message carries no sign-in token, deliberately:** the emailed link may
   carry one because arriving in that inbox proves the address is the reader's; a token handed
   back to whoever typed an address proves nothing and would mint a sign-in for anybody.
4. **RG-0407 WA-NONUMBER-1 (LOCKED)** — every WhatsApp link the app emits is numberless and no
   code path stores a recipient number. The two URL shapes are one character apart. It also
   fences the reserved half of RUL-146 (Business API = money = David's).
5. **EULA v1.17 landed** in `canon.yml` + `LEGAL_VERSIONS.md`. The RUL-133 FAIL was a **literal
   version pin** on a living document; corrected to assert the property, with the real check now
   in **RG-0406 EULA-VERSION-LAND-1**, which compares the four stamps to each other and was
   proven red in both failure directions before locking.
6. **The stale CityLauncher dashboard closed BY PROBE, not by deploying over it** — the live page
   is md5-identical to the repo copy and carries the STATS-HUMAN-1 markers. Another lane fixed it.
7. **THE FINDING OF THE RUN — RG-0413 DOOR-FUNNEL-1. The door the letters point at was the
   dark one.** The eight live outreach templates link to `trustsquare.co/q/<cat>`, which serves
   `genie/q_index.html` — an older fork of the composer. **PROBED on the live page: `typeof
   qTrack` was `undefined`.** Not one beacon, ever. QUICK-FUNNEL-1 (18 Sep) instrumented
   `quick.html`, served at `/quick/`, and was written up as "the Quick door is not dark" — so
   every figure anybody had about arrivals at the Quick door was measured on a page cold
   recipients never see. Instrumented tonight and proven in a real browser: a full walk posts
   `q_door, q_step_1..5, q_draft, q_handover, q_signin_sent`; a render with no human input posts
   `q_door` alone; one scroll plus twelve seconds adds `dwell`.
8. **Also learned, and it corrects a wrong first reading:** that door **cannot** write a listing,
   and that is deliberate and right — no API key may live in a public page, so it keeps the
   answers in `localStorage` and emails a sign-in link. It is not broken. But its only way back
   is email plus one browser's storage, which is precisely what this market lacks — **RG-0414
   DOOR-RETURN-1**, open, with the warning not to paste the `/quick/` WhatsApp button onto it,
   because here there is no server-side draft for it to point at.
9. **Ledger green before and after** (shards + `--combine=8`): every locked fix holding.
10. **Deployed twice and PROBED both times** (a deploy tool that prints a success line is
   EXECUTED, not PROBED — run 14's lesson). `/quick/` carries WA-SELFSEND-1, `/q/homehelp`
   carries DOOR-FUNNEL-1, and a live walk of the door had every beacon accepted 200 by the
   server. **That walk was made with `?src=probe-run15`** so the row is identifiable — exclude
   it before reporting the door's first real numbers.

## DIRECTION CHANGED AGAIN — DAVID, 19 SEP 2026 (live session). READ THIS FIRST.

**The acquisition gap (D5) is answered, and it changes what "next" means.** David's direction:
add every casual and technical role under **Services-Casuals / Services-Technical**, add the
**employer side**, and *"use these service types to enrol their current employees or previous
employees as referrals."* **RUL-150, RUL-151, RUL-152.** The plan is `QUICK_LISTING_SPEC.md`
**Part II** — read it before choosing any work.

- **The employer is the SUPPLY channel, not just a demand side.** 8 human clicks per 2,499 cold
  letters versus one mine's HR department. An institution's confirmation is worth more than a
  household's, and it satisfies the Casuals reference signals at source.
- **Most of it is already built and is called `agencies`** — `create_agency`, `invite_agent`
  (account + cap + magic link, **creates no listing**), `set_agency_verified`, tier sync, rollup.
  Generalise it; do not rebuild it.
- **The hard line: enrollment NEVER creates a listing** (ONBOARDING_GOAL s3). Build the importer so
  it cannot, and assert that in the ledger.
- **The letter is no longer first.** One employer door is worth more than every letter left on the
  list — but opening it is a human conversation, and that is the one genuine hand-off in the plan.
- **RUL-152: stop quoting RUL-075 (or any ruling) back at David as a blocker.** Ask what the rule
  was protecting; if the request does not threaten it, the ruling is silent.

## WHAT THE NEXT RUN SHOULD PICK UP

1. **Write the Sunday summary** (see the note at the top). That is the one required deliverable.
2. Run the number. Read `human_funnel` / `letter_humans` and the `q_*` beacons.
3. Ledger in shards (`--shard=k/8`, then `--combine=8`) + `rulings_check`. If the board opens RED,
   clear `.git/index.lock` with `scripts/git_unlock.py` and re-run **before** believing it.
4. **Then the letter.** It is the one measurable leak, it is mine, and run 14 deferred it, run 15
   deferred it for David's decisions. It should not be deferred a third time.
5. **Read the door's beacons for the first time.** From tonight `/q/<cat>` reports `q_door`,
   `q_step_<n>`, `q_draft`, `q_handover`, `q_signin_sent` and `dwell`. The nightly wave fires at
   00:10 SAST, so the first real numbers for the lane that carries every cold arrival land within
   a day. **Read them against `dwell`, never raw.** Also watch `q_wa_self` on `/quick/` — it is a
   hypothesis about a market, not a fact, and if nobody taps it, say so.
6. **RG-0414 DOOR-RETURN-1 is the next real build** and probably the highest-value one left
   inside this authority: a way back from the public door that does not need an inbox.
7. The four new OPEN entries carry David's unbuilt decisions with the reason each was deferred:
   **RG-0409** ladder values + cap 40 (a scoring change, four hardcoded caps, and NOT on the
   critical path — publishing does not depend on the score) · **RG-0410** reachability gate +
   post-confirm glimpse · **RG-0411** taxi-drop area unit · **RG-0412** EULA in the launch
   languages (**must wait on RG-0400**, or four EULA copies become twenty).

## OPEN LOOPS

- **RG-0400 (open): the EULA a seller actually ticks is a FOURTH, unsynced copy** — `sob-eula-box`
  in marketsquare.html reads v1.10 while the site publishes v1.17. Restyled markup, not a byte
  copy, so there is no safe mechanical sync; the real fix is rendering the box from the one
  source. Needs its own session and eyes on the rendered result. **Blocks RG-0412.**
- `_get_json()` still does not exist (specified by run 13, unwritten). RG-0401 covers most of it;
  14 `json.loads(_get(...))` sites remain individually unprotected against a 200 that is not JSON.
- The ledger's `rg_no_third_party_script_on_surface` downloads ~16 MB per run — why shard 1 is slow.
- `marketsquare.html` reports `[TORN]` to `mount_guard.py` as "mount LARGER than committed but
  git-clean". Probably CRLF normalisation, not a tear — but **never bash-write that file**.
- Listing 386/387/388 ARCHIVED not deleted; 2 files in `_to_delete/` and 9 orphaned `tmp_obj`
  files need a deletion, which is David's (`git_unlock.bat` sweeps the tmp_objs).
- RG-0346 (agency letters lack the console CTA) — open, adds no nightly volume.
- Film 07 (Liquidation) unpublished — David's click, when he chooses.

## SUPPLY — ASSOCIATION LANE NEARLY DONE; LICENCE FILES CARRY NO MAILBOX

- Harvested + drawn: rrca, pacific, moga, wyoga, coa, apha, mpga. New association = one dict entry
  in `CityLauncher/us_register_assoc.py`; run via `run_us_registers.bat`. ZA Durban/PMB rows =
  blocked category, 0 sendable.
- **NOT harvestable, do not re-probe:** Idaho IOGA · NM NMCOG · Utah UOGA · NY NYSOGA · Oregon OOGA
  · WA WOGA · Colorado DPO · Vermont VOGA · Nevada · **Texas TREC (no email column)** · Idaho IOGLB
  · Oregon Marine Board · Alaska CBPL · Wyoming board home page.
- **Working kinds:** member directories that PUBLISH a mailbox. Untested leads: US Forest Service
  outfitter-guide permit-holder lists; chamber-of-commerce (GrowthZone/ChamberMaster) directories;
  state guide associations not yet probed (AZ, NV, SD, ND, NE, KS, OK, AR, MO, MN, WI, MI, PA, VA,
  NC, TN).
- **There is still no acquisition channel at all for the SA housecleaner market** (QUICK_LISTING_
  SPEC D5, David's, open). The product idea is strong and the way to reach her does not exist yet.

## THINGS ALREADY TRIED THAT DID NOT WORK

- Reading raw `funnel` step counts as people (they include scanners) — read `human_funnel`.
- **Instrumenting a lane without checking which URL the letters use.** RG-0405 measured
  `quick.html` (`/quick/`) while every letter points at `/q/<cat>` (`genie/q_index.html`). Open a
  live letter, follow the link, and check `typeof qTrack` on the page it actually opens.
- Believing a ledger RED before clearing `.git/index.lock`. Two REDs, one lock (run 14).
- `request_deploy.py --files <x>` — it does not commit and ships nothing. Use `--all`, then PROBE.
- "Resend is unreachable from the box" (run 13) — wrong; it answers 200 in 0.19 s.
- Pinning an assertion to today's version number (run 15: RUL-133 FAILed on a correct bump).
- Backgrounding work in the device shell — `nohup`/`setsid` are both killed when the call returns.
  Run shards in the FOREGROUND, in parallel, with `wait` (7 shards ≈ 75 s).
- Opening `/admin.html` publicly. `fill_wave_gaps.py` via the queue (401). Reading "no sendable
  prospects" as supply (check `armed`/`gates_green`/`disarmed_by` FIRST). Halving the batch for a
  "measurement week" (RG-0290). US general search scraping. Trusting "wave #N logged". Running the
  ledger in one call. Probing register sites blind (curl first). Retrying a dead mount twice.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

**Three, all from QUICK_LISTING_SPEC.md §4, all positioning or strategy rather than technique —
and none of them blocks anything currently in flight:**

- **D3 — what is she called?** "Housecleaner", "domestic worker", "home help", "cleaner" carry
  very different weight in South Africa. The Quick door is labelled `homehelp` today.
- **D4 — do the South African letters get re-aimed at the Quick door** as the primary call to
  action, rather than sitting as a strip under a "list your business" letter written for companies?
- **D5 — where does she come from at all?** We have no list of housecleaners and no directory to
  harvest. This decides whether the redirection is a four-week or a four-month move.

**One thing David should KNOW, not decide:** on how the letter performs today, 20 by 31 October is
not reachable through that channel. Nothing is blocked; the letter is mine and is next.

## WHAT RUN 15 LEARNED ABOUT ITSELF

**A checker pinned to today's value will one day punish the correct answer.** `rulings_check`
FAILed RUL-133 because the EULA had legitimately moved to v1.17 and the assertion demanded the
literal "v1.16" — the Buzz clause the ruling is actually about was perfectly intact. The cheap cure
is to revert the good change until the checker is quiet, and it would have been indistinguishable
from diligence. Assert the PROPERTY (do the four stamps agree?), never the constant. Same class as
EULA-ANCHOR-1, and worth a look wherever else a literal is standing in for a rule.

**And: verify before you fix.** Two items were handed to this run as work. One — the half-landed
EULA — was real. The other — the stale dashboard — had already been fixed by another lane, and
"refresh it through the normal lanes" would have deployed over a good page on the strength of a
note written the day before. One md5 settled it. PROBED beats READ, including when what you are
reading is your own predecessor's handover.
