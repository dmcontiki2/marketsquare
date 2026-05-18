# MarketSquare · Feature & Fix Backlog
*Updated Session 45 · 7 May 2026*
*Prioritised by: launch-blocking first, UX polish second, future features third.*

---

## 🔴 Launch Blockers — must fix before public launch

| # | Item | Area |
|---|---|---|
| L1 | **Counsel EULA review** — South African attorney must review and fill all `[COUNSEL REQUIRED]` sections before app goes public | Legal |
| L2 | **Company registration number** — insert Trustsquare (Pty) Ltd reg number into EULA Section 2 and app footer | Legal |
| L3 | **NCC direct marketer registration — counsel to confirm first** — counsel must advise whether TrustSquare (Pty) Ltd is required to register as a direct marketer with the NCC under the CPA. Transactional intro emails to opted-in users are likely exempt; CityLauncher cold outreach may not be. Section 6.6 EULA updated to remove false "is registered" claim and replaced with a compliant placeholder pending counsel confirmation. If registration is required, obtain reg number and insert into Section 6.6. | Legal |
| L3a | **support@trustsquare.co mailbox** — confirm mailbox exists and is monitored before EULA published to production. Used in Sections 5.4, 6.5, 6.6, 7.x, 13, 14 and 15. Operational item, not legal — but EULA is undeliverable without it. | Ops |
| L4 | **Privacy Policy page** — draft and publish trustsquare.co/privacy (required by EULA Section 9.1 and POPIA) | Legal |
| L5 | **FSCA guidance on Tuppence** — confirm Tuppence classification as non-virtual-asset with FSCA or comply if reclassified (EULA Section 12) | Legal |
| L6 | **POPIA consent timing** — counsel must confirm whether magic link email collection constitutes prior consent or whether EULA gate must move earlier in the flow | Legal |
| L7 | **Paystack live mode** — paste `sk_live_` + webhook secret into `.env` once CIPC registration approved | Server |
| L8 | **Tuppence refund language — EULA RESOLVED in v1.3 (17 May 2026)** — EULA Sections 5.1, 5.3, 5.4, 6.3, 6.5, 13, 14.3 fully corrected: charge-on-acceptance-only, Banks Act discretionary-reissuance framing, fraud-aversion clause, Casuals role terminology, ECT Act §44 scope, no ZAR cash conversion. Remaining open: purge from Whitepaper v3 and `marketsquare.html` (six edits flagged in `NEXT_SESSION_TUPPENCE_NO_REFUND.md`). Backend (`bea_main.py`) confirmed clean. | Legal · Product · IP |

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
- Beneficial Ownership filed with CIPC ✅ · Certificate: "Benificial Ownership Certificate for Trustsquare PTY (LTD).pdf"
- `/dev/credit` BEA endpoint removed ✅ · Session 30 · commit 3ce6339
- Dev Tools nav tab removed from admin app ✅ · Session 30 · commit 3ce6339

---
*Next session: start with L1+L2 (remove dev tools), then H1 (Local Market listing parity).*
