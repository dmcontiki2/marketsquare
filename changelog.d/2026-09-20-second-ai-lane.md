## 2026-09-20 — The failover was ranked but never provisioned (new OPEN ledger entry)

David's Anthropic API organisation was switched off tonight over an unpaid balance of **US$0.19**.
Checking what that breaks turned up something worse than the 19 cents.

`AI_BASELINE.json` ranks a standby lane FIRST in every tier — openai rank 0, anthropic rank 1,
scaleway rank 2 — so on paper the app rides straight through a dead vendor. It does not. Read at
the point of use (`/proc/<pid>/environ` on the running service, per the RG-0147 rule), the live
box carries `ANTHROPIC_API_KEY` and no standby key at all. Every tier has exactly one reachable
lane. One vendor outage — or an unpaid balance of a few cents — takes the entire AI surface down
with nothing to fall to.

**A ranking is not a failover until the key behind the rank exists.** That gap is now an OPEN
ledger entry, so the machinery carries it instead of a sentence in a chat: it passes the day a
second vendor's key is present in the running process, and prints READY TO LOCK then.
Provisioning it is David's — it is a vendor credential and the money behind it is his call.

For the record, what the API credit actually went on: the app's own AI, ~2 cents a day, $3.47 in
total across 853 calls since it started, 484 of them vision calls at $3.27. Console usage for the
last 30 days shows Haiku 4.5 and Sonnet 4.6 only — the two models the app is configured to use.
