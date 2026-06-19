# AI Provider Dependency — Posture Note
**19 June 2026 · MarketSquare / TrustSquare · prompted by David's Fable-ban question · companion to ROADMAP_4_AI_INDEPENDENCE**

## The question
After the 12 June US export-control suspension of Claude Fable 5 / Mythos 5: can MarketSquare keep depending on Anthropic; if a returned Fable is heavily monitored will its usefulness drop; and should users wean off Claude toward non-US models or toward OpenAI?

## The honest read

**1. The ban does not touch our production stack.** Fable 5 and Mythos 5 are the *frontier* tier. Haiku 4.5, Sonnet 4.6 and Opus 4.8 — what MarketSquare actually runs — are explicitly unaffected and working. Our core flows don't need frontier-tier capability (ROADMAP_4 deliberately pushes work to deterministic / zero-token and reserves an LLM only where judgment genuinely pays), so the ceiling the ban imposes barely overlaps our operating range. First-order impact on us: low.

**2. The real cost is precedent, not today's capability.** The US has shown it will treat models as export-controlled assets and order a provider to cut foreign access with no notice. That risk is now priced into *every US provider* — which is the key to the "should we switch?" question.

**3. "Big brother" when Fable returns ≠ a worse model.** Export-compliance realistically adds *access-layer friction* (nationality / identity verification, geo-gating, audit logging) — a privacy and onboarding cost, not degraded outputs. The "alignment tax" accuracy stories were about Anthropic substituting more constrained models during the outage gap, not about monitoring throttling answers. A covert spy/throttle tool aimed at foreign users would be a genuine red line — but it is speculative today; treat it as a watch-trigger, not a present fact.

## On the alternatives
- **OpenAI is American.** Claude → OpenAI does *nothing* against the US-government risk in question — same export regime, same possible BIS directive. It only diversifies against Anthropic-specific outages (a real but separate problem — 10+ disruptions since 5 June).
- **Non-US (Qwen / DeepSeek / GLM)** swaps US oversight for Chinese oversight + data-localization + the GPU/cloud export controls that target renting those weights on controlled hardware. Symmetric risk — exactly as David already intuited.
- **The only structural insulation is open-weight models we hold and run ourselves.** No provider sits in the loop to receive an order; weights already downloaded cannot be un-shipped and can move jurisdictions. Caveat: the GPU/hardware layer can still be reached (Remote Access Security Act on cloud-GPU rental).

## Posture (recommended — already largely in flight)
- **Do not wean off Claude reactively.** Keep Claude mid-tier as primary: currently unaffected, strong, cheap. Treat it as *replaceable, not foundational*.
- **Make the open-weight failover a tested first-class path, not a someday-plan.** It already exists (`failover/ai_backends.py`, `eval_golden_set.py`, Phase-0 adapter spec) — keep it warm and run it against the golden set on a cadence.
- **Never architect a core flow that requires frontier-tier US capability for foreign users.**
- **Prefer jurisdiction diversity for the GPU layer** (EU/SA-hosted: Scaleway, OVHcloud) over China-linked capacity.

## Trip-wires that would justify actually accelerating off Claude
1. Restrictions extending *down* to Sonnet / Opus / Haiku (a direct hit on us).
2. Region-based latency / throttle disparities for non-US users.
3. Mandatory usage logging routed to government.

The daily MarketSquare AI-Watch monitor is the instrument for catching these.

## Bottom line
The Fable ban validates the AI-Independence roadmap rather than overturning it. Stay on Claude for now, keep the open-weight failover genuinely ready, and let the trip-wires — not the fear — decide if and when to switch.
