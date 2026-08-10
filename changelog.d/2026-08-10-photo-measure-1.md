## 2026-08-10 — PHOTO-MEASURE-1: the blur ceiling now judges the PAINTED OUTPUT (TS-0028/0029), + edit-path upload errors unsilenced (TS-0030)

Maroushka retested on the current build the morning of 10 Aug and filed three photo faults in
eight minutes. Read off the live register and her R2 screenshots, then diagnosed from evidence:
her covers uploaded 11:39-11:53Z THROUGH the live PHOTO-REPLACE-1 gate and still published with
22-32% of the frame smeared (measured empirically on the live images). RG-0044's box-union
measure was not wrong — it was measuring the wrong thing: it predicts coverage from the BOXES
(+ the painter's padding), but the painter also adds a feather falloff margin (m = 2·feather+8)
and angle-aware capsule growth, so the paint the seller SEES is bigger than the number the
ceiling judged. Under-read boxes → no refusal → spoiled cover published.

**The fix — measure the output, not the intent.** `_anon_painted_fraction(before, after)`:
pixel-diff of the pristine entry image against the candidate output through one shared resize,
so feather, capsules and accumulated correction rounds all count exactly once. Both
accepted-image exits of `_anon_blur_until_clean` (clean-verify and last-resort) now consult it
against the SAME `_ANON_MAX_BLUR_FRAC` ceiling before returning; breach returns the
needs-replacement refusal, same seller wording as PHOTO-REPLACE-1. The box measure stays as the
cheap early refusal. Fail-open on measurement error by design: anonymity is guaranteed by the
verify pass, and a broken ruler must not block every upload. Offline proof on the shipped code
text: identical images 0.000, painted 30% → 0.227 (refused), painted 4% → 0.030 (passes).
Tripwire **RG-0047** locks the property (every accepted exit gated, one shared ceiling,
baseline captured) — proven RED on three mutations, green on the real file, full ledger exit 0.

**TS-0030 (HEIC on edit) — diagnosed from the live row, most of it was already working.** All
8 photos stored as valid JPEGs (R2 objects 11:59-12:00Z, listing 335 row correct; the .HEIC
suffix on some keys is just the preserved original filename on JPEG bytes). What was real: the
edit path's `elAddPhoto`/`elReplacePhoto` and the profile-photo path threw a generic
'Upload failed', silencing the server's specific reasons (HEIC guidance, anonymity refusal —
and it would have silenced the new replacement request too). RG-0041 class; all three sites now
surface `detail`. STILL OPEN on the register: her 12:03Z view showed 2 of 8 photos — data was
correct server-side, `cf-cache-status: DYNAMIC` rules out edge cache, so it is client render
state and needs a browser reproduction.

**Stored stock audited.** `Records/BLUR_AUDIT_2026-08-10.md`: 9 of 15 live seller covers exceed
the 18% ceiling (worst 59.3%) — pre-fix blurs PHOTO-MEASURE-1 cannot retro-fix because
originals are never stored (by design). Remediation = replacement requests to the seller; needs
a small notify flow, not yet built.

**Register discipline:** TS-0028/0029 marked duplicates of TS-0022 (recurrence now 3 — rule 3's
design-change threshold, which David's 7 Aug ruling already answered; this change is that
ruling made true in paint). TS-0030 diagnosis + split recorded on the row. Everything above is
LOCAL until the next /ship; fault rows updated via the admin API say so explicitly.
