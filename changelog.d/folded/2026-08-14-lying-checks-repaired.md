## 2026-08-14 — LYING-CHECKS-1: six instruments repaired, five red cards go green

David's challenge, attended: "why so much issues?" then "remove those six". The answer was
that most of the register was not faults, and the sharpest cluster was instruments that had
stopped telling the truth. Fixed in one session.

- **DW-024 / RG-0011 (the worst class)** — the map-filename regex demanded the closing quote
  right after `.html` while all 9 real rows carry `?v=NNN`, so it matched ZERO rows and
  reported "ok" from 29 Jul. Regex fixed; a zero-match now FAILS loudly; the false LOCKED was
  WITHDRAWN rather than left green — RG-0011 is honestly OPEN and names both hidden debts
  (ZA -> adventures_reserve_map.html, GB -> adventures_uk_map.html). Assertion repaired, never
  weakened, per David's standing rule.
- **RG-0068 (LEDGER-META-1), NEW + LOCKED** — "no assertion on this board may pass by matching
  NOTHING". Guards 4 patterns; goes red if any matches zero. The class fix, so DW-024 cannot recur.
- **DW-039** — smoke_test.py:145 asserted the ABSENCE of code that locked fix RG-0054 had
  legitimately introduced. Now asserts the guard itself. Smoke 29/39 -> 30/39.
- **DW-040 (+ merged DW-002)** — audit_global_qa.py now carries the ledger's reviewer cookie on
  every GET and HEAD, so the armed gate no longer blinds our own instrument. Audit went from
  5 findings incl. 3 CRITICAL to 3 findings, all INFO.
- **DW-001** — VERSION-KEY fires only when the bytes ALSO differ; the server's monotonic `?v=`
  bump records as VERSION-KEY-BENIGN instead of crying drift daily.
- **DW-034** — run_daily_checks.py now seeds the CREDENTIAL (not just the host key) and, where it
  cannot, says "NO CREDENTIAL LOADED - this is NOT an outage" at SEV-4 with a machine-readable
  `credential_loaded` flag. Proven by deleting the key and running cold.
- **DW-009** — the finding was wrong: dashboard.server.html:1133 is a DISPLAY LABEL on the +1
  page's vendor-lane diagram, not a call site; downgrading it would have made the diagram lie
  about what Anthropic offers. Sweep now exempts UI label/caption assignments, plus `.maint_agent`
  run exhaust and `.lintenv`. Warnings 3 -> 2 (both remaining are the genuine DW-021 items).
- **DW-012 — scripts/deep_scan.py, NEW** — the Monday lane owns its own tooling at last: pip for
  ruff/vulture/pylint, eslint@9 into a gitignored `.lintenv` (global npm is refused EACCES).
  4/4 tools ran (ruff 0.16.3, vulture 2.16, pylint 4.0.7, eslint 9.39.5); 175 findings,
  0 crash-class; no cyclic-import/undefined-variable in the five core Python files; no errors
  in ms.js. A tool that cannot install is reported UNAVAILABLE with its reason, never dropped.

Register: 33 open -> 13. Coverage map: 18 green / 5 blue / 5 amber / 6 red / 2 grey.
Ledger: 69 entries, 63 LOCKED all holding, 0 REGRESSED, exit 0.

Also this session: the daily-watch task prompt was amended — the watch now CLOSES an item the
day its check re-passes (the "awaiting David's close" limbo is abolished) and reports real
issues only, with everything else collapsed to one counted line.
