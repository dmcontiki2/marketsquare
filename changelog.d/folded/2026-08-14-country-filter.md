## 2026-08-14 — COUNTRY-FILTER-1: adventures borderless by default, filterable on request

Kenya's 24 super listings shipped with no row in the Adventures country picker, so the market was
only reachable under "All countries". Botswana had been in the same state since July.

- Kenya and Botswana rows added (the two countries with live listings and no way in)
- `advCountry` now defaults to `ALL` — borderless is the default, matching the 28 Jun ruling that
  travel-planning categories are not local to the buyer. It previously defaulted to `ZA`, which
  pinned every user to South Africa while the browse grid ignored the picker entirely
- `renderGrid()` now honours the country filter for adventures rows, as `renderAdvGrid()` already did
- The choice persists across reloads instead of resetting

No backend change: Branch C still returns every adventure regardless of city. The picker narrows
what was returned; it is not a precondition for reach.

**RG-0073** locks the invariant — every country present in live `/listings` must have a picker row —
so the next market to ship can't repeat this.

Also: the tester-intake maint-scope guard was asserting the pre-GATE-EXEMPT-MAINT-1 scope and
failing on correct code, putting DANGER on every deploy. Rewritten to assert the ruled scope
(`/admin/faults*` + `/dashboard/maint`, exactly). All 17 guards pass.
