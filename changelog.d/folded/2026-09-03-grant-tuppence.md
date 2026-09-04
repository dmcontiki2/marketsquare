## 2026-09-03 — GRANT-TUPPENCE-1: the +1 page first-lister bonus function, built

**Trigger:** David asked to credit "our first tutor outside the Conradie/Marietjie circle" (the
Waterkloof Maths/Physical Science listing) 25T and email her. Probed the server first: that is
**listing 381, seller walkthrough.tutor@trustsquare.co, user 284 — the test advert this session's
06:05 SAST EULA-ORDER-1 walkthrough created** (see 2026-09-03-human-clicks.md). Not a real
tutor; no email sent, no credit made. Every other Tutors listing is seed (@trustsquare.co /
example.com) or Marietjie. Zero real first-time listers in the last 30 days.

**Built instead (the specced-not-built +1 function):**
- `POST /admin/tuppence/grant` — admin-JWT guarded; kinds `first_lister_bonus` (once per email,
  idempotent) / `tester_grant` / `goodwill`; amount 1..500; user must exist; writes `transactions`
  (type = kind — NEVER `topup`, NEVER `monthly_allocation`, so revenue metrics stay clean and the
  non-rolling sweep never expires it) + `admin_audit`; returns the new balance.
- `GET /admin/tuppence/recent-listers?days=30` — real first-time live listers (seed filtered),
  with bonus-paid state. Feeds the card.
- +1 page card "First-lister bonus · Tuppence grant" on dashboard.server.html (Launch Switch view).
- `onboarding/first_lister_bonus_email.md` — the welcome + 25T email, Free-tier-safe tips only.
- Ledger RG-0256 (OPEN → READY TO LOCK on ship). Ships via the deploy ref.

Cost model impact: none — grants are operator-initiated, capped at 500T, audited.

**18:20 SAST — shipped + LOCKED.** Deploy ref 6411bf5 live (/health ok). Probed on the origin with a
signed admin JWT: grant → 200 tx #200 balance 25 on the walkthrough test account (our own; the only
account it was safe to prove on); repeat → `already:true`, no second credit; unknown email → 404;
anonymous → 401. RG-0256 → LOCKED. The walkthrough account now carries 25T of test credit — it goes
when David deletes listing 381 / user 284 (reserved).
