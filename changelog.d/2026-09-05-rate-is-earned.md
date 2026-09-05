## 2026-09-05 — my own brake was worse than slow: it had disconnected the accelerator (MEASURE-RATE-1 retired)

David: *"Are you still sending email waves as soon as is possible or permissible, rather than on a
planned schedule? We discussed this and want to keep the emails flowing as fast as is possible?"*

He was right to ask. **No.** I had halved `batch_size` from 12 to 6 this morning "for the
measurement week" — which is exactly the calendar-thinking he had ruled against hours earlier in
the same session. Retired the same day it was set.

**The brake was worse than it looked.** The ramp only counts a wave as evidence if it is at least
`min_wave_for_streak` (12). With the base at 6, **every wave was too small to count**, so no city
could ever earn a clean streak and the rate was frozen at base permanently — silently, with
nothing going red. The brake did not merely slow the wave; it disconnected the accelerator.

**What actually governs the rate now**, restored: the ramp doubles a city's batch on each clean
wave (12 → 24 → 48 → 96), and a single dirty wave resets it. Nobody picks a number — "reputation
is earned, not configured", as RAMP-1's own docstring puts it. Measured: pool 332 across 43
cities, **exhausted in 5 nights** at the ramp's pace, against 17 at a flat 12.

Real gates, untouched, and the only things that may hold a send: bounce stop-loss, complaint cap,
suppression register, one-per-org, MX validity, jurisdiction clearance, and one-day-per-city
spacing — that last one is deliverability, not a schedule, and it stays.

Locked as RG-0290, three legs: the ramp is on, the base is never below the ramp's own evidence
floor, and the safety gates still exist. The middle leg is the one that would have caught today.

**Fourth near-miss of the day, recorded because the pattern is the point.** I printed
`defaults.ramp` — which is `null` — and nearly reported the ramp as disabled. It reads the
TOP-LEVEL `ramp` key, and it was on the whole time. Reading a proxy instead of the path the code
takes has now produced three wrong readings and one wrong report in a single session.

**Honest forward look:** at this pace the reachable pool is gone in about five nights, and supply
becomes the binding constraint again around 10 September — earlier than the plan's mid-September
estimate. Scraping and the federation lane earn their place then.
