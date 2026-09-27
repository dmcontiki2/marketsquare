## 2026-09-27 — RUL-188 LAUNCHED-MEANS-OPEN + Ripple E2E fixes (RG-0530)

- **PAID-AI-OPEN-1:** the "closed testing until launch" guard in /tuppence/ai-commit now holds only while launch_switches.mode is not live. Live mode = every signed-in customer with Tuppence can buy an AI report (David: "we have launched a month ago ... there is no excuse").
- **Pro gate dormant with feeds off:** the paid-feed class is Pro-only only while a contracted paid feed or the paid-tier master switch is on (_paid_feed_gate_active), as PRICING_CANON's own note says. Today every paid feed is off, so Jacques can run Collectables (5T) and Property Dossier (3T).
- **ID-NEVER-BLOCKS-1:** an unchecked seller ID no longer stops an introduction (main app or Local Market). The buyer sees "Seller ID not yet checked" and a safety line; GET /listings/{id} carries seller_id_checked for the warning only.
- **LANE-TRUTH-1:** ai_provider.complete() without provider= now follows the live AI Providers card (DB standing lane) via ACTIVE_RESOLVER; 247 translation calls ran on Claude on 27 Sep while the card said OpenAI. Startup fallback is now openai (RUL-002).
- **CONFIRM-SIGNIN-1:** the employer/reference confirmation page signs the person in by 6-digit code on the same page and sends the Yes straight after — no more "Please sign in first" dead end.
- **BUZZ-REPLY-1:** replying to a Buzz email reaches the person who buzzed, not support.
- **AI-PREFILL-1:** City and Currency on AI Features forms are real values from the active city, not grey hints.
- **PRICE-DESC-SYNC-1 / DRAFT-TRUTH-1 / SAVED-BTN-1:** a re-priced listing's "Price:" sentence follows the new price; the edit toast no longer says "live" of a draft; Quick's save button reads Saved/Published, never "Saving…" behind the success card (af/zu/xh/nso words added).
- Ledger: RG-0530 added; RG-0495 and the NPR entry re-anchored on _seller_id_checked. RULINGS.md RUL-188.
