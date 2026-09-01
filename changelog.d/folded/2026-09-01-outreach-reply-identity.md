## 2026-09-01 — OUTREACH-REPLY-IDENTITY-1: the prospect lane was anonymous INBOUND only

**David's question, and it was the right one:** how did a tutor prospect (Alison Tutors) get his
personal address, when a firewall was supposed to prevent exactly that.

**She never had it.** Her reply went to `david@trustsquare.co` — `REPLY_TO` in
`CityLauncher/emailer/emailer.py:81`, with the wave sending as
`David at TrustSquare <david@mail.trustsquare.co>` (the Resend-verified subdomain). That address
forwards into the personal Gmail inbox, which is the only reason it appeared there. **The inbound
half worked exactly as designed.**

**It leaked on the way OUT.** The reply was drafted and sent from the personal Gmail account, so it
left as `dmcontiki2@gmail.com` — sent message `1a05d4a21cfc4d07`, 14:05Z. Claude drafted it there
without checking the send identity; that is the proximate cause and it is Claude's error, not a
tooling surprise.

**But the underlying gap is older and wider than the one draft.** PROBED:
`in:sent from:david@trustsquare.co` returns **zero mail, ever** — the Gmail account has no
"Send mail as" alias for the business address, so *any* reply to *any* prospect from that inbox
leaks the personal address the same way. Four further prospect threads were sitting unanswered in
that inbox at the time of the finding (Addico Group, RE/MAX, Capsicum Cooking, IBTC), each one
carrying the same leak on its first reply.

**RUL-069 does not cover this, by its own words.** The customer-email firewall seals *customer*
mail *inbound* (and is still unarmed — RG-0212 OPEN). Its stated boundary reads: *"the OUTREACH
reply lane (Reply-To david@trustsquare.co on wave mail to prospects) is B2B recruitment mail David
owns personally — it is not customer mail and is not sealed by this ruling."* So this is a
direction and a class the ruling deliberately left open, not a firewall that failed. The lane was
one-way-anonymous and nobody had noticed, because until today nobody had replied.

**RG-0235 OPEN** added — two halves, split deliberately: (a) INBOUND, asserted red-capable every
run, that the wave's `FROM_ADDRESS`/`REPLY_TO` stay trustsquare.co addresses and no personal-webmail
literal appears in the lane; (b) OUTBOUND, which depends on a Gmail send-as alias and **cannot be
probed from the sandbox** — so the entry stays OPEN and says so rather than wearing an unearned
green. Red-capability proven before the green was believed (7 Aug rule): a fixture lane carrying a
gmail.com FROM/REPLY_TO produced three FAILs.

**Closing it is David's act** (account settings + a verification click, RUL-037 reserved class):
Gmail → Settings → Accounts and Import → "Send mail as" → add `david@trustsquare.co`, verify, and
set it default *for replies to the address the mail was sent to*. Promote RG-0235 to LOCKED only
when the alias exists AND an outreach reply is probed leaving under the business address.

**Not doing, per RUL-073:** no correction or apology email to Esther. Sent is sent; one touch stays
one touch. The remedy is upstream.


## UPDATE, same day ~15:30 SAST — the alias is IN, by the root-domain route

Executed with David at the keyboard. The route changed once, mid-flight, and the correction is
worth recording because the first one looked right and was not:

- **First attempt FAILED and the failure was Claude's call.** Alias registered as
  `david@mail.trustsquare.co` (Resend-verified, so SMTP authenticated first time) with Reply-To
  `david@trustsquare.co`. But Gmail sends its confirmation link to the **address being added**, not
  to the Reply-To — and `mail.trustsquare.co` has no MX and no A record, so nothing can accept mail
  there. Bounced: `mailer-daemon@googlemail.com` 14:32Z, *"the domain mail.trustsquare.co couldn't
  be found"*. Claude had probed and cited that missing MX two messages earlier, then failed to
  carry it forward to the verification step.
- **Second attempt SUCCEEDED via root verification.** `trustsquare.co` added as a Resend sending
  domain (region eu-west-1, matching the existing `mail.` lane). Three records added MANUALLY in
  Cloudflare — auto-configure declined deliberately: it takes standing DNS-write on the zone, and
  the August breach reversal is the same principle. PROBED live before believing it: DKIM at
  `resend._domainkey.trustsquare.co` present at 218 chars (identical length to the working `mail.`
  key, so not truncated), `send.trustsquare.co` TXT `v=spf1 include:amazonses.com ~all` + MX
  `feedback-smtp.eu-west-1.amazonses.com` pri 10.
- **Receiving lane untouched, verified after every change**: root MX still
  `route1/2/3.mx.cloudflare.net` (Cloudflare Email Routing). Resend puts its MX on the `send.`
  subdomain, never the apex, which is why root verification is safe here. Resend's "Enable
  Receiving" toggle was deliberately left OFF — arming it would place Resend MX on the apex and
  displace the routing that delivers prospect replies.
- Alias: Name `David at TrustSquare`, address `david@trustsquare.co`, treat-as-alias on, no
  Reply-To needed (the address receives on its own). SMTP `smtp.resend.com:587` TLS, username
  `resend`, key `gmail-sendas-2026-09-01` (Sending access, scoped to trustsquare.co — NOT the
  full-access prod key). Gmail confirmation delivered 15:22Z and clicked.
- **"Reply from the same address the message was sent to"** set — the step that actually closes
  the leak; the alias existing does not.

**RG-0235 STAYS OPEN.** Nothing has been SENT through the new path yet, so the outbound half is
still unmeasured — EXECUTED, not PROBED. It promotes only when a real reply is observed leaving as
`david@trustsquare.co`. The four waiting prospect threads (Addico, RE/MAX, Capsicum, IBTC) are the
natural first measurement.

**RESIDUAL GAP, named not hidden:** the reply-from setting governs REPLIES only. A brand-new
compose to a prospect still defaults to the account's default send-as, which is deliberately left
as the personal address because this mailbox carries personal mail (FNB, CIPC, DebtBusters) as well
as business. So: manual cold compose to a prospect must have its From switched by hand in the
compose window. Cold outreach normally goes through the wave, not by hand, so this is a narrow
edge — but it is the same leak by another door and should not be discovered the hard way twice.
