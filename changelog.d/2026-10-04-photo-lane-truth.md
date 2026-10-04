## 2026-10-04 — Photo scan lane: what actually runs, and why it costs ~5x the budget (GEMINI-429-TRUTH-1, EVAL-HONEST-1)

David: *"the cost for 20 photos at R2.60 is way too much and much more than our budgeted figures. Which photo AI are you
using?"* MEASURED (ai_spend_log, 45 days): every seller photo scan runs on **OpenAI gpt-5.6-terra** (the reasoning tier,
$2/$12 per Mtok) -- 98 calls, 1,647 in / 39 out tokens, **$0.0038 a scan (~R0.063)**. The budget (Rev B) assumed the
**Gemini** lane at $0.0014 a photo. The Gemini canary (RUL-032) was never armed: its eval had never been run.
- Ran `eval_photo_anon.py` on the server: the first "pass" was false -- Google answered 7 photos, then returned 429s, the
  breaker tripped and the rest silently fell back to terra. **EVAL-HONEST-1:** the eval now disables fallback and the
  breaker detour and voids any answer served by another lane. The brief arming of PHOTO_SCAN_CANARY (≈10 min) was
  REVERSED as soon as this was seen; production stayed on terra throughout (no photo left unscanned).
- Honest run: Gemini answered 10 of 22 -- all 10 correct -- at **866 in / 40 out tokens = ~$0.0008 a scan (~R0.013)**;
  the other 12 were Google 429 **RESOURCE_EXHAUSTED: "You exceeded your current quota, please check your plan and
  billing"**. **GEMINI-429-TRUTH-1:** the adapter reported that 429 as a "connection" failure (Google's error body is a
  JSON list); it now reports the real status.
- ⏳ David: raise the Gemini key's quota/billing in Google AI Studio; then the eval is re-run and, at 100% plate recall,
  the canary is armed per RUL-032.
Cost model impact: at the measured Gemini figure a 20-photo advert costs ~R0.27 to scan (budget R0.47); on terra today
~R1.25 (clean photos; blurred ones more).
