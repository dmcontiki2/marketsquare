# TrustSquare - STATUS.md

## Live State
BEA v1.3.0 live at trustsquare.co - FastAPI + SQLite (10 tables) + Redis on Hetzner CPX22
- 5 real Property listings live (IDs 93-97, Pretoria)
- 23 / 60 founding sellers registered
- Demo mode accessible via ?demo=1 OR via in-app DEMO/LIVE toggle (top bar)
- marketsquare.html: 340 KB HTML shell (Session 71 +5 KB from new photo-first zones)
- Static assets: /static/ms.css?v=71 (103 KB) + /static/ms.js?v=71 (499 KB), cached 1 year
- World Heritage: 120 sites from BEA /wonders
- Demo data: 293 listings + 40 sellers from BEA /demo-listings and /demo-sellers
- smoke_test.py: 30-check post-deploy safety net
- ALL FOUR APPS GATED: JWT login required on trustsquare.co/, admin.html, dashboard.html, /launch/
- Team logins: Maurice, Maroushka, David Jnr - temp PIN 123456 - forced change on first use
- POST /listings/vision-draft live (Session 70) — photo-first AI onboarding BEA endpoint
- guided-onboard Step 1 rebuilt (Session 71) — multi-photo upload + AI vision flow live

## Last Completed (Session 71)
- Rebuilt guided-onboard Step 1 with 5-zone photo-first AI pattern (Zone A upload → B strip → C overlay → D draft reveal → E skip)
- Added 13 new JS functions: goHandlePhotos, goRenderPhotoStrip, goRemovePhoto, goResetStep1UI, goVisionNext, goRevealDraft, goVisionFieldUpdate, goApplyVisionToStep2, goPreFillStep2Inputs, goImproveDescription, goUndoImprove, goSkipPhotos, goVisionFallback
- Multi-photo input (1–12), thumbnail strip with delete buttons, primary badge
- Animated analysis overlay: spinner + 3 cycling messages + 40s progress bar + client timeout + graceful fallback
- Draft reveal: editable title/description/price, removable tag chips, AI warnings, confidence bar
- "✨ Improve wording" button → calls /advert-agent/market-note → shows improved text with Undo affordance
- goNextStep patched to apply vision draft fields and pre-fill Step 2 inputs
- Cache-bust: ?v=70 → ?v=71; all 30 smoke checks passing

## Last Completed (Session 70)
- Designed Photo-First AI Onboarding complete flow (6 screens, data contract, error states) — documented in bea_main.py lines 7654–7774
- Implemented POST /listings/vision-draft endpoint: accepts 1–12 photos, calls Claude Vision (claude-sonnet-4-6), returns draft listing JSON
- Built category-aware vision prompt covering all 4 categories (Property, Services, Adventures, Cars) with SA price anchors
- Tested live endpoint 4/4 categories passing: Property 95% confidence · Services/Tutor 98% · Cars 85% · Adventures 97%
- All 30 smoke test checks passing; BEA version bumped to 1.3.0

## Cache-busting rule (AI-enforced)
When ms.css or ms.js change, bump the ?v= version in marketsquare.html to match
the current session number. This forces browsers and Cloudflare to fetch the new file.
Current version: ?v=71

## Open Actions (carry forward)
- support@trustsquare.co mailbox - confirm active
- Privacy Policy page - draft and publish
- Counsel brief for EULA review (remaining [COUNSEL REQUIRED] items: NCC reg no, FICA/KYC justification, NCA applicability, FSCA classification, arbitration clause)
- AI audit of marketsquare.html for pre-launch issues
- Featured strip: mark real BEA listings as featured (strip empty on live site)
- Yield System: select SA patent attorney (required before provisional application)
- Yield System: Solar Council review of YIELD_SYSTEM_TECHNICAL_DISCLOSURE v0.2 (Step 0.2)

## Next Session (Session 72)
Goal: Photo-First AI Onboarding — Integration + Polish (Session 3 of 3-session arc)

### Session 72 Build Plan
8. **Multi-photo upload to BEA** — after vision draft accepted, upload all selected photos (not just primary) via existing `/listings/{id}/photo` endpoint; build photo strip into the listing record
9. **Wire into SOB phase 3** — goHandoff() already passes fields to sobState; verify description + tags flow through to the EULA screen and BEA publish call
10. **"Skip photos" in SOB direct path** — if seller arrives via magic link but has no photos, show "Add photos later" option on SOB phase 1 (draft preview); don't block go-live
11. **Smoke test all paths end-to-end:**
    - Path A: magic link → photos → vision → edit → next → SOB phase 3 → publish
    - Path B: magic link → skip photos → Step 2 form → SOB phase 3 → publish
    - Path C: in-app (Route 2) → cat select → photos → vision → publish
12. **Update smoke_test.py** — add checks for go-vision-overlay, go-draft-reveal, go-photo-strip elements in HTML
13. **Deploy + session end checklist**

### Key implementation notes for Session 72
- goHandoff() passes goState.fields to sobState.drafts[0] — verify description included
- Multi-photo upload: iterate goState.photoFiles, POST each to /listings/{id}/photo?email=&is_primary=false (primary already uploaded or will be uploaded first)
- Photo strip format in description: `[photos:url1::caption|url2::caption|...]` — existing BEA format, no changes needed
- Vision overlay CSS uses `animation:spin 0.9s linear infinite` — @keyframes spin added in ms.css v71

## Blockers
- CIPC registration confirmed (2026/340128/07) - Paystack live mode still pending activation
- Git commits must be run by David from PowerShell (sandbox index.lock conflict)
- Patent registration pending - apps gated until SA provisional filed
