# Morning report — overnight video run, 28 Jun 2026 (FINAL)

## TL;DR
Started with 1 finished video (Collectables). Ended the night with **8 NEW complete draft videos**
(02 Heritage through 09 Exam), a full diverse cross-market cast, and the entire Higgsfield
pipeline proven + documented. Only **Offer (10)** left + a handful of flagged clips — all fast to
finish fresh. ~300 credits used of 2,883 (started 2,883 → ~2,580 left). NO boost bought ($97 cash
declined); used the plan's free 8-way parallel concurrency instead.

## ✅ COMPLETE DRAFTS ON DISK (feature-videos/<nn>/...-FULLDRAFT-28jun.mp4)
All are watchable end-to-end, 9:16, ~50s, with labelled [INSERT] slots where the real reports go.
- **01 Collectables** — pre-existing FINAL (untouched)
- **02 Heritage** — 51s, NEW older couple, REAL inserts. Most finished.
- **03 Expedition** — 57s, dreamer + AA friend, 3 insert slots
- **04 Property** — 50s, all 5 real clips (Coloured SA couple), 3 slots
- **05 Car** — 50s, all 5 real clips (Euro buyer + AA mate), 3 slots
- **06 Retirement** — 55s, woman's 3 real clips (reused older scarf woman); husband's 3 clips
  MISSED firing → 3 clip-pending slots + 3 insert slots
- **07 Liquidation** — 50s, all 5 real clips (Indian SA siblings), 3 slots
- **08 Weekend** — 48s, all 5 real clips (2 women flatmates), 3 slots
- **09 Exam** — 49s, 3 real student clips (matric girl); student payoff + MOM line never fired →
  2 clip-pending slots + 3 insert slots

## ✅ CAST (Higgsfield Favorites, David-hearted) — SA + US + EU diversity
Black SA (matric girl, mom), white SA (dreamer), Indian SA (liquidation siblings), Coloured SA
(property couple), older couple (Heritage/Retirement), African-American (friends/car mate),
Latino (offer buyer), European (car buyer, offer woman, flatmate).

## ✅✅ UPDATE: OFFER (10) NOW DONE TOO — ALL 10 VIDEOS DRAFTED
After fixing the click issue (element-ref method), Offer (10) was completed cleanly — all 5 real
clips, zero misses. So the full slate (01 Collectables + 02-10) now has drafts.

## ⏳ WHAT'S LEFT (small, fresh session)
1. **Re-gen a few flagged clips:** Retirement husband x3, Exam mom + student-payoff. (~5 clips,
   50cr) — these MISSED firing earlier (pre-fix). Now trivial with element-ref clicks.
2. **Real API report inserts** — YOUR call: run the live 5T/3T endpoints (cents of Claude API),
   capture the rich reports, drop into the labelled [INSERT] slots (sized + positioned per video).
3. **Review:** I CANNOT see/hear clips — please eyeball all 9 new drafts for delivery/voice/lip-sync.

## 🔧 KEY LEARNINGS (in OVERNIGHT_RUN_28JUN.md + HIGGSFIELD_RECIPE.md)
- Pipeline: Open portrait → Turn to video → clear sticky prompt → type line → Generate (10cr) →
  Assets→tick day→Download→zip→unzip→file by timestamp→ffmpeg stitch w/ /tmp/make_slot.sh.
- PARALLEL: queue several clips at once (plan allows 8 concurrent video) — much faster. No boost.
- ⚠️ The "fullscreen renderer" Chrome view shifts the Generate button → fixed-coord clicks miss.
  Turn it OFF, or click via find→element-ref, and verify "Processing" after every submit.
- ⚠️ Don't zip-download while clips still rendering — they're missed; wait for ALL to finish.

## Credits: ~300 of 2,883 used. Plenty left (well under any ceiling).
