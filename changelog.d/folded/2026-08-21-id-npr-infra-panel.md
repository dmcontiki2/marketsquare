## 2026-08-21 — ID-NPR-6: the ID-verification lane was missing from the infrastructure panel

David, looking at the +1 page: *"should we not have the new ID checker API/provider here and
live (green)?"* Yes. It should have been there the moment the lane was armed, and it wasn't.

The panel's own header states the doctrine — *"A dead key turns red instead of failing silently
for a month"* — and the code comment beside the dark feeds says it plainer still: *"a partner
you cannot see is a partner that fails silently when its flag flips."* Didit was configured and
serving with no row at all, which is precisely the condition both lines exist to prevent. Every
other external service is listed, including ones that are deliberately dark.

Added, distinguishing three states rather than a binary:
- **ok** — provider named and key present
- **nokey** — provider named, key absent: "lane DARK, no seller can buy a check"
- **warn** — `ID_VERIFY_PROVIDER` set to something unrecognised, so no check can run at all,
  which would otherwise look identical to a missing key
- plus a **warn** if the provider module cannot be imported, naming the deploy manifest — the
  exact failure that was one commit away two days running

**Deliberately PRESENCE-ONLY, and the row says so on its face.** A live probe here would be a
billable DHA query at $1.10, on every dashboard refresh. Green on this row means "provider
named and key present" and must never be read as "a check works" — the same distinction that
made `/id-verify/status` reporting READY not the same thing as the lane being proven. The first
real check is still what proves it (RG-0136, still OPEN).

Ledger RG-0136 now asserts the row exists, that it never calls `verify_id()`, and that the
"presence only" wording stays — so a future edit cannot quietly turn a dashboard refresh into a
spend.

Cost model impact: none, and structurally none — the assertion against a billable probe is the
point.
