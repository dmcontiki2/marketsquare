## 2026-08-17 — COVERAGE-1: the 91k mystery closed at the root
The mystery traffic was OURS: the /launch/ CityLauncher dashboard swept full /listings
payloads for all 93 cities inside its 60-second refresh loop — ~40k requests and
several GB per day from one open tab (referer-proven; the vestigial ph_ filter it
looped for matches ZERO rows). Fix at the root per David ("close it now or it becomes
a huge issue later"): BEA GET /listings/coverage returns every city's counts
(total/demo/real) in one GROUP BY; the dashboard now makes ONE call per refresh with
the old loop kept only as a fallback for a not-yet-deployed BEA. ~99% request cut,
analytics noise gone, edge defenses no longer provoked. RG-0100 LOCKED (endpoint +
no-sweep + live JSON). Cost model impact: POSITIVE — removes GBs/day of self-inflicted
origin transfer.
