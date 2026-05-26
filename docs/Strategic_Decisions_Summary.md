# Trustsquare Strategic Decisions Summary

*Document date: 13 May 2026*

---

## PWA (Progressive Web App) — Selected over App Store

- Launch on iPhone via "Add to Home Screen" — no App Store required, no Apple review gatekeeping
- Add `manifest.json`, service worker, and install prompt to existing trustsquare.co — estimated 1–2 weeks of work
- No Apple 30% cut — Paystack and Stripe payments on the web are fully exempt from Apple's in-app purchase rules
- City Launch emails link to trustsquare.co with a one-line iPhone install instruction — no structural change to the email campaign
- Global reach from day one — any iPhone or Android user with a browser can access the app immediately
- Native App Store app remains an option later, after revenue justifies the 3–6 month, R150K–R500K build cost

---

## Paystack + Global Processor — Dual Processor for Global Day-One Launch

- **Paystack** is the correct and only current payment processor for the SA-registered entity — handles ZA, Nigeria, Kenya, Ghana, Egypt natively with local payment methods including card and mobile money
- **Stripe does NOT directly support South Africa** as a registered business country — SA falls under Stripe's "Extended Network" which operates through Paystack's infrastructure; a standalone Stripe account with SA business details and FNB bank account cannot be created
- Stripe acquired Paystack in 2020 — Paystack IS effectively the Stripe product for Africa
- **For international (USD/EUR/GBP) payments**, three options to evaluate in a future session:
  - **Paddle** — acts as Merchant of Record globally, no US entity or US bank required, settles to FNB account, higher fees (~5% + fixed) but simplest compliance
  - **Lemon Squeezy** — similar to Paddle, simpler setup, good for digital marketplace products
  - **UK Ltd company** (~£50 to register, fully online) — unlocks direct Stripe access and is a common route for SA founders needing global payment reach; aligns well with future offshore restructure planning
- Decision on international processor deferred to next session — launch with Paystack for Africa first while options are evaluated
- Africa-only launch is the interim position; global processor decision does not block Pretoria founding seller cohort

---

## Designed for Offshore Restructure — Structure Preserved, Not Locked

- Operate as TRUSTSQUARE PTY LTD in ZA now — no change to current operations or launch plans
- Keep contracts short-term or month-to-month where possible — avoid long-term agreements in the SA company name that would be costly to transfer later
- Keep shareholder structure simple — no new share issuances or shareholder agreements before international tax consultation
- Offshore restructure target: Mauritius GBC (Global Business Company) — preferred over Isle of Man for SA founders due to the SA-Mauritius Double Taxation Agreement
- Trigger point for restructure: when international revenue reaches approximately $10K–$20K/month — setup cost R50K–R150K in legal and accounting fees
- SA taxes continue on SA-sourced transactions permanently — the offshore structure only captures international revenues in the lower-tax environment
- Engage an SA international tax attorney for a 2-hour consultation (R3K–R6K) before restructuring — not before launch

---

## Trademark and Patent — Registered in David Conradie's Personal Name

- Patent and trademark filed in the name of *David Maurice Conradie* personally — not in TRUSTSQUARE PTY LTD
- TRUSTSQUARE PTY LTD licenses the IP from David via a simple one-page licence agreement — full legal protection and launch sequence unaffected
- Launch sequence preserved: Patent filed → Whitepaper → Launch — no delay or disruption
- When offshore holdco is established, IP is assigned from David personally to the holdco in one clean private transaction — no SA company involvement, no SARS CGT complication
- Instruct your patent attorney from the first meeting: *"File in my personal name with a view to assigning to an offshore holdco later"* — any competent IP attorney will know exactly what this means
- Do not register the trademark in the SA company name — even if filed before the holdco exists, personal name registration keeps the offshore path clean

---

## Stripe Fee Analysis — Payment Tiers and Tuppence Strategy

**Stripe ZA Pay-as-you-go formula:** 0.7% platform + 2.9% processing + $0.30 fixed per transaction

| Tier | Amount | Total Fee | You Receive | Effective Rate |
|------|--------|-----------|-------------|----------------|
| Tuppence (single) | $2.00 | $0.372 | $1.628 | 18.6% ⚠️ |
| Tier 2 | $5.00 | $0.480 | $4.520 | 9.6% |
| Tier 3 | $15.00 | $0.840 | $14.160 | 5.6% |
| Bulk 1 | $10.00 | $0.660 | $9.340 | 6.6% |
| Bulk 2 | $20.00 | $1.020 | $18.980 | 5.1% |
| Bulk 3 | $50.00 | $2.100 | $47.900 | 4.2% ✅ |

- Single $2 Tuppence transactions processed individually carry an 18.6% effective fee — the $0.30 fixed fee dominates small amounts
- Bulk Tuppence purchases are 4.4× more fee-efficient than individual $2 payments — a $50 bulk buy costs $2.10 in fees vs $9.30 for the equivalent 5 individual transactions
- **Goal state architecture:** individual Tuppence spends happen as internal ledger entries against a pre-loaded wallet — the payment processor only sees the bulk top-up charge, never the individual $2 spends — zero per-transaction fees on individual Tuppence use
- This is the same model used by Uber Credits, Airbnb gift cards, and gaming currencies — well-proven pattern
- The existing BEA Tuppence balance and ledger system is already the foundation for this — the top-up mechanic is an extension, not a rebuild
- Incentivise bulk buys with bonus Tuppence (e.g. buy $10 get 11 Tuppence worth) to drive wallet loading behaviour and improve fee economics for both platform and buyer

**Fee analysis applies to whichever global processor is selected in next session — Paddle and Lemon Squeezy have different fee structures to evaluate at that point.**

---

## Infrastructure Redundancy & Storage Architecture — 17 May 2026

### Decision: Write-to-Both Photo Storage

- Every photo upload now writes simultaneously to **Cloudflare R2 (EU)** (primary CDN) and **Hetzner local disk** `/var/www/marketsquare/media/` (redundant mirror).
- R2 remains the primary delivery path — it is a globally distributed CDN with $0 egress, operated by Cloudflare (one of the most reliable infrastructure providers in the world).
- The Hetzner mirror is automatic insurance — if R2 is unreachable for any reason, the local copy is already present, no recovery action needed.
- **JS failover (`r2Fallback()`):** Added to `marketsquare.html`. Every `<img>` that loads from an R2 URL has an `onerror` handler that automatically rewrites the src from `https://pub-xxx.r2.dev/<key>` to `/media/<key>`. From the user's perspective, photos simply load — there is no visible failure state.
- Historical photos already in `/var/www/marketsquare/media/` (from the original local-write phase) are immediately covered by the failover without any migration job.
- **Implementation:** `_s3_upload()` in `bea_main.py` rewritten to write both destinations in every call. R2 failure logs a warning but does not halt the upload — the local write still completes. Local write failure also logs a warning but does not fail the R2 upload.

### Rationale: Risk Posture

The prior architecture had a single point of failure: if Cloudflare R2 had an outage or the S3 credentials expired, every photo on the platform would return a broken image. This is unacceptable for a live marketplace where listing photos are the primary purchase signal. The write-to-both pattern eliminates that risk at zero incremental cost — Hetzner disk space is already paid for under the server subscription.

### Decision: CPX32 Upgrade from 25 May 2026

- **Current:** Hetzner CPX22 — 2 vCPU · 4 GB RAM · 80 GB NVMe · €9.49/month.
- **Upgrade:** Hetzner CPX32 — 4 vCPU · 8 GB RAM · 160 GB NVMe · €15.49/month. Effective 25 May 2026.
- **Cost delta:** €6.00/month. Self-funding: 2 Starter subscribers at $5/month each fully cover the upgrade cost.
- **Trigger for this upgrade:** The write-to-both storage decision means photos now consume disk on both R2 and the local Hetzner disk. CPX22 has 80 GB NVMe — with SQLite databases, OS, app, and logs already occupying ~15 GB, the usable photo headroom on CPX22 is approximately 65 GB (~53,000 listings). CPX32's 160 GB gives ~145 GB usable headroom — sufficient for ~120,000 listings globally without any additional storage provisioning.

### Decision: Hetzner Volume on Standby

- A Hetzner Volume (independent block storage device) at **€0.052/GB/month** is available on standby.
- This is an independent disk that survives server rebuilds and can be attached to any Hetzner server in the same data centre.
- **Activation trigger:** when the CPX32 NVMe disk exceeds 80% utilisation (~128 GB used). At the current storage projection of ~600 bytes/photo-set average (after JPEG compression), this trigger is not expected until beyond 200,000 listings globally.
- **Why not activate immediately:** the CPX32 upgrade alone provides adequate runway for years at current growth projections. The Volume is insurance, not a near-term necessity.

### Storage Projections

| Scenario | Listings | Photos | Total Storage | CPX32 Capacity |
|---|---|---|---|---|
| Pretoria soft launch | 60 | 180 | ~0.1 GB | ✅ Trivial |
| 4-city demo launch | 240 | 720 | ~0.4 GB | ✅ Trivial |
| 10 cities live | 600 | 1,800 | ~1.0 GB | ✅ Comfortable |
| 100 cities live | 6,000 | 18,000 | ~10.4 GB | ✅ Comfortable |
| Global scale (50K listings) | 50,000 | 150,000 | ~29.5 GB | ✅ Well within capacity |

*Photo estimate: 3 images per listing × (200 KB thumb + 400 KB medium) = 1.8 MB/listing × safety factor 1.1 = ~2 MB/listing average compressed.*

### Self-Funding Logic

The platform's own subscription revenue pays for its infrastructure scaling. The CPX32 upgrade (€6/month delta) is covered by 2 Starter subscribers. The Hetzner Volume, if ever activated at 50 GB, costs €2.60/month — covered by 1 additional Starter subscriber. Infrastructure costs grow linearly; subscription revenue grows exponentially with each city launch. The cost structure is structurally sound.

### External API Dependency Audit (17 May 2026)

A full audit of external dependencies was conducted. Risk assessment:

| Service | Purpose | Risk tier | Mitigation |
|---|---|---|---|
| Hetzner (server) | Hosting, storage, compute | Low — Tier 1 EU provider | CPX32 upgrade; Volume standby |
| Cloudflare R2 | Photo CDN | Low-Medium | Write-to-both + r2Fallback() JS failover |
| Cloudflare DNS/DDoS | Domain routing | Low — free tier, no API key | Domain can be moved to another registrar |
| Let's Encrypt | SSL certificates | Low — automated renewal | Standard certbot cron in place |
| Paystack | Payment processing | Medium — single processor | Paddle/Stripe/Lemon Squeezy evaluated as fallback |
| OSM Overpass | POI distance queries | Low-Medium — free, no key | kumi.systems mirror + IPv4 force; graceful degradation if unavailable |
| Nominatim (OSM) | Street address geocoding | Low — free, no key | Geocoding optional; app functions without it |
| GeoNames | Geo seeding (one-time) | Very low — data already seeded | Not a runtime dependency |
| Resend | Transactional email | Low — <3K/month free tier | n8n can switch provider; email not on critical path |

**No consumption-based APIs are active in the production path.** All runtime dependencies are either self-hosted, free-tier, or have the write-to-both / graceful degradation pattern in place.
