# Higgsfield clip generation brief — the 5 genuinely-missing clips (28 Jun 2026)

Reuse-check done first (David's rule). Result: only 5 clips are actually missing.
The "Heritage 2-person hook" is NOT a gap — `02-heritage/clips/hook-couple.mp4` already
exists and is verified (wife + husband both speak their lines). It's an EDIT decision
(use hook-couple vs the newer hook-wife-NEW), not a generation job. No credits needed there.

## Settings for every clip (from HIGGSFIELD_RECIPE.md, proven)
- Video → Ingredients → **9:16** → 1x → **Omni Flash** → **8s** (12 credits).
- Attach the feature's CAST reference (the David-hearted Favorite for that person).
- Style line appended to every prompt:
  "warm natural light, handheld vlog feel, shallow depth of field, 9:16 vertical."
- ⚠️ Clear the STICKY reference (× on the thumbnail) before switching person.
- ⚠️ Turn the fullscreen renderer OFF (it shifts Generate); verify "Processing" after submit.
- ⚠️ Wait for ALL queued clips to finish before zip-download (early zip = missed clips).
- One sentence / one line per 8s clip, ≤ ~22 words.

---

## RETIREMENT (06) — husband ("HE"), 3 clips. Cast = retiring man, 60s, reading glasses.
Anchor to the SAME man already used for `06-hook-woman`'s partner (the retiring-couple Favorite).
Setting: stoep/patio, golden hour (match the woman's clips).

1. `06-hook-husband.mp4` — HE, beside her on the patio, a little daunted:
   "Pensions, visas, healthcare... it's a maze."
2. `06-wt1-husband.mp4` — HE presenting to camera/phone, steadier:
   "Our citizenship, our pension, what we'd want in a home — that's what it asks."
3. `06-wt2-husband.mp4` — HE, impressed, scrolling:
   "Visa and pension reality for South Africans, what our money buys there, healthcare, community — and real matched listings."
(Optional later: a true 2-person payoff to replace the woman-only `06-payoff-woman`. Hard case — skip blind.)

## EXAM (09) — 2 clips. Cast = matric girl (already used for 09-student-A/B/C) + her MOM.
Setting: bedroom desk, evening, textbook chaos.

4. `09-mom.mp4` — MOM at the doorway with a mug of tea, warm/reassuring:
   "Let TrustSquare build your plan. Tonight."
   (NEW person — CLEAR the sticky student reference first, attach the mom Favorite.)
5. `09-student-payoff.mp4` — STUDENT pinning a printed plan above the desk, relieved/proud:
   "Six weeks, week by week, weighted like the real exam — and a trig tutor in week three. Thanks TrustSquare!"
   (Reuse the SAME student reference as A/B/C so the face matches.)

---

## Total: 5 clips × 12cr = ~60 credits (+ retake margin). Well within the ~2,580 balance.

## After generation (the stitch — I do this once clips are on disk)
- Retirement: rebuild `retirement-planner-AD-FULLDRAFT` using the husband clips in their
  beat slots (currently woman-only / clip-pending per the morning report).
- Exam: drop `09-mom.mp4` into the hook (after the student's "where do I START" line) and
  `09-student-payoff.mp4` into the payoff slot.
- Same /tmp/make_slot.sh + ffmpeg concat pipeline, normalized 720x1280@30 / 44.1kHz.

## WHY I'm not auto-generating these right now
- The browser is granted READ-tier (visible, not clickable via these tools) → I can't drive
  Higgsfield's generate UI reliably.
- I cannot see/hear output → can't judge face drift / lip-sync / delivery (your call per notes).
- Generating blind risks credits on takes you'd reject. So: brief is ready; run hands-on.
