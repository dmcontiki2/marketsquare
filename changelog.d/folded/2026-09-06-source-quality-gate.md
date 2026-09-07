## 2026-09-06 — SOURCE-QUALITY-1 + DOMAIN-BOUNCE-RELEASE-1 (the wave can go again, from the lanes that work)

**Asked:** when does the next email go out. **First honest answer:** Wednesday 9 Sep, because
DOMAIN-BOUNCE-1 (shipped this morning) reads 6.61% over its rolling window and holds every wave until
2 and 5 Sep age out. Three days lost punishing a pool for bounces from addresses the clean had already
quarantined. Two fixes, and one near-miss worth recording.

**DOMAIN-BOUNCE-RELEASE-1 — the domain twin of STOP-LOSS-RELEASE-1.** `domain_bounce_state()` now honours
`defaults.domain_bounce_release_at`: the window start moves to the clean, so the gate judges only what we
send from the cleaned list. It never lowers the 5% limit — once 50 post-clean sends exist it rules again
on fresh evidence, and blocks just as hard. `clean_city_list.py` stamps it; today's stamp is back-dated to
the 19:16 SAST run that predates the code (that clean genuinely happened: `rejected_invalid` 256 → 267,
city latches released, DB and policy backups on disk).

**SOURCE-QUALITY-1 — and the rule that was written first and thrown away.** The quality gate was drafted
as `mx_status='mx_ok'`. Probing the pool before trusting it killed it:

| source | sent | bounced | rate | mx state | the mx rule would have… |
|---|---|---|---|---|---|
| register:rrca | 191 | 0 | **0.0%** | unchecked | **BLOCKED** (712 in pool) |
| national key accounts | 19 | 0 | 0.0% | unchecked | **BLOCKED** |
| club:agn | 24 | 1 | 4.2% | unchecked | **BLOCKED** (342 in pool) |
| google_maps | 282 | 22 | 7.8% | mx_ok | allowed |
| openstreetmap | 119 | 13 | 10.9% | mx_ok | allowed |
| teachers_trainers:site | 37 | 6 | 16.2% | mx_ok | allowed |

**MX proves a DOMAIN runs a mail server. It does not prove a MAILBOX exists** — which is exactly what our
8.8% is made of. The rule would have blocked the 1,595 best addresses we own (712 rrca + 342 agn + 266
usatf-ne + 199 wpa + 76 usatf-pacific) and waved through the worst. Replaced with a per-source gate
measured off our own send history: a source with ≥ `source_min_sample` sends **and** ≥
`bounce_stop_min_bounces` bounces **and** a rate over the limit is held; an unmeasured source is allowed,
so a new register lane can prove itself.

**The bounce floor exists for the same reason the city stop-loss has one.** Without it, 2 bounces in 20
sends reads as 10% and holds `teachers_trainers:dbe_emis` — 1,114 addresses, the largest teacher lane we
own — on no evidence. Two bounces is not a rate, for a source exactly as for a city.

**Result:** 6 sources held (site 16.2%, osm 10.9%, adventures 11.8%, teachers:osm 9.8%, google_maps 7.8%,
us_university_tutors 5.8%), every register lane through, **2,872 of 4,125 retained (70%)**. Plan verified:
the only remaining blocks are the daily volume cap and the one-day city gap, both of which clear at
midnight. **The wave goes 00:10 SAST Mon 7 Sep**, drawing Sports Clubs from the 0%-bounce register lanes.
**RG-0314 LOCKED.**
