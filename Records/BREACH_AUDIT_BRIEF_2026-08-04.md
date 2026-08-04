# INDEPENDENT SECURITY AUDIT REQUEST — TrustSquare / Travelpayouts Drive incident

You are an independent application-security auditor. You are being asked to **adversarially review
another AI assistant's incident analysis and remediation**. Your job is not to agree. Assume the
prior analysis contains at least one material error or blind spot, and find it.

Where you disagree, say so plainly and explain why. Where the evidence is insufficient to support a
conclusion, say the conclusion is unsupported rather than filling the gap. Rank anything you find by
severity and by how cheaply it can be fixed.

---

## 1. SYSTEM UNDER REVIEW

| Layer | Detail |
|---|---|
| Product | TrustSquare — a pre-launch peer-to-peer introductions marketplace, `trustsquare.co` |
| Entity | TrustSquare (Pty) Ltd, South Africa. Operator is a sole founder. |
| Source of truth | A Windows folder on the founder's laptop; deployed via `git push origin HEAD:deploy` |
| Deploy chain | laptop → GitHub → `server_deploy.sh` on the server → `/var/www/marketsquare` |
| Server | Hetzner CPX22 VPS. nginx terminates TLS; FastAPI on `127.0.0.1:8000`; SQLite |
| Edge | Cloudflare (proxied), free plan |
| Front page | `marketsquare.html`, deployed as `index.html`, served by nginx: `location = / { root /var/www/marketsquare; try_files /index.html =404; }` |
| Sensitive flow | The **same** `index.html` renders the identity-verification flow (SA Smart ID / passport / driver's licence upload) |
| Auth | Magic-link sign-in; separate bcrypt-checked reviewer credential at `POST /review/login` issuing a 14-day JWT under its own secret |

**Security headers, before and now:** `nginx_security_headers.conf` sets `Content-Security-Policy:
frame-ancestors 'self'` **only**. There is no `script-src` directive. A full CSP was deliberately
deferred because the page carries roughly 163 inline `onclick` handlers. There is no Subresource
Integrity anywhere — zero `integrity=` attributes.

---

## 2. WHAT HAPPENED — OBSERVED FACTS

Facts below marked **[OBSERVED]** were directly measured. Facts marked **[RECORD]** come from the
project's own change log. Nothing here is inferred.

**[RECORD] 2 Aug 2026.** A Travelpayouts affiliate partnership was approved. Their "Drive" loader was
added to the `<head>` of 10 pages: `marketsquare.html` plus 9 `adventures_*_map.html`. The recorded
ruling was *"gate cleared — full Drive on."* The items put to the founder at that moment were: an
EULA disclosure clause, counsel ratification, the accountant's tax treatment of commission income,
and the breadth of Drive's auto-injection. **No security consideration was presented.**

**[OBSERVED] The loader**, at line 4 of the file, before `<meta charset>`:

```html
<script nowprocket data-noptimize="1" data-cfasync="false" data-wpfc-render="false"
        seraph-accel-crit="1" data-no-defer="1" data-cmp-ab="2">
(function () {
  var script = document.createElement("script");
  script.async = 1;
  script.setAttribute("data-cmp-ab","2");
  script.src = 'https://tp-em.com/NTU3Mzkx.js?t=557391';
  document.head.appendChild(script);
})();
</script>
```

Note: `tp-em.com` is a different registrable domain from `travelpayouts.com`. `NTU3Mzkx` is base64
for `557391`, the project ID. The attribute set (`data-cfasync="false"`, `data-no-defer`,
`nowprocket`, `data-noptimize`, `data-wpfc-render="false"`) opts the script out of every common
caching, optimisation and deferral layer, including Cloudflare Rocket Loader.

**[OBSERVED] The pre-launch gate was cosmetic.** It is a `<div id="admin-gate" style="display:none">`
inside the body of the same document, revealed by JavaScript. Its own source comment reads
*"ADMIN LOGIN GATE v2 — inserted by Session 65 — REMOVE BEFORE PUBLIC LAUNCH."* Because nginx serves
the file off disk with no credential check, the complete page reached every requester and JavaScript
then drew a curtain over content that had already arrived.

**[OBSERVED] Browser network capture, taken with the gate displayed and no password entered:**

- `POST https://tp-em.com/collect` — six times in a single page load
- `POST https://tp-em.com/collect_batch`
- `POST https://tp-em.com/link-switch/v1/convert?location=https%3A%2F%2Ftrustsquare.co%2F&trs=557391` → **HTTP 200**
- `GET` of four further script files: `chunk.CIR5CNTC.js`, `chunk.Dux8q1cR.js`, `chunk.DHGU-5oI.js`, `chunk.BD_XmNjn.js`
- `GET https://www.travelpayouts.com/check_auth`
- And, from the same "locked" load, the application's own API returning **HTTP 200 with live data**:
  `/wonders`, `/flags`, `/local-market/listings`, `/geo/cities`, `/tuppence/balance`, and
  `/wishlist/feed?buyer_token=<32-hex>`

**[OBSERVED] Drive configuration at discovery:** monetization boost **Maximum**; *Switch Links* ON
with "switch links from affiliate networks" enabled across 26/26 brands and **Exclude pages: none**;
*Smart Previews* ON for desktop and mobile; *Targeted Offers* ON — described by the vendor as
"analyses visitor behaviour → identifies the offer they're most likely to book → **opens it in a
background tab**", stated to be fully automatic with no configuration.

**[OBSERVED] Secret sweep of all 11 browser-delivered files** (`marketsquare.html`, `ms.js`, the 9
map pages) for `sk_(live|test)_`, `pk_(live|test)_`, `AKIA[0-9A-Z]{16}`, `AIza[...]{35}`,
`gh[pousr]_`, `xox[baprs]-`, bare `eyJ...` JWTs, `Bearer <token>` literals, and generic
`(api_key|secret|password|private_key)\s*[:=]\s*"..."` — **zero matches in every file.**

**[OBSERVED] Server-side secrets** (20 env vars, none of which appear in any browser-delivered file):
`ADMIN_KEY`, `AERODATABOX_KEY`, `ANTHROPIC_API_KEY`, `BREVO_API_KEY`, `CF_CACHE_TOKEN`,
`DUFFEL_ACCESS_TOKEN`, `EMAIL_INBOUND_SECRET`, `GMAIL_APP_PASSWORD`, `GRADING_REVIEW_PASS`,
`HETZNER_S3_ACCESS_KEY`, `HETZNER_S3_SECRET_KEY`, `JUSTTCG_API_KEY`, `MS_ADMIN_KEY`,
`MS_ADMIN_PASSWORD`, `MS_DEPLOY_KEY`, `MS_JWT_SECRET`, `MS_REVIEW_SECRET`, `MS_VAPID_KEY_PATH`,
`PAYSTACK_SECRET_KEY`, `RESEND_API_KEY`.

**[OBSERVED] Browser-held material reachable by any script on the page:**
`sessionStorage`: `ms_admin_token` (sent as the `X-Admin-Token` header), `ms_review_token`,
`_bankNudgeSeen`, `aa_email`, `sob_resume`. `localStorage`: 20 keys including `ms_user_email`,
`ms_user_name`, `ms_seller_profile`, `ms_trust_score`, `ms_superuser`, `ms_city`, photo URLs.

**[OBSERVED]** The one endpoint that mints an API key, `POST /agencies`, is guarded by
`Depends(auth.require_api_key)` — a server-side key, not a browser token.

**Exposure window:** approximately 2 Aug 2026 evening to 3 Aug 2026 evening (~30 hours).

---

## 3. WHAT WAS DONE

1. Loader removed from all 10 pages (−474 bytes each), committed, deployed. **[OBSERVED]** live HTML
   now contains zero `tp-em.com` references.
2. All Drive functions disabled in the vendor panel; boost Maximum → None. Verified: the
   `link-switch` calls and chunk downloads stopped immediately; `/collect` continued until the
   script itself was removed.
3. A Cloudflare WAF custom rule, action **Block**, currently:
   `(not ip.src in {<founder's IP>} and not http.request.uri.path in {"/health" "/payment/webhook"}
   and not starts_with(http.request.uri.path, "/.well-known/"))`
   **[OBSERVED]** from an off-allowlist host: `/` 403, `/index.html` 403, `/?cb=rand` 403,
   `/wonders` 403, `/local-market/listings` 403, `/geo/cities` 403, `/health` 200.
   Exemption rationale: `/health` backs the deploy script's auto-rollback; `/payment/webhook` is
   Paystack; `/.well-known/` is certbot.
4. Cloudflare Zero Trust Access was **declined** — its free tier still requires authorising recurring
   card charges for usage beyond free limits, which the founder judged an unacceptable open-ended
   billing commitment.
5. A regression-ledger assertion that previously required the loader to be *present* was inverted to
   forbid third-party loaders; a new assertion covers the gate.
6. An nginx `auth_basic` migration was written as defence-in-depth but deliberately left unarmed.

**Planned, not yet done:** rotate `MS_JWT_SECRET`, `MS_REVIEW_SECRET`, `MS_ADMIN_PASSWORD` only —
**not** the other 17 secrets, on the reasoning that they never entered a browser. Replace the
client-side curtain with origin enforcement of the existing `/review/login` token. Widen the WAF rule
from a single IP to South Africa so four testers can work.

---

## 4. CONCLUSIONS TO ATTACK

Challenge each of these. State agree / disagree / insufficient evidence, with reasoning.

1. **"API keys were not exposed."** Based on the file sweep and the server-side-only env vars. Is
   this sound? What exposure path would this reasoning miss?
2. **"The material exposure was browser-held session tokens and profile data, chiefly
   `ms_admin_token`."** Is that the correct ceiling, or is there a larger one?
3. **"Rotate three secrets, not twenty."** Is that the right cut? Which of the other 17, if any,
   should move — and by what argument?
4. **"The payload contents are unrecoverable from the operator's side, because the POSTs went
   browser → vendor without traversing the server."** Is that actually true? Is there any artefact —
   CDN, browser, DNS, vendor-facing, legal — that could still establish what was sent?
5. **"A country-scoped Cloudflare block is adequate as a short-term pre-launch gate."** What does
   this fail to defend against, and how badly?
6. **The exemption set** `/health`, `/payment/webhook`, `/.well-known/` — is any of these itself an
   abusable hole while everything else is blocked?
7. **Was anything missed entirely?** Specifically consider: the four extra JS chunks (unexamined),
   service workers / PWA caching persisting old code, Cloudflare's own cache retaining the
   compromised HTML, the 9 map pages as a separate surface, and any supply-chain path through
   `unpkg.com` (Leaflet) or Google Fonts which are also loaded by these pages.
8. **POPIA.** Behavioural profiling of South African visitors by a Hong Kong processor, on a page
   that also collects identity documents, with no consent gate. What are the operator's actual
   obligations — notification thresholds, records, timelines?

---

## 5. OUTPUT REQUESTED

- A verdict on each of the eight items above.
- Anything material the analysis missed, ranked by severity.
- A corrected remediation list if you believe the current one is wrong.
- Explicitly: **what would you have done differently, and what is still unsafe right now?**
