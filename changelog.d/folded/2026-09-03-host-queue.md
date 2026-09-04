## 2026-09-03 — HOST-QUEUE-1: no more "David clicks" (RUL-095)

- David: guardrails stay, but as permission requests; the machine does the click. Built on the
  agent that is ALREADY registered and ticking (autodeploy_agent_log.txt: SHIPPED 06:31 today),
  so no new Task Scheduler registration was needed.
- `host_queue/ALLOWLIST.txt` (git push MarketSquare/CityLauncher; the exchange, sync, stop-loss
  and refill bats; exchange import/export + clean_city_list py). `scripts/host_queue_worker.py`
  refuses a request without a permission= line or off the allowlist, runs one at a time oldest
  first, writes `host_queue/done/<name>.result` (verdict + output tail). `scripts/request_host_action.py`
  is Claude's side (requires --permission, pre-checks the allowlist). autodeploy_agent.bat calls the
  worker after git_unlock and before the deploy legs (CRLF preserved; backup .bak-hostqueue-*).
- PROVED worker logic on a temp queue: no-permission → REFUSED, off-allowlist → REFUSED,
  allowed → DONE, requests moved to done/. Host-side execution unproven until the first tick —
  RG-0257 OPEN, prints READY TO LOCK on the first DONE result.
- Reflected: RULINGS RUL-095, STANDING_ORDERS, Projects/CLAUDE.md rule, .gitignore (req/done).
- First real requests queued under RUL-095/RUL-092: git_push CityLauncher (publish exchange/ for
  Dave), git_push MarketSquare, run_bat clean_stoploss_cities.bat (the click left from this morning).
