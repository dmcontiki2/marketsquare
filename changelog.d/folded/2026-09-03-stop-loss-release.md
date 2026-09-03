## 2026-09-03 — STOP-LOSS-RELEASE-1: a stop-lossed city can now be cleaned and released

- David, 3 Sep: "How do I clear their list?" — there was no answer on disk. The RG-0242 latch had NO release:
  a blocked city never advances last_wave, so the dirty wave stayed "last" forever (New York 5/33 15.2%,
  Pretoria 5/59 8.5%, Polokwane 5/26 19.2%).
- PROBED on a DB copy (sandbox never writes the real DB): 158 of the three cities' sendable rows had never
  been MX-verified. Verdicts: NY 95 pool / 1 no_mx; Pretoria 108 / 9 no_mx; Polokwane 60 / 2 no_mx + 1
  invalid_syntax. 13 rejects total. MX cannot see dead mailboxes on live domains (3 of NY's 5 bounces were
  mx_ok) — so the fix is a RELEASE, not a promise of a clean wave.
- NEW `CityLauncher/clean_city_list.py` (host-side, writes DB): T1-verifies every sendable row in the city,
  quarantines rejects (rejected_invalid) and non-freemail siblings of bounced domains (rejected_bounced_domain),
  then stamps waves_policy cities[city].stop_loss_released_wave = last wave. DB + policy backed up first.
  `clean_stoploss_cities.bat` runs it for NY/Pretoria/Polokwane and prints the resulting plan.
- wave_runner gate_check: stop-loss is skipped ONLY when the stamp equals the current last_wave — one wave
  goes out, its own bounces govern again. Proven end-to-end on the copy: all three cities flip to GREEN.
- Ledger RG-0251 LOCKED (source + behavioural: unstamped blocks, stamped releases, stale stamp blocks).
- NOT EXECUTED on the real DB: desktop-control grant timed out. David's one click: clean_stoploss_cities.bat.
