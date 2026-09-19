## 2026-09-17 — maintenance-loop: the brain's amber was the laptop, not the brain (RG-0382)

**Fault queue: empty.** 0 new, 0 triaged, 0 fix-shipped, 0 escalated (26 verified, 12 closed).
No tester fault work this run. Regression ledger green before and after; no escalation brief
written (no escalations in 24h).

**The one defect this run found was its own instrument.** `/admin/maint/brain` refuses every
caller that is not a process on the box — 403 `brain endpoint is local-only`, MAINT-BRAIN-1's
deliberate control so a leaked maint key can never buy model calls. `maintenance_agent.py`
collapsed that permanent, expected refusal into `AMBER:transport / brain-unreachable`, and
`dashboard.server.html` painted the B2b readiness row amber for it.

That broke the RG-0187 contract at the one instrument gating the whole maintenance lane: an
instrument LIMIT must read NOT EVALUATED, never a FAIL and never a health colour. The harm was
not cosmetic — every remote run painted the same amber a genuine outage would, so a real brain
failure could not report itself in a way anybody would notice.

Fixed on both sides, because a state named honestly by the producer and repainted amber by the
consumer is the same lie with a second opinion:
- `maintenance_agent.py`: `_vantage_refusal()` / `_declined()` classify the local-only 403 apart
  from transport failure; `brain()`, `brain_probe()` and `classify()` all read it as
  `NOT_EVALUATED:remote` / `vantage:local-only`.
- `dashboard.server.html`: the maintenance card renders NOT_EVALUATED grey, labelled
  BRAIN NOT MEASURED, instead of amber.
- The FAIL-SAFE routing to Path B is deliberately UNCHANGED. An unconsultable brain still means
  the human lane; only the NAME of the state changed, because the name is what a person acts on.

**Evidence (PROVED, not read):** 05:37Z run posted `brain_state=AMBER:transport`; a direct POST
returned 403 `{"detail":"brain endpoint is local-only"}`; the 05:42Z run after the fix posted
`brain_state=NOT_EVALUATED:remote`, `error_kind=vantage:local-only`, and `/dashboard/maint`
serves that back.

**RG-0382 LOCKED** — asserts both halves plus the fail-safe, so a future "fix" cannot cure the
label by granting the unconsulted lane autonomy it never had. Its first cut went red against
correct code (a flat 600-char window caught classify()'s later, unrelated pre-launch PATH_A
return); the assertion was fixed the same session to judge the branch's own return statement,
and negative-tested to bite on all three ways the fix could rot.

Not pushed, not deployed — the nightly TSL ships it through the gates.
