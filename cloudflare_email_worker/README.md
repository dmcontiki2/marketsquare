# TrustSquare Inbound Email Worker (Session 94)

Cloudflare Email Worker that forwards inbound `@trustsquare.co` mail to the BEA
AI triage endpoint (`POST /email/inbound`). BEA classifies each email with
Claude and drafts a reply; auto-send stays off until explicitly enabled.

## Architecture

```
Sender → Cloudflare Email Routing → this Worker → POST /email/inbound (BEA)
                                          │                 │
                                          │                 ├─ Claude Haiku classifies
                                          │                 ├─ stores row in email_triage
                                          │                 └─ (optional) Gmail SMTP reply
                                          └─ also forwards a copy to dmcontiki2@gmail.com
```

The worker never replies itself — BEA owns all reply logic and the conservative
auto-send gate. The worker also forwards a copy to the human inbox as a safety
net, so triage augments delivery rather than replacing it.

## One-time deploy

```bash
cd cloudflare_email_worker
npm install
npx wrangler login

# Set the shared secret — MUST equal EMAIL_INBOUND_SECRET in the server's
# /etc/environment (current value is in the Session 94 changelog / ask David).
npx wrangler secret put EMAIL_INBOUND_SECRET

npx wrangler deploy
```

Then in the Cloudflare dashboard:

1. **Email → Email Routing → Email Workers** — confirm `trustsquare-email-triage`
   appears.
2. **Email Routing → Routing rules** — point the catch-all (and/or the
   `support`/`billing`/`legal`/`compliance` addresses) at this worker instead of
   (or in addition to) the current forward-to-Gmail rule.

## Auto-send (off by default)

Auto-reply is gated entirely on the **server**, not here. To enable it later:

1. Generate a Gmail App Password
   (myaccount.google.com/security → App passwords → "TrustSquare BEA").
2. On the server, add to `/etc/environment`:
   ```
   GMAIL_APP_PASSWORD=<16-char-app-password>
   EMAIL_AUTO_SEND=1
   ```
   (`GMAIL_ADDRESS` defaults to dmcontiki2@gmail.com — override if needed.)
3. `systemctl restart marketsquare`.

Even with auto-send on, only routine **support** and **billing** emails that the
model marks `auto_safe` are ever sent automatically. Legal, compliance, disputes,
and anything ambiguous are always drafted and held for human review.

## Review drafts

`GET /admin/email-triage?limit=50` (header `X-Api-Key: <MS_API_KEY>`) lists recent
triaged emails with category, urgency, status, and the drafted reply.
