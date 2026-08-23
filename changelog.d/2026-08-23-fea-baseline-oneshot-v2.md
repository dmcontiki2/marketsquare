## 2026-08-23 — update_fea_baseline.bat v2: wrong copy targeted, guard added

First run hit FileNotFoundError: the bat SSHed to the SOURCE CLONE
(/opt/marketsquare-src), but fea_integrity_check.py resolves index.html/ms.js/ms.css
and its baseline BESIDE ITSELF — the live instrument is the copy in the web root
(/var/www/marketsquare, sensor.py ROOT, the one the 01:30 cron runs). v2 targets that
copy. Second defect the run exposed: a traceback flowed through to the eyeball pause
as if it were a delta — v2 aborts unless step 1 returns FEA JSON, so nothing is ever
updated on garbage input. No ledger entry: first-run path slip fixed same session, and
the only assertable form is a static tautology of the fix; recurs -> entry.
