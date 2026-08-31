## 2026-08-31 — OPTOUT-LANE-1 LIVE (5/5) and the first wave sent with a working opt-out

David: *"fix it now and make it live, irrespective of any perceived other blocks. This is a project kill risk."*

### What was broken — four things, every one of which passed a check
1. **No `/optout` route existed anywhere.** 110 emails since 24 Aug carried an unsubscribe link to a URL with no handler. Nobody could opt out.
2. **`_is_suppressed()` failed OPEN.** With no register table it returned `False` — *send it* — while its docstring said the register "is verified before ANY single email".
3. **The pull's SQL was a syntax error since 30 Aug.** `ph` was built as `''opted_out''` (doubled quotes = empty string + bare identifier), so step [1/3] had **never once run** and the local register was never created.
4. **`sync_to_server.bat`'s guards were inert.** Written as a one-line `^&` block, cmd *echoed* them instead of executing — so a failed pull printed **"SYNC COMPLETE — both directions applied and verified"**.

RG-0220 was LOCKED and green across all of it, because it verified that the files *contained the right strings*.

### Built and proven
- **OPTOUT-LANE-1** — `/optout` GET+POST (one click, no login, idempotent, never errors, does not reveal list membership) + `/optout/status` (counts only). Deployed by David; live.
- **SUPPRESS-FAILCLOSED-1** — an absent register now REFUSES. *An absent register is not permission.*
- **PULL-SQL-1** — quoting fixed; proven by executing the generated query against the real schema (112 verdict rows) and by reproducing the old error exactly.
- **BAT-GUARD-1** — guards rewritten as multi-line blocks; the banner now says "pull and push both returned success" because the bat checks two exit codes and verifies nothing.
- **PULL-LOG-1** — failures write `logs/pull_FAILED_*.log` instead of existing only as text in a console a human must read aloud.
- **GOV-DOMAIN-1 (RG-0228)** — government/military domains refused by DOMAIN, complementing PRIV-OFFICER-1's LOCAL-PART rule.
- **`verify_optout_lane.py` (RG-0229)** — five gates along the path a real opt-out travels. **Now 5/5.**

### Two instrument failures caught, both mine
- The route **compiled** while `HTMLResponse` was unimported at that point in the file — first request would have raised `NameError`. Caught by *running* it, not compiling it.
- Every live probe I made returned Cloudflare **error 1010** (bot block on the prober). I nearly reported `/optout` as nginx-gated and `/health` as broken. The control that exposed it was probing `/health` — a path known to be open. The verifier now **aborts** if `/health` is not 200, saying *"fix the probe, not the lane"*, and probes with a browser User-Agent.
- RG-0229 also broke RG-0187's rule by calling `subprocess.run` directly instead of `_harness()` — it would have cried REGRESSION on a machine with no network. Fixed.

### RG-0220 no longer reads strings
It now **executes** the pull's generated query against a real schema, and fails if the `^&` guard form returns or the bat again claims "applied and verified".

### The first clean wave
`National` wave #1: **20 sent, 0 skipped, 0 failed** — Tour Operators 10, Travel Agencies 4, Estate Agents 3, Car Dealers 3.
- **Opted-out addresses emailed: 0**, against a live 7-row register containing three real opt-outs that the send pool had never seen (`thinkdigitalacademy.org`, `ibtc.co.za`, `cityrock.co.za`). First send in the product's life where that is a measured fact.
- **Five privacy desks held** — including `dpns@grp1.co.za`, which no list ever flagged. The July note named three; a blocklist would have caught three; the shape guard caught five.
- Plan said 22 sendable, 20 went: two Estate Agents fell out because the sync landed between plan and send and marked them rejected/bounced. The pool shrank because it got honest.

### Also cleared
`utcnow()` deprecation spam removed from the whole send path (9 sites) — it was burying real output on David's Python 3.14. Guard behaviour re-verified identical after the change.
