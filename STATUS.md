# TrustSquare — Status

## Live State
BEA v1.3.2 · FastAPI + SQLite + Redis · Hetzner CPX32 · trustsquare.co · 17 live listings · Session 84 complete
Blueprint v1.1 (Sessions 80–84) fully delivered. listing_photos self-maintaining. Expiry workers running.

## Last Completed (Session 84 — 2026-05-25)
- Added _seed_listing_photos(conn, listing_id) helper — idempotent, derives r2_key from URL, inserts listing_photos rows
- Hooked into publish_listing: every newly published listing auto-gets listing_photos rows (try/except, never blocks publish)
- Hooked into create_listing: draft listings with photos already attached get seeded at creation time
- BEA syntax-checked, restarted, active
- Smoke test: all 30 checks passed

## Blueprint v1.1 Complete (Sessions 80–84)
All five sessions of the photo pipeline + listing lifecycle build plan are done:
- listing_photos table (r2_key UNIQUE, ON DELETE CASCADE)
- listing_tier_config (single source of truth for tier timing)
- seller_extra_slots (extra slot purchase audit ledger)
- expires_at + warning_sent_at on listings, all 17 live listings backfilled
- BEA Photo API: presign, confirm, delete, reorder, list
- GET /listings/{id} returns photos[] array
- Expiry worker (live→expired at expires_at, hourly)
- Warning worker (n8n webhook 7 days before expiry, 6-hourly)
- Admin UI: presign→PUT→confirm upload, structured photo strip, per-operation delete
- Auto-seed at publish + create — pipeline fully self-maintaining

## Next Session (85) — Next Milestone TBD
- Read STATUS.md first. Session 84 is complete. Go straight into execution.
- Recommended priorities (check BACKLOG.md for current blockers):
  1. Paystack live mode activation (CIPC registration complete?)
  2. n8n email notification for listing expiry warning (set N8N_WEBHOOK_LISTING_EXPIRY_WARNING env var + build n8n workflow)
  3. Wave 1 outreach — load Pretoria prospects into CityLauncher, trigger batch
  4. Seller tier enforcement — gate listing count against listing_tier_config.max_listings
