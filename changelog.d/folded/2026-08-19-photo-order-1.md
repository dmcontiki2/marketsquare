## 2026-08-19 — PHOTO-ORDER-1: seller controls photo order and the cover; edit-screen photo changes finally reach buyers

Maroushka removed an over-blurred cover photo, uploaded a replacement, and it landed LAST with no way to move it to first (David, 19 Aug: "new users will just give up"). Four defects fixed as one lane:

- **No reorder/set-cover existed anywhere.** Edit screen now has ★ Make cover plus ◀/▶ move controls per photo (`elMakeCover`/`elMovePhoto`, ms.js); cover = position 0, thumb/medium synced on save, same "tap Save Changes to apply" flow as remove.
- **Edit-screen saves never reached buyers.** Buyers read the `[photos:...]` description prefix FIRST; the edit screen saved only `photo_urls`. PUT /listings/{id} (PHOTO-ORDER-1 block, bea_main.py) now rewrites the prefix to match submitted `photo_urls` — captions preserved by URL, thumb/medium defaulted to position 0 server-side. Proven by 6 offline cases incl. caption preservation, remove-all, and same-PUT description edits.
- **Cross-listing photo bleed.** `_elPhotoUrls` (module-level) was never reset; opening a second listing showed — and could save — the first listing's photos. Reset per `openEditListing`.
- **Edit screen blind to prefix-only photos.** Most published listings carry photos only in the prefix (`photo_urls` NULL); the edit screen fell back to a single thumb — the "2 of 8 photos" half of TS-0030. It now parses the prefix.

Tripwire: RG-0118 (OPEN until deployed; live half checks /static/ms.js). Backups: bea_main.py/ms.js `.bak-photoorder-20260819-191259`. NOT YET DEPLOYED.

Blur side of the same report (replacement photo again excessively smeared despite RG-0044/47 gates): deliberately NOT re-patched — David ruled 19 Aug no more micro-fixes on the same machinery; a scan-model vendor swap decision is with him.
