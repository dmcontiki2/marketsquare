# support@trustsquare.co — Mailbox Setup Plan (L3a launch blocker)

**Status:** OPEN · logged Session 100 (1 June 2026)
**Why open:** the AI email-triage pipeline works, but it currently sends replies from
`dmcontiki2@gmail.com` (display name "TrustSquare Support") via Gmail SMTP. There is **no real
`support@trustsquare.co` mailbox** — MX points to Cloudflare Email Routing (forward-only) and
the domain's SPF/DKIM/DMARC are set up for Brevo, neither of which is a send-capable `support@`
identity. At launch, replies must come *from* `support@trustsquare.co`, not a personal Gmail.

---

## Current state (verified Session 100)

| Layer | What's there now |
|---|---|
| **Inbound** | Cloudflare Email Worker → `POST /email/inbound` (auth `EMAIL_INBOUND_SECRET`). MX = `route1/2/3.mx.cloudflare.net` (Cloudflare Email Routing — forwarding only, not a hosted inbox). |
| **Classify/draft** | `_classify_email()` (Claude Haiku) → category + drafted reply, stored in DB. |
| **Send** | `_smtp_send_reply()` → **Gmail SMTP** (`smtp.gmail.com:587`), logs in as `GMAIL_ADDRESS` (= `dmcontiki2@gmail.com`), From header = `"TrustSquare Support" <dmcontiki2@gmail.com>`. Gated by `EMAIL_AUTO_SEND=1` + `GMAIL_APP_PASSWORD`. |
| **DNS already present** | SPF `v=spf1 include:_spf.mx.cloudflare.net ~all`; DMARC `p=none` → `rua@dmarc.brevo.com`; `brevo-code:…` TXT (Brevo domain auth half-done). |

**Problem at launch:** From-address ≠ domain → looks like spoofing to spam filters, exposes your
personal Gmail, mixes personal + support mail, and the EULA (which references support@ in §5.4,
6.5, 6.6, 7.x, 13, 14, 15) is undeliverable until the address is real.

---

## Target setup (no recurring cost)

### A · Receive — Cloudflare Email Routing (already wired, just add the address)
1. Cloudflare dashboard → trustsquare.co → **Email → Email Routing**.
2. Add custom address **`support@trustsquare.co`** → forward to your monitored inbox
   (e.g. `dmcontiki2@gmail.com`). MX already correct — no DNS change needed.
3. (Optional) catch-all → same destination so nothing to the domain is lost.

> Inbound triage already works via the Email Worker → `/email/inbound`; this step just makes the
> human-readable `support@` address resolve so customers/EULA links don't bounce.

### B · Send — switch the reply path to Brevo SMTP, from support@
Brevo is already half-configured in DNS, free tier covers support volume, and it's domain-aligned.

1. **Brevo dashboard** → verify/authenticate the **trustsquare.co** sender domain (finish the
   `brevo-code` + add the DKIM CNAMEs Brevo gives you). Add sender **`support@trustsquare.co`**.
2. Grab a **Brevo SMTP key** (Brevo → SMTP & API → SMTP).
3. Set server env (`/etc/environment`, where the other keys live):
   ```
   SMTP_HOST=smtp-relay.brevo.com
   SMTP_PORT=587
   SMTP_USER=<brevo-account-login-email>
   SMTP_PASS=<brevo-smtp-key>
   SUPPORT_FROM=support@trustsquare.co
   ```
4. **Tighten SPF** to authorise Brevo's senders (Brevo gives the exact include), e.g.
   `v=spf1 include:spf.brevo.com include:_spf.mx.cloudflare.net ~all`, and once aligned,
   move DMARC from `p=none` → `p=quarantine`.

### C · BEA code change (one small, surgical edit — safe driver, not Edit/Write)
In `bea_main.py`, generalise `_smtp_send_reply()` so the host/login/from come from env and
default to the new support identity, keeping Gmail as a fallback:

```python
# env block (~line 903)
SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER", GMAIL_ADDRESS)
SMTP_PASS     = os.getenv("SMTP_PASS", GMAIL_APP_PASSWORD)
SUPPORT_FROM  = os.getenv("SUPPORT_FROM", GMAIL_ADDRESS)

# in _smtp_send_reply()
msg["From"] = formataddr(("TrustSquare Support", SUPPORT_FROM))
...
with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    server.send_message(msg)
```
Backward-compatible: with no new env set, behaviour is identical to today (Gmail). Flip to Brevo
by setting the five env vars above. Deploy via the standard `scp main.py + restart` flow.

### D · Verify before clearing the blocker
1. Send a test query to `support@trustsquare.co` → confirm it forwards to your inbox.
2. Trigger a triage reply → confirm From header is `support@trustsquare.co`, lands in inbox
   (not spam), SPF+DKIM **pass** (check "show original" in Gmail).
3. Then mark L3a DONE in BACKLOG.md + AUDIT_PROGRESS.md.

---

## Ownership
- **You / ops:** Cloudflare routing address (A1–A3), Brevo domain auth + SMTP key (B1–B2),
  env vars on server (B3), SPF/DMARC tighten (B4). These need dashboard/registrar access.
- **Claude (next session):** the BEA code change (C) — one surgical edit, ready to ship the
  moment the Brevo creds exist. Until then the Gmail fallback keeps triage working.
