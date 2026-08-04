## 2026-08-03 — Pre-launch gate closed at the Cloudflare edge (GATE-SERVERSIDE-1, shipped)

**David's ruling:** "close it immediately" — and, on being shown Cloudflare's checkout,
"this is very suspect."

**Closed.** A Cloudflare WAF custom rule, `PRELAUNCH GATE - block all except allowlisted IPs`,
action **Block**, active as rule 1 on trustsquare.co:

```
(not ip.src in {<David's IP>}
 and not http.request.uri.path in {"/health" "/payment/webhook"}
 and not starts_with(http.request.uri.path, "/.well-known/"))
```

This blocks at Cloudflare's edge **before anything reaches the origin**, and covers the
documents *and* the JSON API — so the leak where `/wonders`, `/flags`,
`/local-market/listings`, `/geo/cities` and `/tuppence/balance` answered anonymously behind
the "locked" screen is closed by the same rule. No phase 2 needed.

**Verified from an off-allowlist host:** `/` → 403 · `/index.html` → 403 · `/?cb=rand` → 403 ·
`/wonders` → 403 · `/health` → **200**. From David's own IP the site loads normally.

**Exemptions, and why:** `/health` backs `server_deploy.sh`'s health check and auto-rollback —
gating it would make every future deploy roll itself back. `/payment/webhook` must stay open or
Paystack settlements fail silently. `/.well-known/` keeps certbot renewal working.

**Cloudflare Zero Trust Access was rejected deliberately.** Its free tier (50 seats, $0/month)
still requires ticking *"I authorize Cloudflare to charge this card for usage that exceeds free
limits each month until cancellation"* against the card on file. That is the same uncapped
standing-authorisation shape as the silent ~$360 Google Places burn. The WAF rule achieves the
same closure with no subscription, no card and no seats. Cloudflare itself stays — DNS, CDN, R2
and Workers are unaffected; only that one optional paid-tier product was declined.

**Trade-off accepted:** the rule is IP-based, so it has no identity and no audit trail, and
testers need their IPs added (`Security → Security rules → rule 1 → edit the ip.src set`).
Deliberate: this gate is temporary and gets removed at launch.

**Ledger.** `RG-0027` **LOCKED**. It cannot self-verify from an allowlisted network — a 200 from
David's own machine is expected, not a regression, and the entry says so. It fails on the two
things that are always wrong: a 200 from off-list, or `/health` breaking.

**Still shipped but unarmed:** `migrations/005_prelaunch_server_side_gate.py` (nginx `auth_basic`)
stays in the tree as defence-in-depth if the edge rule is ever removed before launch.
