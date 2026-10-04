## 2026-10-04 — AUDIT-4OCT Batch 3: the remaining High bugs (AUD-004..014, AUD-032..049)

David: *"do you have a batch 3 to perform now?"* Each finding confirmed in today's code first. No price, ruling or table
layout changed. EXECUTED: `scripts/prove_audit_b3.py` (real bea_main.py, throwaway DB) and `scripts/prove_audit_b3_app.js`
(shipped ms.js functions in Node); RG-0871.

**Server**
- AUD-004 (RG-0842): a photo with no advert needs a session; scans are billed to her account or the draft ('draft:<id>'), token-only uploads capped 40/IP/hour; the shared 'photo-upload' pot is gone.
- AUD-005 (RG-0843): web comparables billed and logged per caller, 8 a day, a no-result item not searched again for 6 h. No price change.
- AUD-006 (RG-0844): publish moves only draft / resting / faded; blocked, archived and paused refused; nothing goes live (publish or resume) while an advert is blocked (EULA 14.5).
- AUD-007 (RG-0845): `_LEGAL_SIGNALS` ids corrected and built from estate_agents VERTICALS gate signals. PROBED: the five earned gate credentials live are all house/example accounts.
- AUD-008 (RG-0846): the in-app Home Affairs check stores the confirmed name (users.id_name, existing column).
- AUD-009 (RG-0847): the hard-coded 72-hour sign-in cut-off removed (SIGNIN-LINK-7D's 7 days and agency links' 14-30 now hold); used links remembered 31 days.
- AUD-010 (RG-0848): comps queries read listing_status, live real adverts only, failures logged. PROBED: the query runs on the live schema (Property/Pretoria 17 real live adverts).
- AUD-011 (RG-0849): vertical change -> draft; lapsed-gate agents not listed or reachable (house examples exempt — PROBED: the 3 live agents are house examples).
- AUD-012 (RG-0850): non-Local-Market uploads filed with no LM signal (Edit sends its category); old misfiled uploads listed.
- AUD-013 (RG-0851): invitations change nobody's plan; new accounts get the free seat (10, RUL-048); others are provisioned on acceptance (first sign-in); tier sync only for accepted members; 200 invites/agency/day.
- AUD-014 (RG-0852): the gate decodes a JSON photo list and keeps the good links.
- AUD-032 (RG-0853): five upload handlers are sync (threadpool) — no image/AI/storage work on the event loop.
- AUD-033 (RG-0854): wishlist pushes after the match job commits; max 5 devices per buyer.
- AUD-034 (RG-0855): agency import commits per advert.

**App (ms.js)**
- AUD-035 (RG-0856) hub drops closed requests · AUD-036 (RG-0857) formatZAR uses the shared parser · AUD-037 (RG-0858) Adventures chips mapped from the sellers' own types, empty chips hidden · AUD-038 (RG-0859) search counts by chip key; filter bar tolerant · AUD-039 (RG-0860) Service Type reads service_type · AUD-040 (RG-0861) batch publish handles the Terms 409 · AUD-041 (RG-0862) no AI call on Edit open; plan on tap, escaped · AUD-042 (RG-0863) Local Market form handles the Terms 409 · AUD-043 (RG-0864) Coach LM category normalised (server door too) · AUD-044 (RG-0865) new agency-bound drafts route (+route_policy.json) · AUD-045 (RG-0866) Agent Hub verticals + render guard · AUD-046 (RG-0867) batch price keeps thousands · AUD-047 (RG-0868) Edit uses the trust category · AUD-048 (RG-0869) report photos published (blobs) and shown · AUD-049 (RG-0870) Coach currency from the shared table.
