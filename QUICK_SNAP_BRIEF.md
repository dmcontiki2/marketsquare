# QUICK SNAP — build brief (the fourth layer: snap or say, then one tap)
**David, 19 Oct 2026 19:16–19:19 SAST:** *"Could there exist an even easier/quicker interface? I believe yes"* → *"this is nearly exactly what i had in mind: Snap or say, then one tap."* **Status: brief written the same evening; NOT approved for build yet — the go (cost + scope) is David's.**
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
