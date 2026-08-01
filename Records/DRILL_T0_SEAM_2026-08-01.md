# T0 Ban Drill — seam level, real keys (1 Aug 2026)

**Scenario:** `AI_DRILL_BAN=anthropic` + no Anthropic key present — Claude fully absent.
Real OpenAI key (server lane). Breaker attached (temp DB). App-side call shape
(`provider="anthropic"` requested, as production would).

| Tier | Verdict | Served by | Model | Reply |
|---|---|---|---|---|
| haiku | PASS | openai | gpt-5.6-luna | `Well-Worn Brown Leather Couch With Plenty of Life Left` |
| triage | PASS | openai | gpt-5.6-luna | `billing` |
| sonnet | PASS | openai | gpt-5.6-terra | `{"fair":false,"estimate":7200}` |
| vision | PASS | openai | gpt-5.6-luna | `vision lane alive` |

**Verdict: PASS — every tier served with Claude absent; banned lane wrote no state.**
4 rows are the SERVING lane's (openai) success bookkeeping — correct and desired. The banned lane (anthropic) wrote ZERO rows; statelessness of the drill overlay is proven by test_ai_breaker.py test_09.

Scope honesty: this proves the SEAM serves every tier with Claude absent. The FULL
live-app T0 drill (BIT journeys + real vision-draft + paid flagship on trustsquare.co)
runs post-deploy per AI_AUTO_FAILOVER_P2_DESIGN §8, and logs as the first monthly drill.
