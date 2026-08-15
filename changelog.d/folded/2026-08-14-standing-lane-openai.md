## 2026-08-14 — Standing AI lane moves to OpenAI (independence ruling)

New order: **1. OpenAI (standing) · 2. Anthropic · 3. Scaleway EU · 4. Grok** (capped, text tiers
only, not wired pre-launch).

The driver is vendor independence rather than cost: Anthropic supplies the guidance layer, and having
the same vendor perform the outsourced production work makes judgement and execution a single
correlated dependency. This extends the existing auditor-independence rationale from review to
execution. Cost independently agrees — the 1 Aug funnel ranks gpt-5.6-luna first on haiku, triage and
vision at +78/78/79% with the golden set passed — but was not the reason.

Also amended: the `$50/90d` absolute-saving floor now applies from first revenue rather than
pre-launch. It requires spend volumes that cannot exist before launch, so as a pre-launch gate it was
unpassable by construction.

`ai_price_card.json` `active_lane` → `openai`; chains reordered in `AI_SWAP_ARCHITECTURE.md`; full
reasoning in decision note Addendum 11. The live `/flags` lane still needs the admin flip — RG-0019
will read red until it does, which is the guard working.
