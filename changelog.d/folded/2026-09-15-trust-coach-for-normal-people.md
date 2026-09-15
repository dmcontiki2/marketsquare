## 2026-09-15 — The AI trust plan was written for specialists; it now opens with what anyone can do

**David, with the screen in front of him:** "Nothing on it can be clicked, it does not tell how to do it
or give me a single item at a time, no request for a photo, no request for experience, or ask me what i
have? ... Even the request to add degrees, SACE, PCC, DBS... all of these are some specialists type
credentials and not related to a normal person?"

He was right on every point. What the screen actually showed him: five steps, all "Upload your …",
all pointing at "My Space → Credentials & Qualifications → Add credential" — postgraduate qualification,
SACE, PCC/Child Protection/Sexual Offenders register, bachelor's degree, police clearance/DBS.

**Cause — one sort.** `all_missing = sorted(..., key=points, reverse=True)`, reinforced by a prompt line
saying "Order steps by impact (most points first)". The specialist credentials carry the big numbers
(SACE 12, clearances 10, degrees 14), so they win every time and the five-step cap pushes out everything
an ordinary person can do. TS-0011 (Aug) had pushed credentials UP for the opposite complaint; the answer
is order, not removal.

**Fixed (COACH-ORDER-1 / COACH-STEP-1 / RG-0373 LOCKED):**

- Ordered by what this person can do today: profile → ID → referrals → track record → credentials, and
  the prompt is told to keep that order and to word a credential as "if you have one".
- One step at a time on screen, with a progress dot row, Back, and "Not this one — show me the next".
- A real button where the app has a screen for it (Upload ID), and a plain amber line where it does not,
  rather than a button that goes nowhere.
- Each step is matched to its signal by POINTS, not position — probed 15 Sep, a postgraduate-qualification
  step was carrying the referral action because the model had re-worded and merged steps.

Live, same account, after: 1. complete your profile (+5) · 2. photograph your ID (+3) · 3. ask a past
client for a referral (+5) · 4. two more referrals (+3) · 5. *if you have* an Honours certificate (+14).

**Three things he asked for that the LADDER cannot pay for today — David's call, not a bug:**

- **A photo earns nothing.** `universal.profile_photo` is not in `_TRUST_SIGNALS` at all, yet the no-AI
  fallback offered "Profile photo added +10" — points that could never be awarded. Removed rather than
  left to mislead.
- **Experience earns nothing.** The agent profile form already collects `years_experience`; no signal
  scores it, so the coach never asks.
- **Two of the four actions have no screen.** "Add a credential" and "submit a referral" do not exist in
  the app — the coach can only ever describe them, which is why its instructions name a screen
  ("My Space → Credentials & Qualifications") that is not in ms.js.

The open question for David, in one line: should the ladder pay for what an ordinary person actually has
— a photo, stated years of experience, a first employer confirmation — instead of only for certificates?
