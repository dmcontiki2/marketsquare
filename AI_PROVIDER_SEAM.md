# AI Provider Seam (D1-FIX) — make Claude a swappable plug-in

**Goal:** swap the inference vendor (Claude → OpenAI → local model → …) in ONE place, with no-to-minimal downtime, exactly as `ai_service_tiers.DEFAULT_PROVIDERS` lets us swap *feed* providers. Today Anthropic is hardwired into ~15 BEA call sites (key + endpoint + headers + model). After this, those call sites call `ai_provider.complete(...)` and the vendor is a config choice.

## Design (mirrors the existing feed-provider pattern)
One module, `ai_provider.py`, exposing a tiny stable interface the whole app calls:

    ai_provider.complete(messages, *, task="haiku", max_tokens=700, system=None) -> AIResult
      # AIResult = {text, in_tokens, out_tokens, provider, model}

- **`task`** is an ABSTRACT tier name ("haiku" / "sonnet" / "vision" / "triage"), NOT a vendor model string. The seam maps task→model per the active provider. Call sites stop naming `claude-...`.
- **Active provider chosen by config** — `AI_PROVIDERS` registry + `AI_ACTIVE` env, default "anthropic". Adding OpenAI/local = add one adapter + flip the env. The cost-ceiling + spend-log wrapper stays in the seam (one place), so metering survives a swap.
- **Message shape** is the app's existing list-of-content-blocks (text + base64 image); each adapter translates to its vendor's wire format. Anthropic adapter = today's exact call.
- **Fail-soft**: if the active provider has no key / errors, the seam can fall back to the next configured provider (any-of, like feeds) or return a typed "unavailable" so the caller degrades honestly (deliver-then-charge already handles "no result = free").

## Why this kills the kill-switch
A vendor going dark (or being used as a Fable-style lever) becomes: set `AI_ACTIVE=openai`, restart. One line. No 15-site emergency. The dependency is no longer *irreplaceable* — which is the whole principle.

## Staged rollout (NOT a blind 15-site rewrite — gated, reversible)
1. **Add `ai_provider.py`** with the Anthropic adapter = byte-equivalent to today's call (proven against one endpoint first). Zero behaviour change.
2. **Route ONE low-risk call site** (photo-orient) through it; verify identical output + spend log. Smoke.
3. **Migrate the remaining ~14 call sites** one at a time, each verify-or-revert, each keeping its `_log_ai_spend` line.
4. **Add a second adapter** (OpenAI or local) behind the same interface; test a swap on staging.
5. Model strings (`AA_MODEL`/`SONNET_MODEL`/`TRIAGE_MODEL`) move INTO the seam's task→model map; call sites no longer reference them.

Each step is independently shippable and reversible. David lands each deploy (touches AI + cost paths).

## The agent layer (BIT/Fix) uses the SAME seam
The BIT's "explain a failure / propose a fix" calls (the convenience tier) route through `ai_provider` too — so Claude is swappable for the agent layer as well, and the load-bearing BIT (detect/mitigate) stays pure-Python with no inference dependency at all.
