## 8 Sep 2026 — DEVICE-ENROL-2: the ops dashboard no longer says SIGNED OUT to a signed-in browser

David, from his enrolled phone: *"it now opens but then say signed out?"* — and: *"it also does this on
the laptop for the first login, then i just log in again and it is gone."*

**Fault (PROBED, nginx access.log 03:30:25 UTC):** the phone WAS enrolled and the server DID mint its
admin token (`/admin/device-token` 200), but `/dashboard/summary` answered 87 bytes — the anonymous
heartbeat — in the same second, and the page painted SIGNED OUT. Two fetches race on load: the gate's
silent device token and `loadDashboard()`'s first, tokenless summary call. The summary is SLOW (the
server parses STATUS + BACKLOG + CHANGELOG before it redacts), so the token — from the phone's cookie,
or from David's PIN on the laptop — routinely lands while the tokenless call is still in flight.
`hideGate()` then tried to reload, but its guard was `!DATA || DATA.redacted === 'heartbeat'` and
`DATA` starts life as `{}` — truthy, no `redacted` — so the guard was dead exactly when it mattered.
The stale heartbeat landed second and nobody reloaded. A second login worked only because by then
`DATA.redacted === 'heartbeat'` was true.

**Fix (`dashboard.server.html`, three legs):** (a) `hideGate()` reloads unless a TOKEN-BEARING summary
has already painted (`window._dashAuthedPaint`); (b) `loadDashboard()` DROPS a heartbeat that arrives
for a tokenless call once a token-bearing load has started or painted, and otherwise re-fetches once
with the token that appeared mid-flight (bounded — the retry carries the token); (c) a real paint
removes the SIGNED OUT banner, which was inserted once and never taken down. Every `<script>` block
parses (`node --check`, 18/18).

**Locked:** RG-0341 (source, three legs; trips red on the pre-fix file, verified). Scope: the ops
dashboard is the only page today that both mints a token asynchronously and paints anonymous data
on load; admin.html has no summary paint.
