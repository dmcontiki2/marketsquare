# GOAL_FACTS — durable reference for the onboarding goal (RUL-096)

*Split out of GOAL_STATE.md on 23 Sep 2026 (run 17), on run 16's instruction. GOAL_STATE is
STATE — the number, the last run, the next run. This file is REFERENCE — things that stay true
across runs. Read GOAL_STATE first, every run; read this one when you need the background.*

---

## WHERE THE FUNNEL LEAKS

    2,549 letters  ->  ~330 real people opened one  ->  8 clicked  ->  1 built an advert  ->  0 published

- Read `human_funnel` / `letter_humans`, **never** raw `funnel` (FUNNEL-DENOM-1): raw counts
  include mail scanners. Over 30 days `letter_humans` is **2** — arrived on an outreach link
  AND stayed.
- The open->click loss (8 from ~330) was run 16's target and is real.
- **THE BIGGEST LEAK IS THE LAST STEP, and run 17 found it.** Of the 8 who clicked, 1 built a
  complete advert — four of his own photographs, quality 94 — and it is still a draft. The
  wizard lets a stranger do all the work and then asks for an account and an accepted EULA
  before it will go live. RG-0429 PUBLISH-WALL-1. David already ruled the shape (RUL-145):
  *"After the tap, show them what they just did. NO WALL, NO ACCOUNT."*
- **The app IS the bottleneck now.** Runs 13–16 said it was not, on the strength of one person
  reaching an advert. That same person is the evidence that it is.
- Letters do reach inboxes — Resend, verified subdomain, answers in 0.19 s.

## THE ONBOARDED NUMBER IS NOT THE REGISTERED NUMBER (run 17, RG-0428)

**Never quote a "registered" figure without checking it is not our own mailer.** The reconciler
stamped `prospects.onboarded_at` whenever the address appeared in `marketsquare.users`, and
`/agencies/wave-prep` creates one of those rows **at send time** for every agency-class
prospect. So 42, then 45, "registrations" were 40 estate agents created in the 22:10 UTC wave
minute, none of which has ever been opened, used, or had terms accepted. The honest figure was
one. Same class as FUNNEL-DENOM-1. Fixed 23 Sep; the guard is RG-0428, which RUNS the reconciler
over a synthetic pair rather than grepping it.

## THE SUPPLY FLOOR — cold email runs out this month

**466 addresses were sendable anywhere in the world on 20 Sep; 2,549 had been emailed by 23 Sep,
so roughly 416 remain (derived, not re-probed).** PROBED on 20 Sep by running the wave's own
composer over all 102 cities:

    6,748 on the list -> 2,499 already emailed -> 2,055 scraped rows in armed cities
      -> minus sources our own send history condemns (openstreetmap 10.6%, google_maps 7.0%,
         club:agn 12.5%, club:wpa 11.1%, usatf-new-england 40% — the 5% stop-loss is correct)
      -> minus info@ desks (216), second mailboxes at a firm already written to (225+89),
         government domains (37), placeholder names (15)  ->  466

- **All armed cities gate GREEN. Nothing is stuck.** The decay from ~398 to ~17-43 a night is
  CONSUMPTION, not a fault. Runs 16 and 17 both checked. Count the sendable pool FIRST:
  `wave_runner.sendable_by_category` over every city takes 90 seconds.
- **Do not raise the batch to empty the list faster** — RAMP-1 and the 250/day cap protect the
  sending domain (RUL-111), and the trade buys about one click.
- Where the 466 sat on 20 Sep: **Maine 428** · Pretoria 20 · Cape Town 6 · Durban 4 ·
  Johannesburg 3 · rest 5. **92% of what is left is in the United States.**
- `teachers_trainers` (1,114 rows on dbe_emis) is held by **blocked_categories** — a
  person-only/POPIA decision, David's, not a technique.
- **RUL-106 is the fence around all of this:** a 60-day floor on re-contacting ANY address
  already written to, whatever the lane, enforced in `emailer.send_email` (RECONTACT-1). The
  only door is `TS_RECONTACT_PERMISSION`, dated, from David. RUL-106(e) reserves any follow-up
  programme to him explicitly. **A nudge to someone who stalled is a follow-up programme.**

## SUPPLY — THE ASSOCIATION LANE IS THE ONLY ONE STILL PRODUCING

- Harvested + drawn: rrca, pacific, moga, wyoga, coa, apha, mpga. New association = one dict
  entry in `CityLauncher/us_register_assoc.py`; run via `run_us_registers.bat`.
- **Registers are the best addresses we own** — rrca 2.55%, mpga 2.5%, moga 2.63%, apha 0%
  bounce, against 7–12% for every scraped source. A new register is worth more than a new
  scraper. *The one man who has come closest to publishing came from `register:moga`.*
- **NOT harvestable, do not re-probe:** Idaho IOGA · NM NMCOG · Utah UOGA · NY NYSOGA · Oregon
  OOGA · WA WOGA · Colorado DPO · Vermont VOGA · Nevada · **Texas TREC (no email column)** ·
  Idaho IOGLB · Oregon Marine Board · Alaska CBPL · Wyoming board home page.
- **Untested leads:** US Forest Service outfitter-guide permit-holder lists; chamber-of-commerce
  (GrowthZone/ChamberMaster) directories; state guide associations not yet probed (AZ, NV, SD,
  ND, NE, KS, OK, AR, MO, MN, WI, MI, PA, VA, NC, TN).
- **There is still no acquisition channel at all for the SA housecleaner market**
  (QUICK_LISTING_SPEC D5, David's, open).

## THE QUICK DOOR IS A SOUTH AFRICAN PRODUCT (RG-0419, run 16)

PROBED on the live page: every price chip is in rands (R250–R450 a day), suburb tiles are
Menlyn and Midrand; `localize_html()` proves the US render carries no door strip and no `/q/`
link at all. The ZA-ONLY fence is RIGHT and must not be removed. Consequence: the five-tap lane
serves none of the US addresses left, and the `q_*` beacons will stay near zero however well the
letters perform. Near-zero there is EXPECTED, not a fault.

## THINGS ALREADY TRIED THAT DID NOT WORK

- Reading raw `funnel` step counts as people (they include scanners) — read `human_funnel`.
- **Reading a count of accounts as a count of people** (run 17, RG-0428) — our own mailer makes
  accounts. Ask what CREATES the row before you believe what it means.
- **Instrumenting a lane without checking which URL the letters use** (RG-0405 measured
  `/quick/` while every letter points at `/q/<cat>`) — and its sequel, **assuming a lane that
  exists serves the readers you are sending to** (RG-0419: the door is ZA-only, the list is US).
- **Reading "the sends are decaying" as a fault.** Twice now. It is consumption.
- **Reading a quiet log as a dead agent** (run 17, nearly): `autodeploy_agent_log.txt` had not
  been appended to for 3.5 days and the agent was perfectly alive — it only logs when it has
  work. The liveness instrument is `host_queue/agent_heartbeat.txt`, stamped every tick.
  RG-0355 already says this in writing; read it before raising the alarm.
- **Believing a RED from a checker that reads a file another lane is writing.** rulings_check
  returned 1 FAIL, then 2 FAIL, then 0/0/0 within minutes with no edit between (RG-0437).
  Also: believing a ledger RED before clearing `.git/index.lock` (two REDs, one lock, run 14).
- "Resend is unreachable from the box" (run 13) — wrong; it answers 200 in 0.19 s.
- Pinning an assertion to today's version number or today's phrasing (RUL-133, RUL-104).
  Assert the property. A checker pinned to a constant will one day punish a correct fix.
- Backgrounding work in the device shell — `nohup`/`setsid` are killed when the call returns.
  Run shards in the FOREGROUND, in parallel, with `wait` (8 shards is about 2 minutes, and the
  device_bash call needs `timeout_ms` raised to 180000 or it is cut off at 120 s).
- Opening `/admin.html` publicly. `fill_wave_gaps.py` via the queue (401). Halving the batch for
  a "measurement week" (RG-0290). US general search scraping. Trusting "wave #N logged".
  Running the ledger in one call. Probing register sites blind (curl first). Retrying a dead
  mount twice. `request_deploy.py --files <x>` (ships nothing — use `--all`, then PROBE).

## WHEN SSH TO THE ORIGIN DIES (it will again)

Port 22 to 178.104.73.239 is allowlisted per-IP at Hetzner. **Two vantages now leave by
different addresses** — David's PC and this sandbox — and SANDBOX-EGRESS-1 (23 Sep) makes the
sandbox lane ADD-ONLY so it cannot prune the host out. Cure: `python3
scripts/hetzner_fw_selfheal.py` (token in `.secrets/hetzner_token.txt`), then wait — run 17 saw
the rule already correct while port 22 still timed out, and it answered minutes later. **Check
the rule before believing RG-0099's advice to add the IP; it may already be there.** Discriminate
with a control host: if github.com:22 also times out from the same shell, the block is local
egress, not Hetzner. When SSH is genuinely gone, the number still runs host-side:
`python3 scripts/request_host_action.py run_py "MarketSquare\\scripts\\onboarding_number.py"`.
