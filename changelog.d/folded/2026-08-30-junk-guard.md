## 2026-08-30 — JUNK-GUARD-1: placeholder addresses can no longer be emailed (RG-0217 LOCKED)

Wave 1 (29 Aug, 88 sends) bounced ~6.8% — 6 webhook bounce events — and the send-day note
had already named the culprits: scraper-swallowed template artifacts (user@domain.com,
filler@godaddy.com) that pass MX because those domains resolve. 6.8% sits above BOTH the 5%
stop-loss and RAMP-1's 2% clean bar, so unguarded junk doesn't just waste sends — it blocks
the earned-volume ramp and spends mail.trustsquare.co reputation shared with transactional mail.

Fix at the class, CityLauncher/emailer/emailer.py: `_looks_junk()` (placeholder local-parts,
template domains, reserved TLDs — deliberately conservative, info@/admin@ business addresses
stay sendable) enforced at the send_email chokepoint beside SUPPRESS-1 AND in get_prospects
batch composition (under-filling a batch beats bouncing it). Witness: tests/test_junk_guard.py,
12 assertions incl. both wave-1 culprits and the not-junk boundary. Ledger RG-0217 LOCKED with
a behavioral check (exec of the self-contained guard block). Backups: emailer.py.bak-junkguard-*,
regression_ledger.py.bak-junkguard-*. py_compile clean both files.

Note for the ramp: wave 1 therefore counts DIRTY on true (server) bounce data — batch size for
the next wave stays at defaults (12/category/city), not doubled; local bounced_at still reads 0
because Resend bounce events land server-side only (sync is push-up) — pull-down remains open
under the RG-0176(a)/RG-0204 seam class.
