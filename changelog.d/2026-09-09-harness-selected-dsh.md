## 09 September 2026 — Harness selected: DeepSeek Harness (dsh). RUL-116 recorded.

David closed his own investigation — many harness courses and videos — and made the call:
*"My conclusion is that Deepseek is currently the best, it is totally plug and play, no bias foundation as
with the other harnesses, and when something doesn't work it gets replaced. It is also free and MIT safe."*

**Verified against the sources, 9 Sep 2026** — all three of his reasons check out:
- **MIT licensed.** Confirmed.
- **No foundation bias.** Model-agnostic by design: switching between remote API providers and local runtime
  servers is a YAML/JSON config change, not a code change.
- **Plug and play / replaceable parts.** Micro-kernel architecture where model adapters, tool registries,
  sandboxes, session state handlers, event dispatchers and UIs are all isolated, interchangeable plugins.
- Also carries an **append-only event log** recording user messages, tool invocations, reasoning states and
  **token metrics**. v0.1 ships Standard / Code / Minimal / Creator configurations.

**Recorded as RUL-116** (append-only, RULINGS.md, 116 rows). Consequences written into the ruling:

- **(b) Claude's technical call under RUL-037:** dsh sits **behind** `ai_provider.py`, never instead of it.
  The app keeps calling `ai_provider.complete(task=...)`; dsh becomes one more adapter alongside
  anthropic / openai / scaleway. One chokepoint keeps the cost ceiling, `_log_ai_spend`, the price card and
  RG-0019 working unchanged. A harness metering its own plug-ins would give three ceilings blind to each
  other — three lanes each inside their own limit can still total past David's, and capping everything is his
  stated condition.
- **(c)** dsh's token log becomes the independent cross-check against `ai_spend_log`, closing drift item
  **D3** in AI_BASELINE.json (the app records the *intended* lane; dsh records the one that answered).
- **(d)** Version **pinned** — v0.1 interfaces move, and a self-updating harness in the live path is an
  unreviewed lane change.
- **(e)** Ahead-of-time work runs on the same harness on a low-priority off-peak queue.
- **(f)** n8n stays workflow automation and does not become the model router; the two are not merged.
- **(g)** Still unconfirmed and David's: whether Scaleway carries DeepSeek models.

`genie/GENIE_COST_MODEL.html` updated to rev 4 — harness named in the architecture band, watch list rewritten
around the decision. Per-call arithmetic unchanged from rev 2 onwards.

**Sources:** InfoQ (DeepSeek Harness open-sourcing, Aug 2026) · The New Stack · DataCamp tutorial.
