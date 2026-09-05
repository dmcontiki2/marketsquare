## 2026-09-05 — SUPPORT-AI-LANE-1: both doors into support now share one engine (DW-102, RUL-102)

**David's correction, and he was right twice over.** Told that support-form messages were being emailed
to him: *"That is a fault, users using the support page should also go to AI and not to me. This was
discussed before and i mentioned 100000 users with support queries which will clogg my email?"*

The record agrees with him. **RUL-069** (30 Aug): *"there should be a firewall between users and my
email. After launch no customer emails should be forwarded to my email. All complaints is done between
the users and the apps complaints AI agent."* **RUL-087** (1 Sep): *"How would i respond to 100's of
emails a day if we get traction?"*

**Two doors, one building, different service.** An email to support@ was classified and answered by the
AI. A message typed into /support was filed as a fault and emailed to a human. Same customer, same
question, and only one of them scales. The second door was wired that way by SUPPORT-FORM-REAL-1 **the
same morning** — by the session that had already read both rulings. That is the lesson worth keeping: a
ruling that lives only in a register a session may or may not read is not enforced.

**The fix is subtraction.** The triage engine was lifted out of `/email/inbound` into `_triage_message()`
and the support form calls the same one — no second classifier, no second auto-send policy, no second
reply template. The notify-a-human email is deleted outright. It runs in the background, so the row is
committed before any AI call and a slow lane can neither lose the message nor make a distressed user
watch a spinner. ONE-REPLY-1 is preserved: one message in, exactly one out, with a plain acknowledgement
as the fallback if the lane cannot run — silence is the one outcome a complaint must never get.

**Proved live, both branches.**
- **TS-0039** *"how do I contact a seller?"* → classified **support**, **answered by the AI**: the reply
  explained the introduction option and Tuppence and gave no phone number, which is correct product
  behaviour.
- **TS-0040** — a formal legal complaint naming POPIA and legal action → classified **legal**, **held**
  as a draft for the admin queue. The customer received only the neutral acknowledgement. No legal
  answer was auto-sent.

**Recorded as RUL-102**, which closes the ambiguity that allowed the breach: RUL-069 says *customer
emails*, and a web form is not literally an email. The firewall is now channel-agnostic — by ruling and
by assertion. Asserted by **RG-0289** (both doors share one engine; legal and compliance may never enter
the auto-send set; nothing in the support lane may name a human address) and by `rulings_check` RUL-102,
whose reflection asserts the **absence** of a personal address — the exact shape of the breach.

Also: reply subjects are now capped at ~58 characters. The first cut used the whole first line of the
message, so a one-paragraph complaint became a subject every mail client truncated mid-word.

Test rows TS-0038/0039/0040 closed; fault queue back to **0 new**.

**Honest limit, unchanged.** Inbound *email* to support@ is still forwarded to David's Gmail by the
Cloudflare catch-all. RUL-069's worker firewall (RG-0212) is built and still unarmed, and arming it
remains his act (RUL-027). This sealed the in-app door, which was ours to seal.
