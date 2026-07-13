# SHORTS — Wave 1 (7-second UGC ads) · scripted 12 Jul 2026
Style canon: looks self-shot — handheld selfie framing, eye contact, natural light matching each persona photo, casual SA delivery, hook in the first second, brand name spoken once. NO burned captions at generation (added in post per platform). 9:16 vertical. TTS canon applies: scripts go to voice/lip-sync in lowercase — caps are visual only.

| # | persona file | category | working title |
|---|---|---|---|
| 1 | persona1 (bakkie, garage) | Cars | SOLD in four days |
| 2 | persona2 (beanie, world map) | Adventures | Verified guide |
| 3 | persona3 (laptop, moving boxes) | Property ⚑ | Moving in |
| 4 | persona4 (vinyl collection) | Collectors | Forty years of records |
| 5 | persona5 (student, books) | Tutors | Marks climbing |
| 6 | persona6 (glasses, kitchen) | Services ⚑ | Sorted by Saturday |
| 7 | persona7 (card binders) | Collectors (cards) | First card traded |
⚑ = mapping is Claude's best guess — David to confirm. GAP: no LocalMarket persona in this set — consider an 8th image next batch.

## 1 · Cars — "SOLD in four days"
SPOKEN (7s): "Sold my bakkie in four days — right price, zero strangers with my number. TrustSquare. That's honestly it."
ON-SCREEN: SOLD — 4 days · number never shared
HIGGSFIELD: start frame persona1. Handheld selfie, man talks to camera grinning, gestures back at the bakkie mid-line, golden-hour garage light, slight camera shake, ambient driveway sound. Lip-sync dialogue above (lowercase).

## 2 · Adventures — "Verified guide"
SPOKEN: "Booked a weekend trail with a guide I could actually verify — trust score ninety-one. Best. Hike. Ever. TrustSquare."
ON-SCREEN: Guide ★91 · booked in minutes
HIGGSFIELD: start frame persona2. Desk-lamp night mood, excited lean toward camera, quick glance back at the world map on "weekend trail", warm lamp light, soft room tone.

## 3 · Property — "Moving in"
SPOKEN: "Found this flat on TrustSquare — saw it was available before I even asked. Boxes packed, keys Friday. Moving in!"
ON-SCREEN: Available now → moving in
HIGGSFIELD: start frame persona3. Bright morning light, laptop on knee, delighted direct-to-camera, pats a moving box on the last line, airy room ambience.

## 4 · Collectors — "Forty years of records"
SPOKEN: "Forty years of collecting records. When I finally sold a few — only buyers I could genuinely trust. TrustSquare."
ON-SCREEN: 40 years · trusted buyers only
HIGGSFIELD: start frame persona4. Warm window light, slow calm delivery, hand resting on the record crates, gentle pride, dust-motes atmosphere, quiet room tone.

## 5 · Tutors — "Marks climbing"
SPOKEN: "My maths tutor has a ninety-four trust score. My marks? Also climbing. Even Mum is smiling. TrustSquare."
ON-SCREEN: Tutor ★94 · marks ↑
HIGGSFIELD: start frame persona5. Evening study lamp, bright genuine smile, taps the open textbook on "marks", homely night ambience.

## 6 · Services — "Sorted by Saturday"
SPOKEN: "Needed an electrician, not a gamble. Verified, introduced, job done by Saturday — and he was brilliant. TrustSquare."
ON-SCREEN: Verified → introduced → sorted
HIGGSFIELD: start frame persona6. Kitchen daylight, relaxed chuckle on "gamble", counts the three beats on fingers, close warm framing, kettle-quiet ambience.

## 7 · Collectors (cards) — "First card traded"
SPOKEN: "Traded my first card on TrustSquare — verified buyer, real offer, no awkward car-park meetup. Sold, just like that."
ON-SCREEN: Verified buyer · real offer
HIGGSFIELD: start frame persona7. Bookshelf daylight, holds a card binder up briefly, easy laugh on "car-park meetup", natural handheld drift.

## Pipeline after approval
Generate in Higgsfield (Claude drives via Chrome, David logged in) → /video-qc each (incl. pix_fmt gate + ear-check pass) → name short_<category>_<slug>.mp4 → hold for post-launch publishing per /launch-series. Budget: ≤50% of remaining Higgsfield credits, stop-loss: any short needing a 3rd regeneration gets parked for David.


## MAPPING CORRECTION (David, 12 Jul) + Heritage script
- persona6 glasses gent = **Heritage tour guide (SELLER testimonial)**, NOT Services/electrician.
- persona7 hoodie guy = Cards (confirmed).
- Services/electrician script parked for a future LocalMarket/Services persona.

### 6 (revised) · Heritage tour — "The verified guide" (SELLER voice)
SPOKEN (~6s): "I guide heritage tours. On TrustSquare, travellers see my score before they book — ninety-four, earned. That's real trust."
ON-SCREEN: Guide ★ 94 · earned, not claimed
HIGGSFIELD start frame: glasses gent. Warm daylight, distinguished calm delivery to camera, a knowing smile on "earned", authentic handheld feel.

## Batch fire log (12 Jul)
- Property — DONE (short_property_moving-in_v1.mp4, 6s/9:16/720p, SHIP)
- Cars, Adventures-trail, Vinyl, Tutors, Heritage, Cards — firing now

## Batch result (12 Jul) — ALL 7 GENERATED in Higgsfield
| # | persona | status | local file |
|---|---|---|---|
| Property | moving-boxes woman | ✅ rendered + downloaded + QC SHIP | short_property_moving-in_v1.mp4 |
| Cars | bakkie guy | ✅ rendered (in Higgsfield Today) | pull pending |
| Adventures | world-map guy | ✅ rendered (in Higgsfield Today) | pull pending |
| Collectors-vinyl | records man | ✅ rendered (in Higgsfield Today) | pull pending |
| Tutors | navy-polo student | ✅ rendered (in Higgsfield Today) | pull pending |
| Heritage | glasses gent | ✅ rendered + downloaded + QC SHIP | short_heritage_verified-guide_v1.mp4 |
| Cards | hoodie guy | ✅ rendered (finishing) | pull pending |
All: 6s · 9:16 · 720p · yuv420p · lip-synced audio · Kling 3.0 · correct persona+script verified in each job card.
WORKFLOW FINDING: Higgsfield generation via Chrome works but bulk-DOWNLOAD of finished renders is the slow/unreliable step (UI download button hit-or-miss). Candidate: Higgsfield MCP or a 'collect today's renders' helper. Credits used: 7 × 12 = 84 (within the ≤50% ceiling David set).

## Heritage REVISION (David, 12 Jul) — seller→BUYER, feature = tour plan + downloadable interactive map
OLD (v1, wrong angle): "I guide heritage tours. On TrustSquare, travellers see my score before they book — ninety-four, earned. That's real trust."
NEW (v2): "I booked a four-day heritage tour on TrustSquare — and the whole plan came on a downloaded interactive map. So easy."
Same persona (glasses gent, asset 9d117c4f). Regenerating; v1 file kept as _OLD.
