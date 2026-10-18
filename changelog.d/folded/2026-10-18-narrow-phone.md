## 2026-10-18 -- BUG-AUDIT-1016 rendered sweep: two pages wider than a phone (cloud lane)

- **SPEC-NARROW-1** (ms.js vehSpecPanel; BA-036, RG-1030) -- a car's Vehicle Specs used two '1fr' columns, whose floor is the widest
  word, so listing #318 laid out at 368 px on a 360 px phone: the page slid sideways and 'My Space' was cut off the bottom bar. The
  columns may now shrink, a value that doesn't fit drops to its own right-aligned line (words stay whole), and an empty list no
  longer leaves an empty 'Features' card.
- **BACKBAR-WIDTH-1** (support.html; BA-036, RG-1030) -- the shared sticky "Back to TrustSquare" bar carries -18px side margins for
  pages with 18px body padding; /support has none, so the bar was 396 px wide and the page 378 px on a 360 px phone. Margins removed
  on this page. Both checked in Chromium at 360x800 before shipping.
