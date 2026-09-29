# GOAL_IMPROVEMENTS — the Goal run's one list

Contract: `GOAL_RUN_PROMPT.md` §5. Newest first. Status is SHIPPED (commit + live proof), BUILT (ready,
not yet live — says why), REVIEW NOW, APPROVED or REJECTED.

## REVIEW NOW

### GI-0002 · 29 Sep · Five test adverts are live and public — archive them (deletion-class, so yours)
- **Evidence:** live DB, 29 Sep 21:05 UTC. #425 and #431 "Home cleaner — Menlyn…" (qa-annatjie), #426 honey
  (qa-honey), #429 Krugerrand (qa-jacques), all from the 27 Sep walks; #438 honey (qa-elsabe7, created today
  20:51 by another lane). In South Africa **2 of the 4 Services adverts and 2 of the 4 Local Market adverts a
  stranger sees are tests.** A buyer who asks for an introduction reaches a test mailbox. Drafts #432, #435
  (PROBE-R24 Nomsa), #439, #440 (this run's walk) are invisible but clutter the data.
- **What I would do:** set `listing_status='archived'` on 425, 426, 429, 431 now, and on 438 once its lane
  has finished with it — archive, not delete, so it is one UPDATE to undo. Drafts the same.
- **Recommend:** yes. And the walks should archive their own adverts as their last step (this run's
  contract already says so; the 27 Sep walk deleted four and left four).

### GI-0003 · 29 Sep · A cleaner has no door in Sell that names her (changes a ruling — yours)
- **Evidence:** walk, step 2 (`docs/E2E_2026-09-29.md`). Sell shows seven category cards; the Services
  card is an electrician's toolbox; the only way to Quick is a small line under the grid. You ruled on
  25 Sep (RG-0478) that Quick inside the app should be "small and unobtrusive", so I have NOT enlarged it.
  Within that ruling I changed the words only (GI-0001).
- **What I would do:** a full-width card the size of Local Market — "Work for yourself? Cleaner, gardener,
  nanny, driver — get seen in a minute" — opening Quick. Reversible, one function.
- **How we'd know:** `onboard_steps` q_door sessions with `src=sell-flow` / `sell-sheet` per week, before vs after.
- **Recommend:** yes. The app's own Sell screen is where a person who already found us decides whether we
  are for her; the Quick door is the only flow built for the people the goal now depends on.

### GI-0004 · 29 Sep · The supply is gone; the people who would list are phone-only (legal + spend — yours)
- **Evidence (probed tonight):** the 28 Sep wave was the first live send in ten days: **13 sent, 1 bounced,
  0 human clicks** (3 opens were Google's image proxy within seconds; the one click and both "Quick door"
  sessions came from a mail scanner 60 s after sending, Windows desktop, same second). One plausible
  human open: `info@tripledrie.co.za`, Outlook, next morning. `[sendable]` now reads **9 · runway 0**.
  Twelve of the 13 went to universities, schools and colleges — organisations, not people who publish.
- **The prize §7 asks for:** `gumtree_prospects` holds **1,111 South Africans with a phone and no email**
  who were already advertising their own services (Pretoria 303 services + 58 tutors + 32 casuals, Durban
  117, Bloemfontein 114, East London 103, Nelspruit 102, PE 92, Cape Town 50…). Scraped 26 Apr. These are
  exactly Quick's people. Email cannot reach them; the email list has no one like them left.
- **Why it is yours:** messaging them cold by SMS or WhatsApp is unsolicited electronic direct marketing to
  non-customers. My reading (not legal advice) is that POPIA s69 needs their consent first, so I do **not**
  recommend a cold SMS/WhatsApp wave to this list and I have built nothing that sends to it.
- **SMS for sign-in (the §7 standing objective) — said once:** SMS in South Africa is pay-as-you-go at about
  **R0.12–R0.27 per message, no monthly fee** (smsmessenger.co.za 2026 price guide; BulkSMS is also
  pay-as-you-go, no monthly fee). One-time sign-in codes for 500 phone sign-ups a month ≈ **R100–R135/month**.
  `sms_provider.py` already supports BulkSMS / Clickatell / SMSPortal and fails dark; only the account and
  `SMS_TOKEN` are missing. I will not raise this again.
- **Recommend:** open the SMS account (tiny, and it opens phone sign-up — RUL-167) and treat the 1,111 as a
  question for a lawyer, not a send. The goal's realistic path remains the employer lane (L27).

## Rows

| id | date | change | evidence | expected effect / how we'd know | size | status |
|----|------|--------|----------|---------------------------------|------|--------|
| GI-0004 | 29 Sep | Reach phone-only sellers (SMS account; legal read on the Gumtree 1,111) | see REVIEW NOW | first phone sign-ups; `users.phone_verified_at` count | major | REVIEW NOW |
| GI-0003 | 29 Sep | Full-width "Work for yourself?" card in Sell opening Quick | walk step 2 | sell-flow q_door sessions/week up | small | REVIEW NOW (ruling change, RG-0478) |
| GI-0002 | 29 Sep | Archive QA adverts 425, 426, 429, 431 (+438, drafts) | live DB 21:05Z | 0 test adverts in the public grid | small | REVIEW NOW (deletion-class) |
| GI-0001 | 29 Sep | **HUB-AGENT-FIT-1**: Seller Hub hides the "Agent Hub — estate, car & tour agents" card when every advert she has is outside Property/Cars/Adventures (shown as before when she has none). **Quick line wording** in Sell and the Sell sheet: "In a hurry? 5-tap Quick listing" → "Cleaner, gardener, nanny, driver? Quick listing" (size unchanged, inside RG-0478) | walk steps 2 and 8 | a new cleaner's hub opens on her own advert, not an agents' offer; sell-flow q_door sessions | small | **BUILT, not live** — `ms.js` and `scripts/regression_ledger.py` are under another lane's work lock (`lm-walk`, taken 21:03Z). Patches in `docs/goal_patches/GI-0001_*.patch`, `node --check` clean. A follow-up is scheduled to apply, ledger, deploy and prove it once the lock clears |
