## 2026-08-21 — ID-NPR-2: Didit wired as the NPR provider; the check is now one API key from live

Follow-on to ID-NPR-1 (RUL-039). David: *"How do we implement the seller check now? I want it
to be live and implemented."*

**Provider chosen: Didit** — self-service key at `business.didit.me`, no contract, no sales
call, no credit card, production keys on signup. That matters more than price here: the
alternative routes (DHA direct, SA aggregators) need accreditation or an account-opening
process we cannot finish ten days from launch.

**Price, corrected.** Didit's marketing page says $2.95 per DHA query; the API reference for
`zaf_africa_national_id` says **$1.10 per successful query**. Against 1T = $2 the check is
comfortably covered either way, but the reference is what bills, so $1.10 is what is recorded.
Their billing rule is *conclusive results only* — not charged when the registry is
unreachable, when fields are missing, or when the request is rejected before reaching the
source — which is exactly what the `billable` flag was built to mirror. We never pass on a
cost we did not incur.

**Outcome mapping, and the one that matters:** `MATCH` verifies. **`PARTIAL_MATCH` does
not** — the ID number exists but a name or date-of-birth field did not match, and that is
precisely the shape of someone using an ID that is not theirs. It is conclusive, so Didit
bills us and we bill the seller, but no tick is granted. `NO_MATCH` and `DOCUMENT_NOT_FOUND`
likewise. Anything else, and every transport failure, is not billable.

**Two SA-specific correctness fixes found while wiring it:**

- **Surname particles.** A naive last-word split turns *Johannes van der Merwe* into surname
  *Merwe*, which the register returns as PARTIAL_MATCH — the seller is charged and refused a
  badge because of our string handling. `_split_name` now walks back through particles (van,
  van der, du, de, le, janse van…), so *Anna Janse van Rensburg* keeps her full surname. A
  large share of South African surnames carry one; this is a correctness requirement here,
  not a nicety.
- **Date of birth is derived from the ID number** (first six digits, YYMMDD, century pivot at
  29) rather than asked for again. Didit requires it, and a field the seller has to retype is
  a field they can get wrong — which would fail the check they just paid for.

Guards now 14 (was 10): the particle splitter, the DOB derivation, the conclusive-outcome
billing gate, and that PARTIAL_MATCH can never be treated as a pass.

**Still not live, and precisely why.** The capability is complete on the server and dark. It
needs (a) David to create the free Didit account and paste `ID_VERIFY_API_KEY` +
`ID_VERIFY_PROVIDER=didit` into the server env — his call, it is an account in his name — and
(b) the front-end render of the green tick, the buy button and the buyer warning, which is
the remaining build. Until both, `is_available()` returns False, no seller can buy a check,
and nothing can be charged.

Cost model impact: nil until armed. When armed, $1.10 per conclusive query recovered by a 1T
($2) charge — flat, per-check, no percentage component, and no exposure when a check fails to
reach the source. Free tier of 500 verifications/month may or may not cover Database
Validation queries; the ledger entry says to confirm that on the first real call rather than
assume it.
