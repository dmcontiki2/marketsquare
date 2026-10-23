# ONE DOOR — build brief (ONE-DOOR-1): the one entry screen for every TrustSquare app
**David, 22–23 Oct 2026 (session with the v1–v3 prototypes in `Visuals\MarketSquare\TRUSTSQUARE_ONE_APP_ENTRY_2026-10-22.html`):**
*"you nailed it ... Now it is an app of beauty to open, and it is the collective for all of the variants"* → *"I want this to be the only
entry point ... Demo can be left off for the first page ... non $20 subscribers should land on a visual explaining advert page ... for
subscribers they can go to their AI PA page"* → *"Give me a financial report first, then build the new HMI, and its impacted other changes
for launch ready, with the squire_pro_pa also. Let us first review it before it goes live."* → on the brief cap: *"yes for a monthly cap - it is a safety net."*

## 0 · How this build runs
- Worktree `_door_wt/`, local branch `door`, excluded from main. Never pushed, never deployed, main untouched. Merge + ship on David's word after his review.
- Everything ships dark behind `launch_switches.one_door` (default OFF). `squire_pro_pa` (feature_flags.json) stays OFF; arming either is David's act.
- Save as you go: commit after every unit; `DOOR_PROGRESS.md` names the next unit.

## 1 · The door in one paragraph
On opening, the app is a living collage of the journey photographs (trains, Kenya, Namibia, Botswana, Mozambique, Cape to Cairo) — no demo
stock on the first page. A single-colour slider sits on top: Snap · Quick · TrustSquare. Sliding shows local adverts scrolling past — filtered
to the visitor's interest when one is known (previous use, what she sells, or the CityLauncher prospect row), the general stream when not.
AI PA cards (photographed reports and alerts) appear inside those three streams; tapping one opens the AI PA door. A tap anywhere else opens
the last app of that type where she left it. Tapping the collage before sliding opens the last app used — one tap, as the icon does today.

## 2 · Rulings this build carries (RULINGS.md)
- RUL-243 one door: the only entry point (amends RUL-124(d), RUL-125(a), RUL-223 when `one_door` is armed; Quick's path stays so installed Quick icons keep working).
- RUL-244 the AI PA door: Pro → `/pa` (the AI PA page); everyone else → `/pa/about` (the explainer), never the plans screen.
- RUL-245 no demo on the first page; the AI PA appears within the Snap / Quick / TrustSquare streams, not as a fourth stop.
- RUL-246 Squire brief cap: 30 AI-drafted briefs per Pro user per month; past it the brief is still made from the template at no cost (a ladder, RUL-066).

## 3 · What already exists (glue, not a new engine)
| Part | Where |
|---|---|
| Listings for a city / category | `GET /listings` (reach rules, AI examples marked RUL-040) |
| Interest sources | `demand_prospects.app_category` (email_hash), `users.primary_category`; NEW `users.interest_categories` fed by introductions |
| AI PA engine | Squire 1 (`/squire/*`, live behind baseline_q4) + Squire-2 (merged, PA quote behind `squire_pro_pa`), wishlist signals, quick presets |
| The apps the tap opens | `/quick/?p=snap`, `/quick/`, `/?app=1`, `/pa` |

## 4 · Units (commit after each; DOOR_PROGRESS.md names the next)
U1 brief + worktree · U2 server (switch, two user fields, /door /door/me /door/last /pa /pa/about, brief cap, intro→interest, route_policy, proof)
· U3 door.html + media + index redirect when ON · U4 pa.html + pa_about.html · U5 words (15 Quick languages), How story, +1 page switch,
deploy_manifest, rulings, ledger (OPEN), changelog.d + status.d · U6 rendered proof (headless phone, APIs mocked) + report.

## 5 · Definition of done (for David's review, before any arming)
1. Switch OFF: the live app is byte-for-byte the same experience (index opens as before; every /door and /pa route 404).
2. Switch ON (rendered, mocked APIs): collage → slide → interest-filtered local adverts → tap opens the right existing app; AI PA card → /pa (Pro) or /pa/about.
3. Server proof 18/18 on a throwaway DB copy; route_policy declares every new route; no AI model named anywhere; brief cap in code.
4. Rollback: switch OFF hides the door instantly; code rollback = drop branch `door`.

## 6 · What this does NOT do (said once)
- Snap's share-sheet target stays in Quick's manifest (installed Quick icons keep it); moving it into the single TrustSquare manifest is an OPEN ledger entry.
- 27 of the 81 Pretoria demo adverts carry a mismatched photo; the door does not show demo stock, the fix is an OPEN ledger entry.
- `squire_pro_pa` has nothing to sell until a premium feed carries a monthly cost (`feed_costs_usd_month` is empty).
