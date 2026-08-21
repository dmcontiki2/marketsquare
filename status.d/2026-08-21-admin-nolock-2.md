- **ADMIN-NOLOCK-2 shipped** — David was locked out of the Session Dashboard by his own
  rate limiter (shared bucket with the reviewer lane, counting successes). `/admin/login`
  now has its own failure-only budget; successful token mints cost nothing in either lane;
  429s report exact seconds. Locked as RG-0134. Ledger green, exit 0.
