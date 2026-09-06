## 2026-09-06 — DMARC aggregate reports reviewed; sending-domain reporting gap logged (RG-0305)

**Trigger.** Microsoft DMARC aggregate report received 03:21 SAST for `learn.trustsquare.co`.
David asked whether it needed an action.

**What the reports actually say** (PROBED — attachments decompressed and parsed, not inferred):

- 6 Sep report (window 4–5 Sep): 3 messages, all from Amazon SES / Resend
  (54.240.48.48, 54.240.11.35, 54.240.48.65) to `ucedaschool.edu`, `pace.edu`,
  `nysid.edu`. DKIM (`resend` + `amazonses.com` selectors) **pass**, SPF on
  `send.learn.trustsquare.co` **pass**, disposition `none`. Clean.
- 5 Sep report (window 3–4 Sep): 11 records / 11 messages. 10 full pass.
  **1 fail** — source 35.174.145.124 (AWS EC2, not SES) to `lbc.edu`, both DKIM
  signatures broken, SPF softfail, envelope-from still `send.learn.trustsquare.co`.
  Reading: a **forwarder/inbound scanner re-injecting our own message**, not a spoof —
  a spoofer carries no SES DKIM header and does not reuse our envelope-from.
  Disposition `none`, so nothing was affected either way.

**Verdict: no action required on the .edu lane.** LEARN-LANE-1 (RUL-059d) is
authenticating correctly in the wild. Policy deliberately stays `p=none` on both
sending subdomains — the forwarder fail is exactly why tightening to
`p=quarantine`/`p=reject` on a two-day sample would be premature.

**Gap found, and it is the real finding.** `mail.trustsquare.co` — the sender for
every non-`.edu` outreach letter (`emailer.py _sender_identity()`) — publishes **no
`_dmarc` record of its own**. It therefore inherits the parent zone
`trustsquare.co`, whose `rua` is `rua@dmarc.brevo.com`. Brevo receives those
aggregate reports; we never see them. The busier of the two outreach lanes is the
one we are blind on.

**Logged as RG-0305 (OPEN)** in `scripts/regression_ledger.py` — DNS-probes both
sending subdomains via DoH, passes `learn`, fails `mail`, prints READY TO LOCK the
moment the record appears. Not executable from a session: the sandbox holds no
Cloudflare credential and entering one is barred, so the machinery remembers it
instead of a sentence to David (RUL-037).

**The fix, when access exists** — one additive, monitor-only Cloudflare record,
DNS-only (grey cloud):
`TXT  _dmarc.mail  →  v=DMARC1; p=none; rua=mailto:dmarc@trustsquare.co`
`p=none` blocks nothing, so it cannot cost a delivery.

**Note.** The ledger file took two concurrent-writer id collisions during this session
(another session appended RG-0302/0303/0304 while this entry was being written);
resolved by re-reading and taking the next free id, per the LOCKED-never-moves rule.
