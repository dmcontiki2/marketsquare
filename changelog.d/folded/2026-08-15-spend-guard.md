## 2026-08-15 — SPEND-GUARD-1: no unattended loop holds a metered key; Fable arrangement time-boxed

The first implementation of RUL-013 routed the pre-launch fix lane at `claude-fable-5` through
`ANTHROPIC_API_KEY` — per-token usage credits, driven by an unattended loop three times a day. That
was wrong and is removed: no anthropic `design` row in the seam, no `provider="anthropic"` in any live
agent call. No spend was incurred; the server holds no Anthropic key and the agent had not run.

Fable still resolves pre-launch design requests, but in a Cowork session on the subscription — an
unattended process cannot use a subscription, only a session can.

The arrangement is time-boxed: it **ends 1 Sep 2026** and does not renew. From then, design work
returns to the allocated design agent or its swap option (`design` tier: openai `gpt-5.6-sol`,
scaleway standby). `rulings_check.py` asserts the expiry wording persists.

**RG-0080** locks the invariant — a loop nobody is watching never spends per-token — and also checks a
non-Anthropic design lane remains, so post-1-Sep work has somewhere to go.
