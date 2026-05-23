# TrustSquare - STATUS.md

## Live State
BEA v1.2.0 · cache v=101 · Session 76 complete · AI3=1T · Pack tiers 20/50/100/250T · Batch Cards publish fixed (both apps) · /media/ nginx live · A8 principle locked

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
Current version: ?v=101 (Session 76)

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

## Next Session (Session 77)
Goals:
1. **Yield Calc + AI tools in seller My Space** — add Yield Calc (Property), Rewrite, Why No Intros to seller listing edit screen in buyer app
2. **n8n Email David node** — verify fromEmail matches SMTP authorised sender
3. **Subscription tier design** — sketch gating logic before any code
4. **Batch Cards re-test** — David to re-publish Springbok Rugby Cards via buyer app batch flow; confirm photo appears on listing card (nginx /media/ now live)

Pre-launch rollback checklist (do before go-live):
- grep 🧪 TEST in ms.js → tuppence=50 → 5, fallback '50' → '—', HTML balance values
- Remove Skip buttons in onboarding
- Remove /dev/credit endpoint from BEA
- Switch Paystack to live mode keys
