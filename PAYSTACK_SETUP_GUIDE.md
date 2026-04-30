# Paystack Live Mode Setup — TrustSquare (PTY) Ltd

## What you have ready
- ✅ CIPC Registration: **TRUSTSQUARE (PTY) LTD** · Reg No: 2026/340128/07
- ✅ FNB Gold Business Account: **63208160117** · Branch: 250655 · Swift: FIRNZAJJ

---

## Step 1 — Log into Paystack

Go to **https://dashboard.paystack.com** and sign in.

---

## Step 2 — Complete Business Verification

In the left sidebar: **Settings → Business Information**

Fill in:
| Field | Value |
|---|---|
| Business Name | TRUSTSQUARE (PTY) LTD |
| Business Type | Private Company |
| Registration Number | 2026/340128/07 |
| Business Address | 6 Villa Christiaan, 98 Manie Road, Elarduspark, Pretoria, Gauteng, 0181 |
| Business Email | dmcontiki2@gmail.com |
| Country | South Africa |
| Industry | Marketplace / E-commerce |

**Documents to upload:**
- CIPC Registration Certificate (the CoR15.1A PDF you already have)
- Bank Confirmation Letter (the FNB PDF you already have)
- Your SA ID or passport (as director)

---

## Step 3 — Add Your Bank Account

In the left sidebar: **Settings → Bank Accounts → Add Bank Account**

| Field | Value |
|---|---|
| Bank | First National Bank (FNB) |
| Account Number | 63208160117 |
| Account Name | TRUSTSQUARE (PTY) LTD |
| Branch Code | 250655 |

Paystack will do a small test deposit (a few cents) to verify the account. Watch your FNB app — you'll need to confirm the amount.

---

## Step 4 — Set the Webhook URL

In the left sidebar: **Settings → API Keys & Webhooks**

Set webhook URL to:
```
https://trustsquare.co/payment/webhook
```

Paystack will show you a **Webhook Secret** — copy it. You'll need it in Step 6.

---

## Step 5 — Get Your Live Keys

Still on **Settings → API Keys & Webhooks**:

Once live mode is activated, you'll see:
- **Live Secret Key**: `sk_live_xxxxxxxxxxxxxxxxxx` — copy this

(You can also grab the **Test Secret Key**: `sk_test_xxxxxxxxxxxxxxxxxx` for dev testing)

---

## Step 6 — Update the Server .env

SSH into the server and edit the .env file:

```
ssh root@178.104.73.239
nano /var/www/marketsquare/.env
```

Update these two lines:
```
PAYSTACK_SECRET_KEY=sk_live_YOUR_LIVE_KEY_HERE
PAYSTACK_WEBHOOK_SECRET=YOUR_WEBHOOK_SECRET_HERE
```

Then restart the BEA:
```
systemctl restart marketsquare
```

---

## Step 7 — Deploy the updated files

In PowerShell from `C:\Users\David\Projects\MarketSquare`:

```
scp payments.py root@178.104.73.239:/var/www/marketsquare/payments.py
scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py
ssh root@178.104.73.239 "systemctl restart marketsquare"
```

---

## Step 8 — Verify the connection (no money flows)

Hit this URL in your browser:
```
https://trustsquare.co/payment/test
```

Expected response:
```json
{"status": "ok", "paystack_connected": true}
```

---

## Step 9 — Test a real payment flow with Paystack test cards

Switch back to **test mode** temporarily (use `sk_test_...` key) and run a full end-to-end test using these Paystack test cards:

| Card | Number | Expiry | CVV | Result |
|---|---|---|---|---|
| Successful | 4084 0840 8408 4081 | Any future date | 408 | ✅ Payment succeeds |
| Declined | 4084 0840 8408 4081 | Use CVV 000 | 000 | ❌ Payment fails |

Test flow:
1. Open the buyer app → Wallet → Buy Tuppence
2. Complete checkout with the test card
3. Confirm Tuppence balance increased
4. Check `/payment/test` still returns `paystack_connected: true`
5. Check server logs: `journalctl -u marketsquare -n 50`

Once test passes, switch `.env` back to `sk_live_...` and restart.

---

## What happens during a payment (production flow)

```
Buyer taps "Buy Tuppence"
  → POST /payment/initialize  → Paystack returns authorization_url
  → Buyer redirected to Paystack hosted checkout
  → Buyer pays
  → Paystack fires POST /payment/webhook  (server credits Tuppence — reliable)
  → Paystack redirects buyer back to app
  → App calls GET /payment/verify  (client confirms UI — redundant safety check)
```

The webhook is the **authoritative credit path**. The client-side verify is a belt-and-braces backup.

---

## Notes
- Paystack charges **2.9% + R1** per ZAR transaction (capped at R2,000 per month for high volume)
- 1 Tuppence = R36 → Paystack fee ≈ R2.04 → net to you ≈ R33.96
- Paystack settlements land in your FNB account on a T+1 basis (next business day)
- Keep test mode for development. Only switch to live when you're ready for real buyers.
