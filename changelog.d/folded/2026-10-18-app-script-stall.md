## 2026-10-18 — APP-SCRIPT-STALL-1: empty Home after the bug audit was a stalled Cloudflare copy of ms.js (RG-1061)

- Symptom (David, 15:02 SAST): "after the audit the Trustsquare app is showing no listings" — every category tile read "0 listings".
- PROBED: DB held 146 live listings; the app answered /listings with all of them; nothing was deleted.
- PROBED: in Chrome, `static/ms.js?v=1106&m=1` sat "pending"; the app never started (`openDetail` undefined, `LISTINGS` empty), no console error.
- Cause: the Cloudflare Johannesburg edge was serving a half-filled cached copy of that exact URL at ~30 KB/s (20–40 s reads got 96–870 KB of 1.4 MB). The same file under any other `?v=` arrived in <2 s; the origin served it in 4 ms. A purge-everything (200 OK) did not evict it at once.
- Not caused by the audit's code changes (ms.js parses clean; diff since 4d461c1 reviewed). The audit's deploy simply produced the new URL whose edge fill stalled.
- Recovered 15:20 SAST: Chrome loads 151 live listings, counts correct.
- Lock: RG-1061 downloads the exact ms.js URL the live Home links and goes red if it is incomplete or slower than 15 s. Cure when it trips: ship any deploy (bumps `?v=`).
- This deploy bumps `?v=` so no other edge city keeps the stalled copy.
