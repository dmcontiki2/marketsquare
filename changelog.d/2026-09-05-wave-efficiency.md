## 2026-09-05 — David: "I get the feeling we are not being efficient and effective?" He was right (WAVE-SKIP-EMPTY-1)

Probed the live wave plan rather than answering from the design. Three findings, one of them
embarrassing.

**1. The wave treats 43 cities as equals when two of them hold 91% of the people.**
Pretoria 197 and Cape Town 104 — both the freshly imported club lists — against 31 people spread
across the other 41 cities. **36 of 43 armed cities have nobody to send to at all**, and each one
still got a visit and a 21-second pace: **12.6 minutes of a 15-minute run spent on empty cities**,
and 36 log lines burying the 7 that mattered.

Fixed. `wave_cities.py --with-people` asks the send chokepoint who actually has someone tonight,
so the run visits 7 cities and takes 2.5 minutes instead of 15.1. Asked, never hardcoded — a city
whose pool refills reappears by itself. `rc=2` means "nobody anywhere", a quiet no-op rather than
a failure, and the wave still runs its sync legs.

**2. The 12-per-city cap is guarding the wrong dimension.** What protects us is sending
reputation, which depends on *total* daily volume from our domain — not on how that volume is
divided between cities. Twelve each to 43 cities is the same load as 500 to one. So the cap slows
the only two cities that have anyone and protects nothing. Recorded, not yet changed: raising
total throughput is a deliverability judgement worth taking deliberately rather than in the same
pass as a bug fix.

**3. One wave per city per calendar day is a clock, not a gate.** Pretoria could send, see clean
bounces within the hour, and go again — instead it waits for tomorrow because the rule counts
days. Same class as the two brakes retired earlier today.

**What is working and was left alone:** the doubling. Pretoria's 197 club addresses have never
been mailed; starting at 12 and doubling only after a clean result is prudent, not slow.

**The embarrassing part, recorded because it is the lesson.** The skip-empty filter shipped
broken for ten minutes. `_has_people()` fails OPEN by design — a city it cannot evaluate is
visited, since skipping a city that has people is a real loss. But run as a script, `sys.path[0]`
is `scripts/`, so the emailer package was not importable, every city threw, every city failed
open, and the filter silently did nothing while reporting success. **A guard that fails open must
be asserted on its ability to fail CLOSED**, or it is decoration. The ledger leg now checks the
import path exists and that the flag returns fewer cities than the policy arms.

Visual for David: `Visuals/wave_launch_plan.html`.
