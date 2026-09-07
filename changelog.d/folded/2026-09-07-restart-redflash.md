## 2026-09-07 — RESTART-REDFLASH-1: a one-second deploy restart no longer paints the ops map red

**Reported by David:** "Claude, why are everything red?" — screenshot of the +1 page ops map,
NCR & Feedback tab, stamped 01:32 SAST, every live chip reading `offline`, and the Server Health
panel reading *"Health check failed — server may be restarting"*.

**Finding — the server was never down.** Probed live: `/health`, `/health/resources`,
`/dashboard/bit`, `/dashboard/presence`, `/dashboard/summary`, `/dashboard/cost`,
`/dashboard/email-triage`, `/flags` all 200, twice, including a 14-request burst (no rate
limiting). `systemd` reports `NRestarts=0` (nothing ever crashed) and the journal carries zero
errors since startup. The service was stopped and restarted at **23:24:56** and **23:29:16 UTC**
— deploy restarts — each completing startup in about **one second**. David's screenshot is
stamped 23:32 UTC, i.e. the refresh round that landed inside the second restart window.

**Cause.** `omLoad()` polls ~11 feeds every 60s. During the restart second every one of them
rejects at once, and each `.catch` calls `fail()`, which paints its chips red `offline`. That is
PROVENANCE-1 working as designed — the map never invents a number — but a whole-map red flash is
indistinguishable from a real outage, and it read as one.

**Fix.** New `rfetch()` in `dashboard.server.html`: on a network failure or 5xx it waits 2.5s and
tries once more before the failure reaches `.catch`. Every polled read feed now goes through it
(health/resources, presence, summary, cost, bit, email-triage, flags, fixed-costs,
admin/services-status, admin/faults) plus the Server Health and BIT panels. `401/403/404` are real
answers and are **not** retried; a second failure still goes red, so nothing is invented and no
chip shows a stale number. The user-initiated click-to-retest path is untouched.

**Locked.** Regression ledger **RG-0318** asserts `rfetch()` exists and that every polled feed is
routed through it — a new feed added straight to `fetch()` trips it red.

Scope note: the class is *the deploy window*, not one endpoint. Every polled feed got the retry,
not only the ones on the tab David happened to be looking at.
