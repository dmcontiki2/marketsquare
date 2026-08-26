- **BAT-CRLF-1 + CSP-SCRIPT-SRC-7 (26 Aug, from David's "add secret bat flickered on and
  off?").** The bat died on LF line endings — `.gitattributes` forced `eol=lf` on everything,
  and cmd.exe cannot follow a caret continuation across a bare LF. 16 `.bat` + 10 `.ps1` were
  LF-only including the whole nightly deploy lane; all 26 normalized, `*.bat/*.cmd/*.ps1`
  pinned to CRLF, `check_bat_crlf.py` guard added (RG-0194 LOCKED) — it immediately found two
  more scripts that could exit unreadably. Separately, the report window widened this morning
  surfaced the real cause of four straight 033 failures on the very next deploy:
  `HTTPSConnection` has no `server_hostname` parameter, so every :443 measurement died on the
  constructor and fell back to measuring the :80 redirect. Fixed; the harness now proves the
  call signature by calling it. Four guards that had been red for 8 scans cleared
  (maintenance-agent, tester-intake, pg-readiness) — all three were correct code failing
  guards that matched PROSE instead of code, the day's recurring class, now fixed at source in
  each. **RG-0188 promoted to LOCKED**: David provisioned the Hetzner token and
  `hetzner_fw_selfheal.py --check` probed the live API clean. Ledger 169 ok / 17 open / 1 red
  (RG-0125, needs a deploy to clear); rulings 57/57.
