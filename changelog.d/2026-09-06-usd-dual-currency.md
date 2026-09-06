## 2026-09-06 - The films read in dollars as well as rand (USD-DUAL-1)

David, same day as the launch plan: *"when we created these examples our target group were South
Africa, for Youtube our target group is global. Can you change all references to Rand to rather
show Dollars? I don't want to do it in Higgsfield as that will be much too complicated."*

**Measured before changing anything, because the answer depended on it.** All ten films were
transcribed (faster-whisper). **Three speak a rand amount out loud** — 01 "twenty-four thousand
rand for one card", 08 "under a thousand rand", 10 "is R4,500 fair" and again in its narration.
Those lines are inside lip-synced clips; changing them means regenerating clips, which is the
Higgsfield work David ruled out. So a straight *replacement* of rand with dollars would have made
the picture contradict the soundtrack in three of ten films. That is the fact that decided the
approach, and it was only knowable by listening.

**Put to David as one question with the cost of each answer. He chose SHOW BOTH.**

**What changed (`scripts/usd_dual_patch.py`, new and reusable):**
- The input screen of six films now reads `R420,000 - $25,400` and equivalents. That field is
  static for its whole window, so the patch is drawn in the insert's own DejaVu Sans on its own
  #F2F5FC field colour, inside the field border - it reads as native, verified by eye at full res.
- The report screen scrolls rand for ~10 s and cannot be re-typed without rebuilding the film, so
  a line sits in the empty navy band under the phone: `prices in rand - $1 = R16.5`. Every figure
  on screen then converts. Placed per film against a measured clean-navy band, never over content.
- Audio is stream-copied. **Decoded audio of every new cut is byte-identical to its master** - the
  proof that only pixels moved and no seam entered films that took three sessions to finish.
- Rate R16.52 = $1, which is the rate film 01's own report already prints: the app shows both
  currencies in its reports, so the films now match the product instead of contradicting it.
- Film 01 needed nothing (its report already prints R and $ with the rate). Film 09 has no money
  on screen at all. Both are exempt BY NAME in the ledger so a later session cannot read their
  absence as a gap.

**Packaging:** all ten packages are now in dollars, the ZA-narrow search tags were broadened (the
genuinely South African ones - Kruger, CAPS, matric, the D7 visa - stay), film 01 was folded into
`youtube_pack_build.py` so all ten rebuild from one place, and every package's first line now names
the exact file to upload.

**Two faults caught by looking rather than trusting:** preset "fast" overran a tool call and left a
truncated 4K file (measured: 10 s of 2160x3840 costs ~29 s of wall clock here, so the encode is
pinned to veryfast, superfast for the 69 s film); and a first attempt at the report line was
cropped by the phone on three films until the clean-navy band was measured per film.

Ledger: **RG-0302** LOCKED - every film with money on screen has a dual-currency cut, and every
upload package names it. Same silent-drift family as RG-0299/RG-0301: a change made to the artefact
but not to the instructions that point at it.

**Also today:** a scheduled check now watches `VIDEO_SIGNOFF.md` and stays silent every morning
until it says READY, then reminds David once to sort YouTube access. He asked to be reminded when
we are happy with the videos; nobody has to remember.
