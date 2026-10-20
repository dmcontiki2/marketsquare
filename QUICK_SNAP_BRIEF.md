# QUICK SNAP — build brief (the fourth layer: snap or say, then one tap)
**David, 19 Oct 2026 19:16–19:19 SAST:** *"Could there exist an even easier/quicker interface? I believe yes"* → *"this is nearly exactly what i had in mind: Snap or say, then one tap."* **Status: APPROVED by David, 19 Oct 2026 19:36 SAST — *"go worktree"* — with two conditions and the flow stated by him:**
*"please don't overspend past the current credit, and do keep track of the progress so that we don't lose it if we reach $0, so that i can take it further using the subscription ... This is to end up with 1. A photo, 2. a sentence, 3. Terms acceptance - leading to a live advert. For this flow we will investigate a good video advert."*

## 0 · THE FLOW, IN DAVID'S WORDS (this is the definition; everything below serves it)
**1. A photo → 2. a sentence → 3. Terms acceptance → a live advert.** Both inputs are offered on one screen; either alone is enough,
both together are better (the sentence names the price / area / days the photo cannot). The app fills the rest — kind, title, words,
area from the phone, price from the market — and shows the normal "Here is your listing" screen; her one tap is
"Publish now — I accept the Terms" (RUL-240). **Follow-on, NOT this build:** a video advert for this flow (David, 19 Oct).

## 0a · HOW THIS BUILD RUNS (David's two conditions, 19 Oct 2026)
- **IP HOLD — worktree only.** Build in `_snap_wt/` on local branch `snap` (excluded via .git/info/exclude). Never push it, never
  request a deploy, never touch `main`. The GitHub repo is PUBLIC and nightly_checkpoint.bat pushes main at 05:30 SAST. Merge + deploy
  happen on David's word (his pattern: provisional first, then publish, then live). NOTE: this brief's first version reached GitHub
  main at 19:35 SAST on 19 Oct, before "worktree" was chosen; David was told the same evening.
- **NEVER OVERSPEND THE CREDIT.** One agent, no sub-agents, no fan-out, no new installs, no exploratory reading beyond the files named
  in §2 and §8. Work in the smallest units that make sense (one screen, one route, one proof) and STOP when the definition of done is
  met or when §8's unit list is exhausted — do not open new work.
- **SAVE AS YOU GO (AGENT-SAVE-AS-YOU-GO-1).** After EVERY unit: `git add -A && git commit` on branch `snap` in the worktree, and
  append one line to `_snap_wt/SNAP_PROGRESS.md` (unit done · what was verified · the NEXT unit). The next session — cloud or David's
  subscription — reads SNAP_PROGRESS.md first and continues from the next unit; it never restarts a unit that is committed. A cutoff
  at $0 therefore loses at most one unit.
- **Verification without the live tap.** Prove the rendered screens with the live quick.html in a headless phone and the publish call
  mocked in the browser (the Goal run 44 method); prove the server route on a throwaway copy of the database; the real one-tap live
  proof (a QA advert, deleted after) is done by David's morning session, as on 19 Oct. Never create a listing on the live site in
  this run.
Sibling of QUICK_FASTLANE_BRIEF.md (CCP step 1 + 2). Working name "Snap" — David names things; rename freely.

## 1 · The change in one paragraph
TrustSquare asks for everything; Quick asks the essentials; the Trader remembers them. **Snap asks nothing: it infers.** She shares a photo
(goods) or speaks / types one sentence (people: *"Home cleaner, Mamelodi, Tuesdays and Thursdays, R350"*). The app reads what it is,
takes the area from the phone, suggests a price from the market, writes the advert and shows it on the normal "Here is your listing"
screen. Her only tap is **"Publish now — I accept the Terms"** (RUL-240). The fourth standard flow: same gates, same publish path,
same anonymity, same photo check. Not a chatbot (David's Genie definition, 8 Sep 2026): one thing in, one advert out.

## 2 · What already exists (this is glue, not a new engine)
| Part | Where | State |
|---|---|---|
| Photo → complete listing draft (kind, title, words, price) | `POST /listings/vision-draft` (Photo-First onboarding, Session 70) | live, stateless, 1–12 photos, failover across providers |
| Photo arrives from the gallery share sheet | fast-lane `share_target` + service worker (RUL-222(g)) | live for presets — reuse without a preset |
| One-tap publish with the signature | `POST /listings/quick-publish` `sign_terms` (QUICK-SIGN-1, RUL-240) | live, proven 19 Oct |
| Area from the phone | `/quick/me` geo (network city); phone GPS `msGeoFromGps` pattern in ms.js | live |
| Price from the market | vision-draft price + `_fair_price_resolve` (cards via Scryfall) | live |
| Photo anonymity check, "never a dead end" | PHOTO-KIND-1 (RUL-239) | live |
| One sentence → fields | the fast-find line parser (free capped lane; commas without AI) | live for Find — reuse for Sell |
| Speech → text | the browser's own speech recognition (Chrome Android, Safari) | free, no server, no key; typed fallback always shown |

## 3 · The two doors (both land on the existing "Here is your listing" screen)
- **Snap (goods):** Quick's first screen gains **"Snap it"** (and the share sheet target "Quick · Snap"). Photo → vision-draft →
  category/title/words/price filled → area from the phone (she can change it) → draft screen → e-mail → Publish. Cards, coins,
  stamps, a bakkie, honey, a couch: anything a picture names.
- **Say (people):** **"Say it"** → one sentence by voice (typed box beneath it, always) → the line parser maps role · area · days ·
  price → draft screen → Publish. A cleaner has no photo of her work; the sentence is her photo.
- Anything the reader cannot place lands in normal Quick at the right step with one line saying why — never a dead end, never a guess
  published (the unresolved-card rule, applied to adverts).
- The example photo is never published; her real photo is the advert's photo (RUL-222(e)).

## 4 · Rules this lane must not break
RUL-240 (the tap is the signature — one tap, never zero) · RUL-239 (photo check, hold not refuse) · RUL-115/157 (the work, never a
person; where she works, never where she lives) · 27 Sep "no exceptions to standard flows" · AI spend policy 23 Sep (a free feature
runs on the allocated free lane, capped, budgeted into the free package) · 17 Sep no AI model named anywhere as a label ·
naming parity in every example (both sides of a pair from one naming tradition) · 15 languages for every new word (quick_i18n.json).

## 5 · Cost model (for David's yes/no)
- Build: one scheduled build session (the fast-lane shape), front-end glue + one small server route for the sentence parser on Sell.
- Running: one photo read per Snap advert on the app's allocated lane — cents at most, capped by the existing free-lane cap; speech is free.
- No new tier, no new currency, no Tuppence change. Schema: none (at most `source='quick_snap'` on the listing, an existing column).
- Rulings changed: none. Switch `launch_switches.quick_snap`, ships OFF; David arms it from the dashboard after the rendered check.

## 6 · Definition of done (verified in the RENDERED app, as a stranger, headless phone)
1. A shared photo of a card becomes a live advert with one tap; title, kind, price and area are right; the listing shows on trustsquare.co.
2. "Say it" with the cleaner sentence above becomes a live casuals advert with one tap (invisible until a vouch, RUL-115 — unchanged).
3. An unreadable photo / a sentence the parser cannot place drops into normal Quick at the right step, with one line.
4. The photo check runs on the Snap photo exactly as elsewhere; a held photo still publishes the advert without it.
5. All new words in the 15 Quick languages; How guide has a Snap story; dashboard switch + two counters (snaps, says) + fallbacks.
6. Regression ledger entries for 1–5 in the same session; rulings_check reflections; stranger test PASS; the fast-lane and QUICK-SIGN-1
   entries still green. Rollback: switch OFF hides both doors; git tag at step 0.

## 7 · What this does NOT fix (said once, 19 Oct)
A quicker screen helps the 4 in 100 who tap the text; it does nothing for the 96 who never do. It earns most when it becomes the hook
itself — "send a photo, you are listed" — in the next wave's words and letters (WaveSession2, RUL-241).

## 8 · Unit list for the build run (commit after each; SNAP_PROGRESS.md names the next)
U1 read: CLAUDE.md, STANDING_ORDERS.md, QUICK_FASTLANE_BRIEF.md §5 (house rules), this brief, quick.html's fast-lane module (QUICK-FAST-1 / QF),
   bea_main.py quick_publish + vision_draft; write SNAP_PROGRESS.md with the plan — no code yet.
U2 server: `POST /listings/snap-draft` (one route): accepts up to 3 photos + one sentence (+ city/cc); calls the existing vision_draft
   reader for the photos and the existing find-line parser for the sentence; merges (sentence wins on price/area/days); returns the
   same draft JSON shape quick-publish expects, plus `confidence` and `missing` (what it could not place). Declared in route_policy.json
   (public app key, same as vision-draft). Proof: a script on a DB copy with one card photo from assets/quick_ph and the cleaner sentence.
U3 quick.html: first screen gains "Snap it" (camera / gallery / share sheet) and "Say it" (mic via the browser's own speech recognition,
   typed box always beneath); one combined screen: photo thumbnail + sentence box + "Make my advert"; result lands on the existing draft
   screen (drawDraft) with the fields filled; `missing` drops into normal Quick at that step with one line. Flag `launch_switches.quick_snap`
   (ships OFF; hidden entry points when OFF). HARNESS.html kept identical.
U4 words: every new string in all 15 Quick languages via the existing apply_*_i18n pattern (roles/quick_i18n.json + sync); no AI model named.
U5 dashboard: switch row + two counters (snaps, says) + fallbacks, in dashboard.server.html with provenance (no hand-written greens).
U6 proofs: headless phone on the LIVE quick.html with quick-publish mocked (Goal run 44 method) → screenshots into visuals/snap_*.png;
   server route proof from U2 re-run; stranger_test on the candidate; ledger entries RG-next for U2–U5 (OPEN until shipped, LOCK after);
   rulings_check reflection stub; changelog.d fragment; HARNESS parity.
U7 report: SNAP_PROGRESS.md marked DONE with the one human check (David arms the switch after the live tap proof) — nothing pushed.
