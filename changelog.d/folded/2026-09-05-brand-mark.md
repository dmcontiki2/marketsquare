## 2026-09-05 — the green mark reaches the letters (BRAND-MARK-1)

David, reviewing the club letter he had just link-tested: *"I like its simplicity, and the links
worked. I do miss our green trustsquare icon in the header."*

The header had been a text wordmark since it was written. The mark itself was live on the site
the whole time — `/static/brand/icon-192.png`, the green rounded square with the white tick — and
had simply never reached the outreach templates.

**Done in all 17 letters, not the one he was looking at.** A brand mark on one letter and not the
others is the same drift the orphan-letter sweep caught the same day. The 15 that share the navy
header get it centred above the wordmark at 44px; the two plain utility letters (follow-up and
the relink apology) get it left-aligned at 40px to match their table layout.

**Inlined, not linked — this is the part that matters.** Mail clients block remote images by
default, so a hosted logo would show most recipients a broken box exactly where our first
impression lives. The mark now goes through `inline_images` as a `cid:` attachment: probed on the
real send path, **1 inline attachment, 0 remote images left**. The asset is 5.7 KB, so carrying
it on every send costs nothing. Alt text is set, so a client that strips images still reads
"TrustSquare".

Asserted as RG-0286, two legs — every letter carries it, AND the asset exists on disk. The second
leg is not redundant: `inline()` degrades gracefully by keeping the hosted URL when an asset is
missing, so a deleted file would silently turn the mark back into a blockable remote image with
nothing going red.

Preview regenerated at `Visuals/letters/club_letter_PREVIEW.html` (icon embedded as a data URI so
it renders when opened in a browser). All five links re-checked and unchanged.
