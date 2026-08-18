# Journey photo generation — runbook & run state (26 Jul 2026)

## Where it stands  (updated 26 Jul 09:25)
- Photos: **54 of 104**. Cape to Cairo COMPLETE (31/31, deployed). Namibia COMPLETE
  (23/23) — adventures_na_map.html rebuilt (23 embedded/0 pending), NA UN-GATED in
  ms.js ADV_COUNTRY_MAP (syntax checked, regression ledger 0 regressions). Mozambique
  Mozambique IN PROGRESS: **5/25** (Day 1 done: d1_start/sight/food/view/over). Botswana not started (LAST — 0
  listings). Resume: photo_status --next, continue Mozambique d1_sight onward, then
  Botswana. Un-gate MZ (and BW once it has a listing) in ms.js when each set is done.
  Higgsfield queue slowed ~09:5x-10:0x then recovered; if a gen stalls past ~2 min,
  wait it out or regenerate — it clears.
- All four maps are DEPLOYED and load from `/static/adventures_{c2c,na,bw,mz}_map.html`.
  adventures_c2c_map.html rebuilt 26 Jul with all 31 photos embedded (0 pending) —
  NOT yet uploaded to the server; David runs the deploy.
- `ms.js` v387 is live: NA/BW/MZ are **gated out** of ADV_COUNTRY_MAP (they have no
  photos); live keys are ZA, US, GB, AU, DE. c2c is NOT a gated country entry — the
  Cape to Cairo map surfaces without any ms.js change, so ms.js was left untouched.
  Un-gate a country the moment its photos are done — the commented lines are right there.
- Botswana has **zero listings** live, so even un-gated its map cannot surface.
  A market needs listings before a map means anything.
- Canon for codes and market tiers: `MAP_NAMING_CANON.md`. Enforced by RG-0011.

## NEXT ACTION (start here)
Cape to Cairo DONE. Next: Namibia (23), Botswana (25), Mozambique (25) = 73 photos.
Prompts are in JOURNEY_HIGGSFIELD_PROMPTS.md;
`python3 scripts/photo_status.py --next 10` lists the exact filenames still missing.

## Original notes
4 of 104 photos generated and placed, all in Cape to Cairo:
`l1_start` (Cape Town platform) · `l1_food` (dining-car bobotie) ·
`l1_view` (winelands) · `l1_over` (sleeper cabin).
Run `python3 scripts/photo_status.py` for the live count — the FILESYSTEM is the
progress state, there is no separate ledger to drift.

## To resume (start here)
1. ~~Connect BOTH folders~~ **SUPERSEDED (GRANT-KILL-1 + David, 18 Aug 2026):** Chrome
   now downloads into `MarketSquare\_incoming` inside the always-mounted Projects tree,
   and claim_photos.py prefers that sink automatically. No Downloads grant needed —
   the per-session-approval blocker is gone, so unattended overnight photo runs are
   POSSIBLE again (generation still serialises ~1/min; credits still apply).
2. `python3 scripts/photo_status.py --next 10`  -> the next filenames needed.
3. Prompts: `JOURNEY_HIGGSFIELD_PROMPTS.md` (all 104, generated from the specs).
4. Generate on higgsfield.ai/ai/image — model **Nano Banana Pro**, aspect **3:2**,
   2 credits each. Account greenswan1646, Ultra plan.
5. Claim each batch:
   `python3 scripts/claim_photos.py --since <epoch> cape_cairo l1_sight.jpg ...`
   (`date +%s` BEFORE generating — the guard needs a floor timestamp.)
6. `python3 scripts/build_journey.py journeys/cape_cairo.json` then check the map.

## Hard-won lessons — do not relearn these
- **ONE generation at a time.** Firing 4 in quick succession made 2 fail outright
  ("Failed — Credits refunded"). Rate limiting. They also serialise anyway, so
  parallel buys nothing. ~50-60 s per image.
- **Never claim by count alone.** The first claim script only checked for "unclaimed"
  files; Downloads was full of hf_*.png from earlier batches, so when two downloads
  silently failed it assigned a 22 June and a 22 July image to real stops. The
  rewritten script requires files NEWER than `--since` and claims nothing unless the
  count matches exactly. Keep that guard.
- **The mount blocks unlink.** Cannot delete anything under Projects or Downloads.
  Wrong files get blanked to zero bytes (status + builder both treat 0 bytes as
  absent) and overwritten later.
- **Downloading is the fragile step**, not generating. The hover download icon moves
  when tiles change (failed tiles vanish and reflow), and a mis-click opens the
  lightbox instead. The lightbox Download button is steadier, but downloads stopped
  producing files entirely after ~5 in a row — check Chrome for a blocked-download
  prompt before assuming the click failed.
- **Verify every claim.** Never trust that a download happened; `photo_status.py`
  after each batch is the check.
- **Higgsfield now GROUPS outputs into 2x2/collage tiles (26 Jul).** Each generation
  returns a *set* of images (specific-stop cell + style-block riffs: stations, trains,
  savanna). The hover/tile "Download" on a grouped tile saves the whole set as ONE
  collage PNG, not a single photo. Two working paths, both proven this session:
  (a) SINGLE result — right after generating, scroll the gallery to the TOP; if the
  newest is a lone large tile, open it (lightbox shows one image), Download, claim
  normally with claim_photos.py. (b) GROUPED result — hover-download the collage,
  stage+view it, and crop the matching cell with PIL (2x2 cells are exact quarters;
  a 2+3 layout has 3 narrower bottom cells). The build downsizes to 640px wide, so a
  ~632px cropped cell is full quality — place it straight into assets/journey/<id>/.
  VIEW every crop before placing; that visual check replaces the freshness guard when
  you bypass claim_photos.py.
- **The prompt box vs the search box.** After closing a lightbox with Escape, a stray
  click can land in the top search overlay instead of the prompt field, and your whole
  prompt gets typed into search. Screenshot before typing; if the typed text shows in a
  centred search modal, close it (x) and click the bottom prompt bar again.
- **Food/interior prompts drift to "dining in the cabin."** If a food stop renders as a
  cabin scene with the dish tiny in a corner, regenerate with a tight close-up prompt
  ("close overhead bowl filling the frame, no train interior") — worked first try for l6_food.

## Placeholders are safe
Every stop without a photo renders a styled "photo pending" tile, so all four maps
are fully working and presentable right now. Photos drop in incrementally — no
big-bang needed, and nothing breaks part-way.


## Why a finished map still didn't show — and the fix (26 Jul)
A tour map is a widget that renders ONLY on a super_example adventures listing via
ADV_COUNTRY_MAP[listing.country]. Un-gating a country in ms.js is necessary but NOT
sufficient: there must ALSO be a super adventures listing with that country. Those
listings are created by scripts/seed_super_global.py, which deploy_marketsquare.bat
runs on every deploy (step 3g); its COUNTRIES list only had ZA/US/GB/AU/DE, so NA (and
c2c/mz/bw) never got a listing — the map had nothing to ride on. Existing super demos
(Pretoria x8, US/GB/AU/DE x2) are all intact; nothing was deleted.
FIX for Namibia (done 26 Jul): added NA to seed_super_global.py COUNTRIES + COPY
(a route listing + a lodge listing) and dropped 14 gallery photos into assets/super/
(sup_na_advexp_*.jpg x8, sup_na_advacc_*.jpg x6, reused from assets/journey/nam).
Next deploy auto-creates the two NA listings and the Namibia map surfaces on them.
Same recipe for MZ/BW when their photos are done (+ un-gate in ms.js).
CAPE TO CAIRO still pending a decision: it is not a single country (ZA->Egypt), so it
does not fit country->map. Options: pin to EG (fast, keeps c2c filename, minor RG-0011
canon note like ZA->reserve / GB->uk), or rename map to adventures_eg_map.html (canon
clean, more surgery). Awaiting David's call.


## Per-tour maps — the map follows the TOUR, not the country (26 Jul, David)
Problem: a multi-country tour (Cape to Cairo, ZA->Egypt) has no single country, and the
old code picked the map from listing.country, so one country could only ever show ONE
tour map. Decision: the LISTING'S country = the tour operator's country (drives currency
+ market); the MAP = the tour's own route.
Implementation:
- ms.js: new ADV_TOUR_MAP registry keyed by route code (c2c -> adventures_c2c_map.html).
  Render prefers (l.tour && ADV_TOUR_MAP[l.tour]) then falls back to ADV_COUNTRY_MAP[country],
  so every existing country tour is untouched. (Not checked by RG-0011; c2c filename is
  canon-correct anyway.)
- listings gains a `tour` column (backend serves all columns, so it surfaces as l.tour).
- seed_super_global.py: added ensure_tour_column(); Cape to Cairo seeded as a ZA/Cape Town
  operator listing pair (Rand), then UPDATE stamps tour='c2c' on listings carrying sup_c2c_*
  photos. Namibia seeded as its own NA/Windhoek pair (N$), tour empty (country fallback).
- Gallery photos: assets/super/sup_na_* (8 exp + 6 acc, from assets/journey/nam) and
  sup_c2c_* (8 exp + 6 acc, from assets/journey/c2c).
Result after next deploy: NA map shows on the Namibia listings; Cape to Cairo map shows on
the SA listings, beside the reserve tour. To add a future multi-country tour: drop sup_<r>_*
photos, add its ADV_TOUR_MAP entry, add a COUNTRIES+COPY row (operator country) and a tour
stamp. Single-country tours still just need un-gating + a country listing.

## State refresh — 10 Aug 2026 (SUPER-AFRICA-1)
- NA / BW / MZ / C2C ground sets ALL COMPLETE since the 26 Jul notes. `photo_status.py` is the truth: **111/164**.
- NEW in the queue: **Kenya 32** (whole journey, priority — David 10 Aug) and **21 flight-leg shots** (f1_/f2_* × NA/BW/MZ — the new fly-in bookend days; their maps are live-presentable with placeholders meanwhile).
- Prompts as ever in JOURNEY_HIGGSFIELD_PROMPTS.md (164, regenerated 10 Aug). Same process, same guards — nothing about the method changed. Angola REMOVED from expansion scope (David, 10 Aug); no AO journey will be queued.

## Two new UI lessons — 10 Aug 2026 Kenya run (do not relearn)
- **Download leaves the lightbox OPEN.** Clicking the prompt bar next lands INSIDE the lightbox
  (opens an on-image comment box; typed text goes nowhere). After every Download: wait for the
  hf_*.png to actually appear in Downloads (poll, ~5-20 s), THEN close via the top-right X —
  Escape does not always close it — and only then touch the prompt bar.
- **The lightbox side-panel remembers its last tab.** If it opens on Comments, there is NO
  Download button — click Info first; Download lives at the bottom of the Info tab.
- Aircraft prompts: Nano Banana Pro likes putting FLAMES on wingtips/engines. Add "no flames,
  no fire, no engine glow, winglets clean and unlit" to every aircraft shot; zoom-inspect the
  wings before accepting (first d1_start render had a burning winglet — caught at QC, 2 credits).

## Coordinate-space lesson — 10/11 Aug 2026 overnight run (CRITICAL, do not relearn)
- Chrome-extension CLICKS are in **CSS-pixel space**, screenshots are downscaled. When David's
  window scaling/size changes mid-session, screenshot-derived coordinates silently miss — clicks
  land on gallery tiles behind the translucent prompt bar (symptoms: whole-page ctrl+a selection,
  typed prompts vanishing, accidental tile/profile/video-page navigation).
- FIX: get true coordinates from the DOM: `javascript_tool` →
  `document.querySelector('[contenteditable="true"]').getBoundingClientRect()` (same for the
  Generate button). Verify focus landed with `window.getSelection()` (expect IN-EDITOR), and
  ALWAYS verify the prompt text via JS (`textContent.includes(...)`) BEFORE clicking Generate.
- The prompt editor is a controlled React editor: `execCommand` insertText does NOT work.
- After ~5h continuous use the tab's renderer froze (CDP timeouts) — start each photo session
  with a fresh tab/Chrome restart rather than pushing a stale one.


## Standing rule — every rebuilt map page keeps the REPORT widget (11 Aug 2026)

A map rebuild on 11 Aug dropped `<script src="/static/ts_report.js?v=5" defer></script>`
from all five adventures maps (na/bw/mz/ke/c2c) — twice in one morning, once mid-write
(torn ke caught by the pre-deploy scan). David's ruling (5 Aug) is that the REPORT tab
belongs on EVERY page, and test_tester_intake derives that list from the deploy manifest,
so the deploy gate goes RED and blocks the ship whenever a rebuild loses the line.
When you rebuild ANY adventures_*_map.html: keep (or re-add) that script line just before
</body>, and run `python3 test_tester_intake.py` before finishing the session.

## The invisible click-eater — SOLVED (11 Aug 2026 evening)
The "stale DOM / clicks vanish / typed prompts go nowhere" failures were Higgsfield's
**Supercomputer upgrade MODAL** (`.supercomputer-upgrade-plan-modal`, fixed inset-0) appearing
over the whole page — every click hit the invisible overlay. ONE Escape closes it. Diagnose in
seconds with JS: `document.elementFromPoint(x,y)` — if the element chain shows the modal, Escape
and continue. Also: verify the editor got focus (`document.activeElement`) and the prompt landed
(`textContent.includes(...)`) BEFORE every Generate; get all click targets from
`getBoundingClientRect()` ÷ 1.3604 (send-space = CSS ÷ scale; recalibrate scale per session with
a JS click-listener probe).

## Session-bridge lessons — 12 Aug 2026 morning
- **Higgsfield NSFW false-positives:** "travellers from behind climbing airstairs" got flagged
  (Credits refunded, no charge). Avoid "from behind climbing/boarding" phrasing on people shots —
  use "passengers at a distance walking toward the aircraft steps". If flagged: reword, never repeat verbatim.
- **The extension needs OUR tab as Chrome's front tab.** Background/minimized = clicks blank
  (probe: JS mousedown listener). After any Chrome restart: fresh tab, empirical scale probe
  (some windows are 1:1, some ÷1.3604), JS rects for all targets, lightbox check via elementFromPoint.
- Stray typing risk: a leftover lightbox routes typed text into its COMMENT textarea — always
  elementFromPoint-check the editor before typing; clear any textarea it landed in (12 Aug: 559
  chars caught and cleared, nothing submitted).
