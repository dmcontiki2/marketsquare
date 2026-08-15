- **SPEND-GUARD-1 (David, 15 Aug 2026) — Claude's error, caught by David within minutes.** The first
  cut of RUL-013 routed the pre-launch fix lane at `claude-fable-5` via `ANTHROPIC_API_KEY`: metered
  usage credits at $10/$50 per Mtok, fired by an UNATTENDED loop three times a day with nobody
  watching the meter. David: "eats $ up in seconds... You will bring us to a screeching halt." It
  also broke the standing rule that Fable-via-credits is "reserved for the most important work only"
  (decision note, 11 Jul). **No spend occurred** — the server carries no `ANTHROPIC_API_KEY` and the
  agent had not run since the edit. Removed on both sides: no anthropic `design` row in the seam, no
  `provider="anthropic"` in any live agent call.
- **The corrected design, which was David's point ("let us not break our design"):** Fable still
  resolves pre-launch design requests — **in a Cowork session on the subscription**, where the tokens
  are already paid for. An unattended server process cannot use a subscription; only a session can.
  So the earlier "KNOWN GAP" is not a limitation to close, it IS the design. The agent proposes on
  its normal lane; Fable work happens where it costs nothing extra.
- **TIME-BOXED, and now asserted.** RUL-013's Fable arrangement **ENDS 1 Sep 2026 and does not renew
  by default**. From 1 Sep, design work returns to the allocated design agent or its swapped-out
  option — the `design` task tier (openai `gpt-5.6-sol`, scaleway `mistral-medium-3.5-128b` standby),
  NOT Fable. `rulings_check.py` asserts the expiry wording survives, because a session in October
  reading RUL-013 without it would treat a temporary arrangement as standing policy.
- **RG-0080 locks the general invariant:** a loop nobody is watching never spends per-token. It
  checks the seam has no anthropic design route, the agent pins no anthropic provider in a live call,
  AND that a non-Anthropic design lane still exists so post-1-Sep work has somewhere to go. Sibling
  of RUL-007: unbudgetable cost is barred whether it arrives as a percentage, a retroactive cliff,
  or an autonomous loop holding a metered key — the third form found this week.
- **Numbering note:** this entry was first written as RG-0074 and collided with the concurrent
  session's RG-0074 (admin-gate status branching). Renumbered to RG-0080; theirs untouched. Two
  sessions allocating ledger ids from the same file is a real collision surface — the same class as
  CHANGELOG-COLLISION-1 and STATUS-COLLISION-1, and it has no compiler yet.
