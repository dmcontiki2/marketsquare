# TrustSquare — Status

## Live State
BEA v1.3.1 · FastAPI + SQLite + Redis · Hetzner CPX22 · trustsquare.co · 19 live listings · Session 78 complete
Batch Cards (AI5) flow fully working end-to-end on mobile ✓

## Last Completed (Session 78 — 2026-05-24)
- Fixed JS SyntaxError (stray brace) that broke all admin app JS on phone
- Fixed batch publish fail — `body` ReferenceError in `buildDescription` (silent catch → "no connection")
- Fixed suburb missing on publish → BEA 400 guard, fallback to city name
- Fixed magic link routing — review screen link now includes `drafted=1`, routes to listing preview not photo funnel
- Fixed EXIF canvas dimensions for portrait card orientations
- Fixed price regex for range prices like "R200–R350"
- Added mobile viewport `maximum-scale=1.0` + `overflow-x:hidden`
- Added nginx `no-store, no-cache` headers on admin.html to prevent mobile caching stale JS
- Full 8-card batch flow verified on phone: AI analysis → R2 upload → draft save → magic link → listed ✓

## Next Session (79)
- Fix photo orientation — EXIF rotation still showing cards sideways after publish (persistent issue, needs root cause audit of canvas→R2 pipeline)
- Property batch listing design + build (AI5 equivalent for Property)
- n8n email notifications — magic link delivery to seller email
- Subscription tier design — Free (suburb) / Starter ~$5/mo (city) / Premium ~$15/mo (country)
- Pre-launch: remove /dev/credit endpoint, remove Skip buttons, switch Paystack live mode
