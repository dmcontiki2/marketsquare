# MarketSquare · Feature & Fix Backlog
*Updated Session 31 · 30 April 2026*
*Prioritised by: launch-blocking first, UX polish second, future features third.*

---

## 🔴 Launch Blockers — must fix before public launch

| # | Item | Area |
|---|---|---|
| L1 | **Remove `/dev/credit` BEA endpoint** — dev-only Tuppence seeding, must not be live | BEA |
| L2 | **Remove Dev Tools nav tab from admin app** — bypasses Paystack entirely | Admin |
| L3 | **Paystack live mode** — paste `sk_live_` + webhook secret into `.env` once approved | Server |
| L4 | **File Beneficial Ownership with CIPC** — legally required by ~13 May 2026 | David |

---

## 🟠 High Priority — needed for a solid user experience at launch

| # | Item | Area |
|---|---|---|
| H1 | **Local Market listings — parity with standard listings** | Buyer app |
| | · Cards should look identical to Property/Tutors/Services cards (photo, title, price, suburb, Trust badge) | |
| | · Detail screen should match the standard detail screen layout (photo carousel, full description, seller stats) | |
| | · Browse page LM banner should use same grid as other categories, not a separate layout | |
| | · LM intro flow should feel the same as standard intro (not a separate code path visually) | |
| H2 | **n8n email notifications** — buyer emailed when seller accepts or declines intro | BEA + n8n |
| H3 | **Seller-facing intro notifications** — seller emailed when new intro request arrives | BEA + n8n |
| H4 | **Maroushka + Dave phone test** — lightbox, back buttons, My Requests tab live test | Testing |
| H5 | **Showcase photos** — add `thumb_url` to demo listings 40–51 (royalty-free images) | Buyer app |
| H6 | **Tutors & Services edit parity** — confirm all structured fields save and display correctly after edit | Buyer + Admin |

---

## 🟡 Medium Priority — polish and completeness

| # | Item | Area |
|---|---|---|
| M1 | **Paystack test card end-to-end test** — run full buy flow with test card, confirm Tuppence credited via webhook | Buyer app |
| M2 | **Subscription flow test** — test Global wishlist tier subscribe/verify/activate | Buyer app |
| M3 | **SA corporate tax rows B30:D30 in cost model** — fill once P&L is finalised | Cost model |
| M4 | **Local Market — wishlist feed integration** — LM listings appearing in "For You" home screen feed with LM badge | Buyer app |
| M5 | **Founding seller count** — currently 23/60, need 37 more before public launch | Content |
| M6 | **Maroushka re-listings** — real founding seller content via admin tool | Admin |
| M7 | **City selector bug audit** — verify geo selectors work on mobile Safari and Chrome Android | QA |

---

## 🔵 Future Features — post-launch Wave 1

| # | Item | Area |
|---|---|---|
| F1 | **Adventures category** — Experiences + Accommodation sub-classes, Trust Score signals | All |
| F2 | **Collectors category** — catalogue reference, condition, edition/year fields | All |
| F3 | **Wave 1 cities** — New York · London · Sydney onboarding and CityLauncher campaigns | All |
| F4 | **Stripe international payments** — needed for Wave 1 non-ZAR buyers (IoM or Singapore entity required) | Payments |
| F5 | **Paystack recurring subscriptions** — automate Global wishlist tier renewal (currently manual) | BEA |
| F6 | **Referral system** — Trust Score +5 for verified referrals | BEA + Admin |
| F7 | **Automated git commits from sandbox** — remove need for David to run PowerShell git commands | DevOps |

---

## ✅ Completed this sprint (Sessions 26–31)

- Local Market full implementation (BEA + buyer + admin) ✅
- Trust Score Hub (BEA endpoint + admin UI) ✅
- Wishlist Feed with Web Push ✅
- Edit-after-publish with version control ✅
- 4-level geo hierarchy (Country → Region → City → Suburb) ✅
- Photo storage migrated to Cloudflare R2 ✅
- `payments.py` + Paystack webhook endpoint ✅
- Full payment callback flow in buyer app ✅
- Sandbox SSH fixed permanently ✅
- CIPC registration + FNB account ✅
- Paystack business verification submitted ✅

---
*Next session: start with L1+L2 (remove dev tools), then H1 (Local Market listing parity).*
