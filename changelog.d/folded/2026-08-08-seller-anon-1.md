## 2026-08-08 — SELLER-ANON-1: /listings stops publishing seller identity

`GET /listings` returned `seller_email` on all 50 rows, exposing two real founding sellers'
personal Gmail addresses to any anonymous caller. Swept every public endpoint: `/listings` was
the only one. `/demo-listings`, `/demo-sellers`, `/wonders`, `/flags` and `/geo/countries` are
clean — `/demo-sellers` in particular is genuinely anonymous demo data, exactly as designed.

FIX: one line. `_strip_seller_identity()` — which has guarded the local-market feed since PR-29 —
is now applied to each `/listings` row, placed AFTER the founders lookup that legitimately reads
`seller_email`. Checked before editing that the other five fields the helper removes (`name`,
`email`, `photo_url`, `aa_*`) appear on 0 of 50 rows, so nothing in the UI loses data.

WHY IT HAPPENED, which matters more than the fix. The requirement was never misunderstood. The
helper existed. The detail endpoint next door uses an explicit column allowlist commented "No
seller identity returned". RG-0038 asserts the same requirement for the introduction relay. Three
correct implementations, none of them general. `/listings` builds its payload from `SELECT *` and
is therefore default-OPEN: every column added to `listings` becomes public automatically, and a
July changelog entry recorded that property approvingly ("backend serves all columns, so it
surfaces as l.tour"). Anonymity-until-introduction is not a feature of this product, it IS the
product — sellers pay 1T for exactly that — so it cannot rest on somebody remembering.

NEW LEDGER ENTRY RG-0045, deliberately written against the REQUIREMENT rather than a surface:
it reads the real public response bodies of five endpoints and fails on any non-trustsquare.co
address or any identity key. It cannot be satisfied by code that merely looks correct, and it
cannot go vacuous the way RG-0011 did (DW-024) because it asserts on bytes returned, not on a
regex over source. If it can read nothing at all it FAILS rather than passing quietly.

PROVEN, not assumed: run against the live site before deploying, RG-0045 goes RED and names both
addresses and the field. It should flip green on the deploy that carries this fix — and if it does
not, the fix did not work, which is the whole point of writing it this way round.
