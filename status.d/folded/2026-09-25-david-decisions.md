### David's decisions on the 24 Sep do-list — 25 Sep 2026

- Work lock: "Release" -- the cto-fix lane's work shipped with the employer door in one deploy (live 970181a, 06:48Z).
- Daily heartbeat scheduled task: not yet ("Lets not add a new heartbeat as yet"). None created.
- OpenAI / Grok monthly amounts: "Skip" -- the costing page stays as published 24 Sep.
- SMS lane: David reviews it today -- "it is not 'if' but rather how and when". Ready on the Claude side: the
  wave reads the key from MarketSquare/.secrets/sms.env (template in place, only the token line to fill),
  sends only Mon-Sat 08:00-19:00 SAST, first wave 200 of Pretoria's 430 numbers, once per number ever.
