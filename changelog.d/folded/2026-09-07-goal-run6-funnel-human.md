## 2026-09-07 — FUNNEL-HUMAN-1 + LEDGER-SLICES-1 + MOGA-1 (onboarding-goal run 6, 01:00–02:10 SAST)

**The number: 0** (probe A 0, probe B 0; raw 2 are the e2e seeds, barred). Model: Fable 5.1.

**The wave went, cleanly.** 00:10 SAST: 251 real sends, 0 crashes, across Cape Town (12) and 23 US
state buckets; the ramp doubled to 24 for the three buckets with a clean wave #1 (Northern California,
California, Illinois). 12 more states had their first wave; 17 states (North Carolina → Wyoming, 166
letters) dry-ran on the 250/day cap and go tonight. Bounces so far on the 6 Sep US club wave (203): **0**.
On tonight's 251: 7 so far (2.8%). The domain gate now has its 50 post-clean sends and reads under 5%.
Pretoria, Durban, PE, Kimberley, New York, Sydney drew nothing: the planner prints "-" for their pool
without saying why (Pretoria's club:agn is now 4 bounces in 24 — the source gate, most likely). The
plan output should name the source-gate verdict; it does not yet.

**FUNNEL-HUMAN-1 — the funnel was counting link scanners as sellers.** Yesterday's reading "9 clubs
reached the photo step, none picked a photo" was about to become "they stop at the required photo" in
GOAL_STATE and the plan. PROBED on the server: every one of those 9 sessions was created 20–40 s after
its wave's send time, in bursts of 4 within 8 s (kansas 23:42:20–56Z; northern-california 22:11:29–37Z
against a 22:10:58Z send), and nginx showed 15 `POST /onboard/step` from **Google-Safety** user agents
in the window — a scanner that renders the page, runs our JS and posts `landed` + `photos`. The `yt-*`
"landings" (3–4 per film within seconds of each posting) are the same class. **True humans at the photo
step: 0. True humans landed from the club letters: unknown — the instrument could not tell.**
Fix, shipped twice tonight (relay → live, health-checked): `/onboard/step` stores the user agent and a
bot verdict (same vocabulary `click_register.py` grades email clicks with, plus google-safety); `GET
/onboard/funnel` excludes bot rows AND ungraded pre-column rows unless `bots=1`, and returns `humans` =
sessions that fired the new `dwell` beacon (ms.js: 12 s on the page AND a real pointer/key/touch/scroll
event — a scanner does neither). Live now: `sessions 0 · humans 0 · ungraded 60`. From tonight's wave
on, the funnel's denominator is people. RG-0315 LOCKED (live probe with a Google-Safety UA must be
hidden by default and visible with bots=1); RG-0293's read adjusted to `bots=1` (its own probe is a
machine, correctly flagged).

**LEDGER-SLICES-1 — the ledger could not be run from the sandbox at all.** The bash call cap is now
~178 s (GOAL_STATE said "foreground, ~6 min, timeout 560 s"); a backgrounded run dies with the call;
running it on the server produced 45 false reds (different environment). `scripts/ledger_slices.py`
runs the same LEDGER in N slices (state in the outputs dir), `--report` merges them with the ledger's
own exit codes and names any missing slice. Before: 308 entries, 4 REGRESSED (RG-0154 counter behind,
RG-0187 a hand-rolled subprocess in RG-0308, RG-0194 LF-only .ps1, and the new RG-0315 pre-deploy).
After: **311 entries · 289 holding · 0 REGRESSED · 22 open · 0 unverified.** Fixes: session counter
written (191); `_harness(full=True)` so RG-0308 reads the tool's first-line count through the
dependency-aware path (LEDGER-HARNESS-FULL-1); `install_hetzner_s3.ps1` → CRLF. rulings_check: 0 FAIL.

**RUL-103 check re-pinned.** It required the literal "on disk, unpublished", true on 5 Sep and false
from 6 Sep (David published nine films). LAUNCH_SERIES.md now says so (nine LIVE since 6 Sep, only 07
Liquidation on disk; advanced features approved 00:19 7 Sep so links are clickable); the assertion
checks the standing fact and forbids "| idea |" for a made film.

**MOGA-1 — supply, US, a register.** Probed 14 candidate register pages from the sandbox; one carried
addresses: the **Montana Outfitters & Guides Association** member directory — 199 licensed outfitters
with a mailbox on one page (embedded JSON). Adapter `moga` added to `us_register_reader.py`, harvested
to `us_registers/moga.club.csv` (199 rows, source `register:moga`, category `adventures_experiences`,
bucket Montana, town in suburb); `run_us_registers.bat` carries it; import queued. **Caught before it
mattered:** the CSV had no category column and `club_import.py` defaults to Sports Clubs — the club
letter ("I found your club on your federation's club list") would have gone to hunting outfitters. The
CSV now names its category; RG-0316 LOCKED. The lane is COLLECTED, NOT DRAWN: the adventures letter
predates RUL-099 and lacks the "where we got your address" line, so Montana's priority stays Sports
Clubs — RG-0317 OPEN prints READY TO LOCK when the letter is in shape and the bucket lists the category.
Dead ends this run (do not re-check): orienteeringusa, skifederation, americancanoe, americanhiking,
ioga.org/members (404), usatfmn/usatf-oregon/adventurecycling (no emails), usatf GA/NJ/IN (dead).

**Pool after tonight:** US Sports Clubs uncontacted 815 (Massachusetts 213, Texas 57, California 55…)
≈ 3–4 sending nights at 250/day. Then the US club lane is dry and the next register must already be in.
