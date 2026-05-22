# TrustSquare - STATUS.md

## Live State
BEA v1.2.0 · cache v=100 · Session 75 complete · AI3=2T · AI4 yield calc live · AI5 batch cards live · n8n EMAILING trigger wired · 1 Tuppence = $2 · Intro = 1T

## Last Completed (Session 75)
- AI3 price-check raised 1T → 2T (BEA + ms.js)
- AI4 Yield Calculator added to admin Property edit modal + buyer app Property detail cards
- AI5 Batch Cards entry added to Collectors onboarding (step 3) with photo upload, AI analysis, and queue integration
- n8n EMAILING trigger: `_notify_n8n_emailing()` in adventures_run.py; `05_emailing_trigger.json` n8n workflow deployed; `.env` placeholder added

## Last Completed (Session 74 continued 15)
Heritage & amenities auto-link audit — found + fixed local_market key mismatch in _CAT_AFFINITY, backfilled listing 104 wonders, confirmed POI logic correct for Property, smoke test all green

## Cache-busting rule (AI-enforced)
When ms.css or ms.js change, bump the ?v= version in marketsquare.html to match
the current session number. This forces browsers and Cloudflare to fetch the new file.
Current version: ?v=100

## Open Actions (carry forward)
- support@trustsquare.co mailbox - confirm active
- Privacy Policy page - draft and publish
- Counsel brief for EULA review (remaining [COUNSEL REQUIRED] items: NCC reg no, FICA/KYC justification, NCA applicability, FSCA classification, arbitration clause)
- Tuppence refund purge — NEXT_SESSION_TUPPENCE_NO_REFUND.md — must complete before patent filing
- AI audit of marketsquare.html for pre-launch issues
- Featured strip: mark real BEA listings as featured
- ~~**n8n EMAILING trigger**~~ DONE — webhook live at localhost:5678, .env set, tested 200 OK
- **n8n Email David node**: verify `fromEmail` in the 05_emailing_trigger workflow matches the SMTP credential's authorised sender address (currently set to noreply@trustsquare.co)
- **Batch Cards publish fix (Session 76 — HIGH PRIORITY)**: `sbPublishBatchListings()` returns "Publishing failed" despite good connection. Likely cause: `POST /listings` FormData field mismatch or missing required field (seller_email not sent, or BEA rejects price_suggestion string vs numeric price). Debug by checking BEA logs after a publish attempt. Test with a single card first.
- **Subscription + Tuppence dual model (Session 76 — design before code)**: Three subscription tiers: Free (bottom 15% — suburb reach only), Starter ~$5/mo (80% — city reach), Premium ~$15/mo (collectors/investors — global reach + vision/analytics). Tuppence sits on top of subscription as a pay-per-use layer for AI functions — it is NOT a substitute for subscription. Intro fixed at 2T regardless of tier. AI function T-prices to be set after Anthropic cost audit. Pack tiers 20T/50T/100T/250T. The combination means: free-tier sellers can still list and receive intros but only see suburb buyers; $5 sellers get city exposure; $15 sellers get global reach, enhanced AI analytics, and future bank-hold/escrow functions. Tuppence spend is a separate "in the moment" layer that any tier can access.
- **Tuppence pricing strategy (Session 76 — design before code)**: **1 Tuppence = $2 (fixed).** Intro = 1T ($2). Rationale: $2 absorbs invisibly into any meaningful transaction (property, cars, collectibles, vacations). For local market low-value items, cost sits with the buyer who chooses to make contact. Sellers list free always. Casual buyers pay 1T ($2) intro only when they want contact — still affordable as the 80% floor. AI functions to be re-priced after proper Anthropic cost audit — target "subconscious commitment" spend where high-engagement collectors/investors use AI on a roll without friction. Pack tiers 20T ($40) / 50T ($100) / 100T ($200) / 250T ($500). Session 76 task: (1) audit actual API cost per AI function, (2) set T prices with healthy margin, (3) update BEA pack endpoint + Paystack amounts + wallet UI + all in-app cost labels.

## Next Session (Session 76)
Goals:
1. **Batch Cards publish fix** — debug `sbPublishBatchListings()` against BEA logs; fix field mismatch
2. **Tuppence + subscription pricing** — audit Anthropic API costs per function, set T prices with margin, update pack tiers (20/50/100/250T), update Paystack amounts + wallet UI
3. **Yield Calc + AI tools in seller My Space** — add Yield Calc (Property), Rewrite, Why No Intros to seller's own listing edit screen
4. **n8n Email David node** — verify fromEmail matches SMTP authorised sender

Pre-launch rollback checklist (do before go-live):
- grep 🧪 TEST in ms.js → tuppence=50 → 5, fallback '50' → '—', HTML balance values
- Remove Skip buttons in onboarding
- Remove /dev/credit endpoint from BEA
- Switch Paystack to live mode keys
