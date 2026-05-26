# TrustSquare — Status

## Live State
BEA v1.3.2 · FastAPI + SQLite + Redis · Hetzner CPX32 · trustsquare.co · 17 live listings · Session 85 complete

## Last Completed (Session 85 — 2026-05-26)
- n8n expiry warning workflow live (ID: expiry-warning-s85) — webhook fires branded email to seller 7 days before listing expires
- N8N_WEBHOOK_LISTING_EXPIRY_WARNING set in /etc/environment + .env
- Seller tier enforcement: publish_listing hard-gates at listing_tier_config.max_listings (superusers bypass); create_listing adds advisory cap_warning
- Fixed seller_extra_slots column name (email not seller_email) in both query sites
- Ops tab added to dashboard.html as third nav button — full ops widget layout with live data
- Support Centre live at trustsquare.co/support — password-gated (96315), linked from FEA Me tab + admin header
- Paystack activation response sent — Word doc with 8 screenshots, pricing, refund policy, support infra, live activation request
- Smoke test: 30/30 ✅

## Blueprint v1.1 Complete (Sessions 80–84)
All five sessions of the photo pipeline + listing lifecycle build plan are done:
- listing_photos table (r2_key UNIQUE, ON DELETE CASCADE)
- listing_tier_config (single source of truth for tier timing)
- seller_extra_slots (extra slot purchase audit ledger)
- expires_at + warning_sent_at on listings, all 17 live listings backfilled
- BEA Photo API: presign, confirm, delete, reorder, list
- GET /listings/{id} returns photos[] array
- Expiry worker (live→expired at expires_at, hourly)
- Warning worker (n8n webhook 7 days before expiry, 6-hourly) — NOW WIRED TO LIVE n8n
- Admin UI: presign→PUT→confirm upload, structured photo strip, per-operation delete
- Auto-seed at publish + create — pipeline fully self-maintaining

## Next Session (86) — Next Milestone TBD
- Read STATUS.md first. Session 85 is complete. Go straight into execution.
- Recommended priorities (check BACKLOG.md for current blockers):
  1. Paystack live mode — activate when approval arrives (paste sk_live_ + webhook secret into .env)
  2. Seller intro notification — seller emailed when new connection request arrives (H3 in BACKLOG)
  3. Local Market listing parity — cards + detail screen matching standard listings (H1 in BACKLOG)
  4. Maroushka + Dave phone test — lightbox, back buttons, My Requests tab (H4 in BACKLOG)
  5. Support page content review — refine FAQs, remove password gate when ready for public
