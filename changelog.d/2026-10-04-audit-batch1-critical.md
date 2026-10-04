## 2026-10-04 — AUDIT-4OCT Batch 1: the three Critical bugs fixed (AUD-001, AUD-002, AUD-003)

David: *"Resolve the findings of the 4 October 2026 audit ... Batch 1 (this session): the three Critical bugs."*
Each was confirmed in today's code before it was changed (audit ran at db67a6e).

- **AUD-001 — a withdrawn introduction could still be accepted (RG-0812).** CONFIRMED: accept_intro listed the settled
  states one by one (accepted / declined / expired) and missed `withdrawn`, in both the pre-check and the conditional
  UPDATE; decline_intro had the same gap and could rewrite a withdrawn or expired request to `declined` and fire the
  decline webhook. FIX (class): every intro status write is pending-only — `_settled` is an allow-list, both UPDATEs
  require `COALESCE(LOWER(TRIM(status)),'pending') = 'pending'`; estate_agents decline_agent_intro now carries the same
  precondition (its accept already did). scripts/prove_intro_charge_once.py gained section 6 (withdrawn / expired /
  odd case: 409, no charge, record untouched; NULL legacy still pending) and its stale SQL copies were brought up to date.
- **AUD-002 — one Paystack payment could be credited many times (RG-0813).** CONFIRMED: payments.verify_payment pasted the
  caller's text into the Paystack URL unencoded, so `ref#a`, `ref?x=1`, `../verify/ref` reached the same paid transaction
  while the once-only claim keyed on the typed text; same on the seller-plan and wishlist verify doors. Live before the
  fix: `/payment/verify?reference=…%23a` went to Paystack. FIX: payments.valid_reference() (plain characters, fullmatch),
  URL-encoding, and an answer naming another reference is refused; bea_main `_paystack_verified()` is now the ONE caller of
  payments.verify_payment, used by all three handlers, and returns Paystack's own reference — the only key for the claim,
  the already-credited check and the ledger text. Proven by scripts/prove_paystack_ref_once.py (it also caught that `$`
  lets a trailing newline through — fullmatch used).
- **AUD-003 — a crafted Quick link ran script on trustsquare.co (RG-0814).** REPRODUCED in headless Chromium on the old
  file: the injected handler ran 1-6 times per link with no tap. FIX (class, quick.html = genie/HARNESS.html = /q/):
  qEsc()/qPh() beside $(); all seven answer trails, the draft card's title, body and facts, and the hero picture are
  escaped; the item-name redraw uses textContent; qCleanWip() rebuilds resumed answers field by field (on the ?resume=
  reader and the door's stored copy); restore() never goes past the draft; and only her own Google round trip restores
  without a tap (one-use number in localStorage, carried as &rn=) — anyone else's link waits on "Carry on". After the
  fix: 0 runs with and without a tap; the payload shows as text. Harness: scripts/smoke_harness/verify_quick_resume_xss.mjs.
- **Ledger:** RG-0812..RG-0814 added; RG-0550's quick.html snippet updated from `p.innerHTML=c.draftBody` to
  `p.textContent=…` (same behaviour, the assertion followed the safer paint — not weakened).
- **Register:** AUDIT_2026-10-04_closures.json started (same shape as INSPECTION_2026-09-25_closures.json).
