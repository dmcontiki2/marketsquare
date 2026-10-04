## 2026-10-04 — AUDIT-4OCT Batch 2: the High money, privacy and security bugs (AUD-015..031, AUD-050..054)

David: *"proceed with batch 2"*; on the two questions put first: *"1 but we never remove paid tuppences as oper our rules"*
(RUL-201). Every finding was confirmed in today's code before it was changed. EXECUTED end to end by
`scripts/prove_audit_b2.py` (imports the real bea_main.py on a throwaway database; RG-0840).

**Money**
- AUD-015 (RG-0818): restore_on_return claims the closure row (`restored_at IS NULL`) before writing the credit -- parallel sign-ins restore once.
- AUD-016 (RG-0819, RUL-201(a)): a paid Starter/Pro plan returns to Free (or the agency seat) when its paid 30 days end without a new payment; superusers untouched; nothing deleted. PROBED: no paid plans on the live DB today.
- AUD-017 (RG-0820): both listing deletes close pending introductions and release holds (buyer told by email); the sweep closes orphans. PROBED: 3 orphaned pending requests live, 1 with an unreleased 1T hold -- the next sweep returns it.
- AUD-018 (RG-0821): retained Tuppence is restored at every sign-in (the one session door); POST /users saves the name on an existing row and grants welcome sessions once (zero-amount `welcome_ai_sessions` marker row, no schema change).
- AUD-019 (RG-0822): the security gate rewrites a bound address unless it is EXACTLY the session's; create_intro and batch-cards keep the canonical address.
- AUD-020 (RG-0824, enforces RUL-048): seat_paid needs the admin key; a session cap is clamped to 10 (20 only with a paid seat) and never writes a tier.
- AUD-021 (RG-0823, RUL-201(b)): the monthly reset sweeps only last month's unused grant (grant minus spending since it, net of returned holds/refunds).
- AUD-022 (RG-0825): NOT A BUG in production -- PROBED: the server's PAYSTACK_WEBHOOK_SECRET equals the secret key (compared on the box, value never read). Hardened: falls back to the secret key, bytes compare, docstring corrected.

**Privacy**
- AUD-023 (RG-0826): no street level in Zoom for Property/Services; `_zoom_candidates` strips private columns for every caller (house accounts still sort last via a derived flag).
- AUD-024 (RG-0827): a pending request shows the seller a first name and a contact-free message; messages are scrubbed before storage (also Local Market and the n8n payloads).
- AUD-025 (RG-0828): profile tags/region scrubbed on save; headline/about/tags scrubbed again on the public read.
- AUD-026 (RG-0829): `_squire_minimise` now strips contact details for every Squire text; need text and seller answers always pass through it.
- AUD-050 (RG-0835): ms.js phone mask catches every phone shape, text nodes only. PROBED: 0 of 164 live adverts carry a phone/email, so no backfill.

**Security**
- AUD-027 (RG-0830): Listing/ListingUpdate/LMListingIn accept only https or plain /media/<name> photo addresses; migrate-photos copies only real pictures resolved inside /media; withdraw never deletes a picture another listing uses.
- AUD-028 (RG-0831): uploads may not name verification-result, tx_*, claim-only or no-evidence signals.
- AUD-029 (RG-0832): the five AI routes return plain text (`_ai_plain_out`); ms.js paints the model text escaped.
- AUD-030 (RG-0833): unproven support-form addresses get the fixed acknowledgement only; mailbox-normalised hourly cap; 3 mailboxes per IP per day.
- AUD-031 (RG-0834): lead inbox fields plain + escaped; advert city/area/suburb/price plain text at the model.
- AUD-051 (RG-0836): agency console escaped; buttons use data attributes + one delegated listener; strict invite emails.
- AUD-052 (RG-0837): Zoom buttons read data-* attributes.
- AUD-053 (RG-0838): invite-link values validated at the URL door; the five "near <city>" lines escaped.
- AUD-054 (RG-0839): agent profile text plain on save and on /agents/nearby; agent cards painted from an escaped copy.

Ledger RG-0818..RG-0840. Rulings: RUL-201 (PRICING_CANON s1 note). Register: AUDIT_2026-10-04_closures.json.
