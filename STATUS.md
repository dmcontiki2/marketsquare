# TrustSquare - STATUS.md

## Live State
BEA v1.3.1 · cache v=105 · Session 77 complete · Three-panel AI3 price intelligence + all Collectors UX fixes deployed

## Last Completed (Session 77)
- AI1 Rewrite button in seller edit screen: rewrites title+description, pre-fills form (1T)
- AI2 Why No Intros? button: 3 actionable fixes with reasoning (1T)
- AI4 Yield Calc button: gross/net yield + SA benchmark, Property only (1T)
- AI session counter retired: /advert-agent/coach now charges 1T from wallet (not session counter)
- /advert-agent/status now returns tuppence_balance; pack purchase UI removed
- Issue 7: AI3 price-check max_tokens 350→600, word-wrap fix, 60-word brevity prompt
- Issue 5: aa_publish EXIF rotation applied before R2 upload
- Issue 6: Collectors cards use object-fit:contain (full card visible, no crop)
- Issue 1: "Add your photos" heading, same-item coach copy, Collectors batch nudge
- Issue 9: AI price disclosure under all price results, EULA clause drafted
- Issue 3+8: Three-panel market intelligence card — SA Market / Assessment (price-anchored) / Official+Global prices
  - ai_suggested_price stored on publish; AI3 anchors verdict to this price
  - Local vs global indicator (🇿🇦 cheaper locally / 🌍 better globally / ≈ similar)
- Cache bumped v=105, all four files deployed, BEA restarted

## Last Completed (Session 76)
- Batch Cards publish fix (admin app): added suburb selector to AI5 panel — BEA was rejecting 400 suburb required
- Batch Cards publish fix (buyer app): sbPublishBatchListings redirected to /advert-agent/publish (was hitting JSON endpoint with FormData); /advert-agent/publish now accepts city param
- Tuppence pricing audit: all AI functions >98% margin at 1T; AI3 Price Check corrected 2T→1T in BEA
- Pack tiers updated: 5/10/25T → 20/50/100/250T ($40/$100/$200/$500); AI Guidance separate pack removed (unified wallet)
- A8 principle: Tuppence is NEVER punitive — codified in PRINCIPLE_REQUIREMENTS.md, AGENT_BRIEFING.md, EULA v1.5 draft, Codex v4.7, marketsquare.html
- Photo media fix: nginx /media/ location block added — aa_publish local fallback photos now served correctly at trustsquare.co/media/*
- EULA v1.5 Draft + Codex v4.7: tracked-change documents created for David's review

## Last Completed (Session 75)
- AI3 price-check raised 1T → 2T (BEA + ms.js)
- AI4 Yield Calculator added to admin Property edit modal + buyer app Property detail cards
- AI5 Batch Cards entry added to Collectors onboarding (step 3) with photo upload, AI analysis, and queue integration
- n8n EMAILING trigger: `_notify_n8n_emailing()` in adventures_run.py; `05_emailing_trigger.json` n8n workflow deployed; `.env` placeholder added

## Cache-busting rule (AI-enforced)
When ms.css or ms.js change, bump the ?v= version in marketsquare.html to match
the current session number. This forces browsers and Cloudflare to fetch the new file.
Current version: ?v=105 (Session 77)

## Scheduled Future Sessions

| Session | Task | Model | Notes |
|---|---|---|---|
| Session 80 | **IP Brief v3 + Patent Strategy v2 + Lawyer Handoff Brief** | **Opus** | Read `SESSION_80_OPUS_IP_BRIEF.md` first. Update all patent docs to reflect A8 (no punitive Tuppence), corrected Tuppence model, new features. Produce lawyer-ready handoff summary before filing. |

## Open Actions (carry forward)
- support@trustsquare.co mailbox - confirm active
- Privacy Policy page - draft and publish
- Counsel brief for EULA review (remaining [COUNSEL REQUIRED] items: NCC reg no, FICA/KYC justification, NCA applicability, FSCA classification, arbitration clause)
- Tuppence refund purge — NEXT_SESSION_TUPPENCE_NO_REFUND.md — must complete before patent filing
- AI audit of marketsquare.html for pre-launch issues
- Featured strip: mark real BEA listings as featured
- **n8n Email David node**: verify `fromEmail` in the 05_emailing_trigger workflow matches the SMTP credential's authorised sender address (currently set to noreply@trustsquare.co)
- **Yield Calc + AI tools in seller My Space (Session 77)**: add Yield Calc (Property), Rewrite, Why No Intros to seller's own listing edit screen in the buyer app
- **Subscription tiers (design before code)**: Free (suburb, 15%), Starter ~$5/mo (city, 80%), Premium ~$15/mo (global + analytics). Design tier-gate logic before coding.

## Next Session (Session 78)
Goals:
1. **Property batch listing — design + build** — estate agents need to list multiple properties at once; design the flow (CSV upload or multi-step wizard with address, bedrooms, bathrooms, price, suburb, photos per property), then build it
2. **n8n Email David node** — verify fromEmail matches SMTP authorised sender
3. **Subscription tier design** — sketch gating logic before any code
4. **Seller My Space AI tools** — add Yield Calc (Property), Rewrite, Why No Intros to seller's own listing edit screen in the buyer app (open action from Session 77)

Pre-launch rollback checklist (do before go-live):
- grep 🧪 TEST in ms.js → tuppence=50 → 5, fallback '50' → '—', HTML balance values
- Remove Skip buttons in onboarding
- Remove /dev/credit endpoint from BEA
- Switch Paystack to live mode keys
