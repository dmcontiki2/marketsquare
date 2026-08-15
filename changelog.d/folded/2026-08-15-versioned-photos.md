## 2026-08-15 — VERSIONED-PHOTO-1: why David still saw the old photos, and the fix that sticks
Two causes, neither the deploys: (1) /static/ ships immutable 1-year cache headers, so a
same-filename photo swap never reaches any client that ever saw the old file — both TS-0034
swaps are now re-cut to versioned names (sup_svctech_2_cover_v2.jpg, sup_svccas_3_after_v2.jpg)
with listings 267/268 photo_urls updated; origin-verified 200 at the right sizes. (2) The
"Deploy engine diagnosis" session overwrote the electrician render with the old bytes at 14:27
while working the same fault — restored from the local repo copy. Swap rule added to
HIGGSFIELD_REGEN_QUEUE.md: never same-filename; always version + repoint photo_urls.
