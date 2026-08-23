## 2026-08-23 — update_fea_baseline.bat: DW-061's close becomes one double-click

The FEA instrument measures ON-DISK web-root files, so it runs only on the box; the
sandbox has no SSH lane (BatchMode fails, by design). Rather than hand David a command,
the one-shot bat pattern (add_travelpayouts_key.bat precedent): shows the current FEA
delta for the attended eyeball the DW-061 row requires, pauses, runs --update-baseline
at /opt/marketsquare-src via msdeploy, re-checks, and prints a flat OK / still-alerting
verdict. ssh output piped to %TEMP% + findstr, never for /f. DW-061 closes on the next
watch pass after a clean re-check.
