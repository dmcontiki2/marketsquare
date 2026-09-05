## 2026-09-05 — Run 4 of the onboarding goal: the funnel gets an instrument, the first club wave goes, and two tooling faults come out (ONBOARD-FUNNEL-1, COMMIT-CWD-1)

Scheduled run, 19:00 SAST, on Fable 5.1 as David asked. The number: **0**, both probes agree,
raw 2 = the two seed rows the contract bars.

**The finding.** Since the fixed link went live on 3 Sep, about ten real people had clicked
through to a working page. Zero registered — `marketsquare.users` has no non-test row since
25 Aug. Zero published. The leak is click → register, before a listing exists. Walked the
invited path in a browser: the magic link lands on Step 1 of 6, Photos, "You on the job" is
required and the next button is disabled until the AI accepts the photo. That is David's
photo-first ruling (SELL-FLOW-REDO-2, 15 Jul; reaffirmed 29 Aug) and it was not touched.
What was missing was any way to know whether people stop AT the photo, BEFORE it, or later.

**ONBOARD-FUNNEL-1 — built, shipped, probed live at 19:29.** `POST /onboard/step` (anonymous,
capped per session, always 200) and `GET /onboard/funnel` (distinct sessions per step, split
by wave source and category — counts only, never an address). `ms.js` posts one beacon per
transition: landing (with the wave `src` from the magic link, which the parser had been
dropping), every screen, photo picked / accepted / rejected / fallback, draft, finish,
handoff, publish ok/fail. Probe sources (`probe-*`) are excluded from the default view so
the ledger can post one without polluting the numbers. Verified end to end the same evening:
a browser session walking landed → subpick → photos produced exactly those three rows under
its probe source and nothing under the default view. **RG-0293** locks all three legs.

**The first-ever club wave.** Pretoria's 197 club contacts had been imported after the
morning wave found the city empty, and Pretoria had not sent today — its one-day gap was
clear. Queued `launch_day_wave.bat`; at 19:31 Pretoria sent 12 Sports Clubs emails (real),
six other cities dry-ran on the gap as designed. The skip-empty filter worked on the host:
7 cities visited, not 43.

**The first US general scrape, measured.** `run_us_scraper.bat` ran 11 cities × 7 categories
for 33 minutes and found **one** address — `info@antiques-vintages.co.za`, a South African
shop filed under Austin. The scraper's browser canary passed; the queries simply return no
addresses for US cities. General search scraping is structurally dead for the US.
ONBOARDING_PLAN.md §3 now says so; registers are the supply engine (US-REGISTERS-1, the
parallel session, imported 88 USATF Pacific clubs the same hour).

**COMMIT-CWD-1.** Reading the queue results: the 18:51 "CityLauncher commit" reported rc=0
and pushed to `marketsquare.git`. `CityLauncher\commit.bat` CALLs `MarketSquare\git_unlock.bat`,
which does `cd /d "%~dp0"` and never comes back, so every git command after the call ran in
MarketSquare. CityLauncher's own repo still sat at 3 Sep with 10+ modified files — the
emailer guards, wave_cities.py, club_import.py, the US scraper — uncommitted and unpushed
since the bat was created. One line: re-enter `%~dp0` after the call. **RG-0294** asserts the
class (a helper that changes directory poisons every caller).

**HELP-IS-NOT-A-DEPLOY.** `request_deploy.py --help` fell through and shipped HEAD. It did,
once, this run — already-committed work, health-checked, no harm — and now prints usage.

**Recorded for the next run.** A parallel interactive session was live during this run,
editing the US register files; this run stayed out of them. The sandbox kills background
processes when a call ends, so the ledger must run in the foreground (~6 min). The local
`prospects.db` is often mid-write on the host (scraper, importer, wave) and then unreadable
from the sandbox — read the server copy over SSH instead.

Ledger before/after: 0 regressions, 18 open (RG-0288 click→publish still unmeasured — a fact
about the world, not a defect). Rulings check: 0 fail.
