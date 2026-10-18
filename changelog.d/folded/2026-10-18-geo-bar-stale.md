## 2026-10-18 -- BUG-AUDIT-1016 rendered sweep: the location bar outlived her own city pick (cloud lane)

- **GEO-BAR-STALE-1** (ms.js selectCity; BA-038, RG-1031) -- Home's yellow bar ("Showing New York, United States -- your country
  from your internet connection. Somewhere else?") stayed after she chose another city through the badge -> Countries -> city
  picker, so the badge said "South Africa · Pretoria" under a bar naming New York. Her own pick now removes the bar (it answered
  its question); an automatic pick still re-draws it with the new place. Checked in Chromium through the real picker: live code
  keeps the stale bar, the fix removes it, no page errors.
