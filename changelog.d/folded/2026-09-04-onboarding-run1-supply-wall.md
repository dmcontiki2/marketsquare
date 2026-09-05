## 2026-09-04 — Onboarding run 1 (later): the supply wall, and a wait that wasn't

**Fired the permitted wave and PROBED the result: zero emails sent, and that is correct.**
`launch_day_wave.bat` ran through the host queue at 12:51 local. All 14 city lanes dry-ran:
**9 of 14 reported "no sendable agency prospects — top up the pool first"** (Cape Town,
Bloemfontein, East London, Polokwane, Nelspruit, Kimberley, Pietermaritzburg, London,
Sydney, Pretoria, Johannesburg); Durban and Port Elizabeth were latched by stop-loss
(8.3% and 17.6% bounce); New York was held by min-gap (next allowed 5 Sep). Server
`email_events` confirms: 0 sent today. So with the listing floor repaired, **the binding
constraint on the onboarding goal is now SUPPLY, not plumbing.** Queued the two
allowlisted releases: `clean_stoploss_cities.bat` (STOP-LOSS-RELEASE-1 clears Durban and
PE) and `fill_wave_gaps.py` (tops up the nine empty pools).

**RG-0262 LOCKED — WAIT-REDIR-1: an unattended wait that silently wasn't.**
The wave's result file came back `rc=0` with fourteen identical lines of
`ERROR: Input redirection is not supported, exiting the process immediately` — one per
city, from the `timeout /t 20` that paces the sends. `timeout.exe` refuses to run when
stdin is not a console, which it never is under the host queue, so it returns instantly
and the delay simply does not happen; the bat carries on and still exits 0. Delivery was
unaffected (the python legs ran and logged normally), so this cost pacing only — but the
shape is the point: **a DONE with rc=0 on a run where a guard had been erased.** Had the
pacing mattered to a rate limit, nothing anywhere would have said so. Repaired in all five
allowlisted bats that used it (exchange_sync, launch_day_wave, run_wave2_unattended,
sync_to_server, deploy_citylauncher) with the redirection-safe `ping -n N+1 127.0.0.1`
idiom, and RG-0262 now walks every allowlisted bat so a new one trips red. Sibling of
check_bat_crlf's UNATTENDED set, which catches the loud version of this fault (a `pause`
that hangs); this catches the quiet one.
